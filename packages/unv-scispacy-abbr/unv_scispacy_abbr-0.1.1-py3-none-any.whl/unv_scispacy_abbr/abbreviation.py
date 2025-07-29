"""Abbreviation detection utilities extracted from the *scispacy* project.

The implementation is identical to the original algorithm described in:

    Schwartz, A. S., & Hearst, M. A. (2003). *A simple algorithm for
    identifying abbreviation definitions in biomedical text.*

All `scispacy`-specific dependencies have been removed so the module can be
used independently.  The public API is fully compatible with
`scispacy.abbreviation`.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import spacy
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span

__all__ = [
    "find_abbreviation",
    "span_contains_unbalanced_parentheses",
    "filter_matches",
    "AbbreviationDetector",
]


# ------------------------------------------------------------------------------------
# Core algorithm helpers
# ------------------------------------------------------------------------------------

def find_abbreviation(
    long_form_candidate: Span, short_form_candidate: Span
) -> Tuple[Span, Optional[Span]]:
    """Return the (short, long) abbreviation pair if *short* can be expanded to
    *long* according to the Schwartz & Hearst rules.
    """
    long_form = " ".join([x.text for x in long_form_candidate])
    short_form = " ".join([x.text for x in short_form_candidate])

    long_index = len(long_form) - 1
    short_index = len(short_form) - 1

    while short_index >= 0:
        current_char = short_form[short_index].lower()
        # Skip non-alphanumeric chars in the short form
        if not current_char.isalnum():
            short_index -= 1
            continue

        # Find matching char in the long form
        while (
            (long_index >= 0 and long_form[long_index].lower() != current_char)
            or (
                # First char of abbreviation must align with start of a word.
                short_index == 0
                and long_index > 0
                and long_form[long_index - 1].isalnum()
            )
        ):
            long_index -= 1

        if long_index < 0:
            return short_form_candidate, None

        long_index -= 1
        short_index -= 1

    # Adjust index to start of long form span
    long_index += 1

    word_lengths = 0
    starting_index: Optional[int] = None
    for i, word in enumerate(long_form_candidate):
        word_lengths += len(word.text_with_ws)
        if word_lengths > long_index:
            starting_index = i
            break

    return short_form_candidate, long_form_candidate[starting_index:]


def span_contains_unbalanced_parentheses(span: Span) -> bool:
    stack_counter = 0
    for token in span:
        if token.text == "(":
            stack_counter += 1
        elif token.text == ")":
            if stack_counter > 0:
                stack_counter -= 1
            else:
                return True

    return stack_counter != 0


def filter_matches(
    matcher_output: List[Tuple[int, int, int]], doc: Doc
) -> List[Tuple[Span, Span]]:
    """Given raw matcher output, produce candidate (long, short) span pairs."""
    candidates: List[Tuple[Span, Span]] = []
    for _, start, end in matcher_output:
        # Ignore spans with more than 8 words or those at doc start
        if end - start > 8 or start == 1:
            continue

        # First check for reverse pattern: <abbreviation> (<long form>)
        if start > 0 and end - start > 3:  # Ensure we have content in parentheses
            potential_short = doc[start - 1 : start]
            potential_long = doc[start + 1 : end - 1]  # Content inside parentheses
            
            # Check if the token before parentheses could be an abbreviation
            if (potential_short and 
                short_form_filter(potential_short) and 
                len(potential_long) > 1):  # Long form should have multiple words
                
                # Verify this is a valid abbreviation pair
                _, verified_long = find_abbreviation(potential_long, potential_short)
                if verified_long is not None:
                    candidates.append((verified_long, potential_short))

        # Now check normal patterns with brackets removed
        start_no_bracket = start + 1
        end_no_bracket = end - 1
        
        # Skip if we have empty content after removing brackets
        if end_no_bracket <= start_no_bracket:
            continue
        
        if end_no_bracket - start_no_bracket > 3:
            # Pattern: <long> (<short>) – content inside parentheses is short form
            # The long form is everything before the opening parenthesis
            content_in_parens = doc[start_no_bracket : end_no_bracket]
            long_form_candidate = doc[0 : start]
            # Look for the actual long form by searching backwards from the parenthesis
            if start > 0:
                # Find a reasonable number of words before the parenthesis
                abbreviation_length = sum(len(t.text) for t in content_in_parens)
                max_words = min(abbreviation_length + 5, abbreviation_length * 2)
                long_start = max(0, start - max_words)
                long_form_candidate = doc[long_start : start]
            short_form_candidate = content_in_parens
        else:
            # Pattern: (<short>) – content inside parentheses might be short form
            short_form_candidate = doc[start_no_bracket : end_no_bracket]
            if not short_form_candidate:
                continue
            abbreviation_length = sum(len(t.text) for t in short_form_candidate)
            max_words = min(abbreviation_length + 5, abbreviation_length * 2)
            long_form_candidate = doc[max(start - max_words, 0) : start]

        if short_form_filter(short_form_candidate):
            candidates.append((long_form_candidate, short_form_candidate))

    return candidates


def short_form_filter(span: Span) -> bool:
    # Check for empty span
    if not span or not span.text:
        return False
        
    # Word length between 2 and 10
    if not all(2 <= len(x) < 10 for x in span):
        return False

    # ≥50 % alpha chars
    if (sum(c.isalpha() for c in span.text) / len(span.text)) < 0.5:
        return False

    # Must start with alpha char
    return span.text[0].isalpha()


# ------------------------------------------------------------------------------------
# Pipeline component
# ------------------------------------------------------------------------------------


@Language.factory("abbreviation_detector")
class AbbreviationDetector:
    """spaCy pipeline component that detects abbreviations in a document."""

    def __init__(
        self,
        nlp: Language,
        name: str = "abbreviation_detector",
        make_serializable: bool = False,
    ) -> None:
        # Register custom extensions (idempotent thanks to *force=True*)
        Doc.set_extension("abbreviations", default=[], force=True)
        Span.set_extension("long_form", default=None, force=True)

        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "parenthesis", [[{"ORTH": "("}, {"OP": "+"}, {"ORTH": ")"}]]
        )
        self.make_serializable = make_serializable
        self.global_matcher = Matcher(nlp.vocab)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def find(self, span: Span, doc: Doc) -> Tuple[Span, Set[Span]]:  # noqa: D401
        """Find the long form definition for an already-detected *span*.
        Returns a tuple ``(long_form, {short_form_spans})``.
        """
        # First, check if this abbreviation was already detected
        for abbr in doc._.abbreviations:
            if abbr.start == span.start and abbr.end == span.end:
                # Found it! Return the long form and all occurrences of this abbreviation
                long_form = abbr._.long_form
                # Find all occurrences of this abbreviation
                short_forms = {a for a in doc._.abbreviations if a._.long_form == long_form}
                return long_form, short_forms
        
        # If not found in already detected abbreviations, search for it
        # Look for parentheses patterns around this span
        for match_id, start, end in self.matcher(doc):
            # Check if our span is just before the parentheses (reverse pattern)
            if span.end == start and span.start == start - 1:
                # Pattern: <abbreviation> (<long form>)
                potential_long = doc[start + 1 : end - 1]
                _, verified_long = find_abbreviation(potential_long, span)
                if verified_long is not None:
                    # Find all occurrences of this abbreviation in the document
                    short_forms = set()
                    for i in range(len(doc) - len(span) + 1):
                        if all(doc[i + j].text == span[j].text for j in range(len(span))):
                            short_forms.add(doc[i : i + len(span)])
                    return verified_long, short_forms
            
            # Check if our span is inside the parentheses (normal pattern)
            if start < span.start and span.end < end:
                # Pattern: <long form> (<abbreviation>)
                # Look for the long form before the parentheses
                abbreviation_length = sum(len(t.text) for t in span)
                max_words = min(abbreviation_length + 5, abbreviation_length * 2)
                long_start = max(0, start - max_words)
                long_form_candidate = doc[long_start : start]
                
                _, verified_long = find_abbreviation(long_form_candidate, span)
                if verified_long is not None:
                    # Find all occurrences of this abbreviation in the document
                    short_forms = set()
                    for i in range(len(doc) - len(span) + 1):
                        if all(doc[i + j].text == span[j].text for j in range(len(span))):
                            short_forms.add(doc[i : i + len(span)])
                    return verified_long, short_forms
        
        # If no match found, return the span itself with no short forms
        return span, set()

    # The component call itself ------------------------------------------------
    def __call__(self, doc: Doc) -> Doc:  # noqa: D401
        matches = self.matcher(doc)
        # Pass original matches to filter_matches, not the modified ones
        filtered = filter_matches(matches, doc)
        occurrences = self.find_matches_for(filtered, doc)

        for long_form, short_forms in occurrences:
            for short in short_forms:
                short._.long_form = long_form
                doc._.abbreviations.append(short)

        if self.make_serializable:
            doc._.abbreviations = [
                self.make_short_form_serializable(abbr) for abbr in doc._.abbreviations
            ]
        return doc

    # Internal helpers ---------------------------------------------------------
    def find_matches_for(
        self, filtered: List[Tuple[Span, Span]], doc: Doc
    ) -> List[Tuple[Span, Set[Span]]]:
        rules: Dict[str, Span] = {}
        all_occurrences: Dict[Span, Set[Span]] = defaultdict(set)
        seen_long: Set[str] = set()
        seen_short: Set[str] = set()

        for long_candidate, short_candidate in filtered:
            short, long = find_abbreviation(long_candidate, short_candidate)
            new_long = long is not None and long.text not in seen_long
            new_short = short.text not in seen_short
            if long is not None and new_long and new_short:
                seen_long.add(long.text)
                seen_short.add(short.text)
                all_occurrences[long].add(short)
                rules[long.text] = long
                self.global_matcher.add(long.text, [[{"ORTH": t.text} for t in short]])

        to_remove: Set[str] = set()
        for match_id, start, end in self.global_matcher(doc):
            string_key = self.global_matcher.vocab.strings[match_id]  # type: ignore
            to_remove.add(string_key)
            all_occurrences[rules[string_key]].add(doc[start:end])

        for key in to_remove:
            self.global_matcher.remove(key)

        return [(k, v) for k, v in all_occurrences.items()]

    def make_short_form_serializable(self, abbreviation: Span):
        """Return a JSON-serializable representation of *abbreviation*."""
        long_form = abbreviation._.long_form
        abbreviation._.long_form = long_form.text  # type: ignore[assignment]
        return {
            "short_text": abbreviation.text,
            "short_start": abbreviation.start,
            "short_end": abbreviation.end,
            "long_text": long_form.text,
            "long_start": long_form.start,
            "long_end": long_form.end,
        }

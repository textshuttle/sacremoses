# -*- coding: utf-8 -*-

"""
This is a Python port of the Moses Punctuation Normalizer from
https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer/normalize-punctuation.perl
"""
from __future__ import unicode_literals
import re


def _substitute(string, pattern, substitution):
    return string.replace(pattern, substitution)


def substitute(pattern, substitution):
    return lambda x: _substitute(x, pattern, substitution)


def _substitute_regex(string, compiled_regex, substitution):
    return compiled_regex.sub(substitution, string)


def substitute_regex(regex, substitution, ignore_case=False):
    flags = re.IGNORECASE if ignore_case else 0
    compiled_regex = re.compile(regex, flags=flags)
    return lambda x: _substitute_regex(x, compiled_regex, substitution)


class MosesPunctuationNormalizer:
    """
    This is a Python port of the Moses punctuation normalizer from
    https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer/normalize-punctuation.perl
    """

    SUBSTITUTIONS_EXTRA_WHITESPACE = [  # lines 21 - 30
        substitute('\r', ''),
        substitute('(', ' ('),
        substitute(')', ') '),
        substitute_regex(r' +', r' '),  # TODO why twice? see line 90
        substitute_regex(r'\) ([.!:?;,])', r')\g<1>'),
        substitute('( ', '('),
        substitute(' )', ')'),
        substitute_regex(r'(\d) %', r'\g<1>%'),
        substitute(' :', ':'),
        substitute(' ;', ';'),
    ]

    SUBSTITUTIONS_NORMALIZE_UNICODE_IF_NOT_PENN = [  # lines 33 - 34
        substitute('`', "'"),
        substitute("''", ' " '),
    ]

    SUBSTITUTIONS_NORMALIZE_UNICODE = [  # lines 37 - 50
        substitute('„', '"'),
        substitute('“', '"'),
        substitute('”', '"'),
        substitute('–', '-'),
        substitute('—', ' - '),
        substitute_regex(r' +', r' '),
        substitute('´', "'"),
        substitute_regex(r'([a-z])‘([a-z])', r"\g<1>'\g<2>", ignore_case=True),
        substitute_regex(r'([a-z])’([a-z])', r"\g<1>'\g<2>", ignore_case=True),
        substitute('‘', '"'),
        substitute('‚', '"'),
        # TODO this can cause problems. (In some texts right single quotation marks are used as apostrophes)
        # use regex to look for matching opening quot?
        substitute('’', '"'),
        substitute("''", '"'),
        substitute("´´", '"'),
        substitute("…", "..."),
    ]

    SUBSTITUTIONS_FRENCH_QUOTES = [  # lines 52 - 57
        substitute('\N{NO-BREAK SPACE}«\N{NO-BREAK SPACE}', ' "'),
        substitute('«\N{NO-BREAK SPACE}', '"'),
        substitute('«', '"'),
        substitute('\N{NO-BREAK SPACE}»\N{NO-BREAK SPACE}', '" '),
        substitute('\N{NO-BREAK SPACE}»', '"'),
        substitute('»', '"'),
    ]

    SUBSTITUTIONS_HANDLE_PSEUDO_SPACES = [  # lines 59 - 67
        substitute('\N{NO-BREAK SPACE}%', '%'),
        substitute('nº\N{NO-BREAK SPACE}', 'nº '),
        substitute('\N{NO-BREAK SPACE}:', ':'),
        substitute('\N{NO-BREAK SPACE}ºC', ' ºC'),
        substitute('\N{NO-BREAK SPACE}cm', ' cm'),
        substitute('\N{NO-BREAK SPACE}?', '?'),
        substitute('\N{NO-BREAK SPACE}!', '!'),
        substitute('\N{NO-BREAK SPACE};', ';'),
        substitute(',\N{NO-BREAK SPACE}', ', '),
        substitute_regex(r' +', r' '),
    ]

    SUBSTITUTIONS_EN_QUOTATION_FOLLOWED_BY_COMMA = [
        substitute_regex(r'"([,.]+)', r'\g<1>"'),
    ]

    SUBSTITUTIONS_DE_ES_FR_QUOTATION_FOLLOWED_BY_COMMA = [
        substitute(',"', '",'),
        substitute_regex(r'(\.+)"(\s*[^<])', r'"\g<1>\g<2>'),  # don't fix period at end of sentence
    ]

    SUBSTITUTIONS_DE_ES_CZ_CS_FR = [
        substitute_regex(r'(\d) (\d)', r'\g<1>,\g<2>'),
    ]

    SUBSTITUTIONS_OTHER = [
        substitute_regex(r'(\d) (\d)', r'\g<1>.\g<2>'),
    ]

    def __init__(self, language='en', penn= False):
        """
        Python port of the Moses Perl script for normalization of punctuation.

        :param language: The two-letter language code.
        :param penn: Use Penn Treebank style normalization.
        """
        self.language = language
        self.penn = penn
        # assemble sequence of substitutions
        self.substitutions = self.SUBSTITUTIONS_EXTRA_WHITESPACE
        if not self.penn:
            self.substitutions += self.SUBSTITUTIONS_NORMALIZE_UNICODE_IF_NOT_PENN
        self.substitutions += self.SUBSTITUTIONS_NORMALIZE_UNICODE
        self.substitutions += self.SUBSTITUTIONS_FRENCH_QUOTES
        self.substitutions += self.SUBSTITUTIONS_HANDLE_PSEUDO_SPACES
        if self.language == 'en':
            self.substitutions += self.SUBSTITUTIONS_EN_QUOTATION_FOLLOWED_BY_COMMA
        else:
            self.substitutions += self.SUBSTITUTIONS_DE_ES_FR_QUOTATION_FOLLOWED_BY_COMMA
        if self.language in ['de', 'es', 'cz', 'cs', 'fr']:
            self.substitutions += self.SUBSTITUTIONS_DE_ES_CZ_CS_FR
        else:
            self.substitutions += self.SUBSTITUTIONS_OTHER

    def normalize(self, string):
        """
        Returns a string with normalized punctuation.
        """
        for sub in self.substitutions:
            string = sub(string)
        return string


# Alias for forward compatibility with upstream
class MosesPunctNormalizer(MosesPunctuationNormalizer):
    def __init__(self, lang='en', penn=False, norm_quote_commas=True, norm_numbers=True):
        super().__init__(language=lang, penn=penn)
        if not norm_quote_commas:
            norm_quote_comma_rules = self.SUBSTITUTIONS_EN_QUOTATION_FOLLOWED_BY_COMMA + self.SUBSTITUTIONS_DE_ES_FR_QUOTATION_FOLLOWED_BY_COMMA
            self.substitutions = [s for s in self.substitutions if s not in norm_quote_comma_rules]

        if not norm_numbers:
            norm_number_rules = self.SUBSTITUTIONS_DE_ES_CZ_CS_FR + self.SUBSTITUTIONS_OTHER
            self.substitutions = [s for s in self.substitutions if s not in norm_number_rules]



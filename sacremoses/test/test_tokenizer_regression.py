# -*- coding: utf-8 -*-

"""
Tests for MosesPunctuationNormalizer
"""

import os
import unittest
import subprocess
from shutil import copy

from sacremoses import MosesTokenizer
from sacremoses.normalize import MosesPunctuationNormalizer
from sacremoses.test.utils import download_file_if_not_exists, get_test_file
import sacremoses.test.constants as C

# Hack to enable Python2.7 to use encoding.
import sys

if sys.version_info[0] < 3:
    import io
    import warnings

    open = io.open
    warnings.warn(str('You should really be using Python3!!! '
                      'Tick tock, tick tock, https://pythonclock.org/'))


class TestMosesTokenizer(unittest.TestCase):

    def setUp(self):
        # Download original Perl script if needed
        download_file_if_not_exists(C.MOSES_TOKENIZER_SCRIPT_URL,
                                    C.MOSES_TOKENIZER_SCRIPT_LOCAL_PATH)

    def _create_gold(self, test_file, language='en'):
        """
        Normalizes a file with the original Perl script and returns the path
        to the normalized file.
        """
        flags = []
        if language:
            flags += ['-l', language]
        command = ['perl', C.MOSES_TOKENIZER_SCRIPT_LOCAL_PATH] + flags
        path_gold = '.'.join([test_file, 'tokenized', 'gold'] + flags)
        with open(test_file, encoding='utf-8') as stdin, open(path_gold, 'w', encoding='utf-8') as stdout:
            process = subprocess.Popen(command, stdin=stdin, stdout=stdout)
            process.wait()
        return path_gold

    def _test_tokenize(self, test_file, language='en'):
        """
        Compares MosesPunctuationNormalizer's output to the output of the
        original Perl script.
        """
        tokenizer = MosesTokenizer(lang=language)
        # Normalize test file with original Perl script and given flags
        path_gold = self._create_gold(test_file, language)
        # Compare to output of original Perl script
        with open(test_file, encoding='utf-8') as u, open(path_gold, encoding='utf-8') as g:
            for text, gold in zip(u, g):
                tokenized = tokenizer.tokenize(text, return_str=True)
                self.assertEqual(tokenized, gold.rstrip())
        # Delete output of original Perl script
        # os.remove(path_gold)

    def test_tokenize_en(self):
        test_file = get_test_file('en')
        self._test_tokenize(test_file=test_file, language='en')

    def test_tokenize_de(self):
        test_file = get_test_file('de')
        self._test_tokenize(test_file=test_file, language='de')

    def test_tokenize_fr(self):
        test_file = get_test_file('fr')
        self._test_tokenize(test_file=test_file, language='fr')

    def test_tokenize_it(self):
        test_file = get_test_file('it')
        self._test_tokenize(test_file=test_file, language='it')
    # TODO: add tests for other languages


if __name__ == '__main__':
    unittest.main()

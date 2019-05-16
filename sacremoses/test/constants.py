# -*- coding: utf-8 -*-

TEST_FILE = {
    'en': ('https://norvig.com/big.txt', 'test.en.txt'),
    'de': ('https://www.debian.org/releases/stable/s390x/release-notes.de.txt', 'test.de.txt'),
    'fr': ('https://www.debian.org/releases/stable/s390x/release-notes.fr.txt', 'test.fr.txt'),
    'it': ('https://www.debian.org/releases/stable/s390x/release-notes.it.txt', 'test.it.txt')
}

MOSES_NORMALIZER_SCRIPT_URL = 'https://raw.githubusercontent.com/moses-smt/mosesdecoder/master/scripts/tokenizer/normalize-punctuation.perl'
MOSES_NORMALIZER_SCRIPT_LOCAL_PATH = 'normalize-punctuation.perl'

MOSES_TOKENIZER_SCRIPT_URL = 'https://raw.githubusercontent.com/moses-smt/mosesdecoder/master/scripts/tokenizer/tokenizer.perl'
MOSES_TOKENIZER_SCRIPT_LOCAL_PATH = 'tokenizer.perl'

MOSES_DETOKENIZER_SCRIPT_URL = 'https://raw.githubusercontent.com/moses-smt/mosesdecoder/master/scripts/tokenizer/detokenizer.perl'
MOSES_DETOKENIZER_SCRIPT_LOCAL_PATH = 'detokenizer.perl'

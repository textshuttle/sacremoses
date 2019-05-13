# -*- coding: utf-8 -*-

from functools import partial
from itertools import chain
from tqdm import tqdm

import click

from sacremoses.tokenize import MosesTokenizer, MosesDetokenizer
from sacremoses.truecase import MosesTruecaser, MosesDetruecaser
from sacremoses.normalize import MosesPunctNormalizer
from sacremoses.util import parallelize_preprocess

# Hack to enable Python2.7 to use encoding.
import sys
import warnings
if sys.version_info[0] < 3:
    import io
    import warnings
    open = io.open
    warnings.warn(str('You should really be using Python3!!! '
                      'Tick tock, tick tock, https://pythonclock.org/'))


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass

@cli.command('tokenize')
@click.option('--language', '-l', default='en', help='Use language specific rules when tokenizing')
@click.option('--processes', '-j', default=1, help='No. of processes.')
@click.option('--aggressive-dash-splits', '-a', default=False, is_flag=True,
                help='Triggers dash split rules.')
@click.option('--xml-escape', '-x', default=True, is_flag=True,
                help='Escape special characters for XML.')
@click.option('--protected-patterns', '-p', help='Specify file with patters to be protected in tokenisation.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def tokenize_file(language, processes, xml_escape, aggressive_dash_splits, protected_patterns, encoding):
    moses = MosesTokenizer(lang=language)

    if protected_patterns:
        with open(protected_patterns, encoding='utf8') as fin:
            protected_patterns = [pattern.strip() for pattern in fin.readlines()]

    moses_tokenize = partial(moses.tokenize,
                        return_str=True,
                        aggressive_dash_splits=aggressive_dash_splits,
                        escape=xml_escape,
                        protected_patterns=protected_patterns)

    with click.get_text_stream('stdin', encoding=encoding) as fin:
        with click.get_text_stream('stdout', encoding=encoding) as fout:
            # If it's single process, joblib parallization is slower,
            # so just process line by line normally.
            if processes == 1:
                for line in tqdm(fin.readlines()):
                    print(moses_tokenize(line), end='\n', file=fout)
            else:
                for outline in parallelize_preprocess(moses_tokenize, fin.readlines(), processes, progress_bar=True):
                    print(outline, end='\n', file=fout)


@cli.command('detokenize')
@click.option('--language', '-l', default='en', help='Use language specific rules when tokenizing')
@click.option('--processes', '-j', default=1, help='No. of processes.')
@click.option('--xml-unescape', '-x', default=True, is_flag=True,
                help='Unescape special characters for XML.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def detokenize_file(language, processes, xml_unescape, encoding):
    moses = MosesDetokenizer(lang=language)
    moses_detokenize = partial(moses.detokenize,
                        return_str=True,
                        unescape=xml_unescape)
    with click.get_text_stream('stdin', encoding=encoding) as fin:
        with click.get_text_stream('stdout', encoding=encoding) as fout:
            # If it's single process, joblib parallization is slower,
            # so just process line by line normally.
            if processes == 1:
                for line in tqdm(fin.readlines()):
                    print(moses_detokenize(str.split(line)), end='\n', file=fout)
            else:
                document_iterator = map(str.split, fin.readlines())
                for outline in parallelize_preprocess(moses_detokenize, document_iterator, processes, progress_bar=True):
                    print(outline, end='\n', file=fout)


@cli.command('train-truecase')
@click.option('--modelfile', '-m', required=True, help='Filename to save the modelfile.')
@click.option('--processes', '-j', default=1, help='No. of processes.')
@click.option('--is-asr', '-a',  default=False, is_flag=True,
                help='A flag to indicate that model is for ASR.')
@click.option('--possibly-use-first-token', '-p', default=False, is_flag=True,
                help='Use the first token as part of truecasing.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def train_truecaser(modelfile, processes, is_asr, possibly_use_first_token, encoding):
    moses = MosesTruecaser(is_asr=is_asr, encoding=encoding)
    with click.get_text_stream('stdin', encoding=encoding) as fin:
        model = moses.train_from_file_object(fin,
                    possibly_use_first_token=possibly_use_first_token,
                    processes=processes, progress_bar=True)
        moses.save_model(modelfile)


@cli.command('truecase')
@click.option('--modelfile', '-m', required=True, help='The trucaser modelfile to use.')
@click.option('--processes', '-j', default=1, help='No. of processes.')
@click.option('--is-asr', '-a',  default=False, is_flag=True,
                help='A flag to indicate that model is for ASR.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def truecase_file(modelfile, processes, is_asr, encoding):
    moses = MosesTruecaser(load_from=modelfile, is_asr=is_asr, encoding=encoding)
    moses_truecase = partial(moses.truecase, return_str=True)
    with click.get_text_stream('stdin', encoding=encoding) as fin:
        with click.get_text_stream('stdout', encoding=encoding) as fout:
            for line in tqdm(fin):
                print(moses.truecase(line, return_str=True), end='\n', file=fout)
            #FIXME: parallelize job don't work properly for MosesTruecaser.truecase
            ##else:
            ##    for outline in parallelize_preprocess(moses_truecase, fin.readlines(), processes, progress_bar=True):
            ##        print(outline, end='\n', file=fout)


@cli.command('detruecase')
@click.option('--processes', '-j', default=1, help='No. of processes.')
@click.option('--is-headline', '-a',  default=False, is_flag=True,
                help='Whether the file are headlines.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def detruecase_file(processes, is_headline, encoding):
    moses = MosesDetruecaser()
    moses_detruecase = partial(moses.detruecase,
                        return_str=True,
                        is_headline=is_headline)
    with click.get_text_stream('stdin',  encoding=encoding) as fin:
        with click.get_text_stream('stdout',  encoding=encoding) as fout:
            # If it's single process, joblib parallization is slower,
            # so just process line by line normally.
            if processes == 1:
                for line in tqdm(fin.readlines()):
                    print(moses_detruecase(line), end='\n', file=fout)
            else:
                for outline in parallelize_preprocess(moses_detruecase, fin.readlines(), processes, progress_bar=True):
                    print(outline, end='\n', file=fout)


@cli.command('normalize')
@click.option('--language', '-l', default='en', help='Use language specific rules when normalizing.')
@click.option('--processes', '-j', default=1, help='No. of processes.')
@click.option('--normalize-quote-commas', '-q',  default=True, is_flag=True,
                help='Normalize quotations and commas.')
@click.option('--normalize-numbers', '-d',  default=True, is_flag=True,
                help='Normalize number.')
@click.option('--encoding', '-e', default='utf8', help='Specify encoding of file.')
def normalize_file(language, processes, normalize_quote_commas, normalize_numbers, encoding):
    moses = MosesPunctNormalizer(language,
                                 norm_quote_commas=normalize_quote_commas,
                                 norm_numbers=normalize_numbers)
    moses_normalize = partial(moses.normalize)

    with click.get_text_stream('stdin', encoding=encoding) as fin:
        with click.get_text_stream('stdout', encoding=encoding) as fout:
            # If it's single process, joblib parallization is slower,
            # so just process line by line normally.
            if processes == 1:
                # TODO: Actually moses_normalize(fin.read()) gives the same output
                #       and it's a lot better but it's inconsistent with the other
                #       preprocessing interfaces, so we're doing it line by line here.
                for line in tqdm(fin.readlines()):
                    # Note: not stripping newlines, so don't need end='\n' when printing to stdout.
                    print(moses_normalize(fin.read()), end='', file=fout)
            else:
                for outline in parallelize_preprocess(moses_normalize, fin.readlines(), processes, progress_bar=True):
                    # Note: not stripping newlines, so don't need end='\n' when printing to stdout.
                    print(outline, end='', file=fout)

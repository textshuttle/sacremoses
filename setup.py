from distutils.core import setup
import setuptools

console_scripts = """
[console_scripts]
sacremoses=sacremoses.cli:cli
"""

setup(
  name = 'sacremoses',
  packages = ['sacremoses'],
  version = '0.0.19',
  description = 'SacreMoses',
  long_description = 'LGPL MosesTokenizer in Python',
  author = '',
  license = '',
  package_data={'sacremoses': ['share/perluniprops/*.txt', 'share/nonbreaking_prefixes/nonbreaking_prefix.*']},
  url = 'https://github.com/alvations/sacremoses',
  keywords = [],
  classifiers = [],
  install_requires = ['six', 'click', 'joblib', 'tqdm'],
  entry_points=console_scripts,
)

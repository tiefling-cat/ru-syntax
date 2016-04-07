# ru-syntax
Repository for ru-syntax command line tool.

## Requirements
* Python v.3.4+
* Mystem
* TreeTagger
* MaltParser v.1.8.1+

## Sample config
```
[DEFAULT]
APP_ROOT = /home/nm/repos/ru-syntax/ru-syntax
BIN_PATH = %(APP_ROOT)s/bin
OUT_PATH = %(APP_ROOT)s

[mystem]
MYSTEM_PATH = %(BIN_PATH)s/mystem_ruscorpora

[malt]
MALT_ROOT = %(BIN_PATH)s/maltparser-1.8.1
MALT_NAME = maltparser-1.8.1.jar
MODEL_NAME = PTM

[dicts]
COMP_DICT_PATH = %(APP_ROOT)s/static/dictionaries/composites.csv

[treetagger]
TREETAGGER_BIN = %(BIN_PATH)s/treetagger/bin/tree-tagger
TREETAGGER_PAR = %(BIN_PATH)s/treetagger/lib/tree_alltags_model.par
```

## Usage
```
Usage: ./ru-syntax.py [-o OUTPUT_FILE] INPUT_FILE

Options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --out=OUTPUT_FILE
                        output results to OUTPUT_FILE.
```

# ru-syntax
Here is the repository for ru-syntax command line tool.

## Requirements
* Python v.3.4+
* Mystem
* TreeTagger
* MaltParser v.1.8.1+
* our MaltParser model

## Installation
In order to get everything up and running, you 

## Sample config
```
[DEFAULT]
# full path to the folder containing ru-syntax.py
APP_ROOT = /home/nm/repos/ru-syntax
# path to the folder containing Mystem, Treetagger and MaltParser
BIN_PATH = %(APP_ROOT)s/bin
# path to the folder for output
OUT_PATH = %(APP_ROOT)s

[mystem]
# path to mystem binary
MYSTEM_PATH = %(BIN_PATH)s/mystem

[malt]
# full path to the folder containing MaltParser
MALT_ROOT = %(BIN_PATH)s/maltparser-1.8.1
# name of MaltParser binary file
MALT_NAME = maltparser-1.8.1.jar
# name of MaltParser model
MODEL_NAME = PTM

[dicts]
# path to composites dictionary file
COMP_DICT_PATH = %(APP_ROOT)s/static/dictionaries/composites.csv

[treetagger]
# path to Treetagger binary file
TREETAGGER_BIN = %(BIN_PATH)s/treetagger/bin/tree-tagger
# path to Treetagger model
TREETAGGER_PAR = %(APP_ROOT)s/tree_alltags_model.par
```

## Usage
In order to annotate your file, you need to run the wrapper script ru-syntax.py from the command line:

```
Usage: ./ru-syntax.py [-o OUTPUT_FILE] INPUT_FILE

Options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --out=OUTPUT_FILE
                        output results to OUTPUT_FILE.
```

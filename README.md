# ru-syntax
Here is the repository for ru-syntax command line tool, which allows for, ahem, syntactic parsing of Russian texts, plain text in, anniotated conll out. You can visit project's <a href="http://web-corpora.net/wsgi3/ru-syntax/" target="_blank">web page</a> to parse some text online and find out more about the pipeline.

The work is done as a side project of Kira Droganova and Nikita Medyankin at Higher School of Economics, Moscow, Faculty of Humanities, master's programme <a href="https://www.hse.ru/en/ma/ling/" target="_blank">Computational Linguistics</a>.

## Requirements
* <a href="https://www.python.org/downloads/" target="_blank">Python v.3.4+</a>
* <a href="https://tech.yandex.ru/mystem/" target="_blank">Mystem</a>
* <a href="http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/" target="_blank">TreeTagger</a>
* <a href="http://www.maltparser.org/" target="_blank">MaltParser v.1.8.1+</a>
* our MaltParser model from <a href="http://web-corpora.net/wsgi3/ru-syntax/downloads target="_blank">ru-syntax website</a>

## Installation
In order to get everything up and running, you need to make sure you have all the requirements, clone this repository or just download it as a zip-file, and unpack it. After that, you basically have two options.

#### 1. Use sample config and move Mystem, MaltParser and TreeTagger to adjust for it
1. Create 'config.ini' file in the folder containing ru-syntax.py.
2. Copy the sample config given below to config.ini.
3. Replace the path in `APP_ROOT = /home/nm/repos/ru-syntax` line with the full path to the folder containing ru-syntax.py.
4. Create 'bin' folder in your folder containing ru-syntax.py.
5. Put Mystem binary, full TreeTagger folder, and full MaltParser folder into that bin folder.
6. Make sure they are written in config.ini exactly the same as they are named (e.g., option `MYSTEM_PATH = %(BIN_PATH)s/mystem` might need to be replaced by something like `MYSTEM_PATH = %(BIN_PATH)s/mystem-3.0-win7-32bit.exe`).
7. Put MaltParser model downloaded from <a href="http://web-corpora.net/wsgi3/ru-syntax/downloads target="_blank">ru-syntax website</a> into the same folder as MaltParser jar file.

#### 2. Put Mystem, MaltParser and TreeTagger anywhere you like and tweak the config
1. Create 'config.ini' file in the folder containing ru-syntax.py.
2. Copy the sample config given below to config.ini.
3. Tweak the paths in the config according to where you have your Mystem, TreeTagger, MaltParser, and MaltParser model.

Please note that constructions like `%(SOME_OPTION)s` simply substitute with the contents of `SOME_OPTION.` You don't have to use them but may rather just specify full paths. In order to use such a construction, you have to make sure that `SOME_OPTION` is specified either in `[DEFAULT]` section or in the same section where `%(SOME_OPTION)s` is invoked.

Also note that regardless of how you place MaltParser folder, you have to put the model into exactly the same folder as MaltParser jar file.

## Sample config
```
[DEFAULT]
# full path to the folder containing ru-syntax.py
APP_ROOT = /home/nm/repos/ru-syntax
# path to the folder containing Mystem, TreeTagger and MaltParser
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
COMP_DICT_PATH = %(APP_ROOT)s/dictionaries/composites.csv

[treetagger]
# path to TreeTagger folder
TREETAGGER_BIN = %(BIN_PATH)s/treetagger/bin/tree-tagger
# path to Treetagger model
TREETAGGER_PAR = %(APP_ROOT)s/tree_alltags_model.par
```

## Usage
In order to annotate your file, you need to run the wrapper script `ru-syntax.py` from the command line:

```
Usage: python3 ru-syntax.py [-o OUTPUT_FILE] INPUT_FILE

Options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --out=OUTPUT_FILE
                        output results to OUTPUT_FILE.
```

If `OUTPUT_FILE` is not specified, the output file will have the same name as input file but with conll extension.

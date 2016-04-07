#! /usr/bin/python3

import sys, os
from configparser import ConfigParser
from optparse import OptionParser
from processing import process

def get_options():
    """
    Parse commandline arguments
    """
    usage = "USAGE: ./%prog [-o OUTPUT_FILE] INPUT_FILE"
    op = OptionParser(usage=usage)

    op.add_option("-o", "--out", dest="ofname",
                  help="output results to OUTPUT_FILE.", 
                  metavar="OUTPUT_FILE",
                  default=None)

    (opts, args) = op.parse_args()

    if len(args) == 0:
        op.error("missing input file name.")
        op.print_help()
        sys.exit(1)

    if len(args) > 1:
        op.error("too many arguments.")
        op.print_help()
        sys.exit(1)

    return args[0], opts.ofname

def check_infile(in_fname):
    """
    Sanity checks for input file.
    """
    try:
        in_file = open(in_fname, 'r', encoding='utf-8')
    except FileNotFoundError:
        print('Failed to locate input file \'{}\'. '
              'Have you misspelled the name?'.format(in_fname))
        sys.exit(1)
    try:
        in_file.read()
        in_file.close()
    except UnicodeDecodeError:
        print('Sorry, file must be plain text encoded in utf-8!')
        sys.exit(1)

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    in_fname, out_fname = get_options()
    check_infile(in_fname)

    if '.' in in_fname:
        fname_clean = in_fname.rsplit('.', 1)[0]
    else:
        fname_clean = in_fname

    tmp_fsuffixes = ['_mystem_in.txt', '_mystem_out.txt',
                     '_treetagger_in.txt', '_treetagger_out.txt',
                     '_raw.conll']
    tmp_fnames = [os.path.join(config['DEFAULT']['app_root'], 
                               fname_clean + fsuffix)
                    for fsuffix in tmp_fsuffixes]

    if out_fname is None:
        out_fname = os.path.join(config['DEFAULT']['out_path'],
                                 fname_clean + '.conll')
    else:
        out_fname = os.path.join(config['DEFAULT']['out_path'], out_fname)

    process(in_fname, out_fname,
            config['DEFAULT']['app_root'],
            config['mystem']['mystem_path'],
            config['malt']['malt_root'],
            config['malt']['malt_name'],
            config['malt']['model_name'],
            config['dicts']['comp_dict_path'],
            config['treetagger']['treetagger_bin'],
            config['treetagger']['treetagger_par'],
            *tmp_fnames)

    for fname in tmp_fnames:
        os.remove(fname)

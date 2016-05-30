#! /usr/bin/python3

import os
from sys import version_info
from configparser import ConfigParser
from processing import process

ifolder = '/home/nm/corpus-txt/post1950/nauka'
ofolder = '/home/nm/corpus-annotated/post1950/nauka'

# the means of measuring time
if version_info > (3, 2):
    from time import perf_counter as time_counter
else:
    from time import clock as time_counter

def get_paths(ifolder, ofolder, init_ext='.txt', result_ext='.conll', plain=False):
    """
    ifolder: root folder of corpus
    ofolder: root folder for results
    init_ext_list: extensions to look up among input files
    result_ext: extension for resulting files
    plain: do not recreate subfolder structure of ifolder in ofolder

    return: matching lists of input and output file paths
    """
    ifname_list, ofname_list = [], []
    if not os.path.exists(ofolder):
        os.makedirs(ofolder)

    for root, subdirs, fnames in os.walk(ifolder):
        for fname in fnames:
            # check for files with extension init_ext
            if fname.endswith(init_ext):
                ifname_list.append(os.path.join(root, fname))
                ofname = os.path.splitext(fname)[0] + result_ext

                if plain: # just output everything to ofolder
                    ofname_list.append(os.path.join(ofolder, ofname))
                else: # recreate subfolder structure
                    osubfolder = root.replace(ifolder, ofolder)
                    if not os.path.exists(osubfolder):
	                    os.makedirs(osubfolder)
                    ofname_list.append(os.path.join(osubfolder, ofname))

    return ifname_list, ofname_list

if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')
    ifname_list, ofname_list = get_paths(ifolder, ofolder)

    # temporary files and folder
    tmp_fnames = ['mystem_in.txt', 'mystem_out.txt',
                  'treetagger_in.txt', 'treetagger_out.txt',
                  'raw.conll']
    tmp_fnames = [os.path.join(config['DEFAULT']['TMP_PATH'], fname) for fname in tmp_fnames]

    total = len(ifname_list)
    for i, (ifname, ofname) in enumerate(zip(ifname_list, ofname_list)):
        print('{}/{} Processing {}'.format(i+1, total, ifname))
        # check if we have already got this file
        # during the previous run of the script
        if os.path.exists(ofname):
            print('Already processed')
        else:
            print('Destination {}'.format(ofname))
            start_time = time_counter()
            process(ifname, ofname,
                config['DEFAULT']['APP_ROOT'],
                config['mystem']['MYSTEM_PATH'],
                config['malt']['MALT_ROOT'],
                config['malt']['MALT_NAME'],
                config['malt']['MODEL_NAME'],
                config['dicts']['COMP_DICT_PATH'],
                config['treetagger']['TREETAGGER_BIN'],
                config['treetagger']['TREETAGGER_PAR'],
                *tmp_fnames)
            print('Performed in {:.3f} sec'.format(time_counter() - start_time))

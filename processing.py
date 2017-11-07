import re, json, os, sys, shlex
from shutil import copyfile
from subprocess import call
from ru_syntax_utils import segment, posttok, posttag

mystem_options = [
        '--format=json', # plaintext at input, json at output
        '-i', # print grammar tags
        '-d', # use lexical disambiguation
        '-c', # copy input onto output
        '--eng-gr', # grammar tags in English
    ]
malt_call_line = 'java -jar {} -c {} -i {} -o {} -m parse'


def process(ifname, ofname, app_root, mystem_path, malt_root, malt_name, model_name,
    comp_dict_path, treetagger_bin, treetagger_par,
    mfname_i, mfname_o, ttfname_i, ttfname_o, raw_fname):
    """
    Process text file.
    """
    with open(ifname, 'r', encoding='utf-8') as ifile:
        raw_text = ifile.read()  # used to be .readlines()

    # segmentation
    segmented_text = segment.segment_text(raw_text)
    with open(mfname_i, 'w', encoding='utf-8') as tmp_file:
        tmp_file.write(segmented_text)

    # mystem
    mystem_call_list = [mystem_path] + mystem_options + [mfname_i, mfname_o]
    call(mystem_call_list)
    with open(mfname_o, 'r', encoding='utf-8') as tmp_file:
        text = tmp_file.read()
        analyzed = json.loads(text.strip())

    # post-mystem correction
    comp_dict = posttok.get_comp_dict(comp_dict_path)
    sentences = posttok.mystem_postprocess(analyzed, comp_dict)
    tt_tokens = posttag.treetagg(sentences, ttfname_i, ttfname_o, 
                                        treetagger_bin, treetagger_par)
    sentences = posttag.tt_correct(sentences, tt_tokens)
    with open(raw_fname, 'w', encoding='utf-8') as raw_file:
        segment.flush(sentences, raw_file)

    # malt
    os.chdir(malt_root)
    # if Windows, use it as is; else: comment three lines below this one and uncomment the 52th one
    line = malt_call_line.format(malt_name, model_name, raw_fname, ofname)
    # print(line)
    call(line)
    #call(shlex.split(malt_call_line.format(malt_name, model_name, raw_fname, ofname)))
    os.chdir(app_root)

    return 0

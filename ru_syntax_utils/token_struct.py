import re
from ru_syntax_utils.rearrange_tags import rearrange

gtfo_tag_list = ['parenth', 'geo', 'awkw', 'persn', 'dist', 'mf', 'obsc', 'patrn', 'praed', 'inform', 'rare', 'abbr', 'obsol', 'famn',
    'act', 'tran', 'intr']
repl_tag_dict = {'abl':'loc', 'loc':'loc2'}
repl_pos_dict = {'ADVPRO':'ADV', 'ANUM':'A', 'APRO':'A', 'SPRO':'S', 'ADV-PRO':'ADV', 'A-PRO':'A', 'S-PRO':'S'}
spro_set = {'Я', 'МЫ', 'ТЫ', 'ВЫ', 'ОН', 'ОНА', 'ОНО', 'ОНИ', 'СЕБЯ'}

#plain_word_re = re.compile('^[а-яё]+[а-яё-]*$')
#abbr_re = re.compile('^([а-яё]+\.+)[а-яё.]*$')
#plain_la_re = re.compile('^[a-z]+$')
#compl_la_re = re.compile('^([a-z]+[.:/@]+)+$')]

num_re = re.compile('^([0-9]+[.:/]*)+$')
roman_re = re.compile('^[IVXDCLM]+$')
percent_re = re.compile('^%$')
space_re = re.compile('^\s$')
punc_re = re.compile('^[^A-Za-zА-ЯЁа-яё0-9]+$')

post_mystem = [
        (roman_re, None, 'NUM', 'NUM - - -'),
        (num_re, None, 'NUM', 'NUM - - -'),
        (percent_re, 'ПРОЦЕНТ-ЗНАК', 'S', 'S m inan gen pl'),
        (space_re, 'ПРОБЕЛ', 'SPACE', 'SPACE'),
    ]

post_punc = (punc_re, None, 'PUNC', 'PUNC')

## Everything about token structure in output conll

forced_fullstop = tuple(('.', '.', 'SENT', 'SENT', 'SENT'))

def nonlex_token(text):
    """
    Used in segmentation for special tokens.
    """
    return tuple((text, text.upper(), 'NONLEX', 'NONLEX', 'NONLEX'))

def terminal_token(line):
    return line[:2] + ('SENT', 'SENT', 'SENT')

def punc_token(punc):
    if re.match('[()«»"\']', punc):
        lemma = '_'
    else:
        lemma = punc
    return tuple((punc, punc, lemma, lemma, 'PUNC'))

def parse_analysis(analysis):
    """
    Parse mystem analysis for one token.
    """
    lemma = analysis['analysis'][0]['lex'].upper()
    pos, feat, glued = parse_gr(lemma, analysis['analysis'][0]['gr'])
    if pos in ['S', 'A']:
        feat = [feat]
        for variant in analysis['analysis'][1:]:
            vpos, vfeat, vglued = parse_gr(lemma, variant['gr'])
            feat.append(vfeat)
    return tuple((analysis['text'], lemma, pos, feat, feat))

def typed_token(text, regexp):
    if regexp[1] is None:
        lemma = text
    else:
        lemma = regexp[1]
    return tuple((text, lemma.upper(), regexp[2], regexp[3], regexp[3]))

def num_token(text):
    """
    Used in segmentation for special tokens.
    """
    return tuple((text, text, 'NUM', 'NUM - - -', 'NUM - - -'))

def comp_token(tok_list, feats):
    word = ' '.join([tok[0] for tok in tok_list])
    return (word, word) + tuple(parse_gr(word, feats))

def parse_gr(lemma, gr, repl=True):
    """
    Parse grammar tags.
    """
    parsed = gr.replace('=', ',').split(',')

    if not (parsed[0] in ['SPRO', 'S-PRO'] and lemma in spro_set):
        parsed[0] = repl_pos_dict.get(parsed[0], parsed[0])
    else:
        parsed[0] = 'SPRO'

    pos = parsed[0]
    morpho = [tag for tag in parsed[1:] if tag not in gtfo_tag_list]

    if repl:
        morpho = [repl_tag_dict.get(tag, tag) for tag in morpho]

    if 'partcp' in morpho:
        pos = 'PARTCP'

    morpho = rearrange(pos, morpho, lemma)

    if morpho == [] or morpho == ['']:
        feat = pos
        glued = 'ZERO'
    else:
        feat = ' '.join([pos] + morpho)
        glued = ''.join(morpho)
    return pos, feat, glued

def glue_tokens(tokens, main):
    form = tokens[0][0] + tokens[1][0]
    lemma = tokens[0][1] + tokens[1][1]
    return tuple((form, lemma, tokens[main][2], tokens[main][3], tokens[main][4]))

def feats_include(feats, test):
    include = True
    for feat in test:
        include = include and feat in feats
    return include

def correct_token_deep(token, pos, test_feat):
    """
    Correct S and A feats got from mystem with treetagger feats.
    """
    tok_pos = token[2]
    if tok_pos != pos:
        return token[:2] + tuple((tok_pos, token[3][0], token[3][0])) + token[5:]
    test_feat_list = test_feat.split(' ')
    for feat in token[3]:
        feat_list = feat.split(' ')
        if feats_include(feat_list, test_feat_list):
            return token[:2] + tuple((pos, feat, feat)) + token[5:]
    return token[:2] + tuple((pos, test_feat, test_feat)) + token[5:]

def correct_token_shallow(token, pos, feats):
    """
    Correct token with new pos and feats.
    """
    return token[:2] + tuple((pos, feats, feats)) + token[5:]

def correct_tags(token, pos, feat):
    """
    Obsolete function?
    """
    feat_list = feat.split(' ')
    feat_list = [repl_tag_dict.get(tag, tag) for tag in feat_list]
    feat = ' '.join(feat_list)
    return token[:2] + tuple((pos, feat, feat)) + token[5:]

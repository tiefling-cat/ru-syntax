import re
from collections import namedtuple

FeatMatch = namedtuple('FeatMatch', ['regex', 'default'])

gender = FeatMatch(re.compile(r'\b[mfn]\b'), '-')
number = FeatMatch(re.compile(r'\b(sg|pl)\b'), '-')
anim = FeatMatch(re.compile(r'\b(inan|anim)\b'), '-')
case = FeatMatch(re.compile(r'\b(nom|gen|dat|acc|ins|loc|part|loc2|voc)\b'), '-')
brev = FeatMatch(re.compile(r'\b(brev|plen)\b'), 'plen')
relat = FeatMatch(re.compile(r'\b(comp|supr)\b'), '-')
tense = FeatMatch(re.compile(r'\b(inpraes|praet)\b'), '-')
aspect = FeatMatch(re.compile(r'\b(i?pf)\b'), '-')
repres = FeatMatch(re.compile(r'\b(indic|imper|inf|ger)\b'), '-')
person = FeatMatch(re.compile(r'\b([123]p)\b'), '-')
voice = FeatMatch(re.compile(r'\b(pass|act)\b'), 'act')

pos_dict = {
        'S': (gender, anim, case, number),
        'SPRO': (number, person, gender, case),
        'A': (relat, case, number, brev, gender, anim),
        'ADV': (relat,),
        'NUM': (case, gender, anim),
        'V': (aspect, tense, number, repres, gender, person),
        'PARTCP': (aspect, tense, case, number, brev, gender, voice, anim)
    }

def rearrange(pos, feat, lemma):
    """
    Get part of speech, tags, amd lemma.
    Extract all tags depending on lemma.
    """
    feat_line = ' '.join(feat)
    if pos in pos_dict:
        feat = [extract_feat(feat_match, feat_line) 
                    for feat_match in pos_dict[pos]]

        if pos == 'V':
            feat[0] = feat[0].replace('-', 'ipf')
            if feat[0] == 'ipf':
                feat[1] = feat[1].replace('inpraes', 'praes')
            elif feat[0] == 'pf':
                feat[1] = feat[1].replace('inpraes', 'fut')
        elif pos == 'PARTCP':
            feat[1] == feat[1].replace('inpraes', 'praes')
        elif lemma.startswith('ПО'):
            if pos == 'ADV' and 'comp' in feat_line:
                feat = ['comp2']
            elif pos == 'A':
                feat = ['comp2', '-', '-', 'plen', '-', '-']
    return feat

def extract_feat(feat_match, feat_line):
    """
    Get str of feats and extract particular feat.
    """
    match = feat_match.regex.search(feat_line)
    if match:
        return match.group(0)
    return feat_match.default

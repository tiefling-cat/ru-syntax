from subprocess import call
from ru_syntax_utils.token_struct import *
import ru_syntax_utils.rearrange_tags as rt

def treetagg(sentences, ttfname_i, ttfname_o, tt_bin, tt_par):
    """
    Output everything to a file, one token on a line,
    process with treetagger, return generator of treetagged tokens.
    """
    tokens = sum([[token[0] for token in sent] for sent in sentences], [])
    with open(ttfname_i, 'w', encoding='utf-8') as tmp_file:
        tmp_file.write('\n'.join(tokens))

    call([tt_bin, '-token', tt_par, ttfname_i, ttfname_o])
    with open(ttfname_o, 'r', encoding='utf-8') as tmp_file:
        text = tmp_file.read()
        tok_gen = (token.split('\t') for token in text.split('\n'))
    return tok_gen

def detect_nonflex(token):
    """
    Detect nonflex case, gender, number for S.
    """
    all_feats = ' '.join(token[3])
    case, gender, number = False, False, False
    cases = list(set(rt.case[0].findall(all_feats)))
    if len(cases) >= 6:
        case = True
        genders = rt.gender[0].findall(all_feats)
        if len(genders) >= len(cases) * 2 and len(list(set(genders))) > 1:
            gender = True
            numbers = rt.number[0].findall(all_feats)
            if len(numbers) >= len(cases) * len(list(set(genders))) * 2 and len(list(set(numbers))) > 1:
                number = True
        elif len(genders) == 0:
            numbers = rt.number[0].findall(all_feats)
            if len(numbers) >= len(cases) * 2 and len(list(set(numbers))) > 1:
                number = True
    return case, gender, number

def tt_correct(sentences, tt_tokens):
    """
    Correct sentences with treetagger tags.
    """
    corrected_text = []
    for sentence in sentences:
        corrected_sentence = []
        for i, token in enumerate(sentence):
            tt_token = next(tt_tokens)
            pos, feat, glued = parse_gr(tt_token[0], tt_token[1], repl=False)
            if token[2] == 'A' and token[1] in ['ЕГО', 'ЕЕ', 'ИХ']:
                token = correct_token_shallow(token, 'A', 'A - nonflex nonflex plen nonflex -')
            elif token[2] == 'S' and len(token[3]) >= 6:
                case, gender, number = detect_nonflex(token)
                token = correct_token_deep(token, pos, feat)
                feats = token[3].split()
                if case:
                    feats[3] = 'nonflex'
                if number:
                    feats[4] = 'nonflex'
                token = token[:2] + (' '.join(feats), ' '.join(feats))
            elif token[2] in ['S', 'A']:
                token = correct_token_deep(token, pos, feat)
            elif token[2] in ['PART'] and token[1] in ['ЭТО', 'ТО']:
                token = correct_token_shallow(token, pos, feat)
            corrected_sentence.append(token)
        corrected_text.append(corrected_sentence)
    return corrected_text

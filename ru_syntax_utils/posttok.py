import re
from ru_syntax_utils.token_struct import *
from ru_syntax_utils.segment import special_tokens

glue_terminal_re = re.compile('[.!?]+')

# regexp to check if end token of tokenised sentence is a terminal
mark_terminal_re = re.compile('([.!?]+)|[:;…"»)]')

# templates to retokenise most common abbreviations
abbr_templates = [
        (('т.', 'т'), 
         ('д', 'д.', 'е', 'е.', 'з', 'з.', 
          'к', 'к.', 'н', 'н.', 'о', 'о.', 
          'п', 'п.', 'с', 'с.')),
        (('и.'), ('о', 'о.'))
    ]

dot_templates = ['.']

def tokenise_punc(puncline):
    """
    Tokenise special cases of punctuation.
    """
    if len(puncline) == 1:
        punclist = [punc_token(puncline)]
    else:
        punclist, prev = [], 0
        puncline = puncline.replace(' ', '')
        for match in glue_terminal_re.finditer(puncline):
            if puncline[prev:match.start()] != '':
                punclist.extend([punc_token(punc) 
                    for punc in list(puncline[prev:match.start()])])
            punclist.append(punc_token(match.group(0)))
            prev = match.end()
        if puncline[prev:]:
            punclist.extend([punc_token(punc) 
                for punc in list(puncline[prev:])])
    return punclist

def get_comp_dict(comp_dict_path):
    """
    Load dictionary with composites.
    """
    with open(comp_dict_path, 'r', encoding='utf-8') as comp_file:
        comp_list = comp_file.readlines()
    comp_dict = [{}, '']
    for comp_line in comp_list:
        comp = comp_line.split()
        parts = comp[:-1]
        tags = comp[-1]
        curr_dict = comp_dict
        for part in parts:
            if not part in curr_dict[0]:
                curr_dict[0][part] = [{}, '']
            curr_dict = curr_dict[0][part]
        curr_dict[1] = tags
    return comp_dict

def detect_composites(in_list, comp_dict):
    """
    Detect composite tokens.
    """
    out_list = []
    curr_dict = comp_dict
    dump_list = []
    for token in in_list:
        if token[0].lower() in curr_dict[0]:
            dump_list.append(token)
            curr_dict = curr_dict[0][token[0].lower()]
        else:
            if dump_list != []:
                if curr_dict[1] != '':
                    new_tok = comp_token(dump_list, curr_dict[1])
                    out_list.append(new_tok)
                else:
                    out_list.extend(dump_list)
                dump_list = []
                curr_dict = comp_dict
            out_list.append(token)
    return out_list

def glue_special(tokens):
    """
    Reconstruct special tokens.
    """
    for sp_token_template in special_tokens:
        sp_token = ''
        if tokens[0][0] == sp_token_template[1]:
            glue = True
            new_tokens = []
        else:
            glue = False
            new_tokens = [tokens[0]]
            
        for token in tokens[1:]:
            if glue:
                if token[0] == sp_token_template[2]:
                    glue = False
                    new_tokens.append(sp_token_template[3](sp_token))
                    sp_token = ''
                else:
                    sp_token = sp_token + token[0]
            else:
                if token[0] == sp_token_template[1]:
                    glue = True
                else:
                    new_tokens.append(token)
        tokens = new_tokens
    return tokens

def try_types_post(text):
    for regexp in post_mystem:
        if regexp[0].match(text):
            return [typed_token(text, regexp)]
    if post_punc[0].match(text):
        return tokenise_punc(text)
    return [nonlex_token(text)]

def check_templates(parts, templates):
    check = False
    for template in templates:
        check = check or check_template(parts, template)
    return check

def check_template(parts, template):
    check = True
    for part, templ_part in zip(parts, template):
        check = check and part in templ_part
    return check

def rework(in_list, templates, check_last=False):
    """
    Rearrange tokens according to templates.
    """
    out_list = [in_list[0]]
    for token in in_list[1:-1]:
        if check_last:
            parts = (out_list[-1][0], token[0])
        else:
            parts = (token[0])
        if check_templates(parts, templates):
            out_list[-1] = glue_tokens([out_list[-1], token], 0)
        else:
            out_list.append(token)
    out_list.append(in_list[-1])
    return out_list

def post(glued, comp_dict):
    """
    Reconstruct special cases.
    """
    # reconstruct special tokens
    glued = glue_special(glued)
    # glue dots after abbreviations
    glued = rework(glued, dot_templates)
    # glue т.е. and the like
    glued = rework(glued, abbr_templates, check_last=True)
    # reconstruct composites
    glued = detect_composites(glued, comp_dict)
    return glued

def mystem_postprocess(analyzed, comp_dict):
    """
    Postprocess mystem output.
    """
    sentences = []
    current_sentence = []
    for analysis in analyzed:
        if '|' in analysis['text']: # the end of the line
            pieces = analysis['text'].split('|')
            pieces = [piece.strip() for piece in pieces]
            if current_sentence:
                if pieces[0] != '':
                    current_sentence.extend(try_types_post(pieces[0]))
                if mark_terminal_re.match(current_sentence[-1][1]):
                    current_sentence[-1] = terminal_token(current_sentence[-1])
                else:
                    current_sentence.append(forced_fullstop)
                sentences.append(post(current_sentence, comp_dict))
                current_sentence = []
                if pieces[1] != '':
                    current_sentence.extend(try_types_post(pieces[1]))
        else:            
            if 'analysis' in analysis: # can it be morphotagged?
                if analysis['analysis'] != []:
                    current_sentence.append(parse_analysis(analysis))
                else: # is it something nonlex?
                    current_sentence.extend(try_types_post(analysis['text']))
            else: # is it a punctuation?
                if analysis['text'].strip() != '': # is it a whitespace?
                    current_sentence.extend(try_types_post(analysis['text'].strip()))
    if current_sentence:
        if mark_terminal_re.match(current_sentence[-1][1]):
            current_sentence[-1] = terminal_token(current_sentence[-1])
        else:
            current_sentence.append(forced_fullstop)
        sentences.append(post(current_sentence, comp_dict))
    return sentences

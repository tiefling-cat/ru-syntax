from ru_syntax_utils import get_tokens_and_sent_segmentation
import re
from collections import namedtuple
from ru_syntax_utils.token_struct import nonlex_token, num_token

ws_re = re.compile('\s')

# regexp to find for suspected end of sentence
sent_end_cand_re = re.compile('((([.!?]+)|…)["»)]*\s)|;|(:\s[-—])')

# all regexps to check if candidate for end of sentence should be excluded

# decimal dot or
decimal_dot_re = re.compile('\d[.:]\d')
# commas
post_comma_re = re.compile('[.!?…]["»)]?,')
# potential part of web address
www_dot_re = re.compile('[a-z]\.[a-z]')
# dot in abbreviation with no space
abbr_dot_re = re.compile('[А-ЯЁа-яё]\.[А-ЯЁа-яё]')
# dot following single uppercase letter
init_dot_re = re.compile('(^|[^А-ЯЁ])[А-ЯЁ]\.')
# http start
http_re = re.compile('http://')
# lowercase letter
lowercase_re = re.compile('(?<![А-ЯЁA-Z])[а-яёa-z]')
# digits following abbreviations
abbrdigit_re = re.compile('[а-яё]\. [0-9]')
# wtf???
mixedpunc_re = re.compile('[.!?…]["»]*\)(?!=[.!?…])')
# some abbreviations
spec_abbr_re = re.compile('ред\.')
# end of direct speech
direct_end_re = re.compile('["»]\s[-—]')

# terminal symbol
terminal_re = re.compile('[.!?]+')

# checks for overriding end of sentence candidates
EndCheck = namedtuple('EndCheck', ['regex', 'offset'])

sent_end_checks_start = [
        EndCheck(decimal_dot_re, -1),
        EndCheck(post_comma_re, -1),
        EndCheck(post_comma_re, 0),
        EndCheck(www_dot_re, -1),
        EndCheck(abbr_dot_re, -1),
        EndCheck(init_dot_re, -2),
        EndCheck(http_re, -4),
        EndCheck(mixedpunc_re, 0),
        EndCheck(spec_abbr_re, -3)
    ]

sent_end_checks_end = [
        EndCheck(lowercase_re, 0),
        EndCheck(direct_end_re, -1)
    ]

# special tokens to be found before mystem processing
web_address_re = re.compile('((http://)|/)?'
                            '([A-Za-z][A-Za-z0-9-]+[./@])+'
                            '[A-Za-z0-9-]+/?')
number_re = re.compile('([0-9]+[.,:])+[0-9]+')
date_re = re.compile('([0-9]+/){2,}[0-9]+')

SpecialToken = namedtuple('SpecialToken', ['regex', 'start', 'end', 'token_type'])

special_tokens = [
        SpecialToken(web_address_re, 'STARTWEB', 'ENDWEB', nonlex_token),
        SpecialToken(number_re, 'STARTNUM', 'ENDNUM', num_token),
        SpecialToken(date_re, 'STARTNUM', 'ENDNUM', num_token)
    ]

def check_sent_end(line, match):
    """
    Run through the overriding rules, check if suspected end of sentence is really one.
    """
    check = True
    for end_check in sent_end_checks_start:
        check = check and not end_check.regex.match(line[match.start() + end_check.offset:])
    for end_check in sent_end_checks_end:
        check = check and not end_check.regex.match(line[match.end() + end_check.offset:])
    return check

def detect_special_tokens(line):
    """
    Find special tokens, e.g., html addresses, and put them into tags.
    """
    for special_token in special_tokens:
        special_line, prev = '', 0
        # insert tags for each found special token
        for st_match in special_token.regex.finditer(line):
            special_line = ' '.join([special_line, line[prev:st_match.start()],
                special_token.start, st_match.group(0), special_token.end, ''])
            prev = st_match.end()
        # append the tail
        if line[prev:]:
            special_line = special_line + line[prev:]
        line = special_line
    return line

def segment_line(line):
    """
    Break line into sentences.
    """
    # detect special tokens
    line = detect_special_tokens(line.strip())

    # now segment the line
    sentences, prev = [], 0
    # go through all candidates for end of sentence
    for end_match in sent_end_cand_re.finditer(line):
        # check if the candidate is for real
        if check_sent_end(line, end_match):
            sentences.append(line[prev:end_match.end()])
            prev = end_match.end()
    # append the rest
    if line[prev:]:
        sentences.append(line[prev:])

    return sentences


def segment_text(raw_text):
    """
    Segment raw text.
    """
    """segmented =[]
    for line in raw_text:
        segmented.extend(segment_line(ws_re.sub(' ', line)))"""
    tokenizer = get_tokens_and_sent_segmentation.Text(fname='', text_in_string=raw_text, path_input=False)
    tokenizer.process()
    # removing all the punctuation from tokens so as to count number of words in text
    segmented = [' '.join(sent) for sent in tokenizer.get_sentence_segmentation()]
    return ' | '.join(segmented)

def flush(sentences, ofile):
    """
    Output segmented sentences to ofile.
    """
    for sent in sentences:
        for i, token in enumerate(sent):
            ofile.write('\t'.join([str(i + 1)] + list(token) + ['_'] * 4) + '\n')
        ofile.write('\n')

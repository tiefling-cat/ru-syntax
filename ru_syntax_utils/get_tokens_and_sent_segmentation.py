#-*-coding=utf-8-*-

"""
The first version of code by Elmira Mustakimova is taken from
https://github.com/elmiram/RusTokenizer/blob/master/get_tokens_and_sent_segmentation.py
Modified for Python-3 by Mikhail Sadov.
"""
import os
import re
from html import parser

__author__ = 'elmiram'

# Splitter Regex
regSpaces1 = re.compile(u' {2,}| +|\t+|&nbsp;| ', flags=re.U | re.DOTALL)
regSpaces2 = re.compile(u'(?: *\r\n)+ *', flags=re.U | re.DOTALL)
regTags = re.compile(u'</?(?:a|img|span|div|p|body|html|head)(?: [^<>]+)?>|[\0⌐-♯]+',
                     flags=re.U | re.DOTALL)
regNonstandardQuotesL = re.compile(u'[“]', flags=re.U | re.DOTALL)
regNonstandardQuotesR = re.compile(u'[”]', flags=re.U | re.DOTALL)
regEndSentence = re.compile(u'(?:[.!?;;]+(?:[)\\]}>/»\r\n]|$)|^\r?\n$|\\\\n)',
                            flags=re.U | re.DOTALL)
regSeparatePunc = re.compile(u'^(.*?([.?!;;]+[)\\]>}»]+)*(\\\\n|[.?!;;])+)(.*)$',
                             flags=re.U | re.DOTALL)
regPuncSpaceL = re.compile(u'^[(\\[<{«-‒–—―]', flags=re.U)
regPuncSpaceR = re.compile(u'[)\\]>}»-‒–—―.,:?!;;%‰‱··]$', flags=re.U)
regDigit = re.compile(u'^(?:[0-9]{1,2}|[0-9][0-9\\-.,]+[0-9][%‰‱]?)$',
                      flags=re.U)


# Language Specific Regex

regLat = re.compile(u'^[a-zA-Z]+$', flags=re.U)
regCaps = re.compile(u'^[A-ZА-ЯЁ]+$', flags=re.U)  # WORD
regCap = re.compile(u'^[A-ZА-ЯЁ]', flags=re.U)  # Word
regPuncWords = re.compile(u'([.,!?:;·;·\\)\\]>/])([A-Za-zА-ЯЁа-яё(\\[<{«])',
                          flags=re.U | re.DOTALL|re.I)  # punctuation inside a word
regTokenSearch = re.compile(u'^([^A-Za-zА-ЯЁа-яё0-9]*)' +\
                            u'([0-9,.\\-%]+|' +\
                            u'[A-Za-zА-ЯЁа-яё0-9\\-\'`´‘’‛/@.,]+?)' +\
                            u'([^A-Za-zА-ЯЁа-яё0-9]*)$',
                            flags=re.U | re.DOTALL)
regQuotesL = re.compile(u'([\\s(\\[{<\\-])"([A-Za-zА-ЯЁа-яё0-9\\-\'`´‘’‛@.,-‒–—―•])',
                        flags=re.U | re.DOTALL)
regQuotesR = re.compile(u'([A-Za-zА-ЯЁа-яё0-9\\-\'`´‘’‛/@.,-‒–—―•.,!?:;·;·])"([\\s)\\]}>\\-.,!])',
                        flags=re.U | re.DOTALL)

# Abbreviations

def file_opener(filename):

    with open(filename, encoding='utf-8') as opener:
        file = opener.read()

    contents = file.split('\n')

    return contents

abbr_puncts, abbr_names, pref, endings = file_opener(r'C:\Users\Mike\PycharmProjects\ru-syntax\ru_syntax_utils\lists\abbr_puncts.txt'), \
                                         file_opener(r'C:\Users\Mike\PycharmProjects\ru-syntax\ru_syntax_utils\lists\abbr.txt'),\
                                         file_opener(r'C:\Users\Mike\PycharmProjects\ru-syntax\ru_syntax_utils\lists\prefixes.txt'),\
                                         file_opener(r'C:\Users\Mike\PycharmProjects\ru-syntax\ru_syntax_utils\lists\endings.txt')

# для сокращений и т.д., и т.п., т.е., 2014 г., в т.ч., какой-л., какой-н.

hPrs = parser


class Token:
    dictAna = {}

    def __init__(self, token):
        token = token.replace(u'\r\n', u'\n').replace(u'\r', u'').strip()
        self.text = token
        self.tokenType = u'wf'
        self.sentencePos = u''
        self.lang = u''
        self.graph = u''
        self.punctl = u''
        self.punctr = u''

    def define_type(self):
        if regLat.search(self.text):
            self.lang = u'lat'
        elif regDigit.search(self.text):
            self.lang = u'digit'
        if regCaps.search(self.text):
            self.graph = u'caps'
        elif regCap.search(self.text):
            self.graph = u'cap'
    
    def xml_clean(self, s):
        return s.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;').replace(u'\'', u'&apos;')

    def __str__(self):
        result = ''
        if self.sentencePos == u'bos':
            result = '<s>\r\n'
            if self.punctl != '':
                result += self.punctl + '\r\n'
        result += self.xml_clean(self.text) + '\r\n'
        if self.punctr:
            result += self.punctr + '\r\n'
        if self.sentencePos == u'eos':
            result += '</s>\r\n'
        return result


# for one file; simply returns the result
class Text:
    def __init__(self, fname='', text_in_string='', path_input=True):
        if path_input:
            try:
                f = open(fname, 'r', encoding='utf-8')
                self.text = f.read()
                f.close()
            except:
                print(u'Error when loading text ', fname)
                self.text = u''
        else:
            self.text = text_in_string
        self.wordsCnt = 0
        self.sentsCnt = 0
        self.sentno = u''
        self.wordno = u''
        self.clean_text()

    def clean_text(self):
        self.convert_html()
        self.clean_spaces()
        self.separate_words()
        self.convert_quotes()
        self.clean_other()

    def convert_html(self):
        self.text = regTags.sub(u'', self.text)  # deletes all tags in angle brackets
        self.text = hPrs.unescape(self.text)  # changes all escaped characters (like &quot;) back to their normal view (like ")

    def clean_spaces(self):
        if u'\r' not in self.text:
            self.text = self.text.replace(u'\n', u'\r\n')
        self.text = regSpaces1.sub(u' ', self.text.strip())  # unify all spaces
        self.text = regSpaces2.sub(u'\r\n ', self.text)  # normalize new lines

    def separate_words(self):
        # punctuation inside a word
        self.text = regPuncWords.sub(u'\\1 \\2', self.text)  # adds a space between punctuation and next letter

    def convert_quotes(self):
        self.text = regQuotesL.sub(u'\\1«\\2', self.text)
        self.text = regQuotesR.sub(u'\\1»\\2', self.text)
        self.text = regNonstandardQuotesL.sub(u'«', self.text)
        self.text = regNonstandardQuotesR.sub(u'»', self.text)

    def clean_other(self):
        self.text = self.text.replace(u'…', u'...')
        self.text = self.text.replace(u'\\', u'/')
        # print self.text

    def get_word_r(self, iWf):
        """Finds the first word in self.wfs after the item with index iWf."""
        for i in range(iWf + 1, len(self.wfs)):
            if self.wfs[i].tokenType == u'wf':
                return self.wfs[i]
        return None

    def check_hyphen(self, text):
        if '-' not in text:
            return True
        if text in abbr_names:
            return True
        words = text.split('-')
        if words[0] in pref:
            return True
        if words[1] in endings:
            return True
        if all(i[0].isupper() for i in words if i != ''):
            return True
        if all(all(i.isdigit() for i in word) for word in words[:2]):
            return False
        if all(i.isdigit() for i in words[0]):
            return True
        return False
    
    def tokenize(self):
        self.rawTokens = self.text.split(u' ')
        self.wfs = []
        totalWords = 0
        for token in self.rawTokens:
            if len(token) <= 0:
                continue
            m = regTokenSearch.search(token)
            if m is None:
                if token in u'\r\n':
                    self.wfs.append(Token(u'\r\n'))
                    self.wfs[-1].tokenType = u'punc'
                elif len(token) > 0:
                    self.wfs.append(Token(token))
                    self.wfs[-1].define_type()
                continue
            puncl = Token(m.group(1))
            if len(puncl.text) > 0:
                self.wfs.append(puncl)
                self.wfs[-1].tokenType = u'punc'

            middle_wf = m.group(2)
            if self.check_hyphen(middle_wf):
                wf = Token(middle_wf)
                if wf.text in u'\r\n':
                    wf.text = u'\r\n'
                    self.wfs.append(wf)
                    self.wfs[-1].tokenType = u'punc'
                elif len(wf.text) > 0:
                    self.wfs.append(wf)
                    totalWords += 1
                    self.wfs[-1].define_type()
            else:
                parts = middle_wf.split('-')
                wf = Token(parts[0])
                if wf.text in u'\r\n':
                    wf.text = u'\r\n'
                    self.wfs.append(wf)
                    self.wfs[-1].tokenType = u'punc'
                elif len(wf.text) > 0:
                    self.wfs.append(wf)
                    totalWords += 1
                    self.wfs[-1].define_type()
                for part in parts[1:]:
                    puncl = Token('-')
                    if len(puncl.text) > 0:
                        self.wfs.append(puncl)
                        self.wfs[-1].tokenType = u'punc'
                    wf = Token(part)
                    if wf.text in u'\r\n':
                        wf.text = u'\r\n'
                        self.wfs.append(wf)
                        self.wfs[-1].tokenType = u'punc'
                    elif len(wf.text) > 0:
                        self.wfs.append(wf)
                        totalWords += 1
                        self.wfs[-1].define_type()

            puncr = Token(m.group(3))
            if len(puncr.text) > 0:
                self.wfs.append(puncr)
                self.wfs[-1].tokenType = u'punc'

        self.wordsCnt = totalWords
        return totalWords

    def split_sentences(self):
        prevWord = None
        sentno = 1
        wordno = 1
        firstWord = self.get_word_r(-1)
        if firstWord is not None:
            firstWord.sentencePos = u'bos'
        for iWf in range(len(self.wfs)):
            wf = self.wfs[iWf]
            if wf.tokenType == u'punc' and\
               regEndSentence.search(wf.text) is not None:
                wordR = self.get_word_r(iWf)
                if prevWord is not None and\
                   wordR is not None and len(wordR.text) > 0 and\
                   (wordR.text[0].isupper() or wordR.text[0].isdigit()) and\
                   (prevWord.text not in abbr_puncts and (len(prevWord.text) > 1 or\
                    prevWord.text.islower())):
                    if prevWord.sentencePos == u'':
                        prevWord.sentencePos = u'eos'
                    wordR.sentencePos = u'bos'
                    wordno = 1
                    sentno += 1
            elif wf.tokenType == u'wf':
                wf.sentno = sentno
                wf.wordno = wordno
                wordno += 1
                prevWord = wf
        self.sentsCnt = sentno

    def separate_punc(self, punc):
        m = regSeparatePunc.search(punc)
        if m is None:
            return punc, punc
        return self.add_space_to_punc(m.group(1)),\
               self.add_space_to_punc(m.group(4))

    def add_space_to_punc(self, punc):
        if regPuncSpaceL.search(punc):
            punc = u' ' + punc
        if regPuncSpaceR.search(punc):
            punc += u' '
        return punc
    
    def add_punc(self):
        """Adds punctuation to the words."""
        prevPunc = u''
        prevWord = None
        for wf in self.wfs:
            if wf.tokenType == u'wf':
                if prevWord is not None and\
                   (prevWord.sentno != wf.sentno or u'\\n' in prevPunc):
                    punc1, punc2 = self.separate_punc(prevPunc)
                else:
                    prevPunc = self.add_space_to_punc(prevPunc)
                    punc1, punc2 = prevPunc, prevPunc
                if prevWord is not None:
                    prevWord.punctr = punc1
                wf.punctl = punc2
                prevWord = wf
                prevPunc = u''
            elif wf.tokenType == u'punc':
                prevPunc += wf.text.replace(u'\'', u'’')
        if prevWord is not None:
            prevWord.punctr = prevPunc

    def process(self):
        totalWords = self.tokenize()
        self.split_sentences()
        self.add_punc()
        return totalWords

    def write_out(self, fname):
        try:
            f = open(fname, 'w', encoding='utf-8')
            for wf in self.wfs:
                if wf.tokenType == u'wf':
                    f.write(str(wf))
            f.close()
        except IOError:
            print ('ERROR', fname)


    def get_sentence_segmentation(self):
        total_result = []
        pre_total_result = []
        local_result = []
        for wf in self.wfs:
            if wf.tokenType == u'wf':
                local_result.append(wf.xml_clean(wf.text))

                if wf.punctr != '':
                    local_result.append(wf.punctr)

                if wf.sentencePos == u'eos':
                    pre_total_result.append(local_result)
                    local_result = []

        pre_total_result.append(local_result)

        for sent in pre_total_result:
            additional_segmentation = []
            prev_splitter_position = 0
            flag = False

            for i in range(len(sent)-2):

                if sent[i][0] in ['.', '?', '!'] and sent[i+1] == '-' and sent[i+2][0].isupper():
                    flag = True
                    additional_segmentation.append(sent[prev_splitter_position: i+1])
                    prev_splitter_position = i+1

                if i == len(sent) - 3:
                    additional_segmentation.append((sent[prev_splitter_position:]))

            if flag:
                for add_sent in additional_segmentation:
                    total_result.append(add_sent)
            else:
                total_result.append(sent)

        return total_result


# for a bunch of files; writes the results in the separate files
class Corpus:
    """def __init__(self):
    pairs = [(u'lists/abbr_puncts.txt', abbr_puncts), (u'lists/abbr.txt', abbr_names),
             (u'lists/prefixes.txt', pref), (u'lists/endings.txt', endings)]
    for fname, arrname in pairs:
        f = codecs.open(fname, 'r', 'utf-8')
        for line in f:
            line = line.strip()
            arrname.append(line)
        f.close()"""

    def process_dir(self, dirname, outdirname, restricted=None):
        if restricted is None:
            restricted = []     # directories to be omitted
        restricted = set(restricted)
        totalWords = 0
        for root, dirs, files in os.walk(dirname):
            curdirnames = set(re.findall(u'[^/\\\\]+', root, flags=re.U))
            if len(curdirnames & restricted) > 0:
                # print u'Skipping ' + root
                continue
            print (u'Processing %s : currently %s words.' % (root, totalWords))
            for fname in files:
                if not fname.endswith(u'.txt'):
                    continue
                fname = os.path.join(root, fname)
                t = Text(fname)
                curWords = t.process()
                totalWords += curWords

                # write the output to the output directory
                fname_tokenized = fname
                fname_tokenized = re.sub(u'^[^/\\\\]+([/\\\\])', outdirname + u'\\1',
                                  fname_tokenized)
                fname_tokenized = fname_tokenized.replace(u'\'', u'_').replace(u'"', u'_')
                outPath = os.path.dirname(fname_tokenized)
                if not os.path.exists(outPath):
                    os.makedirs(outPath)
                t.write_out(fname_tokenized)
        return totalWords


# to get the segmentation

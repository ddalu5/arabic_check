#!/usr/bin/python
# coding=UTF-8

import sys, os, re
from io import open


REPORT_FILENAME = 'report.txt'
AROK_FILENAME = 'NF_AR_ok_letters.txt'
ARNOTOK_END_FILENAME = 'AR_WORDS_nottoendwith.txt'
ARNOSPACE_FILENAME = 'AR_NOSPACE_letters.txt'
TIME_PATTERN = r'(\d+) : (\d+):(\d+):(\d+):(\d+) (\d+):(\d+):(\d+):(\d+)'

META_EXTRACTION_PATTERN = (r''
                           '(\d+)'
                           '\s:\s(\d+:\d+:\d+:\d+)'
                           '\s(\d+:\d+:\d+:\d+)')

ASCII_OK = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '(', ')', '"', '.', ':',
            '-', ' ', '!', '/', '\\', '\u2010']


TWOCHARS_FILTER = (
    ('0644', '0654', 'Wrong LAM'),
    ('0644', '064b', 'Wrong LAM2'),
    ('0627', '064f', 'Wrong Dammah'),
    ('0627', '0651', 'Wrong Shaddah'),
    ('', '', 'Double Space'),
    ('0627', '064e', 'Fatha on Alef'),
    ('', '060c', 'Space before coma'),
    ('2010', '', 'Space after hyphen'),
                   )

ASCII_OK_TWOCHARS_FILTER = (
    ('', '.', 'Space before full stop'),
)

MAX_CHAR_PERLINE = 42


def print_error(error, report_filepath=REPORT_FILENAME):
    print(error)
    f = open(report_filepath, 'a')
    f.write(unicode(error)+"\n")
    f.close()


class TextSubFileWrapper:

    def __init__(self, file_path):
        self.elements = {}
        self.__load_file(file_path)

    def __load_file(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as f:
            tmp_list = f.readlines()
            y = 0
            for element in tmp_list:
                element = element.strip('\r').strip('\n').replace(u'\ufeff', '')
                if re.match(TIME_PATTERN, element.strip()):
                    i = 0
                    eid, stt, ent = self.__get_element_metas(element)
                    tmp_container = {'id': eid, 'start_time': stt,
                                     'end_time': ent, 'lines': []}
                elif element == '' and 'id' in tmp_container:
                    key = tmp_container['id']
                    self.elements[key] = tmp_container
                elif element != '' and y == len(tmp_list)-1:
                    tmp_container[i] = element
                    key = tmp_container['id']
                    self.elements[key] = tmp_container
                elif element == '':
                    pass
                else:
                    tmp_container['lines'].append(element)
                    i += 1
                y += 1

    def get_elements(self):
        return self.elements

    def __get_element_metas(self, key):
        return re.findall(META_EXTRACTION_PATTERN, key)[0]


def filter_line(element_id, row, ar_ok, ar_nospace):
    has_errors = False
    lastchar = ''
    for singlechar in list(row):
        singlecharcode = singlechar.encode("unicode_escape")
        if singlecharcode.strip('\u').strip(' ') not in ar_ok:
            if singlecharcode not in ASCII_OK:
                print_error("Subtitle number "+element_id)
                print_error("error > " + row)
                print_error('  ' + singlechar + ' [ ' + singlecharcode + ' ]\n')
                has_errors = True
            else:
                for f_lastchar, f_actchar, f_message in ASCII_OK_TWOCHARS_FILTER:
                    if singlecharcode.strip('\u').strip(' ') == f_actchar and lastchar == f_lastchar:
                        print_error("Subtitle number "+element_id)
                        print_error("error > " + row)
                        print_error(f_message+"\n")
                        has_errors = True
        else:
            for f_lastchar, f_actchar, f_message in TWOCHARS_FILTER:
                if singlecharcode.strip('\u').strip(' ') == f_actchar and lastchar == f_lastchar:
                    print_error("Subtitle number "+element_id)
                    print_error("error > " + row)
                    print_error(f_message+"\n")
                    has_errors = True
            for nospace_char in ar_nospace:
                if singlecharcode.strip('\u').strip(' ') == '' and lastchar == nospace_char:
                    print_error("Subtitle number "+element_id)
                    print_error("error > " + row)
                    print_error("There is a space after a non-space arabic char\n")
                    has_errors = True
        lastchar = singlecharcode.strip('\u').strip(' ')
    return has_errors


def load_arabic_chars(file_path):
    with open(file_path, 'r') as f:
        ar_ok = []
        for row in f:
            chartoadd = row[2:].rstrip('\n')
            ar_ok.append(chartoadd)
        return ar_ok


def load_ar_not_end(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        ar_not_end = []
        for row in f:
            ar_not_end.append(row.strip("\n"))
        return ar_not_end


def end_with(row, chars):
    try:
        data = row[row.strip('\u').index(chars, -1):]
        return data.strip() == chars
    except:
        pass
    return False


def start_with(row, chars):
    try:
        return row.strip('\u').index(chars) == 0
    except:
        pass
    return False

if __name__ == '__main__':
    if os.path.isfile(REPORT_FILENAME):
        os.remove(REPORT_FILENAME)
    local_dir = os.path.dirname(os.path.realpath(__file__))
    arnospace_filepath = os.path.join(local_dir, ARNOSPACE_FILENAME)
    arok_filepath = os.path.join(local_dir, AROK_FILENAME)
    arnotok_end_filepath = os.path.join(local_dir, ARNOTOK_END_FILENAME)
    sub_filepath = sys.argv[1]
    arok_chars = load_arabic_chars(arok_filepath)
    arnospace_chars = load_arabic_chars(arnospace_filepath)
    arnotok_end_words = load_ar_not_end(arnotok_end_filepath)
    sub_file_wrapper = TextSubFileWrapper(sub_filepath)
    elements = sub_file_wrapper.get_elements()
    contain_errors = False
    for item in elements:
        for line in elements[item]['lines']:
            if filter_line(item, line, arok_chars, arnospace_chars):
                contain_errors = True
            if u' و ' in line:
                print_error("Subtitle number "+item)
                print_error("error > " + line)
                print_error("Arabic \""+u' و '+"\" char with two spaces\n")
                contain_errors = True
            if len(line.strip()) > MAX_CHAR_PERLINE:
                print_error("Subtitle number "+item)
                print_error("error > " + line)
                print_error("MAX chars ("+str(MAX_CHAR_PERLINE)+") per line exceeded\n")
                contain_errors = True
            for word in arnotok_end_words:
                tmp_line = line.encode("unicode_escape")
                tmp_word = ' '+word.strip('\r').strip('\n').replace(u'\ufeff', '').encode("unicode_escape")
                try:
                    if tmp_line[tmp_line.index(tmp_word):].strip() == tmp_word.strip():
                        print_error("Subtitle number "+item)
                        print_error("error > " + line)
                        print_error("End with:\""+word+"\"\n")
                        contain_errors = True
                except:
                    pass
            try:
                if line[line.index('...')+3:line.index('...')+4] == ' ':
                    print_error("Subtitle number "+item)
                    print_error("error > " + line)
                    print_error("Space after ...\n")
                    contain_errors = True
            except:
                pass
        if len(elements[item]['lines']) > 2:
            print_error("Subtitle number "+item)
            print_error("Number of rows > 2\n")
            contain_errors = True
        elif len(elements[item]['lines']) == 2:
            if end_with(elements[item]['lines'][1], u'،'):
                print_error("Subtitle number "+item)
                print_error("error > " + elements[item]['lines'][1])
                print_error("Second line ends with coma\n")
                contain_errors = True
            if not start_with(elements[item]['lines'][0], u'-') \
                    and not start_with(elements[item]['lines'][1], u'-') \
                    and len(elements[item]['lines'][0]+elements[item]['lines'][1]) < MAX_CHAR_PERLINE:
                print_error("Subtitle number "+item)
                print_error("Lines don't start with - and both less than MAX chars "
                            "("+str(MAX_CHAR_PERLINE)+")\n")
                contain_errors = True

    if not contain_errors:
        print("All is Good!")

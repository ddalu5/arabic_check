#!/usr/bin/python

import sys, os, re

subfile = 'test.txt'
mydir = os.path.dirname(os.path.realpath(__file__))


class TextSubFileWrapper:

    def __init__(self, file_path):
        self.elements = {}
        self.__load_file(file_path)

    def __load_file(self, file_path):
        time_pattern = r'(\d+) : (\d+):(\d+):(\d+):(\d+) (\d+):(\d+):(\d+):(\d+)'
        with open(file_path, 'r') as f:
            tmp_list = f.readlines()
            y = 0
            for element in tmp_list:
                original_element = element.strip('\r').strip('\n')
                element = original_element.strip('\r').strip('\n')
                if re.match(time_pattern, element.strip().strip('\xef\xbb\xbf')):
                    i = 0
                    tmp_container = {'key': element}
                elif element == '' and 'key' in tmp_container:
                    key = tmp_container['key']
                    del tmp_container['key']
                    self.elements[key] = tmp_container.items()
                elif element != '' and y == len(tmp_list)-1:
                    tmp_container[i] = element
                    key = tmp_container['key']
                    del tmp_container['key']
                    self.elements[key] = tmp_container.items()
                elif element == '':
                    pass
                else:
                    tmp_container[i] = element
                    i += 1
                y += 1

    def get_elements(self):
        self.elements

    def get_element_id(self):



if __name__ == '__main__':
    sub_file_wrapper = TextSubFileWrapper('test.txt')

# This file is called by genomeSearch
# It clears out the temporary directory before doing anything to it.

import sys
import os
import logging

def main():
    args = sys.argv
    dir_to_clear = args[1]
    if dir_to_clear[-3:] == 'tmp':
        files_list = os.listdir(dir_to_clear)
        if "mmseqstmp" in files_list:
            files_list.remove('mmseqstmp')
        for filename in files_list:
            if os.path.isfile(filename):
                os.unlink(os.path.join(dir_to_clear, filename))


main()

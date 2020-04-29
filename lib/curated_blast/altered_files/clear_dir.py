# This file is called by genomeSearch
# It clears out the temporary directory before doing anything to it.

import sys
import os
import logging

def main():
    """Input should be a directory"""
    args = sys.argv
    dir_to_clear = args[1]
    # We make sure it is a tmp directory
    if dir_to_clear[-3:] == 'tmp':
        clear_directory(dir_to_clear, ['mmseqstmp'])

def clear_directory(dir_path, except_files):
    for f in os.listdir(dir_path):
        if f not in except_files:
            if os.path.isfile(f):
                os.unlink(os.path.join(dir_path, f))
            else:
                logging.info("Found directory {} in clear_directory".format(
                    f))

if __name__ == "__main__":
    main()

#python

'''
Retesting old usearch functions



'''

import os
import logging

"""
Inputs:
    fna_filepath: (str) Filepath to file with nucleotide sequence of genome.
    output_filename: (str) name of file to write out to.
    usearch_path: (str) Filepath to usearch executable file.        
    mincodons: (str) Number representing the min length for protein analysis.
Outputs:
    response: (str) Represents success of function.

"""
def usearch_fast_x(fna_filepath, output_filename, usearch_path, mincodons):
    
    os.chmod(usearch_path, 0o777)
    response =  os.system(usearch_path + " -fastx_findorfs " + fna_filepath + " -aaout " + output_filename + " -orfstyle 7 -mincodons " + mincodons )
    logging.debug(response)

    return response


def usearch_tester(usearch_path):
    #Checking problem with executable:
    logging.debug(os.system("file " + usearch_path))
    logging.debug(os.system("uname -m"))
    



def usearch_blast():

    return 0



    









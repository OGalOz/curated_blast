# This file is used to replace usearch ublast.


import os
import logging
import sys
import shutil
from Bio import SeqIO

# ublast command: $usearch -ublast $chitsfaaFile -db $seqFile -evalue $maxEvalue -blast6out $ublastFile >& /dev/null"
# Make every temporary file exist in the same temporary directory
def ublast_replace(qry_filepath, trgt_filepath, out_filepath, e_value, log_info):
    """
    Inputs:
        qry_filepath: (str) Filepath to query file
        trgt_filepath: (str) Filepath to target file
        out_filepath: (str) Filepath to the output, may not yet exist.
        e_value: (str) str of float
        log_info: (str) String that contains all of logging info not outputted.
    
    """

    mmseqs_search(qry_filepath, trgt_filepath, out_filepath, e_value, log_info)
    log_info = remove_high_e_values_and_multiply_identity(out_filepath, e_value,
                                                        out_filepath, log_info)
    with open("../tmp/log_info_main", "w") as f:
        f.write(log_info)

    return 0


# We check the file format and convert it to one that's appropriate for mmseqs, 
# i.e 1 line per id, then 1 line per sequence.
def mmseqs_search(qry_filepath, trgt_filepath, out_filepath, e_value, log_info):

    #Clear out all the previous temporary directories:
    #This clears out PaperBLAST/cgi/tmp
    # We are currently in PaperBLAST/cgi
    folder_1 = os.path.join(os.getcwd(),"tmp")

    if os.path.exists(folder_1):
        clear_directory(folder_1)
    else:
        os.mkdir(folder_1)


    #Here we clear out PaperBLAST/tmp/mmseqstmp
    folder_2 = '/PaperBLAST/tmp/mmseqstmp'
    if os.path.exists(folder_2):
        clear_directory(folder_2)
    else:
        logging.info("Making tmp/mmseqstmp")
        os.mkdir(folder_2)

    logging.info("Cleared out two directories: " + folder_1 + " " + folder_2) 

    #RUNNING MMSEQS:
    output = os.system("mmseqs createdb " + qry_filepath + " queryDB")
    if output != 0:
        os.system("rm *DB*")
        raise Exception("Failed to create queryDB from query file; there might "
                        "be something wrong with the query file format. "
                            "The command mmseqs createdb failed")

    output = os.system("mmseqs createdb " + trgt_filepath + " targetDB")
    if output != 0:
        os.system("rm *DB*")
        raise Exception("Failed to create targetDB from target file; "
                            "there might be something wrong with the target "
                            "file format. The command mmseqs createdb failed.")

    output = os.system("mmseqs createindex targetDB tmp")
    if output != 0:
        os.system("rm *DB*")
        raise Exception("Failed to index targetDB. The command mmseqs createindex failed.")

    run_mmseqs_at_varying_sensitivities()

    output = os.system("mmseqs convertalis queryDB targetDB resultDB " + out_filepath)
    if output != 0:
        os.system("rm *DB*")
        raise Exception("mmseqs convertalis failed.")

    #FOR DEBUGGING:
    shutil.copyfile(out_filepath, "../tmp/mmseqs_search_output.txt")
    os.system("mv queryDB* targetDB* resultDB* ../tmp/mmseqstmp/")
    logging.info("Moved all temporary files to mmseqstmp dir")

    return 0


def run_mmseqs_at_varying_sensitivities():
    for s in ['6.0','5.0','4.0','3.0','2.0','1.0']:
        # this is the mmseqs command that is most likely to fail.
        # we try it in different sensitivities.
        cmd = "mmseqs search queryDB targetDB resultDB tmp --alignment-mode 3 "
        cmd += "-s " + s
        logging.info("Running MMSEQS search at sensitivitiy " + s)
        output = os.system(cmd)
        if output == 0:
            logging.info("MMSEQS search succeeded at sensitivity " + s)
            break
        else:
            logging.critical("mmseqs search failed at sensitivity " + s)
            if s == '1.0':
                logging.warning("mmseqs search failed at all sensitivities")




#Here we remove all e values that are higher than the threshold
def remove_high_e_values_and_multiply_identity(filepath, e_value, out_file, log_info):
    with open(filepath, "r") as f:
        file_str = f.read()


    #DEBUGGING
    log_info += 'File:-------------\n' + file_str + 'EOF---------\n'

    #CODE
    file_list = file_str.split('\n')
    trgt_file_ids_dict = get_target_file_ids()
    new_file_list = []
    for blast_line in file_list:
        line_list = blast_line.split('\t')
        if len(line_list) > 10:
           #The e value is in the 11th spot (10th index in python)
           if float(line_list[10]) < float(e_value):

               #Making the identity in percentage, eg instead of 0.13, 13
               line_list[2] = str(float(line_list[2]) * 100)

               #Making sure the identifier is the same as in the target file:
               if line_list[1] in trgt_file_ids_dict:
                   line_list[1] = trgt_file_ids_dict[line_list[1]]
               else:
                   logging.critical('could not find corresponding id in target file for id: ' + line_list[1])
               new_file_list.append(line_list)
        else:
            logging.critical("The following line had a surprising number of "
                            "tsvs.")
            logging.critical(blast_line)

    log_info = write_list_d2_to_file(new_file_list, out_file, log_info)
    #For debugging purposes:
    log_info = write_list_d2_to_file(new_file_list, '../tmp/testing_ublast', log_info)
    return log_info

# List d2 just means a list with dimension 2- as in list within a list.
def write_list_d2_to_file(d2_list, filename, log_info):
    new_file_str_list = ['\t'.join(line_list) for line_list in d2_list]
    log_info += '\n NEW FILE STRING LIST \n' + str(new_file_str_list)
    new_file_str = '\n'.join(new_file_str_list)
    with open(filename, "w") as g:
        g.write(new_file_str)
    return log_info

def clear_directory(folder):
    for f in os.listdir(folder):
            file_path = os.path.join(folder, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    dir_to_rm = os.path.join(folder, file_path)
                    shutil.rmtree(dir_to_rm)
            except Exception as e:
                    logging.debug(e)



def get_target_file_ids():
    crnt_dir = os.getcwd()
    with open(os.path.join(crnt_dir,"../tmp/trgt_copy"), "r") as f:
        file_str = f.read()
    line_list = file_str.split('\n')
    ids_list = []
    # We take only the ids (lines that start with '>')
    for i in range(len(line_list)):
        if i%2 == 0:
            ids_list.append(line_list[i])

    # We maintain a dictionary of all the ids in the target file such that: 
    # {'part of id before first white space': 'entire id', again etc.}
    ids_dict = dict()
    for i in range(len(ids_list)):

        x = ids_list[i].split(' ')
        if isinstance(x, list):
            if x[0] != '>':
                if x[0] != '':
                    if x[0][0] != '>':
                        raise Exception("parsing error on target file")
                    else:
                        ids_dict[x[0][1:]] = (ids_list[i])[1:]
            else:
                ids_dict[x[1]] = (ids_list[i])[1:]
    
    return ids_dict

# If fasta file is in an incorrect format (i.e. not one line per id and per sequence)
def reformat_fasta_file(filename):
    out_str = ''
    seq_list = []
    for sequence in SeqIO.parse(filename, 'fasta'):
        out_str += sequence.id + '\n'
        out_str += str(sequence.seq) + '\n'
    os.system("rm " + filename)
    f = open(filename, "w")
    f.write(out_str)








#The following functions were only for comparison of ublast and mmseqs---------------------

def sort_blast_file_by_bit_score(filename, ublast_true):
    f = open(filename, "r")
    file_str = f.read()
    f.close()
    os.system("rm " + filename)
    file_list = file_str.split('\n')
    double_list = [x.split('\t') for x in file_list]

    #Sometimes the final line has no values
    if len(double_list[-1]) < 3:
        double_list = double_list[:-1]
        logging.debug("short list")
    logging.debug(double_list)


    sorted_list = sorted(double_list, key=lambda bit: bit[11])
    if ublast_true == True:
        sorted_list = clean_ublast_list(sorted_list)
    write_list_d2_to_file(sorted_list, filename)
    return sorted_list

def run_ublast(qry_filepath, trgt_filepath, out_filepath, e_value):
    output = os.system("usearch -ublast " + qry_filepath + " -db " + trgt_filepath + " -evalue " + str(e_value) + " -blast6out " + out_filepath)
    if output != 0:
        raise Exception("ublast failed")

def testing_multiple_proteins(test_dir, trgt_filepath, e_value):
    dir_list = os.listdir(test_dir)
    dir_list.remove('mprt.py')
    dir_list.remove('space')
    dir_list.remove('Trash')
    logging.debug(dir_list)
    for faa_file in dir_list:
        qry_path = os.path.join(test_dir, faa_file)
        out_path = faa_file + 'out'
        mmseqs_search(qry_path, trgt_filepath, out_path + 'mmseqs', e_value)
        run_ublast(qry_path, trgt_filepath, out_path + 'ublast', e_value)

        #Sorting both output files
        sort_blast_file_by_bit_score(out_path + 'mmseqs', False)
        sort_blast_file_by_bit_score(out_path + 'ublast', True)

        #Sending them both to the same file for comparison
        os.system("cat " + out_path + 'mmseqs space ' + out_path + 'ublast > ' + out_path)

def clean_ublast_list(list_d2):
    for list_d1 in list_d2:
        list_d1[0] = list_d1[0].split(' ')[0]
        list_d1[1] = list_d1[1].split(' ')[0]
    return list_d2

# Arguments will be -ublast $chitsfaaFile -db $seqFile -evalue $maxEvalue -blast6out $ublastFile >& /dev/null"
# Arguments need to include qry file, target file, evalue, outfile name, type of command
def main():

    logging.basicConfig(level=logging.DEBUG)

    # Current dir should be PaperBLAST/cgi
    logging.debug("Current Dir:")
    logging.debug(os.getcwd())

    logging.debug("PaperBLAST tmp dir files:")
    logging.debug(os.listdir('/PaperBLAST/tmp'))

    if len(sys.argv) < 5:
        raise Exception("Not enough args in input to main")

    arguments = sys.argv
    logging.info('arguments to main.py: ')
    logging.info(arguments)
    x, qry, trgt, out_fp, e_value = arguments[1:6]
    logging.debug("qry: {}\ntrgt: {}\n out_fp: {}\n evalue: {}".format(qry, 
        trgt, out_fp, e_value))

    for fp in [qry, trgt]:
        if not os.path.exists(fp):
            raise Exception("Internal File {} does not exist".format(fp))

    logging.info("Query and Target Files both exist.")

    output = os.system("cp " + trgt + " ../tmp/trgt_copy")
    if output != 0:
        logging.critical("Error copying target")
    if arguments[1] == "-ublast":
        logging.info("running mmseqs search".upper())
        log_info = ''
        ublast_replace(qry, trgt, out_fp, e_value, log_info)


if __name__ == "__main__": 
    main()

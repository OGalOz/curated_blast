# This file is used to replace usearch ublast.


import os
import logging
import sys
import shutil
from Bio import SeqIO

# ublast command: $usearch -ublast $chitsfaaFile -db $seqFile -evalue $maxEvalue -blast6out $ublastFile >& /dev/null"
# Make every temporary file exist in the same temporary directory

def ublast_replace(qry_filepath, trgt_filepath, out_filepath, e_value, log_info):
 
    mmseqs_search(qry_filepath, trgt_filepath, out_filepath, e_value, log_info)
    log_info = remove_high_e_values_and_multiply_identity(out_filepath, e_value, out_filepath, log_info)
    f = open("../tmp/log_info_main", "w")
    f.write(log_info)


# You need to check the file format and convert it to one that's appropriate for mmseqs, i.e 1 line per id, then 1 line per sequence.
def mmseqs_search(qry_filepath, trgt_filepath, out_filepath, e_value, log_info):

    '''
    logging.debug("QRY FP: " + qry_filepath)
    logging.debug("TRGT FP: " + trgt_filepath)
    logging.debug("OUT FP: " + out_filepath)
    logging.debug("E value: " + e_value)
    '''

    #reformat_fasta_file(qry_filepath)
    #reformat_fasta_file(trgt_filepath)
    
    #Clear out all the previous temporary directories:
    #This clears out PaperBLAST/cgi/tmp
    folder_1 = os.path.join(os.getcwd(),"tmp")
    #logging.debug("f1 : " + folder_1)
    if os.path.exists(folder_1):
        clear_directory(folder_1)
    else:
        os.mkdir(folder_1)

    #Here we create the PaperBLAST/tmp folder if it doesn't exist yet.
    folder_2 = os.path.join('/'.join(os.getcwd().split('/')[:-1]), "tmp")
    if not os.path.exists(folder_2):
        os.mkdir(folder_2)
    #clear_directory(folder_2)
    #logging.debug("f2 : " + folder_2)

    #Here we clear out PaperBLAST/tmp/mmseqstmp
    folder_3 = os.path.join(folder_2, "mmseqstmp")
    if os.path.exists(folder_3):
        clear_directory(folder_3)
    else:
        os.mkdir(folder_3)


    logging.info("Cleared out two directories: " + folder_1 + " " + folder_3) 

    """
    """

    #RUNNING MMSEQS:
    output = os.system("mmseqs createdb " + qry_filepath + " queryDB")
    if output != 0:
        #reformat_fasta_file(qry_filepath)
        #output = os.system("mmseqs createdb " + qry_filepath + " queryDB")
        #if output != 0:
        os.system("rm *DB*")
        raise Exception("Failed to create queryDB from query file; there might be something wrong with the query file format. The command mmseqs createdb failed")
    output = os.system("mmseqs createdb " + trgt_filepath + " targetDB")
    if output != 0:
        #reformat_fasta_file(trgt_filepath)
        #output = os.system("mmseqs createdb " + trgt_filepath + " targetDB")
        #if output != 0:
        os.system("rm *DB*")
        raise Exception("Failed to create targetDB from target file; there might be something wrong with the target file format. The command mmseqs createdb failed.")
    output = os.system("mmseqs createindex targetDB tmp")
    if output != 0:
        os.system("rm *DB*")
        raise Exception("Failed to index targetDB. The command mmseqs createindex failed.")
    output = os.system("mmseqs search queryDB targetDB resultDB tmp --alignment-mode 3 -s 6.0")
    
    if output != 0:
        logging.critical("mmseqs search failed at sensitivity 6")

        #The following code could try mmseqs search at lower sensitivities:
        """
        output = os.system("mmseqs search queryDB targetDB resultDB tmp --alignment-mode 3 -s 5.0")
        if output != 0:
            logging.critical("mmseqs search failed on sensitivity 5 and 6, skipping to sensitivity 3")
            output = os.system("mmseqs search queryDB targetDB resultDB tmp --alignment-mode 3 -s 3.0")
            if output != 0:
                #look for output file (resultDB)
                #If it doesn't exist throw error
                raise Exception("mmseqs search failed on alignment mode 3 with sensitivity 6 and 5.")
        """
    output = os.system("mmseqs convertalis queryDB targetDB resultDB " + out_filepath)
    if output != 0:
        os.system("rm *DB*")
        raise Exception("mmseqs convertalis failed.")
    #FOR DEBUGGING:
    g = open(out_filepath, "r")
    file_str = g.read()
    g.close()
    d = open("../tmp/mmseqs_search_output.txt", "w")
    d.write(file_str)
    d.close()

    os.system("mv queryDB* targetDB* resultDB* ../tmp/mmseqstmp/")
    logging.info("Moved all temporary files to mmseqstmp dir")


#Here we remove all e values that are higher than the threshold
def remove_high_e_values_and_multiply_identity(filepath, e_value, out_file, log_info):
    f = open(filepath, "r")
    file_str = f.read()


    #DEBUGGING
    log_info += file_str

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
            logging.critical("The following line was parsed from the file")
            logging.critical(line_list)

    log_info += write_list_d2_to_file(new_file_list, out_file, log_info)
    #For debugging purposes:
    log_info += write_list_d2_to_file(new_file_list, '../tmp/testing_ublast', log_info)
    return log_info

def write_list_d2_to_file(d2_list, filename, log_info):
    new_file_str_list = ['\t'.join(line_list) for line_list in d2_list]
    log_info += '\n NEW FILE STRING LIST \n' + str(new_file_str_list)
    new_file_str = '\n'.join(new_file_str_list)
    g = open(filename, "w")
    g.write(new_file_str)
    g.close()
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
    f = open(os.path.join(crnt_dir,"../tmp/trgt_copy"), "r")
    file_str = f.read()
    line_list = file_str.split('\n')
    ids_list = []
    #We take only the ids (lines that start with '>')
    for i in range(len(line_list)):
        if i%2 == 0:
            ids_list.append(line_list[i])

    #We maintain a dictionary of all the ids in the target file such that: {'part of id before first white space': 'entire id', again etc.}
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


# Arguments will be -ublast $chitsfaaFile -db $seqFile -evalue $maxEvalue -blast6out $ublastFile >& /dev/null"
# Arguments need to include qry file, target file, evalue, outfile name, type of command
def main():
    log_info = ''
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        logging.info(arguments)
        logging.debug("qry: " + arguments[1])
        logging.debug("trgt: " + arguments[2])
        logging.debug("out_filepath: " + arguments[3])
        logging.debug("evalue: " + arguments[4])
        output = os.system("cp " + arguments[2] + " ../tmp/trgt_copy")
        if output != 0:
            logging.critical("Error copying target")
        if arguments[0] == "-ublast":
            logging.info("running mmseqs search")
            qry_filepath, trgt_filepath, out_filepath, e_value = arguments[1], arguments[2], arguments[3], arguments[4]
            ublast_replace(qry_filepath, trgt_filepath, out_filepath, e_value, log_info)

        
    
main()





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

















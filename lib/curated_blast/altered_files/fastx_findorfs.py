#This file is a replacement for the usearch fastx_findorfs command.
'''
The command format (on usearch website):
    usearch -fastx_findorfs reads.fastq -ntout -nt.fa -aaout aa.fa -orfstyle 7 -mincodons 16
The command in Curated Blast: 
    system("$usearch -fastx_findorfs $fnafile -aaout $xfile -orfstyle 7 -mincodons $minCodons >& /dev/null") == 0

File format includes:
    (nt.fa): ">" + Sequence id + '|' "+/- 1/2/3" : "start - end" (total length) no spaces
    
The function main() is called at the end of the file.
'''

from Bio import SeqIO
from Bio.Seq import Seq
import re
import logging
import sys
from shutil import copyfile


# mincodons is variable. Orfstyle is always 7
# This means: ORF can start at the beginning of the nucleotide sequence.
# ORF can start right after a STOP codon.
# ORF can end at the end of a nucleotide sequence, doesn't need a STOP codon.
def main():
    args = sys.argv[1:]
    if len(args) < 8:
        raise Exception("Not enough arguments passed to fastx_findorfs file.")
    filename = args[1]
    min_codons = int(args[7])

    print("Fastx findorfs Arguments: ")
    print(args)

    #The name of the file to output to:
    protein_out = args[3]

    #Sequences are parsed into Bio sequence format, with name and then sequence string inside a class.
    sequences = get_all_sequences_in_Bio_python_format(filename)


    #Initialize a protein out file string
    protein_file_str = ''


    #Initialize a nucleotide file string (not currently in use)
    nucleotide_file_str = ''


    for sequence in sequences:

        #Reverse direction
        seq_str = str(sequence.reverse_complement().seq)
        file_strings = get_orfs_from_sequence(seq_str, str(sequence.id), True, min_codons)
        nucleotide_file_str += file_strings[0]
        protein_file_str += file_strings[1]

        #Forward direction
        seq_str = str(sequence.seq)
        file_strings = get_orfs_from_sequence(seq_str, str(sequence.id), False, min_codons)
        nucleotide_file_str += file_strings[0]
        protein_file_str += file_strings[1]
    
    g = open(protein_out, "w")
    g.write(protein_file_str)

    #DEBUGGING
    copyfile(protein_out, "/fastx_protein_out.txt")


    return 0



# filename: (str)
def get_all_sequences_in_Bio_python_format(filename):
    sequence_list = []
    for sequence in SeqIO.parse(filename, 'fasta'):
        sequence_list.append(sequence)
    if len(sequence_list) < 1:
        raise Exception("Could not parse any sequences from file: " + filename)
    return sequence_list



#STOP CODONS ARE: TAG , TGA, and TAA
# Reverse boolean is true if it is the reverse complement of the strand.
"""
min_codons: (int)
reverse_bool: (bool)
sequence_name: (str)
sequence_str: (str)
"""
def get_orfs_from_sequence(sequence_str, sequence_name, reverse_bool, min_codons):

    nucleotide_out_string = ''
    protein_out = ''

    #Renaming sequence_str to something shorter.
    s = sequence_str


    tot_len = len(s)
    
    #Checking that there's enough nucleotides in the sequence to perform search 
    if tot_len > (min_codons * 3):

        #Find the locations of all the stop codons:
        end_indices = [m.start() for m in re.finditer("TAG", s)] + [m.start() for m in re.finditer("TGA", s)] + [m.start() for m in re.finditer("TAA", s)]

        # These lists hold locations in terms of reading frames.
        end_codon_indeces_frame_one = []
        end_codon_indeces_frame_two = []
        end_codon_indeces_frame_three = []

        #Finding the indices given the reading frame:
        for index in end_indices:
            if (index % 3) == 0:
                end_codon_indeces_frame_one.append(index)
            elif (index % 3) == 1:
                end_codon_indeces_frame_two.append(index)
            else:
                end_codon_indeces_frame_three.append(index)
        
        #Adding the last indeces to the open frames...
        last_index = tot_len - 1
        x = last_index % 3
        end_codon_indeces_frame_one.append(last_index - x)
        if x == 0:
            end_codon_indeces_frame_two.append(last_index - 2)
            end_codon_indeces_frame_three.append(last_index - 1)
        elif x == 1:
            end_codon_indeces_frame_two.append(last_index)
            end_codon_indeces_frame_three.append(last_index - 2)
        elif x == 2:
            end_codon_indeces_frame_three.append(last_index)
            end_codon_indeces_frame_two.append(last_index - 1)

        end_codon_indeces_frame_one.sort()
        end_codon_indeces_frame_two.sort()
        end_codon_indeces_frame_three.sort()


        # If it's the reverse sequence then we give it -, if it's the original sequence give it +
        if reverse_bool == True:
            symbol = "-"
        else:
            symbol = "+"

        #The base Identifying information:
        base_sq_id = ">" + sequence_name + "|" + symbol

        #If we are working with the forward DNA Sequence directly, not the reverse complement
        if reverse_bool == False:

            #Old indx represents starting point for the frame. It's used to check if protein is long enough.
            old_indx = 0
            #
            Out_Strings = add_all_valid_sequences(end_codon_indeces_frame_one, old_indx, s, base_sq_id, 1, min_codons, tot_len, reverse_bool)

            nucleotide_out_string += Out_Strings[0]
            protein_out += Out_Strings[1]

            old_indx = 1

            Out_Strings = add_all_valid_sequences(end_codon_indeces_frame_two, old_indx, s, base_sq_id, 2, min_codons, tot_len, reverse_bool)

            nucleotide_out_string += Out_Strings[0] 
            protein_out += Out_Strings[1]


            old_indx = 2

            Out_Strings = add_all_valid_sequences(end_codon_indeces_frame_three, old_indx, s, base_sq_id, 3, min_codons, tot_len, reverse_bool)

            nucleotide_out_string += Out_Strings[0]
            protein_out += Out_Strings[1]

        #If we are working with the reverse complement
        else:

            old_indx = 2

            Out_Strings = add_all_valid_sequences(end_codon_indeces_frame_three, old_indx, s, base_sq_id, 3, min_codons, tot_len, reverse_bool)
          
            nucleotide_out_string += Out_Strings[0]
            protein_out += Out_Strings[1]

            old_indx = 1

            Out_Strings = add_all_valid_sequences(end_codon_indeces_frame_two, old_indx, s, base_sq_id, 2, min_codons, tot_len, reverse_bool)
            nucleotide_out_string += Out_Strings[0]
            protein_out += Out_Strings[1]


            old_indx = 0

            Out_Strings = add_all_valid_sequences(end_codon_indeces_frame_one, old_indx, s, base_sq_id, 1, min_codons, tot_len, reverse_bool)
            nucleotide_out_string += Out_Strings[0]
            protein_out += Out_Strings[1]


    return [nucleotide_out_string, protein_out]
    

# This function returns a string formatted in the way usearch fastx-findorfs formats it.
"""
Inputs:
    indx_list: (list)
    old_indx: (int)
    sequence: (str)
    base_sq_id: (str)
    frame_num: (int)
    min_codons: (int)
    tot_len: (int)
    reverse_bool: (bool)
Outputs:
    return_list: (list) List of length 2
        nucleotide_out_string: (str) Our fastx nucleotide string
        protein_out_string: (str) Our fastx amino acid string.
"""
def add_all_valid_sequences(indx_list, old_indx, sequence, base_sq_id, frame_num, min_codons, tot_len, reverse_bool):
    s = sequence
    nucleotide_out_string = ''
    protein_out_string = ''
    sequence_list = []

    for indx in indx_list:
        #Here we make sure only the sequences who code for more than the min codons are passed
        if (indx - old_indx) > (min_codons * 3):
            if reverse_bool == False:
                sequence_list.append([base_sq_id + str(frame_num) + ":" + str(old_indx + 1) + "-" + str(indx) + "(" + str(tot_len) + ")", s[old_indx:indx]])
            else:
                sequence_list.append([base_sq_id + str(frame_num) + ":" + str(tot_len - indx) + "-" + str(tot_len - old_indx) + "(" + str(tot_len) + ")", s[old_indx:indx]])
        old_indx = indx + 3
    for seq in sequence_list:
            nucleotide_out_string += seq[0] + "\n"
            nucleotide_out_string += seq[1] + "\n"
            protein_out_string += seq[0] + "\n"
            protein = Seq(seq[1]).translate()
            protein_out_string += str(Seq(seq[1]).translate()) + "\n"

    return_list = [nucleotide_out_string, protein_out_string]

    return return_list 

#This is an unused testing function which uses an old test file, Ros_9435.fasta.txt from Rosalind.
def test():
    logging.basicConfig(level=logging.DEBUG)
    filename = "Ros_9435.fasta.txt"
    sequences = get_all_sequences_in_Bio_python_format(filename)
    logging.debug(len(sequences))
    nucleotide_file_str = ''
    protein_file_str = ''
    for sequence in sequences:
        #Reverse direction
        seq_str = str(sequence.reverse_complement().seq)
        file_strings = get_orfs_from_sequence(seq_str, str(sequence.id), True, 16)

        nucleotide_file_str += file_strings[0]
        protein_file_str += file_strings[1]
        #Forward direction
        seq_str = str(sequence.seq)
        file_strings = get_orfs_from_sequence(seq_str, str(sequence.id), False, 16)
        nucleotide_file_str += file_strings[0]
        protein_file_str += file_strings[1]

    #logging.debug(protein_file_str)


main()

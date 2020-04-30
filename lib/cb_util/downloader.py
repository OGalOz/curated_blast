#!python3

import os
import logging
from Bio import SeqIO

def download_genome(genome_ref, gfu, scratch_dir):
    """ 
    genome_ref is string 'A/B/C', gfu is GenomeFileUtil object
    
    We use gfu to download two things:
        genome_protein meta and genome genbank
    """
    genome_protein_meta = gfu.genome_proteins_to_fasta({'genome_ref': genome_ref})

    #DEBUG
    logging.debug("GENOME PROTEIN META")
    logging.debug(genome_protein_meta)

    
    genome_protein_filepath = genome_protein_meta['file_path']
    
    
    #CODE 
    #Downloading the nucleotide sequence
    genome_nucleotide_meta = gfu.genome_to_genbank({'genome_ref': genome_ref})
    
    #DEBUG
    logging.debug("GENOME NUCLEOTIDE META")
    logging.debug(genome_nucleotide_meta)

    #CODE
    genome_genbank_filepath = genome_nucleotide_meta['genbank_file']['file_path']
    genome_fna_file_name = 'Genome_fna'
    genome_fna_fp = os.path.join(scratch_dir, genome_fna_file_name)
    SeqIO.convert(genome_genbank_filepath, "genbank",genome_fna_fp ,"fasta")

    return [genome_protein_filepath, genome_fna_fp]

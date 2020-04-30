#!python3 Set up directories for CuratedBLAST to run

import os
import logging
from shutil import copyfile

def set_up_CB(inp_d):
    """
    Setting up directories and altered files

    In this function we create all the needed directories and transfer
    the files that were changed in order to get the program to work in KBase
    into the PaperBLAST directory.
    inp_d (input dict) must contain the following keys:
        pb_home
        genome_protein_filepath
        genome_nucleotide_filepath
        genome_dir
    """
    pb_home = inp_d['pb_home']

    tmp_dir = os.path.join(pb_home, "tmp")
    fbrowse_data_dir = os.path.join(pb_home,"fbrowse_data")
    data_dir = os.path.join(pb_home, "data")
    private_dir = os.path.join(pb_home,"private")
    genome_dir = os.path.join(pb_home, inp_d['genome_dir']) 
    blast_dir = os.path.join(pb_home, "bin/blast") 
    alt_file_dir = '/kb/module/lib/curated_blast/altered_files'

    # Creating Directories in PaperBLAST directory
    for d in [tmp_dir, fbrowse_data_dir, data_dir, private_dir, genome_dir,
                blast_dir]:
        if not os.path.exists(d):
            os.mkdir(d)
        else:
            logging.warning("Directory {} already exists".format(d))

    # Copying Files Over to PaperBLAST directory
    pb_bin = os.path.join(pb_home, "bin")
    for base_file in ["clear_dir.py","fastx_findorfs.py", "main.py", "usearch"]:
        copyfile(os.path.join(alt_file_dir, base_file ),os.path.join(pb_bin, base_file))
        os.chmod(os.path.join(pb_bin, base_file), 0o111)

    # Copying the main CGI file
    copyfile(os.path.join(alt_file_dir, 'dbg_genomeSearch.cgi' ), 
            os.path.join(pb_home,"cgi/dbg_genomeSearch.cgi"))
    os.chmod(os.path.join(pb_home,"cgi/dbg_genomeSearch.cgi"), 0o111)

    # Changing file mode
    for fn in ["bl2seq", "blast/fastacmd", "blast/blastall", "blast/formatdb"]:
        os.chmod(os.path.join(pb_bin, fn), 0o111)


    #Copying Altered PaperBLAST files to appropriate directories within PaperBLAST
    logging.debug("Altered files Dir: ")
    new_files = os.listdir(alt_file_dir)
    logging.debug(new_files)
    
    #Removing current FetchAssembly (from github) and replacing with newer version
    os.unlink(os.path.join(pb_home, "lib/FetchAssembly.pm"))
    copyfile(os.path.join(alt_file_dir, 'FetchAssembly.pm'), os.path.join(pb_home, "lib/FetchAssembly.pm"))
    os.chmod(os.path.join(pb_home, "lib/FetchAssembly.pm"), 0o111)

    #We copy the genome files to their location within PaperBLAST
    genome_p_location_pb = os.path.join(genome_dir,"faa")
    genome_n_location_pb = os.path.join(genome_dir, "fna")
    copyfile(inp_d['genome_protein_filepath'], genome_p_location_pb)
    copyfile(inp_d['genome_nucleotide_filepath'], genome_n_location_pb)

    #CODE
    #We copy the reference data in the Docker data directory
    data_dir = "/data"
    pb_data_dir = os.path.join(pb_home, "data")
    for f in os.listdir(data_dir):
        # We only copy files and not directories
        if os.path.isfile(os.path.join(data_dir,f)):
            copyfile(os.path.join(data_dir, f),os.path.join(pb_data_dir,f))    

    logging.info("Succesfully completed creation of dirs and transfer of files")

    return None




def set_up_return(pb_home, scratch_dir):
    # We take the mmseqs blast output and store it in our tempdir 
    # and return it to user
    file_links = []
    raise_excep_bool = False
    tmp_dir = os.path.join(pb_home, "tmp")
    for fn in ["mmseqs_search_output.txt", "fastx_protein_out.txt", 
            "usearch_mmseqs_out", "fastx_replace_out"]:
        in_fp = os.path.join(tmp_dir, fn)
        out_fp = os.path.join(scratch_dir, fn)
        if os.path.exists(in_fp):
            copyfile(in_fp, out_fp)
            file_links.append(
                    {
                    'path': out_fp, 
                    'name': fn[:-4]
                    }
                )
            logging.info("Copied {} over to {}".format(in_fp, out_fp))
        else:
            logging.warning("Curated Blast output file {} not found".format(
                in_fp))

    if len(file_links) == 0:
        logging.critical("No output files created - Part of Program Failed " \
                + "for unknown reason." )

    return file_links

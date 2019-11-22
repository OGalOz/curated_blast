# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import stat
from shutil import copyfile
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.WorkspaceClient import Workspace
from cb_util.cb_functions import fix_html
from Bio import SeqIO

#END_HEADER


class curated_blast:
    '''
    Module Name:
    curated_blast

    Module Description:
    A KBase module: curated_blast
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.2"
    GIT_URL = "https://github.com/OGalOz/curated_blast.git"
    GIT_COMMIT_HASH = "cb732727addb493974f3bdbaf83bf6e8526e5d51"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.DEBUG)
        self.ws_url = config['workspace-url']
        #END_CONSTRUCTOR
        pass


    def run_curated_blast(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_curated_blast
        report_client = KBaseReport(self.callback_url)
        
        
        token = os.environ.get('KB_AUTH_TOKEN', None)

        if "genome_ref" in params:
            genome_ref = params['genome_ref']
            logging.debug("Genome Ref: " + genome_ref)
        else:
            logging.info('the genome reference number is not in the params.')
            raise Exception("no genome ref to download")

        if 'search_query' in params:
            search_query = params['search_query']
            logging.info("Search Query: " + search_query)
            if len(search_query) == 0:
                raise Exception("length of search query is 0 - cannot perform search")
            #Perform other tests on search query
            if ' ' in search_query:
                logging.critical("search query contains a space")
        else:
            raise Exception("search query not passed into params")

        if "match_whole_words" in params:
            mww = params["match_whole_words"]
            logging.info("Match Whole Words: " + mww)
            if mww == "1":
                whole_words_query = "&word=on"
            elif mww == "0":
                whole_words_query = ""
            else:
                raise Exception("Cannot recognize match_whole_words value")
        else:
            raise Exception("params does not include match_whole_words option.")

                   
        #Is it necessary to get the workspace?
        ws = Workspace(self.ws_url, token=token)

        #CODE
        #Downloading the Genome information in protein sequence
        gf_tool = GenomeFileUtil(self.callback_url)
        genome_protein_meta = gf_tool.genome_proteins_to_fasta({'genome_ref': genome_ref})

        #DEBUG
        logging.debug("GENOME PROTEIN META")
        logging.debug(genome_protein_meta)

        #CODE
        genome_protein_filepath = genome_protein_meta['file_path']

        #CODE 
        #Downloading the nucleotide sequence
        genome_nucleotide_meta = gf_tool.genome_features_to_fasta({'genome_ref': genome_ref})

        #DEBUG
        logging.debug("GENOME NUCLEOTIDE META")
        logging.debug(genome_nucleotide_meta)

        #CODE
        genome_nucleotide_filepath = genome_nucleotide_meta['file_path']

        #HACK CODE
        gp_file_name = genome_protein_filepath.split('/')[-1]
        gn_file_name = genome_nucleotide_filepath.split('/')[-1]

        #CODE - creating directories for curated blast
        pb_home = "/PaperBLAST"
        if not os.path.exists(os.path.join(pb_home, "tmp")):
            os.mkdir(os.path.join(pb_home, "tmp"))
        if not os.path.exists(os.path.join(pb_home,"fbrowse_data")):
            os.mkdir(os.path.join(pb_home, "fbrowse_data"))
        if not os.path.exists(os.path.join(pb_home, "data")):
            os.mkdir(os.path.join(pb_home,"data"))
        if not os.path.exists(os.path.join(pb_home,"private")):
            os.mkdir(os.path.join(pb_home, "private"))
        if not os.path.exists(os.path.join(pb_home, "tmp/ababffffbaba")):
            os.mkdir(os.path.join(pb_home, "tmp/ababffffbaba"))
        genome_dir_path = os.path.join(pb_home, "tmp/ababffffbaba")


        #CODE
        #Copying Altered PaperBLAST files to appropriate directories within PaperBLAST
        alt_file_dir = os.path.join('/kb/module','lib/curated_blast/altered_files')
        logging.debug("Altered files Dir: ")
        new_files = os.listdir(alt_file_dir)
        logging.debug(new_files)
        copyfile(os.path.join(alt_file_dir, 'dbg_genomeSearch.cgi' ),os.path.join(pb_home,"cgi/dbg_genomeSearch.cgi"))
        os.chmod(os.path.join(pb_home,"cgi/dbg_genomeSearch.cgi"), 0o111)
        
        #Removing current FetchAssembly (from github) and replacing with newer version
        os.unlink(os.path.join(pb_home, "lib/FetchAssembly.pm"))
        copyfile(os.path.join(alt_file_dir, 'FetchAssembly.pm'), os.path.join(pb_home, "lib/FetchAssembly.pm"))
        os.chmod(os.path.join(pb_home, "lib/FetchAssembly.pm"), 0o111)

        pb_bin = os.path.join(pb_home, "bin")
        copyfile(os.path.join(alt_file_dir,"clear_dir.py" ),os.path.join(pb_bin,"clear_dir.py"))
        os.chmod(os.path.join(pb_bin,"clear_dir.py"), 0o111)

        copyfile(os.path.join(alt_file_dir,"fastx_findorfs.py" ),os.path.join(pb_bin,"fastx_findorfs.py"))
        os.chmod(os.path.join(pb_bin,"fastx_findorfs.py"), 0o111)

        copyfile(os.path.join(alt_file_dir,"main.py"),os.path.join(pb_bin,"main.py"))
        os.chmod(os.path.join(pb_bin,"main.py"), 0o111)

        copyfile(os.path.join(alt_file_dir, "usearch" ),os.path.join(pb_bin,"usearch"))
        os.chmod(os.path.join(pb_bin,"usearch"), 0o111)

        if not os.path.exists(os.path.join(pb_bin,"blast")):
            logging.info("bin/blast dir does not exist in PaperBLAST")
            os.mkdir(os.path.join(pb_bin,"blast"))
        else:
            logging.info("bin/blast path exists in PaperBLAST")

        
        #The first one should just be in pb_bin, not in the blast dir
        os.chmod(os.path.join(pb_bin,"bl2seq"), 0o111)
        os.chmod(os.path.join(pb_bin, "blast/fastacmd"), 0o111)
        os.chmod(os.path.join(pb_bin,"blast/blastall"), 0o111)
        os.chmod(os.path.join(pb_bin,"blast/formatdb"), 0o111)


        #CODE
        #We copy the genome files to their location within PaperBLAST
        genome_p_location_pb = os.path.join(genome_dir_path,"faa")
        genome_n_location_pb = os.path.join(genome_dir_path, "fna")
        copyfile(genome_protein_filepath, genome_p_location_pb)
        copyfile(genome_nucleotide_filepath, genome_n_location_pb)

        #CODE
        #We copy the reference data in the PaperBLAST data directory
        data_dir = "/data"
        pb_data_dir = os.path.join(pb_home, "data")


        #CODE
        #copying data from data directory to PaperBLAST data directory
        #This is slow?
        for f in os.listdir(data_dir):
            if os.path.isfile(os.path.join(data_dir,f)):
                copyfile(os.path.join(data_dir, f),os.path.join(pb_data_dir,f))


        #CODE - RUNNING CELLO --------------------------->>>>>>>>>>>>>>
        #We start the input string to the program
        search_input = 'gdb=local&gid=ababffffbaba&query=' + search_query + whole_words_query

        #We run the program internally from within PaperBLAST's cgi directory
        os.chdir(os.path.join(pb_home,"cgi"))
        cmnds = ['perl','dbg_genomeSearch.cgi', search_input]
        with open('cb_out.html', "w") as outfile:
            subprocess.call(cmnds, stdout=outfile)

        #FINISHED RUNNING CELLO
    

        #DEBUG
        #We take the mmseqs blast output and store it in our tempdir and return it to user
        copyfile(os.path.join(pb_home,"tmp/mmseqs_search_output.txt"), os.path.join(self.shared_folder,"mmseqs_search_output.txt"))
        copyfile("/fastx_protein_out.txt", os.path.join(self.shared_folder,"fastx_protein_out.txt"))
        
        file_links = []
        file_links.append({'path':os.path.join(self.shared_folder,"mmseqs_search_output.txt"), "name": "mmseqs_search_output"})
        file_links.append({'path': os.path.join(self.shared_folder,"fastx_protein_out.txt"),"name": "fastx_out"})
        

        #We take the file that the program outputted and move it back to the shared folder
        # with the following edits: Add new base link. Remove "Searching in" line.
        f = open("cb_out.html", "r")
        html_file_str = f.read()
        f.close()

        new_file_str = fix_html(html_file_str)
        
        #writing output file to a place where KBase SDK can get to it
        os.chdir('/kb/module')
        html_path = os.path.join(self.shared_folder,"cb_out.html")
        g = open(html_path,"w")
        g.write(new_file_str)
        g.close()


        #CODE
        #preparing file for output
        html_dict = [{"path": html_path, "name":"Results", "label": "curated-blast-results"}]

        report_info = report_client.create_extended_report({

        'file_links' : file_links,
        'direct_html_link_index': 0,
        'message' : 'The results from running Curated Blast',
        'workspace_name' : params['workspace_name'],
        'html_links' : html_dict,

        })


        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_curated_blast

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_curated_blast return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]

# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import stat
import time
from shutil import copyfile
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.WorkspaceClient import Workspace
from cb_util.cb_functions import fix_html, genbank_to_faa
from cb_util.validate import validate_params
from cb_util.downloader import download_genome
from cb_util.setup_dirs import set_up_CB, set_up_return
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
    VERSION = "0.0.3"
    GIT_URL = "https://github.com/n1mus/curated_blast"
    GIT_COMMIT_HASH = "956b612e0dedfeca6649076229450815d6660cf7"

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


        # Timing:
        start_time = time.time()

        # Creating useful classes
        report_client = KBaseReport(self.callback_url)
        token = os.environ.get('KB_AUTH_TOKEN', None)
        ws = Workspace(self.ws_url, token=token)
        gf_tool = GenomeFileUtil(self.callback_url)

        #Extracting params
        whole_words_query = validate_params(params)
        genome_ref = params['genome_ref']
        search_query = params['search_query']
        
        
        # We get genome_protein_file and genome_fna_file
        genome_protein_filepath, genome_nucleotide_filepath = download_genome(
                genome_ref, gf_tool, self.shared_folder)

        # Creating directories for curated blast
        pb_home = "/PaperBLAST"
        # genome_dir must be regex match to ^[0-9A-Fa-f]+$
        genome_dir = "d1"
        set_up_inp_dict = {"pb_home": pb_home,
                "genome_protein_filepath": genome_protein_filepath,
                "genome_nucleotide_filepath": genome_nucleotide_filepath,
                "genome_dir": "tmp/" + genome_dir}
        set_up_CB(set_up_inp_dict)


        # RUNNING CURATED BLAST --------------------------->>>>>>>>>>>>>>
        # We initialize the input string to the program
        search_input = 'gdb=local&gid=' + genome_dir + '&query=' + \
                search_query + whole_words_query

        #We run the program internally from within PaperBLAST's cgi directory
        HTML_OUT = "cb_out.html"
        cmnds = ['perl','dbg_genomeSearch.cgi', search_input]
        os.chdir(os.path.join(pb_home,"cgi"))
        with open(HTML_OUT, "w") as outfile:
            subprocess.call(cmnds, stdout=outfile)
        #FINISHED RUNNING CURATED BLAST
        logging.info("Finished Running Curated BLAST, " \
                        + "now we set up return files.")

        # We take the mmseqs blast output files and store them in our tempdir 
        # which allows us to return it to the user using KB report client 
        file_links = set_up_return(pb_home, self.shared_folder)

        # We take the HTML file outputted and move it back to the shared folder
        # with the following edits: Add new base link. Remove "Searching in" 
        # line.
        with open(HTML_OUT, "r") as f:
            html_file_str = f.read()
        new_file_str = fix_html(html_file_str)
        
        #writing output file to a place where KBase SDK can get to it
        os.chdir('/kb/module')
        html_path = os.path.join(self.shared_folder, HTML_OUT)
        with open(html_path, "w") as g:
            g.write(new_file_str)


        #Timing:
        end_time = time.time()
        logging.debug("Time Taken to Run program: ")
        logging.debug(str(end_time - start_time) + " seconds")

        #CODE
        #preparing file for output
        html_dict_list = [
                {
            "path": html_path, 
            "name":"Results", 
            "label": "curated-blast-results"
            }
            ]

        report_info = report_client.create_extended_report(
            {
                'file_links' : file_links,
                'direct_html_link_index': 0,
                'message' : 'The results from running Curated Blast',
                'workspace_name' : params['workspace_name'],
                'html_links' : html_dict_list
            }
        )

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

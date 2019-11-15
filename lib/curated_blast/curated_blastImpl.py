# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
from shutil import copyfile
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.WorkspaceClient import Workspace
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
            if len(search_query) == 0:
                raise Exception("length of search query is 0 - cannot perform search")
            #Perform other tests on search query
            if ' ' in search_query:
                logging.critical("search query contains a space")
        else:
            raise Exception("search query not passed into params")


                   
        #Is it necessary to get the workspace?
        ws = Workspace(self.ws_url, token=token)
        #obj_info = ws.get_object_info3({'objects': [{'ref': genome_ref}]})

        #CODE
        gf_tool = GenomeFileUtil(self.callback_url)
        genome_protein_meta = gf_tool.genome_proteins_to_fasta({'genome_ref': genome_ref})

        #DEBUG
        logging.debug("GENOME PROTEIN META")
        logging.debug(genome_protein_meta)

        #CODE
        genome_protein_filepath = genome_protein_meta['file_path']
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
        pb_home = "/kb/module/lib/curated_blast/PaperBLAST"
        if not os.path.exists(os.path.join(pb_home, "tmp")):
            os.mkdir(os.path.join(pb_home, "tmp"))
        if not os.path.exists(os.path.join(pb_home,"fbrowse_data")):
            os.mkdir(os.path.join(pb_home, "fbrowse_data"))
        if not os.path.exists(os.path.join(pb_home, "tmp/ababffffbaba")):
            os.mkdir(os.path.join(pb_home, "tmp/ababffffbaba"))
        genome_dir_path = os.path.join(pb_home, "tmp/ababffffbaba")

        #DEBUG
        logging.debug("Bin Dir: ")
        logging.debug(os.listdir(os.path.join(pb_home, "bin")))
        
        #CODE
        #We copy the genome files to their location within PaperBLAST
        genome_p_location_pb = os.path.join(genome_dir_path,"faa")
        genome_n_location_pb = os.path.join(genome_dir_path, "fna")
        copyfile(genome_protein_filepath, genome_p_location_pb)
        copyfile(genome_nucleotide_filepath, genome_n_location_pb)

        #CODE
        #We copy the reference data in the PaperBLAST data directory
        data_dir = "/data"
        pb_data_dir = "/kb/module/lib/curated_blast/PaperBLAST/data"

        #DEBUG
        logging.debug(os.listdir(data_dir))

        #CODE
        #copying data from data directory to PaperBLAST data directory
        for f in os.listdir(data_dir):
            if os.path.isfile(os.path.join(data_dir,f)):
                copyfile(os.path.join(data_dir, f),os.path.join(pb_data_dir,f))

        #DEBUG
        logging.debug(os.listdir(pb_data_dir))

        #CODE
        #We start the input string to the program
        search_input = 'gdb=local&gid=ababffffbaba&query=' + search_query

        #We run the program internally from within PaperBLAST's cgi directory
        os.chdir('/kb/module/lib/curated_blast/PaperBLAST/cgi')
        logging.info(os.access('dbg_genomeSearch.cgi', os.X_OK))
        cmnds = ['perl','dbg_genomeSearch.cgi', search_input]
        with open('cb_out.html', "w") as outfile:
            subprocess.call(cmnds, stdout=outfile)

        #We take the file that the program outputted and move it back to the shared folder
        # with the following edits: Add new base link. Remove "Searching in" line.
        f = open("cb_out.html", "r")
        file_str = f.read()

        #DEBUG
        logging.debug(len(file_str))

        #CODE
        #Updated base link:
        base_html = '<base href="http://papers.genomics.lbl.gov/cgi-bin/" target="_blank">'
        
        #finding and inserting the base link:
        file_list = file_str.split('\n')

        #DEBUG
        logging.info("Number of lines in output file: " + str(len(file_list)))

        #CODE
        #inserting the base html line
        new_file_list = file_list[:8] + [base_html] + file_list[8:]
        
        #finding lines to remove
        bad_lines = []

        #finding a line to replace
        replace_line = 0

        #Finding and removing searching in line
        for i in range(len(new_file_list)):
            if '(ababffffbaba)' in new_file_list[i]:
                bad_lines.append(i)
            elif 'Running ublast with E' in new_file_list[i]:
                bad_lines.append(i)
            elif 'relevant proteins in Proteome with' in new_file_list[i]:
                bad_lines.append(i)
            elif 'Running ublast against the 6-frame translation.' in new_file_list[i]:
                replace_line = i

        #Replacing last ublast line:
        if replace_line != 0:
            new_file_list[replace_line] = new_file_list[replace_line].replace('ublast','mmseqs2')
        else:
            logging.critical("Could not find ublast line")
        #Going through the indeces in reverse and removing the lines
        bad_lines.sort()
        for j in range(len(bad_lines)):
            i = len(bad_lines) - j - 1
            ind = bad_lines[i]
            new_file_list = new_file_list[:ind] + new_file_list[ind+1:]


        
        new_file_str = '\n'.join(new_file_list)
        
        #writing output file to a place where KBase SDK can get to it
        os.chdir('/kb/module')
        html_path = os.path.join(self.shared_folder,"cb_out.html")
        g = open(html_path,"w")
        g.write(new_file_str)
        g.close()

        #DEBUG
        h = open(html_path, "r")
        logging.debug(h.read())

        #CODE
        #preparing file for output
        html_dict = [{"path": html_path, "name":"Results", "label": "curated-blast-results"}]

        report_info = report_client.create_extended_report({

        'direct_html_link_index': 0,
        'message' : 'The results from running Curated Blast',
        'workspace_name' : params['workspace_name'],
        'html_links' : html_dict

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

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
    '''
#BEGIN_CLASS_HEADER
#END_CLASS_HEADER
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

        gf_tool = GenomeFileUtil(self.callback_url)
        genome_protein_meta = gf_tool.genome_proteins_to_fasta({'genome_ref': genome_ref})
        genome_protein_filepath = genome_protein_meta['file_path']
        genome_nucleotide_meta = gf_tool.genome_features_to_fasta({'genome_ref': genome_ref})
        genome_nucleotide_filepath = genome_nucleotide_meta['file_path']
        #Getting just the file's name, not full path
        gp_file_name = genome_protein_filepath.split('/')[-1]
        gn_file_name = genome_nucleotide_filepath.split('/')[-1]

        #Making a directory for the genome fasta file
        genome_dir_path = os.path.join('/kb/module',"lib/PaperBLAST/tmp/ababffffbaba")
        if not os.path.exists(genome_dir_path):
            os.mkdir(genome_dir_path)

        #We copy the genome files to their location within PaperBLAST
        genome_p_location_pb = os.path.join(genome_dir_path,"faa")
        genome_n_location_pb = os.path.join(genome_dir_path, "fna")
        copyfile(genome_protein_filepath, genome_p_location_pb)
        copyfile(genome_nucleotide_filepath, genome_n_location_pb)

        #We create symlinks for the reference data in the PaperBLAST data directory
        data_dir = "/data"
        pb_data_dir = "/kb/module/lib/PaperBLAST/data"
        logging.debug(os.listdir(data_dir))
        for f in os.listdir(data_dir):
            if os.path.isfile(os.path.join(data_dir,f)):
                copyfile(os.path.join(data_dir, f),os.path.join(pb_data_dir,f))
        logging.debug(os.listdir(pb_data_dir))
        #We start the input string to the program
        search_input = 'gdb=local&gid=ababffffbaba&query=' + search_query

        #We run the program internally from within PaperBLAST's cgi directory
        os.chdir('/kb/module/lib/PaperBLAST/cgi')
        logging.info(os.access('dbg_genomeSearch.cgi', os.X_OK))
        cmnds = ['perl','dbg_genomeSearch.cgi', search_input]
        with open('cb_out.html', "w") as outfile:
            subprocess.call(cmnds, stdout=outfile)

        #We take the file that the program outputted and move it back to the shared folder
        # with the following edits: Add new base link. Remove "Searching in" line.
        f = open("cb_out.html", "r")
        file_str = f.read()

        #Updated base link:
        base_html = '<base href="http://papers.genomics.lbl.gov/cgi-bin/" target="_blank">'
        
        #finding and inserting the base link:
        file_list = file_str.split('\n')
        new_file_list = file_list[:8] + [base_html] + file_list[8:]
        bad_lines = []
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
        html_path = os.path.join(self.shared_folder,"cb_out.html")
        g = open(html_path,"w")
        g.write(new_file_str)
        os.chdir('/kb/module')

        html_dict = [{"path": html_path, "name":"Results"}]

        report_info = report_client.create_extended_report({

        'direct_html_link_index': 0,
        'message' : 'Here are the pathway completeness results',
        'workspace_name' : params['workspace_name'],
        'html_links' : html_dict

        })


        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
#END run_curated_blast
#BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
#END_STATUS

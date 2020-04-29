# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from curated_blast.curated_blastImpl import curated_blast
from curated_blast.curated_blastServer import MethodContext
from curated_blast.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class curated_blastTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('curated_blast'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'curated_blast',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = curated_blast(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    '''
    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        search_query = 'gdb=NCBI&gid=GCF_000236665.1&query=perchlorate'
        ret = self.serviceImpl.run_curated_blast(self.ctx, {'workspace_name': self.wsName,
                                                             'parameter_1': 'Hello World!',
                                                             'search_query': search_query })
    '''
    def _test_genome_download(self):

        genome_ref = '33506/4/1'
        search_query = 'manganese'
        match_whole_words= '1'
        ret = self.serviceImpl.run_curated_blast(self.ctx, {'workspace_name': self.wsName,
                                                            'genome_ref':genome_ref,
                                                             'search_query': search_query,
                                                             'match_whole_words': match_whole_words})
    def test_not_whole_words(self):
        genome_ref = '33506/5/1' #Shewanella_amazonensis_SB2B
        genome_ref = '60798/5/1' # prod, Shewanella_amazonensis_SB2B
        search_query = "glucosamine"
        match_whole_words = '0'
        ret = self.serviceImpl.run_curated_blast(self.ctx, {'workspace_name': self.wsName,
                                                            'genome_ref':genome_ref,
                                                             'search_query': search_query,
                                                             'match_whole_words': match_whole_words})


    def _test_search_term_returned_too_many_hits(self):
        genome_ref = '60798/2/1' # prod, Carsonella rukki PV RAST
        search_query = 'DNA'
        match_whole_words = '1'
        ret = self.serviceImpl.run_curated_blast(self.ctx, {
            'workspace_name': self.wsName,
            'genome_ref': genome_ref,
            'search_query': search_query,
            'match_whole_words': match_whole_words})




    def _test_no_curated_entries(self):
        genome_ref = '60798/2/1' # prod, Carsonella rukki PV RAST
        search_query = 'F0F1'
        match_whole_words = '0'
        ret = self.serviceImpl.run_curated_blast(self.ctx, {
            'workspace_name': self.wsName,
            'genome_ref': genome_ref,
            'search_query': search_query,
            'match_whole_words': match_whole_words})







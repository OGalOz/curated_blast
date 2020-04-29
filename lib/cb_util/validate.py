#!python3


import logging


def validate_params(params):

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
            raise Exception("length of search query is 0 - cannot perform "
                            "search as it does not exist")
        #Perform other tests on search query
        if ' ' in search_query:
            logging.critical("search query contains a space")
            raise Exception("Search query cannot contain a space:\n {}".format(
                search_query))
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


    return whole_words_query

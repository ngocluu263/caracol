import zerorpc
import psycopg2 # the Python driver for Postgres
from nltk import word_tokenize, sent_tokenize
import json
import os.path
import string
from bs4 import BeautifulSoup
import logging
from scipy import sparse
from gensim import corpora, models, similarities
import logging


#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

AllUsersMmCorpusFile     = './tmp/initCorp.mm'
AllUsersDictionaryFile = './tmp/init.dict'
AllUsersSimilarityFile = './tmp/similarities.index'
#AllUsersModelFile

UserMmCorporaDir          = './tmp/UserMmCorpora/'
UserWordCountsDir         = './tmp/UserWordCounts/'
UserCorporaIdToDbIdMapDir = './tmp/IdMappings/'
UserDictionariesDir       = './tmp/UserDictionaries/'
UserSimIndicesDir         = './tmp/UserSimIndices/'

TokensOnceFile = './tmp/tokens_once.dict'
# TODO - read file into dictionary


#tokens_once_dict   = read_file_into_dictionary(TokensOnceFile)


# NOTE: CAN USE DictinoaryHash FOR FASTER LOOKUP - NO LONGER GUARANTEED ID MAPPING IS A BIJECTION (COLLISIONS POSSIBLE)

all_users_tokens_once_dict = corpora.Dictionary([[]])
all_users_tokens_once_dict.load_from_text(TokensOnceFile)
all_users_tokens_once_dict.add_documents([['word1', 'word2']])
all_users_tokens_once_dict.save_as_text(TokensOnceFile)

all_users_tokens_once_object = {}

with open(TokensOnceFile) as f:
    for line in f.readlines():
        all_users_tokens_once_object[line.split()[1]] = line.split()[0]

# print '\n\na_u_t_o_o:\n\n'
# print all_users_tokens_once_object

# for word in tokens_once_dict:
#     tokens_once_object[word] = 1


all_users_dict = corpora.Dictionary([[]])  # corpora.Dictionary([['blocker', 'vaccinated', 'werent', 'liked']])
all_users_dict = all_users_dict.load_from_text(AllUsersDictionaryFile)

all_users_dictionary_object = {}   # for lookups

with open(AllUsersDictionaryFile) as d:
    for line in d:
        split = line.split()
        # print split[1] + "  " + str(split[0])
        all_users_dictionary_object[split[1]] = split[0]   # map word to id

# print '\n\n printing dictionary object:'
# print all_users_dictionary_object
# print '\n\n'

###  Test load_from_text in the python console    <-------

# print '\n\n printing dictionary:'
# print all_users_dict.token2id
# print '\n\n'

# with open(AllUsersDictionaryFile) as f:
#     for line in f.readlines():
#         all_users_dictionary_object[line.split()[1]] = line.split()[0]
# print '\n\na_u_d_o:\n\n'
# print all_users_dict_object

# for word in all_users_dict:
#     all_users_dict_object[word] = 1

# Needed? How well can we access the dictionary file using gensim directly?
# vs. implementing the below  (VERDICT: SEEMS TO BE UNNECESSARY)
# all_users_dict = read_file_into_dictionary(AllUsersDictionaryFile)
# def read_file_into_dictionary(file):
#     dictionary = {}
#     return dictionary


# Open connection to the database
credentials = json.load(open(os.path.abspath(os.path.join(os.path.dirname(__file__),"../config/dbconfig.json"))))

# Import config for Python server
pyserver = json.load(open(os.path.abspath(os.path.join(os.path.dirname(__file__),"../config/python.json"))))
#print pyserver


MmCorpus_File = './tmp/initCorp.mm'
DictFile      = './tmp/init.dict'
SimsFile      = './tmp/similarities.index'
#LsiFile       = 
#Tokens_once   = 

# in v2 - explore smart ways to put these in db
UserDictionaries = './tmp/UserDicts/'   #for now, place individual user dictionary files in this directory
UserDictDir      = './tmp/UserDicts/'
UserLSImodels    = 
UserSimIndices   = 


tokens_once_file = {}


def filter(clipping):
    stopwords = "a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your"
    stopwords = stopwords.split(",")
    filtered = [trim(token.lower()) for token in clipping if "\'" not in token and token not in string.punctuation]
    filtered = [trim(token) for token in filtered if len(token) > 0]
    filtered = [trim(token) for token in filtered if token not in stopwords]

    tokens_once = set(word for word in filtered if filtered.count(word) == 1)

    # These tokens occur once in clipping - we want to know if they occur once in the corpus of all users

    # If they're in the all_users_dict(ionary), we've already encountered at least 2 instances, so remove them from tokens_once 

    # If they're not in a_u_dictionary, check them against the global tokens_once_dict (t_o_d)
    #    if in t_o_d, remove from global tokens_once_dict, remove from this tokens_once set, and add to a_u_dictionary
    #       else, add to t_o_d, leave them in tokens_once to be removed in the next line

    words_to_add_to_tokens_once_dictionary = []
    words_to_add_to_all_users_dictionary = []

    #print '\n\n Examining once-occurring words \n\n'

    for word in tokens_once:
        if word in all_users_dictionary_object:
            tokens_once = tokens_once - set(word)
            #print 'here 1'
            #print '\n'
        else:
            if word in all_users_tokens_once_object:
                del all_users_tokens_once_object[word]
                tokens_once = tokens_once - set(word)
                all_users_dictionary_object[word] = -1;   # don't yet know dictionary id
                words_to_add_to_all_users_dictionary.append(word)
                # print 'here 2'
                # print '\n'
            else:
                all_users_tokens_once_object[word] = -1;
                words_to_add_to_tokens_once_dictionary.append(word)
                # print 'here 3'
                # print '\n'


    # Add_documents takes corpora - lists of lists of words (lists of documents)
    all_users_dict.add_documents([words_to_add_to_all_users_dictionary])
    all_users_tokens_once_dict.add_documents([words_to_add_to_tokens_once_dictionary])

    # tokens_once_dict.add_documents(words_to_add_to_tokens_once_dictionary)

    # CHECK THIS <---------- <------- <--------
    # 'hypertensionstrokes', 'premiummaybe'  <------ note: EXAMINE OTHER WORD-FUSION MISTAKES LIKE THIS WITHIN T1

    # Write to file
    all_users_tokens_once_dict.save_as_text(TokensOnceFile)   # TO DO: instead of creating a dict for this, write it line by line to simple .txt file


    filtered = [word for word in filtered if word not in tokens_once]

    return filtered



def trim(s):
    if s.endswith(".\""): s = s[:-2]
    if s.endswith("\"") or s.endswith("."): s = s[:-1]
    if s.startswith("\"") or s.startswith("."): s = s[1:]
    unicodeStart = string.find(s,'\xe2')
    if unicodeStart != -1: 
      unicodeEnd = unicodeStart + 3
      s = s[:unicodeStart] + s[unicodeEnd:]
    return s


class RPC(object):

    def process_new_article(self, clipping_id, user_id):
    #def remove_html_and_tokenize_clipping_content(self, clipping_id):
        # Open connection to the database
        conn = psycopg2.connect(host=credentials["host"],database=credentials["database"],user=credentials["user"],password=credentials["password"])
        cur = conn.cursor()
        # Remove html from the content and tokenize
        cur.execute("SELECT content FROM clippings WHERE id = (%s)", ([clipping_id]))
        content = cur.fetchone()[0]
        content_sans_html = BeautifulSoup(content, "lxml").get_text()

        print 'content_sans_html'
        print content_sans_html

        cur.execute("UPDATE clippings SET content_sans_html = (%s) WHERE id = (%s)", (content_sans_html, clipping_id))
        cur.execute("UPDATE clippings SET content_sans_html_tokenized = (%s) WHERE id = (%s)", ([word for sent in sent_tokenize(content_sans_html) for word in word_tokenize(sent)], clipping_id))
        cur.execute("SELECT content_sans_html_tokenized FROM clippings")
        
        tokenized = cur.fetchone()[0]
        # Save the changes to the database

        filtered = filter(tokenized)

        # IN FILE, DEFINE MAPPING BETWEEN CLIPPING_ID_IN_CORPUS and CLIPPING_ID_IN_DB
        # remember to 0-index CL_ID_IN_CORPUS

        # THEN DO TESTS

        # recommendations = add_clipping_to_user_corpus(self, cur, filtered, clipping_id, clipping_index_in_this_batch, user_id)

        #cur still accesible inside f_i_n_u_c?
        #fold_in_new_user_clipping(self, cur, filtered, clipping_id, user_id):

        conn.commit()
        # Close database connection
        cur.close()
        conn.close()

        return "Cleaned the content of HTML and tokenized"


def read_user_word_counts(wc_file):
    counts = {}
    for line in wc_file.readlines():
        split_line = line.split()
        word_id = split_line[0]
        count = split_line[1]
        counts[word_id] = count
    return counts


# returns bow representing corpus: list of tuples representing (word_id, word_ct)
def write_user_word_counts_to_file(this_user_word_counts, wc_file):
    wc_file.seek(0)  # beginning of file - write it fresh
    word_counts_list = this_user_word_counts.items()
    word_counts_list = sorted(word_counts_list, key=lambda item: int(item[0]))
    ctr = 0
    for (key, val) in word_counts_list:
        wc_file.write(key + ' ' + str(val) + '\n')
        word_counts_list[ctr] = (int(key), int(val))
        ctr = ctr + 1
    return word_counts_list


def update_user_word_counts(this_user_word_counts, new_bow_vec):
    for entry in new_bow_vec:
        if str(entry[0]) in this_user_word_counts:
            this_user_word_counts[str(entry[0])] = int(this_user_word_counts[str(entry[0])]) + entry[1]
        else:
            this_user_word_counts[str(entry[0])] = entry[1]
    return this_user_word_counts


#  MM-deserialized corpus (as used in similarity testing) is 0-indexed
def word_counts_list_to_zero_indexing(this_user_word_counts_list):
    ctr = 0
    for (key, val) in this_user_word_counts_list:
        this_user_word_counts_list[ctr] = (key-1, val)
        ctr = ctr + 1
    return this_user_word_counts_list



def read_and_split_summary_line_of_user_corpus(f):
    lenFirstLine = len('%%MatrixMarket matrix coordinate real general\n')
    f.seek(lenFirstLine, 0)
    summary_split = f.readline().split()
    return summary_split


#WRITE:
# FLOW FOR RECEIVING NEW BMARK, PARSING & FILTERING w.r.t. TO ENTIRE CORPUS 

# LOAD USER CORPUS
# FETCH RECOMMENDATION FOR THIS ARTICLE                  <---  DEFERRED TO LATER VERSION
# FETCH RECOMMENDATION FOR ALL ARTICLES
# (COMPUTE & ) STORE RECOMMENDATION FOR THIS ARTICLE     <---  DEFERRED TO LATER VERSION
# (RECOMPUTE & ) STORE RECOMMENDATIONS FOR ALL ARTICLES  <---  NECESSARY IN THIS VERSION?



def get_number_of_files_in_user_corpus(f):
    summary_split = read_and_split_summary_line_of_user_corpus(f)
    return int(summary_split[0])


def writeToUserMmCorpusFile(f, filtered, new_bow_vec, clipping_id_in_corpus):
    
    summary_split = read_and_split_summary_line_of_user_corpus(f)

    nDocs  = summary_split[0]
    nWords = summary_split[1]
    nLines = summary_split[2]
    
    #updates
    nDocs  = str(int(nDocs) + 1)       # one more document in corpus
    nLines = str(int(nLines) + len(new_bow_vec))
    # nWords = str(int(nWords) + n_new_words)    # note we are not currently computing the number of distinct words in the user's dictionary

    lenFirstLine = len('%%MatrixMarket matrix coordinate real general\n')

    f.seek(lenFirstLine, 0)

    summaryLine = str(nDocs) + ' ' + str(0) + ' ' + str(nLines)
    nSpaces = 20 - len(summaryLine)
    for i in range(nSpaces):
        summaryLine = summaryLine + ' '
    summaryLine = summaryLine + '\n'

    f.write(summaryLine)    #str(0): note we are not currently computing the number of distinct words in the user's dictionary

    f.seek(0,2)   #start writing from end of the file
    for pair in new_bow_vec:
        word_id = pair[0]
        word_ct = pair[1]
        line = str(clipping_id_in_corpus) + ' ' + str(word_id) + ' ' + str(word_ct) + '\n'
        f.write(line)



def format_clipping(tokenized_ids):
    clippings = [];
#(first_tokenized, last_tokenized)
    conn = psycopg2.connect(host=credentials["host"],database=credentials["database"],user=credentials["user"],password=credentials["password"])
    cur = conn.cursor()
    # Remove html from the content and tokenize

    counter = 1    # note - documents in corpus are indexed 1-up
    for cl_id in tokenized_ids:
      print "\ncl_id:\n"
      print cl_id
      print "\n"
      cur.execute("SELECT content_sans_html_tokenized FROM clippings WHERE id=(%s)", ([cl_id]) )

      tokenizedClipping= cur.fetchone()[0]    #[word for sent in sent_tokenize(cur.fetchone()[0]) for word in word_tokenize(sent)]

    print "\nbefore filtering:\n"
    print tokenizedClipping

    filtered = filter(tokenizedClipping)
    clippings.append(filtered)

    print "\nafter filtering:\n"
    print filtered

    cur.close()
    conn.close()

    print 'returning from fetch...'
    return clippings


def add_user_clippings(self, cursor, clippings, clipping_ids_in_db, user_id):
    counter = 0  # note - documents in corpus are indexed 1-up, but when computing similarities, they are displayed as 0-up
    for clipping in clippings:
        cl_id = clipping_ids_in_db[counter]
        this_user_word_counts_list = add_clipping_to_user_corpus(None, cursor, clipping, cl_id, counter+1, UserIdDummy)
        counter = counter + 1
    return this_user_word_counts_list


# Perhaps use the clipping_id_in_db as the clipping id we store for the corpus as well?

def add_clipping_to_user_corpus(self, cursor, filtered, clipping_id_in_db, clipping_index_in_this_batch , user_id):

    bow_vec = all_users_dict.doc2bow(filtered) #, allow_update=True)  # updates dictionary - don't want this until LATER ITERATION
                                                                   # note indices for doc2bow is initially off-by-one from the dictionary indexing
                                                                   # ask about this on mailing list?

    all_users_dict.save_as_text(AllUsersDictionaryFile)

    new_bow_vec = []
    ctr = 0
    for entry in bow_vec:
        new_bow_vec.append((entry[0] + 1, entry[1]))
        ctr = ctr + 1

    # RETURN HERE IF IT IS INDEED NECESSARY TO KNOW THE NUMBER OF DISTINCT WORDS THAT APPEAR IN A

    this_user_word_counts_list = []
    IdMappingFile = UserCorporaIdToDbIdMapDir + str(user_id)
    ThisUserMmCorpusFile = UserMmCorporaDir + str(user_id) + '.mm'
    # only write to MmCorpusFile if we haven't seen the file before?
    try:
        with open(ThisUserMmCorpusFile, 'r+') as f:
            print '\n\nSuccessully opened "ThisUserMmCorpusFile" for user # ' + user_id + '\n\n'
            print 'Adding additional words to corpus: '

            nFilesInCorpus = get_number_of_files_in_user_corpus(f)
            clipping_id_in_corpus = clipping_index_in_this_batch + nFilesInCorpus
            writeToUserMmCorpusFile(f, filtered, new_bow_vec, clipping_id_in_corpus)

            ThisUserWordCountsFile = UserWordCountsDir + user_id
            this_user_word_counts = {}

        with open(ThisUserWordCountsFile, 'r+') as wc:
            this_user_word_counts = read_user_word_counts(wc)
            this_user_word_counts = update_user_word_counts(this_user_word_counts, new_bow_vec)
            this_user_word_counts_list = write_user_word_counts_to_file(this_user_word_counts, wc)

        with open(IdMappingFile, 'r+') as map_file:
            map_file.seek(0,2)
            map_file.write(str(clipping_id_in_corpus - 1) + ' ' + str(clipping_id_in_db) + '\n')   # convert corpus id to zero-indexing before computing similarity

    except IOError:

        print '\n\n"ThisUserMmCorpusFile" not found for user # ' + user_id + ' \n\n Now creating this file \n\n'

        clipping_id_in_corpus = clipping_index_in_this_batch      #  = 1, presumably

        with open(ThisUserMmCorpusFile, 'w+') as f:             # Create File
            f.write('%%MatrixMarket matrix coordinate real general\n') 
            f.write('0 0 0               \n')
            writeToUserMmCorpusFile(f, filtered, new_bow_vec, clipping_id_in_corpus)
        #corpora.MmCorpus.serialize(ThisUserMmCorpusFile, [[]]) #don't really need to create here, do we? can simply save after

            this_user_corpus = corpora.MmCorpus(ThisUserMmCorpusFile)   # <----- NEED THIS?

            this_user_word_counts = {}
            this_user_word_counts = update_user_word_counts(this_user_word_counts, new_bow_vec) 
            ThisUserWordCountsFile = UserWordCountsDir + user_id

        with open(ThisUserWordCountsFile, 'w+') as wc:       # Create File - Assumption: IdMappingFile does not exist, because ThisUserMmCorpusFile does not exist
            this_user_word_counts_list = write_user_word_counts_to_file(this_user_word_counts, wc)  #N.B. at this point, this_user_word_counts_list is 1-indexed - it will need to be zero-indexed before computing similarity

        with open(IdMappingFile, 'w+') as map_file:
            # map_file.seek(0,2)   # unnecessary - assumption: IdMappingFile does not exist, because ThisUserMmCorpusFile does not exist
            map_file.write(str(clipping_id_in_corpus - 1) + ' ' + str(clipping_id_in_db) + '\n')   # convert corpus id to zero-indexing before computing similarity

    all_users_corpus = corpora.MmCorpus(AllUsersMmCorpusFile)

    return this_user_word_counts_list

def corpus_to_index(corpus):
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    corpus_tfidf = tfidf[corpus]      # wrap our corpus w/ the model - will be computed later
    lsi = models.LsiModel(corpus_tfidf, id2word=all_users_dict, num_topics=3)
    corpus_lsi = lsi[corpus_tfidf]

    corpus_index = similarities.MatrixSimilarity(corpus_lsi)  # not lsi[corpus], yes?
    corpus_index.save(AllUsersSimilarityFile)

    # print "\n\nprinting topics: \n\n"
    # lsi.print_topics(3)         # WHY NOT DISPLAYING?  <--- ASK LIST? 
    return [corpus_index,  tfidf,  lsi]

def retrieve_user_corpus_to_db_id_mappings(user_id):
    id_map = {}

    IdMappingFile = UserCorporaIdToDbIdMapDir + str(user_id)
    with open(IdMappingFile, 'r') as f:
        for line in f.readlines():
            [corpus_id, db_id] = line.split()
            id_map[corpus_id] = int(db_id)
    return id_map

# Entering this function, the corpus should not yet contain the document
# When a recommendation based on a user's entire corpus is sought, 
# 'document' represents the user's full corpus, as a bag-of-words concatenation of all articles bookmarked by a user)
# 
def findSimilaritiesToDocument(corpus, document_bowvector, user_id):      #, clipping_ids_in_db):

    #  MM-deserialized corpus (as used in similarity testing) is 0-indexed
    document_bowvector = word_counts_list_to_zero_indexing(document_bowvector)

    # TODO: IN LATER ITERATION, USE 'SIMILARITY' instead of 'MATRIX SIMILARITY', load straight from the index, and add documents here 

    [corpus_index, tfidf, lsi] = corpus_to_index(corpus)

    doc_tfidf = tfidf[document_bowvector]          #uses the doc frequencies assoiated with 'corpus'
    doc_lsi = lsi[doc_tfidf]                       # convert the query to LSI space

    sims = corpus_index[doc_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    id_map = retrieve_user_corpus_to_db_id_mappings(user_id)

    similar_articles = []
    for (corpus_id, sim_score) in sims:
        db_id = id_map[str(corpus_id)]
        similar_articles.append((db_id, sim_score))

    #similar_articles = map( lambda (corpus_id, sim_score): ( int(id_map(corpus_id)), sim_score)   ,  sims)

    # USE MAPPING FROM CORPUS_ID TO CLIPPING_DB_ID     <----------------------------

    print "\n\n ranked articles: \n\n"
    print similar_articles
    print "\n\n"

    return similar_articles

# with open(AllUsersMmCorpusFile) as f:
#     for line in f.readlines():
#         print line                  # ensure format match
#     print "\n\n"


# TODO   <-----------  <-----------  <-----------  <-----------  <-----------  
# MAKE THE BELOW A FUNCTION - for populating a corpus of content that we can compare against:
#           populate_source_corpus -  (for testing - contains ~half of the articles that each person liked)
#    
# Put the other half in personal corpus: populate_personal_corpus
# Write a function that does all of this in one go - divide into different users, and source vs personal
#
#
# For now the two types of corpora won't mix - later, personal corpora will be 
# At that time, we'll have to exclude User A's articles from being recommended to her



clipping_ids = [429]   #[2, 3, 290])
clippings = format_clipping(clipping_ids)

all_users_corpus = corpora.MmCorpus(AllUsersMmCorpusFile)

# SOURCE CORPUS
# add_to_source_corpus(None, cursor, clippings, cl_ids)   <--- Make this User 1  (or -1) in the db? 

# USER CORPUS
UserIdDummy = 'test_user_1'   # replace with real user_id
this_user_word_counts_list = add_user_clippings(None, None, clippings, clipping_ids, UserIdDummy)
recommendations = findSimilaritiesToDocument(all_users_corpus, this_user_word_counts_list, UserIdDummy)


# all_users_dict = corpora.Dictionary(clippings)        <-----  USE IN TEST
# all_users_dict.save_as_text(AllUsersDictionaryFile)   <-----  "


#corpus = [all_users_dict.doc2bow(clipping) for clipping in clippings]                     <-----  USE IN TEST

#corpora.MmCorpus.serialize(AllUsersMmCorpusFile, corpus) # store to disk, for later use   <-----  "

# doc = "Health care coverage"                             <-------- First test
# doc_bowvector = all_users_dict.doc2bow(doc.lower().split())
# findSimilaritiesToDocument(corpus, doc_bowvector, user_id)

# with open(AllUsersMmCorpusFile) as f:
#     for line in f.readlines():
#         print line                  # ensure format match
#     print "\n\n"

# print "printing corpus: \n\n"
# print corpus
# print "\n\n printing all_users_dict\n\n"
# print all_users_dict
# print "\n\nprinting token-id mappings: \n\n"
# print all_users_dict.token2id


# print texts

# for clipping in corpus:
#   print "\n\n\n\n\n\n" + str(clipping) + ":\n\n"
#   print clipping


s = zerorpc.Server(RPC())
s.bind("tcp://0.0.0.0:" + pyserver["port"])
s.run()
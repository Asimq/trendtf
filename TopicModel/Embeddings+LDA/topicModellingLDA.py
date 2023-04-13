"""Importing Libraries"""

import time
import re
import yaml
import os
import csv
import torch
import itertools
import numpy as np
import random
from collections import Counter

import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamodel import LdaModel
from nltk.cluster.util import cosine_distance
from nltk.cluster import KMeansClusterer

from transformers import *
from dataPreprocessing import *

class TopicModelling:
    """TopicModelling class transform preprocessed textual tokens of document into embeddings, perform k-means clustering
    and finally use LDA to find topics of the document"""

    def __init__(self, clusters=10, tokenizer="", model="", fileName=""):
        """Set up parameters like tokenizer type, embeddings model, filename to save topics, number of clusters, number of topics
        and number of words in each topic

        Parameters:
        clusters (Int): number of cluster to make after transforming preprocessed textual tokens of document into embeddings
        tokenizer : type of tokenizer to be used with embeddings model
        model : type of embeddings model to be used for transforming preprocessed textual tokens of document
        fileName (String): file name to save the results after performing the topic modelling process on document
        """

        self.tokenizer = tokenizer
        self.model = model
        self.fileName = fileName
        self.NUM_CLUSTERS = clusters
        self.number_topics = 1
        self.number_words = 1
        self.lemmatizer = WordNetLemmatizer()
        self.idf = {}                             #Inverse Document Frequency for TF-IDF
        self.lda_model = None
        
        #Reading the Configuration file
        with open('Config.yaml', 'r') as cfg_file:
            cfg = yaml.load(cfg_file, Loader=yaml.FullLoader)
            self.input_directory = cfg['lda']['input_dir']
            self.output_directory = cfg['lda']['output_dir']
            self.word_embedding_only = cfg['lda']['mode']['word_embedding_only']
            self.LDA_only = cfg['lda']['mode']['LDA_only']
            self.word_embedding_LDA = cfg['lda']['mode']['word_embedding_LDA']
            self.save_model = cfg['lda']['save_model']
            self.load_model = cfg['lda']['load_model']
            
        assert sum([self.word_embedding_only, self.LDA_only, self.word_embedding_LDA]) == 1, 'Only ONE Approach can be applied at a time'
        
        print('Doing Topic Modelling using the Approach: {}'.format(
              'Word Embedding Only' if self.word_embedding_only else 'LDA Only' if self.LDA_only else 'Word Embedding and LDA'))
        
        if self.word_embedding_only:
            print('Calculating the Inverse Document Frequency for the whole Corpus')
            
            #Listing and Preprocessing the documents
            preprocessed_docs = PreprocessingDocuments(basepath=self.input_directory)
            documents_list = preprocessed_docs.listAllDocs()
            
            for document in documents_list:
                try:
                    #Preprocessing the document text
                    doctokens = preprocessed_docs.tokenArray(document)[0]
                    
                    #Removing duplicate words
                    doctokens = list(set(doctokens))
                    
                    #Updating word counts for the whole corpus
                    for word in doctokens:
                        if word in self.idf.keys():
                            self.idf[word] += 1
                        else:
                            self.idf[word] = 1
                except Exception as e:
                    pass
            
            #Calculating Inverse Document Frequency (IDF) for each word
            self.idf = {key: np.log(len(documents_list) / value) for key, value in self.idf.items()}
            
    def set_model_type_multilingual_bert(self):
        """Function that set up specific configurations in order to transform preprocessed textual tokens into word embeddings
        using Multilingual Bert model
       """
        config = AutoConfig.from_pretrained("bert-base-multilingual-uncased")
        config.output_hidden_states = True
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-uncased")
        self.model = AutoModelForMaskedLM.from_pretrained("bert-base-multilingual-uncased", config=config)
        self.fileName = "germanResultstest_multilingualBert.csv"

    def set_model_type_dmbz(self):
        """Function that set up specific configurations in order to transform preprocessed textual tokens into word embeddings
        using MDZ Digital Library German BERT model
       """
        self.tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-german-uncased")
        self.model = AutoModelForMaskedLM.from_pretrained("dbmdz/bert-base-german-uncased", output_hidden_states=True)
        self.fileName = "germanResultstest_dbmdz.csv"

    def set_model_type_electra(self):
        """Function that set up specific configurations in order to transform preprocessed textual tokens into word embeddings
        using German Electra BERT model
       """
        self.tokenizer = AutoTokenizer.from_pretrained("german-nlp-group/electra-base-german-uncased")
        self.model = AutoModelForPreTraining.from_pretrained("german-nlp-group/electra-base-german-uncased",
                                                             output_hidden_states=True)
        self.fileName = "germanResultstest_German_Electra.csv"

    def set_model_type_gottbert(self):
        """Function that set up specific configurations in order to transform preprocessed textual tokens into word embeddings
        using Gott BERT model
       """
        self.tokenizer = AutoTokenizer.from_pretrained("uklfr/gottbert-base")
        self.model = AutoModelForMaskedLM.from_pretrained("uklfr/gottbert-base", output_hidden_states=True)
        self.fileName = "germanResultstest_GottBert.csv"

    def transform_tokens_to_embeddings(self, dArrary):
        """Function that read the preprocessed textual tokens, convert the tokens into batch of 512 tokens, transform the
        tokens into word embeddings and finally concatenated all the word embeddings together

        Parameters:
        dArrary (List): list of preprocessed textual tokens

        Returns:
        batch_input (List): return words embeddings of the preprocessed textual tokens
        wordtoken (list): return preprocessed textual tokens

        """
        data = dArrary[0]
        total_embeddings = []
        wordtoken = []
        for data_chunk in self.batch(data, 512):
            indexed_tokens = []
            tokens_stripped = [num.strip() for num in data_chunk]
            wordtoken.append(tokens_stripped)
            indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokens_stripped)
            segments_ids = [1] * len(tokens_stripped)
            tokens_tensor = torch.tensor([indexed_tokens])
            segments_tensors = torch.tensor([segments_ids])
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(tokens_tensor, segments_tensors)
                hidden_states = outputs[1]
                token_embeddings = torch.stack(hidden_states, dim=0)
                total_embeddings.append(token_embeddings)

        batch_input = torch.cat(total_embeddings, dim=2)
        return batch_input, wordtoken

    def batch(self, iterable, n=1):
        """Generator Function that divide the iterable into chunks and yield chunk of specific length of iterable

        Parameters:
        iterable (List): list of preprocessed textual tokens

        Returns:
        list: return chunk of specific length of iterable
        """

        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    def assigned_clusters(self, token_embeddings, NUM_CLUSTERS):
        """Function that cluster the word embeddings using k-means clustering

        Parameters:
        token_embeddings (List): list of word embeddings
        NUM_CLUSTERS (Int): number of clusters to make from word embeddings

        Returns:
        Dictionary: return clustered word embeddings

        """
        rng = random.Random()
        rng.seed(123) #set specific seed in order to make results consisten when we perform k-means clustering again
        kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=cosine_distance, repeats=25, avoid_empty_clusters=True,
                                     rng=rng)
        n12 = np.squeeze(np.asarray(token_embeddings))
        assigned_clusters = kclusterer.cluster(n12[0], assign_clusters=True)
        return assigned_clusters

    def seperate_clusterwords(self, wordtoken, assigned):
        """Function that separate words assigned to each cluster

        Parameters:
        word token (List): list of word embeddings
        assigned (List): list of assigned cluster to specific word embedding

        Returns:
        list: return list of lists in which each element is list of words assigned to specific cluster

        """

        word = list(itertools.chain(*wordtoken))
        count = 1
        j = 0
        doc = []
        while j < self.NUM_CLUSTERS:
            idx = [i for i in range(len(assigned)) if assigned[i] == j]
            words = []
            j += 1
            k = 0
            while k < len(idx):
                words.append(word[idx[k]])
                k += 1
            doc.append(words)
        docstring = []
        for key in doc:
            string = '';
            for word in key:
                string = string + ' ' + word
            docstring.append(string)

        return docstring

    def fit_lda_model(self, docstring):
        """Function that uses the LDA model to find topic in each cluster of words

        Parameters:
        docstring (List): list of lists in which each element is list of words assigned to specific cluster

        Returns:
        topic_words_total: return list of topics found in the document
        coherence_lda: return coherence score of the topics found in the document
        """

        tokenized_words = []
        
        for doc in docstring:
            for text in doc:
                tokenized_words.append(word_tokenize(text))
            
        # Create Dictionary
        id2word = corpora.Dictionary(tokenized_words)

        # Term Document Frequency
        corpus = [id2word.doc2bow(text) for text in tokenized_words]

        lda_model = LdaModel(corpus=corpus, id2word=id2word,
                              num_topics=20,
                              iterations=100,
                              random_state=100,
                              update_every=1,
                              chunksize=100,
                              passes=10,
                              alpha=0.3,
                              per_word_topics=True,
                              eta=0.31)
        
        # Compute Coherence Score
        coherence_model_lda = CoherenceModel(model=lda_model, texts=tokenized_words, dictionary=id2word, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        return corpus, lda_model, coherence_lda

    def printCsv(self, rows, filename = ''):
        """Function to write the topics found in the document to file

        Parameters:
        rows (List): list containing topics of the document and the language of the document
        """
        row = rows.split(',')
        lang = row[len(row) - 1]
        
        if filename == '':
            filename = self.fileName

        with open(self.output_directory + filename, 'a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([rows])

    def evaluation_document_topics(self, topics, doctokens, coherence_score):
        """Function prints the topics, its language and its coherence score of all the documents 
        to a file as a result

        Parameters:
        topics (List): List of topics from LDA
        doctokens (List): List of topics language
        coherence_score (Double): Coherence score of the topics found in the document
        

        Returns: None
        """
        
        language = str(doctokens[2])
        tId = str(doctokens[1])
        csvRow = tId + ',' + str(topics) + ',' + language + ',' + str(coherence_score)
        self.printCsv(csvRow)
        
    def extractCompletedFiles(self, dir_path, filename):
        """
        This function will first extract all the files that are already processed and return that in a list

        Parameters
        ----------
        dir_path : String
            The directory path where the completed files are stored.
        filename : String
            The file name in which the list of file are saved.

        Returns
        -------
        completed_filenames : List
            The list containing all the file names which are already processed.

        """
        try:
            #Empty list to store the processed files
            completed_filenames = []
            
            #Checking if the file exist
            if not os.path.exists(dir_path + filename):
                return completed_filenames
            
            #Opening the file and reading the content
            data = ''
            with open(dir_path + filename, 'rt', encoding='utf-8') as f:
                data = f.read()
            data = data.split('\n')
            
            #Iterating over each record and extracting the file names and appending it in the list
            for result in data:
                r = re.match('(.*),(\[.*\]),(.*),(.*)',result.strip('"'))
                if r != None: completed_filenames.append(r.group(1))
            
            #Returning the final list of file names
            return completed_filenames
        except Exception as e:
            print(e.__str__())
            with open('exception.txt', 'a+') as file:
                file.write(e.__str__())
                
    def topic_word_embeddings_only(self, docstring, use_c_tfidf = False):
        """
        The function takes the clustered text and extracts the topics from each cluster and return it as an output.

        Parameters
        ----------
        docstring : List
            The list containing the text which have been clustered already.
        use_c_tfidf : Boolean
            Whether to use C-TF-IDF for finding the important words in a cluster or not.

        Returns
        -------
        topics : List
            The list of topics extracted from the clustered text.
        """
        try:
            #List containing the topics for the current document
            topics = []
            
            #Iterating over all the word clusters
            for word_cluster in docstring:
                words = word_cluster.strip().split()
                c = Counter(w for w in words)
                
                if use_c_tfidf:
                    
                    #Initializing variables to store most important word
                    highest_tfidf, highest_tfidf_word = 0, ''
                    
                    #Iterating over all unique words in the cluster
                    for key, value in c.items():
                        try:
                            #Calculating the C-TF-IDF of the word
                            tf_idf = (value / len(words)) * self.idf[key]
                            
                            #Updating the highest C-TF-IDF word
                            if tf_idf > highest_tfidf:
                                highest_tfidf = tf_idf
                                highest_tfidf_word = key
                        except Exception as e:
                            pass
                    
                    #Appending the word with the highest C-TF-IDF
                    topics.append(highest_tfidf_word)
                else:
                    #Appending the word which is occured the most
                    topics.append(c.most_common(1)[0][0])
            
            return topics
        except Exception as e:
            print(e)
            with open('exception.txt', 'a+') as file:
                file.write(e)
            return None
    
    
    def word_embeddings_only_coherence_score(self, word_embedding_only_docstring, word_embedding_only_topics, word_embedding_only_doctokens):
        """
        The function calculates the coherence score for each topic list using the entire corpus in the word embedding only mode.

        Parameters
        ----------
        word_embedding_only_docstring : List
            List of document Strings
        word_embedding_only_topics : List
            List of Topics.
        word_embedding_only_doctokens : List
            List of documents details.

        """
        try:
            tokenized_words = []
            for docstr in word_embedding_only_docstring:
                for text in docstr:
                    tokenized_words.append(word_tokenize(text))
            
            # Create Dictionary
            id2word = corpora.Dictionary(tokenized_words)

            #Calculating the coherence score for each topic
            cm = CoherenceModel(topics = word_embedding_only_topics, texts = tokenized_words, dictionary = id2word, coherence='c_v')
            coherence_score = cm.get_coherence_per_topic()
            
            #Writing the results on the File
            for i in range(len(word_embedding_only_topics)):
                self.evaluation_document_topics(word_embedding_only_topics[i], word_embedding_only_doctokens[i], coherence_score[i])
        except Exception as e:
            print(e)
            with open('exception.txt', 'a+') as file:
                file.write(e)
    
    def mainProcess(self):
        """Function that list all the documents, preprocessed documents text, transform text of document into word embeddings,
        perform k-means clustering and finally use LDA to find topics of the document

        Parameters:
        documents_directory_path (String): directory path which contain documents on which topic modelling is to performed
        """

        preprocessed_docs = PreprocessingDocuments(basepath=self.input_directory)
        documents_list = preprocessed_docs.listAllDocs()  # return list of all documents
        print("Total Documents", len(documents_list))
        count = 0
        
        start_time = time.time()
        
        # Initializing the a dictionary to store average time for each module
        module_meantime = {'embeddings': 0,
                           'clustering': 0,
                           'lda': 0}
        
        #Initializing variables to store topics in word embedding only mode
        word_embedding_only_docstring = []
        word_embedding_only_topics = []
        word_embedding_only_doctokens = []
        
        #Initializing the corpus lda tokens
        lda_corpus_tokens = []
        lda_corpus_doctokens = []
                
        for document in documents_list:
            try:
                #Starting to process a new document
                print('\nStarting to process document: {}'.format(document))
                
                if os.path.getsize(self.input_directory + document) < 1000:
                    print('File Size is less than 1000 bytes, so ignoring this file')
                    count = count + 1
                    continue
                
                #Preprocessing the document text
                doctokens = preprocessed_docs.tokenArray(document)
                
                #Performing Word Emebeddings and Clustering
                if self.word_embedding_only or self.word_embedding_LDA:
                    module_start_time = time.time()
                    batch_input, wordtoken = self.transform_tokens_to_embeddings(
                        doctokens)  # transform text of document into word embeddings
                    module_meantime['embeddings'] += (time.time() - module_start_time)
                    module_start_time = time.time()
                    assigned = self.assigned_clusters(batch_input,
                                                      self.NUM_CLUSTERS)  # perform k-means clustering on word embeddings
                    docstring = self.seperate_clusterwords(wordtoken,
                                                            assigned)  # separate list of words that exist in specfic cluster
                    module_meantime['clustering'] += (time.time() - module_start_time)
                    
                    if self.word_embedding_only:
                        
                        #Extracting the topics
                        topics = self.topic_word_embeddings_only(docstring, use_c_tfidf=False)
                        
                        #Saving the topics and the text for later to calculate the Coherence Score
                        word_embedding_only_docstring.append(docstring)
                        word_embedding_only_topics.append(topics)
                        word_embedding_only_doctokens.append(doctokens)
                        
                        #Moving to the next document
                        count = count + 1
                        print("Processed Document : ", document, " , count: ", count)
                        
                #Fitting the LDA model
                if self.LDA_only or self.word_embedding_LDA:
                    LDA_only_doctokens = [' '.join(doctokens[0])]
                    
                    #Appending tokens and document details in a list
                    lda_corpus_tokens.append(LDA_only_doctokens)
                    lda_corpus_doctokens.append(doctokens[1:])
                    
                    count = count + 1
                    print("Processed Document : ", document, " , count: ", count)
            except Exception as e:
                print(e)
                with open(self.output_directory + 'unprocessed.txt', 'a+') as file:
                    file.write(document)
                    file.write('\n')
        
        if self.word_embedding_only:
            print('\nCalculating the Coherence Scores for each document in Word Embedding Only Mode...\n')
            self.word_embeddings_only_coherence_score(word_embedding_only_docstring, word_embedding_only_topics, word_embedding_only_doctokens)
        else:
            module_start_time = time.time()
            print('\nFitting an LDA model on the whole corpus...\n')
            lda_corpus, trained_lda_model, coherence_score = self.fit_lda_model(lda_corpus_tokens)
            module_meantime['lda'] = (time.time() - module_start_time)
            
            #Writing all the topics and its Coherence Score to the file
            self.printCsv('Topics extracted by the LDA:', filename = 'germanResultstest_extracted_topics.csv')
            
            for top in trained_lda_model.print_topics(num_topics=-1):
                top = top[1].split('+')
                top = [t.replace('"', '').strip() for t in top]
                self.printCsv(str(top), filename = 'germanResultstest_extracted_topics.csv')
                
            self.printCsv('Coherence Score: {}'.format(coherence_score), filename = 'germanResultstest_extracted_topics.csv')
            
            print('\nMapping each document to a topic..\n')
            for index, doc in enumerate(lda_corpus):
                doc_topic_mapping = trained_lda_model.get_document_topics(doc)
                
                #Taking the first topic which has the highest probability
                topics = trained_lda_model.print_topic(doc_topic_mapping[0][0])
                topics = topics.split('+')
                topics = [top.replace('"', '').strip() for top in topics]
                
                doc_doctokens = lda_corpus_doctokens[index]
                topic_prob = doc_topic_mapping[0][1]
                
                csvRow = doc_doctokens[0] + ',' + str(topics) + ',' + doc_doctokens[1] + ',' + str(topic_prob)
                self.printCsv(csvRow, filename = 'germanResultstest_topics_mapping.csv')
                
        time_taken = time.time() - start_time
        module_meantime['embeddings'] /= len(documents_list)
        module_meantime['clustering'] /= len(documents_list)
        count = 0
        
        if self.save_model:
            print('\nSaving the model..\n')
            trained_lda_model.save('lda_model')
            print('\nSaving the model DONE\n')
        
        print('Total Time Taken to Process all Documents is: {}'.format(time_taken))
        print('Average time for each module is: ')
        print(module_meantime)
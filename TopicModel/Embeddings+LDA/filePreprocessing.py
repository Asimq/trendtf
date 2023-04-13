"""Importing Libraries"""
from nltk.stem.wordnet import WordNetLemmatizer
from dataPreprocessing import PreprocessingDocuments
from xml.dom.pulldom import parse, START_ELEMENT
import spacy
import time
import json
import os
import yaml

class FileProcessing():
    """
    The FileProcessing class is used to perform all the Preprocessing Steps on each document and saves
    the results in a new file for further processing in LDA step
    """
    
    def __init__(self):
        """
        Setup parameters like original documents directory and output directory path.Further it initializes
        the Spacy module with the pretrained model.
        """
        #Reading the Configuration file and Saving the Input and the Output Directories Path for Preprocessing Documents
        with open('Config.yaml', 'r') as cfg_file:
            cfg = yaml.load(cfg_file, Loader=yaml.FullLoader)
            self.documents_directory = cfg['preprocessing']['input_dir']
            self.processed_documents_directory = cfg['preprocessing']['output_dir']
            self.xml_data_path = cfg['preprocessing']['xml_dump_path']
            self.process_xml_dump = cfg['preprocessing']['process_xml_dump']
        
        ###Lemmatize using WordNet's built-in morphy function. Returns the input word unchanged if it cannot be found in WordNet.
        self.lemmatizer = WordNetLemmatizer()
        
        #Loading the Spacy German corpus for tagging purposes
        self.spacy_de = spacy.load('de_core_news_sm')
        self.spacy_de.max_length = 3000000
        
    def removeUnnecessaryWords(self, filedata):
        """Function to remove the Unnecessary words like Proper Nouns, Adjective etc. from the text

        Parameters
        ----------
        filedata : (String)
            Text from the file which has to be processed

        Returns
        -------
        String:
            return processed text

        """
        
        tags_to_remove = ['ADJ', 'AUX', 'PUNCT', 'ADP', 'DET','VERB','ADV', 'PROPN', 'INTJ', 'PART', 'PRON', 'SPACE']
        
        single_string = self.spacy_de(filedata)
        
        edited_sentence = [word.orth_ for word in single_string if word.pos_ not in tags_to_remove]
        
        return ' '.join(edited_sentence)
    
    def cleanData(self, data):
        """
        This function cleans the data using different techniques and returns the cleaned data for
        further processing

        Parameters
        ----------
        data : String
            The data to be cleaned.

        Returns
        -------
        data : String
            The cleaned and processed data.

        """
        try:
            preprocessed_docs = PreprocessingDocuments('')
            
            # function to transform text of document to lower case
            words = data.lower()
            #Removing splitted words over the newline            
            words = words.replace('-\n', '')
            # function to split the text of document based on newline character '\n'
            #words = input_lower.split()
            # function to remove numbers from the text of document
            words = preprocessed_docs.remove_numbers(words)  
            # function to remove spaces from the text of document
            words = preprocessed_docs.spaces(words)
            # function to remove punctuations from the text of document
            words = preprocessed_docs.remove_punctuation(words)
            # function to remove whitespace from the text of document
            words = preprocessed_docs.remove_whitespace(words)
            # function to remove special characters from the text of document
            words = preprocessed_docs.specialCharector(words)
            # function to remove words that are 3 character long  from the text of document
            words = preprocessed_docs.removeThreechar(words)
            # function removes all the Unnecessary words like Proper Nouns, Adjective etc.
            words = self.removeUnnecessaryWords(words)
            # function to tokenize the text of document
            tokenwords = preprocessed_docs.tokens(words) 
            # function to remove english stopwords from the text of document
            tokenwords = preprocessed_docs.removeStopwordsEnglish(tokenwords)  
            # function to remove german stopwords from the text of document
            tokenwords = preprocessed_docs.removeStopwordsGerman(tokenwords)  
            # function to remove duplicate tokens from the text of the document
            tokenwords = preprocessed_docs.removeDuplicateTokens(tokenwords)  
            # function to remove english stopwords from the text of document
            tokenwords = preprocessed_docs.removeStopwordsEnglish(tokenwords)  
            # function to remove german stopwords from the text of document
            tokenwords = preprocessed_docs.removeStopwordsGerman(tokenwords)  
            # Joining all the words to form the String
            data = ' '.join(tokenwords)
            
            #Returning the cleaned and processed data string
            return data
        except Exception as e:
            print(e.__str__())
    
    def xmlStreamParsing(self, completed_filenames):
        """
        This function is used to parse the data from the xml file using streams and returns the cleaned data

        Parameters
        ----------
        completed_filenames : List
            The list of file names which are already processed and don't have to be processed again.

        Returns
        -------
        average_time : Float
            Average time for processing a single document.
        total_small_files : Int
            Total files which were less than 1000 bytes.
        total_files : Int
            Total documents which were processed.

        """
        #Variable to store average time for Preprocessing each document
        average_time = 0
        total_small_files = 0
        idx = 0
        
        #Opening and parsing the XML file in a Stream
        event_stream = parse(self.xml_data_path)
        
        #Iterating over the XML tags
        for event, node in event_stream:
            try:
                #Initializing the time and data variable
                start_time = time.time()
                data = ''
                
                # The data to process is inside the page tag in the XML file
                if event == START_ELEMENT and node.tagName == 'page':
                    
                    #This function expands all the child nodes of the current focused tag
                    event_stream.expandNode(node)
                    
                    #Extracting the PPN value
                    ppn = node.getElementsByTagName('revision')[0].getElementsByTagName('id')[0]
                    ppn = ppn.firstChild.data
                    
                    #Creating the new file name which will contain the processed data
                    filename = '{}.txt'.format(ppn)
                    
                    #Checking if the current file is already processed
                    if filename in completed_filenames:
                        print('File: {} is already preprocessed, so skipping this file'.format(filename))
                        idx += 1
                        continue
                    
                    #Starting to process a new document
                    print('\nStarting to process document: {}'.format(filename))
                    
                    #If the total length of data is less than 1000 bytes than we will skip that file because
                    #it won't output any interesting results.
                    if int(node.getElementsByTagName('text')[0].getAttribute('bytes')) < 1000:
                        print('File: {} have content less than 1000 bytes, so ignoring this file'.format(filename))
                        total_small_files += 1
                        continue
                    
                    #Extracting the actual data/text which has to be processed
                    for temp in node.getElementsByTagName('text')[0].childNodes:
                        data += temp.data + ' '
                    
                    #Cleaning the data using different methods
                    data = self.cleanData(data)
                    
                    #Saving the pre-processed data into a new file
                    with open(self.processed_documents_directory + filename, 'w', encoding="utf8") as f:
                        f.write(data)
                    
                    #Summing the average time
                    average_time += time.time() - start_time
                
                    print("Processed Document : ", filename, " , count: ", idx +  1)
                    idx += 1
            except Exception as e:
                print(e.__str__())
                with open('xml_parsing_preprocessing_unprocessed.txt', 'a+') as file:
                    file.write(filename)
                    file.write('\n')
        
        #Returning the stats
        return average_time, total_small_files, idx
    
    def documentsParsing(self, completed_filenames):
        """
        This function is used to parse the data from the files and returns the cleaned data

        Parameters
        ----------
        completed_filenames : List
            The list of file names which are already processed and don't have to be processed again.

        Returns
        -------
        average_time : Float
            Average time for processing a single document.
        total_small_files : Int
            Total files which were less than 1000 bytes.
        total_files : Int
            Total documents which were processed.

        """
        #Variable to store average time for Preprocessing each document
        average_time = 0
        total_small_files = 0
        
        #Getting the Documents List for Preprocessing
        preprocessed_docs = PreprocessingDocuments(basepath=self.documents_directory)
        documents_list = preprocessed_docs.listAllDocs()  # return list of all documents
        print("Total Documents", len(documents_list))
        
        #Iterating over all the documents
        for index, document in enumerate(documents_list):
            try:
                #Checking if the current file is already processed
                if document in completed_filenames:
                    print('File: {} is already preprocessed, so skipping this file'.format(document))
                    continue
                
                #Starting to process a new document
                print('\nStarting to process document: {}'.format(document))
                
                #Initializing the time and data variable
                start_time = time.time()
                data = total_bytes = ''
                
                #Splitting the filename into name and its extension because of separate processing
                name, extension = os.path.splitext(self.documents_directory + document)
                
                #Reading the content of the file to process
                with open(self.documents_directory + document, "rt", encoding="utf8") as f:
                    if extension == '.txt':
                        data = str(f.read())
                    elif extension == '.json':
                        data = json.load(f)
                        total_bytes = int(data['page']['revision']['text']['bytes'])
                        data = data['page']['revision']['text']['content']
                    else:
                        print('Invalid file found, Skipping this file')
                        continue
                
                #If the total length of data is less than 1000 bytes than we will skip that file because
                #it won't output any interesting results.
                if (extension == '.json') and (total_bytes < 1000):
                    print('File: {} have content less than 1000 bytes, so ignoring this file'.format(document))
                    total_small_files += 1
                    continue
                    
                #Cleaning the data using different methods
                data = self.cleanData(data)
                
                #Saving the pre-processed data into a new file
                with open(self.processed_documents_directory + document, 'w', encoding="utf8") as f:
                    f.write(data)
                
                #Summing the average time
                average_time += time.time() - start_time
            
                print("Processed Document : ", document, " , count: ", index +  1)
            except Exception as e:
                print(e)
                with open('document_preprocessing_unprocessed.txt', 'a+') as file:
                    file.write(document)
                    file.write('\n')
        
        #Returning the stats
        return average_time, total_small_files, len(documents_list)
        
    
    def mainProcess(self):
        """
        The function first extracts all the documents from the directory, apply all the preprocessing steps
        and finally save the preprocessed text into a new file with the same file name and in a new 
        directory.
        """
        #Variable to store average time for Preprocessing each document
        average_time = 0
        total_small_files = 0
        total_processed_doc = 0
        
        #Checking for the completed files in the output directory
        print('\nChecking for already completed Files...')
        completed_filenames = os.listdir(self.processed_documents_directory)
        print('Total Preprocessed Files: {}\n'.format(len(completed_filenames)))
        
        # Processing and Cleaning the documents
        average_time, total_small_files, total_processed_doc = self.xmlStreamParsing(completed_filenames) if self.process_xml_dump else self.documentsParsing(completed_filenames)
        
        #Printing the final some statistics
        print('\nAverage Time taken for preprocessing each documents is: {}'.format(average_time / total_processed_doc))
        print('\nTotal Files which were less than 1000 bytes are: {}'.format(total_small_files))
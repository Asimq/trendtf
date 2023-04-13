"""Importing Libraries"""

from nltk import jaccard_distance
from spellchecker import SpellChecker
from compound_split import char_split
import re
import csv
import time
import yaml
import os

class ValidateResults():
    """
    The ValidateResults class validates the results of LDA step by checking if the words are valid/dictionary
    word and does these words make sense.
    """
    
    def __init__(self):
        """
        Setup parameters like filename, input_file path and output file path.Further it also initializes
        the Pyspellchecker for checking correctness of each words
        """
        
        #Loading PySpellChecker with German corpus to detect Incorrect Words
        self.spell = SpellChecker(language=['en', 'de'])
        self.spell.word_frequency.load_text_file('wordlist-german.txt')
        
        #Reading the Configuration file and Saving the Input and the Output File Path
        with open('Config.yaml', 'r') as cfg_file:
            cfg = yaml.load(cfg_file, Loader=yaml.FullLoader)
            self.filename = cfg['validation']['lda_filename']
            self.input_filepath = cfg['validation']['input_dir']
            self.output_filepath = cfg['validation']['output_dir']
    
    def clean_results(self, topics, document_index):
        """This function cleans the resultant LDA topic in two ways:
            1. Removing any duplicate values
            2. Removing the words that are not part of German Dictionary

        Parameters:
        topics (List): List of topics from LDA

        Returns:
        topics: return list of cleaned topics 
        """
        
        #Removing the duplicate topics
        topics = list(set(topics))
        final_topics = []
        dict_desc = '\nDocument Id: {}\n\n'.format(document_index+1)
        
        #Iterating over all the topics and validating
        for topic in topics:
            word_to_check = topic.strip()
            compound_word_prob = char_split.split_compound(word_to_check)
            
            #Checking if the word is a compound word and if it is than extracting the split with the
            #highest probabilty
            if (len(compound_word_prob) > 1) and (compound_word_prob[0][0] > 0):
                word_to_check = compound_word_prob[0][1]
                dict_desc += 'Compound word found:\n{}'.format(compound_word_prob)
            
            dict_word = self.spell.correction(word_to_check)
            dict_desc += 'Original Word: {}\tDictionary Word: {}\tJaccard similarity: {}\n'.format(
                topic, dict_word, jaccard_distance(set(dict_word), set(topic)))
            
            #Checking for the garbage words which are not part of the dictionary
            if (dict_word == word_to_check) and (not self.spell.known(self.spell.edit_distance_1(word_to_check))):
                dict_desc += 'Incorrect word found: {}'.format(topic)
                continue
            
            #Checking how far is the dictionary word from the original word using Jaccard Distance
            if (dict_word == word_to_check) or (jaccard_distance(set(dict_word), set(word_to_check)) < 0.2):
                dict_desc += 'Appending {} to the final list\n'.format(topic.strip() if len(compound_word_prob) > 1 else dict_word)
                final_topics.append(topic.strip() if len(compound_word_prob) > 1 else dict_word)
        
        #Writing the validation results for each topic in a separate file
        with open(self.output_filepath + 'file_stat.txt', 'a+', encoding='utf-8') as f:
            f.writelines(dict_desc)
        
        return list(set(final_topics))
    
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
            
            #Empty list to store the processed files
            data = ''
            with open(dir_path + filename, 'rt', encoding='utf-8') as f:
                data = f.read()
            data = data.split('\n')
            
            #Opening the file and reading the content
            for result in data:
                r = re.match('(.*),(\[.*\]),(.*),(.*)',result.strip('"'))
                if r != None: completed_filenames.append(r.group(1))
            
            #Returning the final list of file names
            return completed_filenames
        except Exception as e:
            print(e.__str__())
            with open('exception.txt', 'a+') as file:
                file.write(e.__str__())
    
    def mainProcess(self):
        """
        This function first reads the LDA's results from a file and then validate each result. 
        """
        try:
            #Variable to store average time for validating each results
            average_time = 0
            
            #Opening and Reading the content of LDA's results file
            data = ''
            with open(self.input_filepath + self.filename, 'rt', encoding='utf-8') as f:
                data = f.read()
            data = data.split('\n')
            
            print('\nChecking for already completed Files...')
            completed_filenames = self.extractCompletedFiles(self.output_filepath, self.filename)
            print('Total already Processed Files: {}\n'.format(len(completed_filenames)))
            
            #Iterating over all results
            for index, result in enumerate(data):
                start_time = time.time()
                
                #Grouping all the parts in the CSV row (Filename,Topics,Language,Coherence Score)
                r = re.match('(.*),(\[.*\]),(.*),(.*)',result.strip('"'))
                
                #Checking if the file is already processed
                if r.group(1) in completed_filenames:
                    print('File: {} is already processed, so skipping this file'.format(r.group(1)))
                    continue
                
                #Starting to process a new document
                print('\nStarting to process document: {}'.format(r.group(1)))
                
                #Extracting topic words and checking if they are valid using Pyspellchecker
                topics = r.group(2).strip('[ ]').replace('\'', '').split(',')
                topics = self.clean_results(topics, index)
                
                #If there no topics, then coherence score should be 0
                coherence_score = r.group(4)
                if len(topics) == 0:
                    coherence_score = 0.0
                
                csvRow = str(r.group(1)) + ',' + str(topics) + ',' + str(r.group(3)) + ',' + str(coherence_score)
                
                #Saving the results in a new file
                with open(self.output_filepath + self.filename, 'a+', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([csvRow])
                
                #Summing the average time
                average_time += time.time() - start_time
                
                print("Processed Document : ", r.group(1), " , count: ", index +  1)
                
            print('\nAverage Time taken for Validating each Results is: {}'.format(average_time / len(data)))
        except Exception as e:
            print(e)
            with open(self.output_filepath + 'exception.txt', 'a+') as file:
                file.write(e.__str__())
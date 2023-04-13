#!/usr/bin/env python
# coding: utf-8

"""Importing Packages"""

import sys
from topicModellingLDA import TopicModelling
from filePreprocessing import FileProcessing
from validateResults import ValidateResults
import os

if __name__ == '__main__':
    
    #Checking if the user has provided the any argument
    if len(sys.argv) < 2:
        print('This program is expecting one argument, please provide the proper argument value for running this program')
        print('Possible argument values are: ')
        print('1. preprocess\n2. lda\n3. validate')
        sys.exit()
    
    argument = sys.argv[1].strip().lower()
    
    #Checking if the config exist or not
    config_filename = 'Config.yaml'
    if not os.path.exists(config_filename):
        print('This program requires a config file: {}, which is not found.\nPlease attach the config file with this code file!'.format(config_filename))
        sys.exit()
    
    #Running the Module based on the provided Arugument
    if argument == 'preprocess':
        fileProcess = FileProcessing()
        fileProcess.mainProcess()
    elif argument == 'lda':
        topicModellingEvaluation = TopicModelling()
        topicModellingEvaluation.set_model_type_multilingual_bert()
        topicModellingEvaluation.mainProcess()
    elif argument == 'validate':
        validateResults = ValidateResults()
        validateResults.mainProcess()
    else:
        print('Invalid Argument provided')
        sys.exit()


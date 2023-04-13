import pandas as pd
import shutil
import os
from os.path import isfile, join
import re
import csv
from xml.dom.pulldom import parse, START_ELEMENT

class Utility:
    """
    A utility class containing all the helping function to be used in the process
    """
    
    def extract_filenames_from_directory(self,
                          directory_path,
                          filetypes = [],
                          filter_filetype = False):
        """
        This function extracts all the file names (optionally based on the filter) from the specified folder.

        Parameters
        ----------
        directory_path : String
            The folder path from where to read the file names.
        filetypes : List, optional
            The list of file extensions which has to be filtered. The default is [].
        filter_filetype : Boolean, optional
            Flag to indicate if we have to filter files or not. The default is False.

        Returns
        -------
        dir_filenames : List
            List of File names extracted from the specified folder.

        """
        try:
            #Checking the condition that filetypes list should not be empty if filter_filetype is True
            assert not filter_filetype or filetypes, 'Function: {}, Argument Validation Failed'.format(self.extract_filenames_from_directory.__name__)
            
            #Empty list to hold extracted file names
            dir_filenames = []
            
            #Iterating over the files in the specified directory
            for filename in os.listdir(directory_path):
                
                #If it is not a file then skip that item
                if not isfile(join(directory_path, filename)):
                    continue
                
                if filter_filetype and filename.endswith(tuple(filetypes)):
                    dir_filenames.append(filename)
                elif not filter_filetype:
                    dir_filenames.append(filename)
            
            #Returning the final file name list
            return dir_filenames
        except Exception as e:
            print(e)
            with open('exception.txt', 'a+') as file:
                file.write(e.__str__())
        
    
    def transfer_files(self,
                       base_src_path, base_dest_path, file_details, filenames = [],
                       use_explicit_filenames = False):
        """
        This function will first extract the file names from the input file and then transfer these files from the
        source directory to the destination directory

        Parameters
        ----------
        base_src_path : String
            The directory path containing all the files. 
        base_dest_path : String
            The directory path where we have to transfer the files from the source directory. 
        file_details : String
            The file contaning the filenames which we have to transfer from source to destination folder.
        filenames : List, optional
            List of file names to copy from source directory to destination directory
        use_explicit_filenames : Boolean, optional
            If True, then uses the filenames list otherwise extracts the file names from a separate file provided
            in the file_details variable

        """
        try:
            #Checking the condition that filenames list should not be empty if use_explicit_filenames is True
            assert not use_explicit_filenames or filenames, 'Function: {}, Argument Validation Failed'.format(self.transfer_files.__name__)
            
            #List to save file names that were not found
            files_not_found = []
            
            #Extracting the file names from the input file
            if not use_explicit_filenames:
                file_extension = '.txt'
                files_list = pd.read_csv(file_details)
                filenames = files_list['PPN'].to_list()
                filenames = [fname + file_extension for fname in filenames]
            
            print('Total Files to Copy: {}'.format(len(filenames)))
            
            #Iterating over all the files which has to be copied
            for f in filenames:
                full_filename = os.path.join(base_src_path, f)
                if os.path.isfile(full_filename):
                    dst = os.path.join(base_dest_path, f)
                    shutil.copyfile(full_filename, dst)
                    print('File: {} Copied Successfully'.format(full_filename))
                else:
                    files_not_found.append(f)
            
            print('Total files copied: {}'.format(len(filenames) - len(files_not_found)))
            print('Total number of files which were not found: {}\n'.format(len(files_not_found)))
            print('\n\nFollowing Files were not found:\n')
            print(files_not_found)
        except Exception as e:
            print(e)
            with open(base_src_path + 'exception.txt', 'a+') as file:
                file.write(e.__str__())
        
    def separate_file_types(self, src_path, dest_path, filename):
        """
        This function separates different file types into different individual files

        Parameters
        ----------
        src_path : String
            Source directory path.
        dest_path : String
            Destination directory path.
        filename : String
            File to process.

        """
        try:
            #Opening and Reading the content of LDA's results file
            data = ''
            with open(src_path + filename, 'rt', encoding='utf-8') as f:
                data = f.read()
            data = data.split('\n')
            
            #Iterating over all results
            for index, result in enumerate(data):
                
                #Extracting the filenames and based on that distributing results into different files
                r = re.match('(.*),(\[.*\]),(.*),(.*)',result.strip('"'))
                file_type = r.group(1).split('.')[1]
                new_filename = '{}_{}.{}'.format(filename.split('.')[0], file_type, filename.split('.')[1])
                
                #Saving the results in a new file
                with open(dest_path + new_filename, 'a+', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([result.strip('\"')])
                
                print("Processed Document : ", r.group(1), " , count: ", index +  1)
        except Exception as e:
            print(e)
            with open(dest_path + 'exception.txt', 'a+') as file:
                file.write(e.__str__())
                
    def change_filenames(self, dir_path, filenames_path):
        """
        This function is used to rename the file name which was first named using the title and change it so
        that it contain id instead.

        Parameters
        ----------
        dir_path : String
            The directory path containing all the files.
        filenames_path : String
            The file containing all the file details including title and id.

        """
        try:
            event_stream = parse(filenames_path)
            total_files_renamed = 0
            
            #Iterate over all the page tags containing the text for each document
            for event, node in event_stream:
                try:
                    if event == START_ELEMENT and node.tagName == 'page':
                        
                        #expand node will expand all the child nodes of the specifed tag
                        event_stream.expandNode(node)
                        
                        #Extracting the original title and the modified title
                        original_title = node.getElementsByTagName('title')[0].firstChild.data
                        modified_title = '{}.txt'.format(re.sub(r"[^a-zA-Z0-9äöüÄÖÜß]+", ' ', original_title))
                        
                        #Extracting the PPN value
                        ppn = node.getElementsByTagName('revision')[0].getElementsByTagName('id')[0]
                        ppn = ppn.firstChild.data
                        
                        #Formulating the new filename using the id instead of title
                        new_title = '{}.txt'.format(ppn)
                        
                        #Checking if the file exist with the previous filename and if exist 
                        #renaming it with new filename
                        if os.path.exists(dir_path + modified_title):
                            os.rename(dir_path + modified_title, dir_path + new_title)
                            print('The file: {} has been renamed to: {} successfully'.format(modified_title, new_title))
                            total_files_renamed += 1
                    
                    #If total files that is renamed becomes greater than total files in directory, than we
                    #have checked every file and we can stop
                    if total_files_renamed >= len(os.listdir(dir_path)):
                        print('Process of Changing Filenames has been completed')
                        break
                except Exception as e:
                    print(e)
            print('Process of Changing Filenames has been completed')
            print('Total Files renamed: {}'.format(total_files_renamed))
        except Exception as e:
            print(e)
            with open('exception.txt', 'a+') as file:
                file.write(e.__str__())
                
    def merge_files(self, source_dir, dest_dir, files_list = []):
        """
        This function merges all the files present in the source directory into a single file
        and save it into the destination directory.

        Parameters
        ----------
        source_dir : String
            The directory path where all the files are present for merging.
        dest_dir : String
            The destination directory path where to put the final merged file.
        files_list : List
            If the list is empty, then merge all the files present in the source_dir otherwise
            merge only the files present in the files_list.
        """
        try:
            
            #File name of the merged file
            merged_file_name = 'merged_file.txt'
            
            #Data to be written
            merged_data = ''
            
            #Total files already read
            total_files_read = 0
            
            #Iterating over all the files present in the source directory
            for filename in os.listdir(source_dir):
                
                #Checking if only specific files have to be merged
                if files_list and filename not in files_list:
                    continue
                
                #If it is not a file then skip that item
                if not isfile(join(source_dir, filename)):
                    continue
                
                #Opening the current file and reading its contect
                with open(source_dir + filename, 'r', encoding='utf8') as readFile:
                    merged_data += '{}\n'.format(str(readFile.read()))
                    total_files_read += 1
                
                #After every 10 files read, writing the merged content into the merged file
                if total_files_read % 10 == 0:
                    with open(dest_dir + merged_file_name, 'a+', encoding='utf8') as writeFile:
                        writeFile.write(merged_data)
                        merged_data = ''
                    print('Appended the content, total files merged: {}'.format(total_files_read))
            
            #If some content is left, writing it into the merged file
            if merged_data != '':
                with open(dest_dir + merged_file_name, 'a+', encoding='utf8') as writeFile:
                    writeFile.write(merged_data)
            
        except Exception as e:
            print(e)
            with open('exception.txt', 'a+') as file:
                file.write(e.__str__())
                
    def change_filename_csv(self, src_path, dest_path, filenames_path):
        try:
            print('Starting the process of changing filenames in the LDA result file')
            
            #Dictionary to store lda file data
            csv_data = {}
            
            #Filename of the LDA results
            lda_filename = 'germanResultstest_multilingualBert.csv'
            modified_lda_filename = 'germanResultstest_multilingualBert_modified.csv'
            
            #Opening and Reading the content of LDA's results file
            data = ''
            with open(src_path + lda_filename, 'rt', encoding='utf-8') as f:
                data = f.read()
            data = data.split('\n')
            
            #Iterating over all results
            for index, result in enumerate(data):
                
                if result is None or result == '':
                    continue
                
                #Extracting the filenames and based on that distributing results into different files
                r = re.match('(.*),(\[.*\]),(.*),(.*)',result.strip('"'))
                old_filename = r.group(1)
                
                #Formating the string contaning all the data excepts the filename
                topics = list(set(r.group(2).strip('[ ]').replace('\'', '').split(',')))
                topics = [top.strip() for top in topics]
                csvRow = str(str(topics) + ',' + str(r.group(3)) + ',' + str(r.group(4)))
                
                #Saving the data in the dictionary
                csv_data[old_filename] = csvRow
            
            print('LDA file reading completed')
            print('Total files extracted: {}'.format(len(csv_data.keys())))
            
            print('Starting to read the XML file')
            #Parsing the XML dump file
            event_stream = parse(filenames_path)
            
            total_keys_modified = 0
            total_xml_read = 0
            
            #Iterate over all the page tags containing the text for each document
            for event, node in event_stream:
                try:
                    if event == START_ELEMENT and node.tagName == 'page':
                        
                        #expand node will expand all the child nodes of the specifed tag
                        event_stream.expandNode(node)
                        
                        #Extracting the original title and the modified title
                        original_title = node.getElementsByTagName('title')[0].firstChild.data
                        modified_title = '{}.txt'.format(re.sub(r"[^a-zA-Z0-9äöüÄÖÜß]+", ' ', original_title))
                        
                        #Extracting the PPN value
                        ppn = node.getElementsByTagName('revision')[0].getElementsByTagName('id')[0]
                        ppn = ppn.firstChild.data
                        
                        #Formulating the new filename using the id instead of title
                        new_title = '{}.txt'.format(ppn)
                        
                        #Checking if the file exist with the previous filename and if exist 
                        #renaming it with new filename
                        csv_data[new_title] = csv_data.pop(modified_title)
                        
                        total_keys_modified += 1
                        total_xml_read +=1
                        
                        if (total_keys_modified % 10000) == 0:
                            print('Total Filename Modified: {}'.format(total_keys_modified))
                            print('Total Files from XML read: {}'.format(total_xml_read))
                except Exception as e:
                    total_xml_read += 1
                    continue
                    # print('Exception: {}'.format(e))
            
            print('XML file reading complete')
            print('Total files in the dictionary: {}'.format(len(csv_data.keys())))
            print('Writing the final results to a new file')
            
            #Writing the results in the new File
            for key in csv_data.keys():
                
                csvRow = '{},{}'.format(key, csv_data.get(key))
                
                #Saving the results in a new file
                with open(dest_path + modified_lda_filename, 'a+', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([csvRow])
        except Exception as e:
            print(e)
            with open('exception.txt', 'a+') as file:
                file.write(e.__str__())

    def calc_average_coherence_score(self, filepaths):
        """
        The function calculates the average coherence score for each file provided as an input.

        Parameters
        ----------
        filepaths : List
            List of File paths containing the lDA results.

        """
        
        #Iterating over all the file paths
        for file in filepaths:
            
            #Checking if the path is Valid or not
            if not os.path.isfile(file):
                print('{} is not a correct File Path'.format(file))
                continue
            
            #Variable to store average coherence score
            average_coherence_score = 0
            
            #Extracting the filename from the Path
            filename = file.split('/')[-1]
            
            #Opening and Reading the content of file
            data = ''
            with open(file, 'rt', encoding='utf-8') as f:
                data = f.read()
            data = data.split('\n')
            
            #Iterating over all results
            for index, result in enumerate(data):
                
                #Grouping all the parts in the CSV row (Filename,Topics,Language,Coherence Score)
                r = re.match('(.*),(\[.*\]),(.*),(.*)',result.strip('"'))
                
                #Extracting the coherence score
                average_coherence_score += float(r.group(4)) if r != None else 0.0
                
            #Calculating the average coherence score
            average_coherence_score /= len(data)
            
            print('Average Coherence Score for File: {} is {}'.format(filename,average_coherence_score))
                
                

if __name__ == '__main__':
    
    utility = Utility()
    
    filepaths = ['./multilingualBert_word_embedding_only.csv',
                 './word_embedding_only2.csv',
                 './multilingualBert_LDA_only.csv', 
                 './germanResultstest_multilingualBert_word_embedding_LDA.csv']
    utility.calc_average_coherence_score(filepaths)
        
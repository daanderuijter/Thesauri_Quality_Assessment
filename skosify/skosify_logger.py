# -*- coding: utf-8 -*-
"""
@author: Daan

Performs a Skosify transformation and keeps track of the different log messages
Outputs a text file containing all log messages, and a summary text file in which the different types of log messages are summed
"""

import skosify  # contains skosify, config, and infer
import os
import logging
from imp import reload
reload(logging)

def main():
    #Initializes the input and output files and directories
    create_output_dir()
    targeted_input_files = ["rma-skos-lib"]
    input_file = targeted_input_files[0]
    source_file = os.path.join(os.path.abspath('..\\xslt_mapping\\output'), input_file) + '.rdf'
    LOG_FILENAME = os.path.join('output', 'Skosify_log_') + input_file + '.txt'
    LOG_SUMMARY_NAME = os.path.join('output', 'Skosify_log_summary_') + input_file + '.txt'
    
    #Set the logging configuration to write log messages to a text file, then perform the Skosify transformation
    logging.basicConfig(filename = LOG_FILENAME, filemode='w', level=logging.DEBUG)
    voc = skosify.skosify(source_file, label = input_file + '_skosified_ontology')
    voc.serialize(destination=os.path.join('output', input_file) + '_skosified.rdf', format='xml')
    logging.shutdown()
    
    #Count the different log messages and export them to a summary file
    log_file = open(LOG_FILENAME, 'r')
    log_file_lines = log_file.readlines()
    count_log_messages(LOG_SUMMARY_NAME, log_file_lines)
    log_file.close()

def create_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output') 

def count_log_messages(LOG_SUMMARY_NAME, log_file_lines):
    f = open(LOG_SUMMARY_NAME, 'w')
    
    #Initialize write string and different counter variables
    write_string = ""
    white_space_stripped_counter = 0
    top_concept_counter = 0
    hierarchy_cycle_counter = 0
    hierarchical_inconsistency_counter = 0
    redundant_hierarchical_relationship_counter = 0
    
    #Go through each log line and add value to the correct counter variable
    #If the find() function returns -1, the string is not found
    for line in log_file_lines:
        if line.startswith('DEBUG:root:Phase'):
            write_string += line
        if line.find('WARNING:root:Stripping whitespace from label') != -1:
            white_space_stripped_counter += 1
        if line.find('INFO:root:Marking loose concept') != -1:
            top_concept_counter += 1
        if line.find('INFO:root:Hierarchy cycle detected') != -1:
            hierarchy_cycle_counter += 1
        if line.find('connected by both') != -1:
            hierarchical_inconsistency_counter += 1
        if line.find('WARNING:root:Redundant hierarchical relationship') != -1:
            redundant_hierarchical_relationship_counter += 1
    
    #Add the counter variable values to the write string, and write it to the summary file
    write_string += '\nwhite space stripped: ' + str(white_space_stripped_counter)    
    write_string += '\ntop concepts marked: ' + str(top_concept_counter)
    write_string += '\nhierarchy cycles detected: ' + str(hierarchy_cycle_counter)
    write_string += '\nhierarchical inconsistencies removed: ' + str(hierarchical_inconsistency_counter)
    write_string += '\nredundant hierarchical relationships detected: ' + str(redundant_hierarchical_relationship_counter)
    
    f.write(write_string)
    f.close()
    
    print('Analysis completed and placed in the output folder')

if __name__ == "__main__":
    main()

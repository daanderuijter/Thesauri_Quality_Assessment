# -*- coding: utf-8 -*-
"""
@author: Daan

Analyzes the structure of a MARC thesaurus. Finds invalid 550 tags, the range of dates in which the concepts are created, the duplicate labels and orphan concepts.
Results are exported to a text file, the invalid 550 tags are exported to a csv based on the invalid code.
"""

import xmltodict
import os.path
import pandas as pd

def main():
    #Initializes the input and output files and directories
    create_output_dir()
    targeted_input_files = ["authexport_TOPIC_20181213"]
    input_file = targeted_input_files[0]
    source_file = os.path.join(os.path.abspath('..\\xslt_mapping\\data'), input_file) + '.xml'
    
    with open(source_file, encoding='utf8') as fd:
        doc = xmltodict.parse(fd.read())
    
    write_analysis(doc,input_file)

def create_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output') 

def get_invalid_code_w(df_550_tags):
    #A valid w code is either 'g' or 'h'
    #The ~ is an inversion
    invalid_code_w_df = df_550_tags.code_w.dropna()
    invalid_code_w_df = invalid_code_w_df.loc[~invalid_code_w_df.isin(['g','h'])]
    return(invalid_code_w_df)

def get_invalid_code_a(df_550_tags):
    #A valid a code is any input containing a string, so only NULL values are invalid
    invalid_code_a_df = df_550_tags.code_a
    invalid_code_a_df = invalid_code_a_df.loc[df_550_tags.code_a.isnull()]
    invalid_code_a_df = invalid_code_a_df.fillna('NULL')
    return(invalid_code_a_df)

def get_invalid_code_0(df_550_tags):
    #A valid 0 code is (NL-AmRIJ)000000, we find these using a regex
    #(NLAmRIJ)000000 is also allowed because we manually include them in the XSLT conversion to SKOS
    #The ~ is an inversion
    invalid_code_0_df = df_550_tags.code_0.fillna('NULL')
    invalid_code_0_df = invalid_code_0_df.loc[~invalid_code_0_df.str.contains('\([A-Za-z-]+\)\d+')]
    return(invalid_code_0_df)

def get_550_df(doc):
    df_550_tags = pd.DataFrame(columns=["code_w", "code_a", "code_0"])
    for record in doc['collection']['record']:
        for datafield in record['datafield']:
            if datafield['@tag'] == '550':
                subfieldvalues = [None, None, None]
                if type(datafield['subfield']) is list:
                    for subfield in datafield['subfield']:
                        if subfield['@code'] == 'w':
                            subfieldvalues[0] = subfield['#text']
                        if subfield['@code'] == 'a':
                            subfieldvalues[1] = subfield['#text']
                        if subfield['@code'] == '0':
                            subfieldvalues[2] = subfield['#text']
                else:
                    if datafield['subfield']['@code'] == 'w':
                        subfieldvalues[0] = subfield['#text']
                    if subfield['@code'] == 'a':
                        subfieldvalues[1] = subfield['#text']
                    if subfield['@code'] == '0':
                        subfieldvalues[2] = subfield['#text']                    
                df_550_tags.loc[len(df_550_tags)] = subfieldvalues
    return(df_550_tags)
            
def add_labels_to_list(doc):
    preflabel_list = []
    altlabel_list = []
    for record in doc['collection']['record']:
        for datafield in record['datafield']:
            if datafield['@tag'] == '150':
                preflabel_list.append(datafield['subfield']['#text'])
            if datafield['@tag'] == '680' and 'Vertaling:' in datafield['subfield']['#text']:
                translation = ' '.join(datafield['subfield']['#text'].split()[1:])
                preflabel_list.append(translation)
            if datafield['@tag'] == '450':
                altlabel_list.append(datafield['subfield']['#text'])
                                 
    label_list = preflabel_list + altlabel_list
    return(label_list)

def get_duplicates(label_list):
    unique = []
    duplicates = []
    for i in label_list:
        if i not in unique:
            unique.append(i)
        else:
            duplicates.append(i)
    return(sorted(duplicates))

def get_orphan_concept_list(doc):
    orphan_concept_list = []
    for record in doc['collection']['record']:
        record_is_orphan = True
        for datafield in record['datafield']:
            if datafield['@tag'] == '550':
                record_is_orphan = False
        if record_is_orphan == True:
            for controlfield in record['controlfield']:
                if controlfield['@tag'] == '001':
                    record_id = 'http://hdl.handle.net/10934/RM0001.LIBTHESAU.' + controlfield['#text']
                    orphan_concept_list.append(record_id)

    return(orphan_concept_list)

def get_creation_dates(doc):
    creation_dates = []
    for record in doc['collection']['record']:
        for controlfield in record['controlfield']:
            #if the first digit of the 008 tag (representing a decennia) is in [0,1], we assume the year to be somewhere after 2000
            if controlfield['@tag'] == '008' and int(controlfield['#text'][0]) in [0,1]:  
                marc_date = controlfield['#text'][0:6]
                skos_date = '20' + marc_date[0:2] + '-' + marc_date[2:4] + '-' + marc_date[4:6]                        
                creation_dates.append(skos_date)
            #if the first digit of the 008 tag (representing a decennia) is in [2,3,4,5,6,7,8,9], we assume the year to be somewhere before 2000
            if controlfield['@tag'] == '008' and int(controlfield['#text'][0]) in [2,3,4,5,6,7,8,9]:
                marc_date = controlfield['#text'][0:6]
                skos_date = '19' + marc_date[0:2] + '-' + marc_date[2:4] + '-' + marc_date[4:6]                        
                creation_dates.append(skos_date)
    return(sorted(creation_dates))

def write_analysis(doc,input_file):
    #Get a list of all labels, and check if any duplicates exist
    label_list = add_labels_to_list(doc)
    if len(label_list) != len(set(label_list)):
        duplicate_list = get_duplicates(label_list)
    else:
        duplicate_list = []
    
    #Get all orphan concepts and creation dates    
    orphan_concept_list = get_orphan_concept_list(doc)
    creation_dates = get_creation_dates(doc)
    
    #Get all invalid 550 tags
    df_550_tags = get_550_df(doc)
    invalid_code_w_df = get_invalid_code_w(df_550_tags)
    invalid_code_a_df = get_invalid_code_a(df_550_tags)
    invalid_code_0_df = get_invalid_code_0(df_550_tags)
    
    #Write the invalid 550 tags to csv files for each code    
    invalid_code_w_df.to_csv ('output/' + 'MARC_invalid_code_w_' + input_file + '.csv', index = None, header=True)
    invalid_code_a_df.to_csv ('output/' + 'MARC_invalid_code_a_' + input_file + '.csv', index = None, header=True)
    invalid_code_0_df.to_csv ('output/' + 'MARC_invalid_code_0_' + input_file + '.csv', index = None, header=True)

    #Initialize output text file
    ANALYSIS_FILENAME = os.path.join('output', 'MARC_analysis_') + input_file + '.txt'
    f = open(ANALYSIS_FILENAME, 'w')
    write_string = ""
    write_string += 'Analysis report for: ' + str(input_file) + '.rdf'
    
    #Write the amount of invalid 550 tags
    write_string += '\n\nAmount of invalid w codes in the 550 tag: ' + str(len(invalid_code_w_df))
    write_string += '\nAmount of invalid a codes in the 550 tag: ' + str(len(invalid_code_a_df))
    write_string += '\nAmount of invalid 0 codes in the 550 tag: ' + str(len(invalid_code_0_df))
    write_string += '\nAmount of invalid 0 tags that are "NULL: ' + str(len(invalid_code_0_df[invalid_code_0_df == 'NULL']))
    
    #Write creation dates
    write_string += '\n\nCreation dates range from ' + creation_dates[0] + ' to ' + creation_dates[-1]
    
    #Write duplicate labels
    if len(duplicate_list) == 0:
        write_string += '\n\nDuplicate labels don\'t exist in this file.'
    else:
        write_string += '\n\nAmount of duplicate labels: ' +str(len(duplicate_list)) + '\nThese labels are:\n'
        for label in duplicate_list:
            write_string += '\n' + label
        
    #Write orphan concepts
    if len(orphan_concept_list) == 0:
        write_string += '\n\nOrphan concepts don\'t exist in this file.'
    else:
        write_string += '\n\nAmount of orphan concepts: ' + str(len(orphan_concept_list)) + '\nThese concepts are:\n'
        for concept in orphan_concept_list:
            write_string += '\n' + concept
    
    f.write(write_string)
    f.close()
    
    print('Analysis completed and placed in the output folder')

if __name__ == "__main__":
    main()
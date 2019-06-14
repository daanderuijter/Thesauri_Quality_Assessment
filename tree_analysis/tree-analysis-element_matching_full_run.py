# coding: utf-8
"""
@author: Daan

Finds alignments between two thesauri by performing exact string matching on all possible combinations of types of labels (prefLabel and altLabel) and language (nl and en)
Does a second round of matching in which alignments are found by looking at the stemmed forms of strings that did not have a previous match
A numeric analysis of the alignments is exported to a csv file
"""
import xmltodict
import os.path
import pandas as pd
from nltk.stem import PorterStemmer

def main():
    #Initializes the input and output files and directories
    create_output_dir()
    targeted_input_files = ["rma-skos-thesaurus-amalgame","rma-skos-materials-amalgame","rma-skos-lib-amalgame","rma-skos-thesaurus-amalgame-scheme-KEYWORD"]
    input_file_1 = targeted_input_files[2]
    source_file_1 = os.path.join(os.path.abspath('..\\xslt_mapping\\output'), input_file_1) + '.rdf'
    
    with open(source_file_1, encoding='utf8') as fd:
        doc_1 = xmltodict.parse(fd.read())
    
    input_file_2 = targeted_input_files[0]
    source_file_2 = os.path.join(os.path.abspath('..\\xslt_mapping\\output'), input_file_2) + '.rdf'
    
    with open(source_file_2, encoding='utf8') as fd:
        doc_2 = xmltodict.parse(fd.read())
    
    """
    Can be used to check the length of the different input files, which is important when deciding a source and a target for the mapping
    """
    #print(len(doc_1['rdf:RDF']['rdf:Description']))
    #print(len(doc_2['rdf:RDF']['rdf:Description']))
    
    #Perform the matching and export results to a csv
    match_df, stemmed_match_df = full_matching_run(doc_1,doc_2)
    match_df.to_csv ('output/' + 'Full_label_matches_stemmed_' + input_file_1 + "_" + input_file_2 + '.csv', index = None, header=True)
    stemmed_match_df.to_csv ('output/' + 'Full_label_matches_stemmed_strings' + input_file_1 + "_" + input_file_2 + '.csv', index = None, header=True)

    print('Analysis completed and placed in the output folder')
    
def create_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output')    

def full_matching_run(doc_1,doc_2):
    #Initialize the dataframes and possible matches
    matching_df = pd.DataFrame(columns=["label_type","language","matches_doc_1","matches_doc_1_stemmed","matches_doc_2","matches_doc_2_stemmed"])
    stemmed_matching_df = pd.DataFrame(columns=["label_type","language","original_string","matching_stemmed_string"])
    possible_matches = [[["skos:prefLabel","skos:altLabel"],["nl","en"]],
                        [["skos:prefLabel","skos:altLabel"],["nl"]],
                        [["skos:prefLabel","skos:altLabel"],["en"]],
                        [["skos:prefLabel"],["nl","en"]],
                        [["skos:prefLabel"],["nl"]],
                        [["skos:prefLabel"],["en"]],
                        [["skos:altLabel"],["nl","en"]],
                        [["skos:altLabel"],["nl"]],
                        [["skos:altLabel"],["en"]]]

    for matching_inputs in possible_matches:
        #First round of exact string matching
        element_list_1 = get_element_list(doc_1,matching_inputs[0],matching_inputs[1])
        element_list_2 = get_element_list(doc_2,matching_inputs[0],matching_inputs[1])
        matching_strings = match_strings(element_list_1,element_list_2)
        matching_concepts_1, matching_concepts_2 = get_matching_concepts(element_list_1,element_list_2,matching_strings)
        
        #Performs stemming on all strings that did not previously match, and does a second round of matching
        unmatching_concepts_1,unmatching_concepts_2 = get_unmatching_concepts(element_list_1,element_list_2,matching_strings)
        matching_stemmed_strings = match_stemmed_strings(unmatching_concepts_1,unmatching_concepts_2)
        matching_stemmed_concepts_1, matching_stemmed_concepts_2 = get_matching_concepts(element_list_1,element_list_2,matching_stemmed_strings)
        
        #Add the results to the dataframes
        matching_df.loc[len(matching_df)] = [matching_inputs[0],matching_inputs[1],len(matching_concepts_1),len(matching_concepts_1) + len(matching_stemmed_concepts_1),len(matching_concepts_2),len(matching_concepts_2) + len(matching_stemmed_concepts_2)]
        porter = PorterStemmer()
        for i in matching_stemmed_strings:
            stemmed_matching_df.loc[len(stemmed_matching_df)] = [matching_inputs[0],matching_inputs[1],i,porter.stem(i)]
          
    return(matching_df, stemmed_matching_df)

#Converts an element list to a dataframe    
def list_to_df(input_list):
    df = pd.DataFrame(columns=["@rdf:about","skos:prefLabel"])
    for i in input_list:
        df.loc[len(df)] = [i[0], i[1]]
    return(df)

def match_stemmed_strings(list_1,list_2):
    porter = PorterStemmer()
    
    stringlist_1 = []
    stringlist_2 = []
    match_list = []
    
    for i in list_1:
        stringlist_1.append(i[1])
    for i in list_2:
        stringlist_2.append(i[1])
        
    for i in stringlist_1:
        stemmed_string = porter.stem(i)
        if stemmed_string in stringlist_2:
            match_list.append(i)
    
    return(match_list)

def get_unmatching_concepts(element_list_1,element_list_2,match_list):
    unmatching_concepts_1 = []
    unmatching_concepts_2 = []
    
    for concept in element_list_1:
        if concept[1] not in match_list:
            unmatching_concepts_1.append(concept)

    for concept in element_list_2:
        if concept[1] not in match_list:
            unmatching_concepts_2.append(concept)
    
    return(unmatching_concepts_1,unmatching_concepts_2)   

def get_matching_concepts(element_list_1,element_list_2,match_list):
    matching_concepts_1 = []
    matching_concepts_2 = []
    
    for concept in element_list_1:
        if concept[1] in match_list:
            matching_concepts_1.append(concept)

    for concept in element_list_2:
        if concept[1] in match_list:
            matching_concepts_2.append(concept)
    
    return(matching_concepts_1,matching_concepts_2)

def match_strings(list_1,list_2):
    stringlist_1 = []
    stringlist_2 = []
    match_list = []
    
    for i in list_1:
        stringlist_1.append(i[1])
    for i in list_2:
        stringlist_2.append(i[1])
        
    for i in stringlist_1:
        if i in stringlist_2:
            match_list.append(i)
    
    return(match_list)

def get_element_list(doc,element,lang):
    element_list = []
    for label_type in element:
        for concept in doc['rdf:RDF']['rdf:Description']:
            if label_type in concept:
                if type(concept[label_type]) is list:
                    for selected_element in concept[label_type]:
                        for language in lang:
                            if selected_element["@xml:lang"] == language:
                                element_list.append([concept["@rdf:about"], selected_element["#text"]])
                else:
                    for language in lang:
                        if concept[label_type]["@xml:lang"] == language:
                            element_list.append([concept["@rdf:about"], concept[label_type]["#text"]])
    return(element_list)

if __name__ == "__main__":
    main()

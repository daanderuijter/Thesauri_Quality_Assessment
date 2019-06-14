# coding: utf-8
"""
@author: Daan

Finds alignments between two thesauri by performing exact string matching on a single type of label (prefLabel or altLabel) and language (nl or en)
Matching strings are exported to a text file, alignments are exported to csv files
"""
import xmltodict
import os.path
import pandas as pd

def main():
    #Initializes the input and output files and directories
    create_output_dir()
    targeted_input_files = ["rma-skos-thesaurus-amalgame","rma-skos-materials-amalgame","rma-skos-lib-amalgame"]
    input_file_1 = targeted_input_files[1]
    source_file_1 = os.path.join(os.path.abspath('..\\xslt_mapping\\output'), input_file_1) + '.rdf'
    
    with open(source_file_1, encoding='utf8') as fd:
        doc_1 = xmltodict.parse(fd.read())
    
    input_file_2 = targeted_input_files[2]
    source_file_2 = os.path.join(os.path.abspath('..\\xslt_mapping\\output'), input_file_2) + '.rdf'
    
    with open(source_file_2, encoding='utf8') as fd:
        doc_2 = xmltodict.parse(fd.read())
    
    #Get lists of all elements that match the input parameters and find exact string matches        
    element_list_1 = get_element_list(doc_1,"skos:prefLabel","nl")
    element_list_2 = get_element_list(doc_2,"skos:prefLabel","nl")
    matching_strings = match_strings(element_list_1,element_list_2)
    matching_concepts_1,matching_concepts_2 = get_matching_concepts(element_list_1,element_list_2,matching_strings)
    
    write_analysis(matching_concepts_1,matching_concepts_2,matching_strings,input_file_1,input_file_2)
    
def create_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output')    

#Converts an element list to a dataframe
def list_to_df(input_list):
    df = pd.DataFrame(columns=["@rdf:about","skos:prefLabel"])
    for i in input_list:
        df.loc[len(df)] = [i[0], i[1]]
    return(df)

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
    for concept in doc['rdf:RDF']['rdf:Description']:
        if element in concept:
            if type(concept[element]) is list:
                for selected_element in concept[element]:
                    if selected_element["@xml:lang"] == lang:
                        element_list.append([concept["@rdf:about"], selected_element["#text"]])
            else:
                if concept[element]["@xml:lang"] == lang:
                    element_list.append([concept["@rdf:about"], concept[element]["#text"]])
    return(element_list)

def write_analysis(matching_concepts_1,matching_concepts_2,matching_strings,input_file_1,input_file_2):
    #Convert lists to dataframes
    df1 = list_to_df(matching_concepts_1)
    df2 = list_to_df(matching_concepts_2)
    
    #And export the dataframes to csv
    df1.to_csv ('output/' + 'Label_matches_' + input_file_1 + '.csv', index = None, header=True)
    df2.to_csv ('output/' + 'Label_matches_' + input_file_2 + '.csv', index = None, header=True)
    
    #Initialize output text file
    ANALYSIS_FILENAME = os.path.join('output', 'Label_matches_') + input_file_1 + '_' + input_file_2 + '.txt'
    f = open(ANALYSIS_FILENAME, 'w', encoding="utf8")
    write_string = ""
    write_string += 'Analysis report for: ' + input_file_1 + '.rdf and ' + input_file_2 + '.rdf'
    
    #Write the matching strings
    write_string += '\n\nMatches found: ' + str(len(matching_strings))
    for match in matching_strings:
        write_string += '\n' + match
    
    write_string += '\n\nConcepts that matched are exported to .csv'
    f.write(write_string)
    f.close()
    
    print('Analysis completed and placed in the output folder')

if __name__ == "__main__":
    main()


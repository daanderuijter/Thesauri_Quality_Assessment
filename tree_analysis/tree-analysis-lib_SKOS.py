# -*- coding: utf-8 -*-
"""
@author: Daan

Analyzes the structure of a SKOS thesaurus. Finds the range of dates in which the concepts are created, the duplicate labels and orphan concepts.
Results are exported to a text file
"""

import xmltodict
import os.path

def main():
    #Initializes the input and output files and directories
    create_output_dir()
    targeted_input_files = ["rma-skos-lib"]
    input_file = targeted_input_files[0]
    source_file = os.path.join(os.path.abspath('..\\xslt_mapping\\output'), input_file) + '.rdf'
 
    with open(source_file, encoding='utf8') as fd:
        doc = xmltodict.parse(fd.read())
    
    write_analysis(doc,input_file)

def create_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output') 

def add_labels_to_list(doc):
    preflabel_list = []
    altlabel_list = []
    for concept in doc['rdf:RDF']['skos:Concept']:
        if type(concept['skos:prefLabel']) is list:
            for i in concept['skos:prefLabel']:
                preflabel_list.append(i['#text'])                     
        else: #type(concept['skos:prefLabel']) == 'collections.OrderedDict'
            preflabel_list.append(concept['skos:prefLabel']['#text'])
        
        if 'skos:altLabel' in concept:
            if type(concept['skos:altLabel']) is list:
                for i in concept['skos:altLabel']:
                    altlabel_list.append(i['#text'])                     
            else: #type(concept['skos:prefLabel']) == 'collections.OrderedDict'
                altlabel_list.append(concept['skos:altLabel']['#text'])
                                 
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
    
#Also check outgoing links when looking for orphan concepts
def get_orphan_concept_list_final(doc,orphan_concept_list):
    orphan_concept_list_final = orphan_concept_list
    hierarchical_relations = ['skos:broader', 'skos:narrower', 'skos:related']
    
    #Loops through each concept that's not in the orphan concept list
    #If a concept has a hierarchical reference to a concept that is in the orphan concept list, we remove it from the final orphan concept list
    for concept in doc['rdf:RDF']['skos:Concept']:
        if concept['@rdf:about'] not in orphan_concept_list:
            for relation in hierarchical_relations:
                if relation in concept:
                    if type(concept[relation]) is list:
                        for concept_relation in concept[relation]:
                            if concept_relation['@rdf:resource'] in orphan_concept_list_final:
                                orphan_concept_list_final.remove(concept_relation['@rdf:resource'])
                    else: 
                        if concept[relation]['@rdf:resource'] in orphan_concept_list_final:
                            orphan_concept_list_final.remove(concept[relation]['@rdf:resource'])                    
    
    return(orphan_concept_list_final)

def get_orphan_concept_list(doc): # only checks outgoing relations
    orphan_concept_list = []
    for concept in doc['rdf:RDF']['skos:Concept']:
        if not('skos:broader' in concept or 'skos:narrower' in concept or 'skos:related' in concept):
            orphan_concept_list.append(concept['@rdf:about'])
    """
    Also checks the orphan list for incomming links
    The difference between the two (27 in my case) shows how many outgoing links are missing
    The amount of orphans with this function called is exactly the same as after skosification
    """
    #orphan_concept_list = get_orphan_concept_list_final(doc,orphan_concept_list)
    
    return(orphan_concept_list)

def get_creation_dates(doc):
    creation_dates = []
    for concept in doc['rdf:RDF']['skos:Concept']:
        creation_dates.append(concept['dct:created'])
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
    
    #Initialize output text file
    ANALYSIS_FILENAME = os.path.join('output', 'SKOS_analysis_') + input_file + '.txt'
    f = open(ANALYSIS_FILENAME, 'w')
    write_string = ""
    write_string += 'Analysis report for: ' + str(input_file) + '.rdf'
    
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
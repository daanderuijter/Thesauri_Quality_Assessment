# coding: utf-8
"""
@author: Daan

Finds all different concept schemes in a thesaurus and adds the rdf:Description tags to the file
This allows the Amalgame program to regocnize the concept schemes
"""
import xmltodict
import os.path
from collections import OrderedDict

def main():
    #Initializes the input and output files and directories
    create_output_dir()
    targeted_input_files = ["rma-skos-thesaurus-amalgame","rma-skos-materials-amalgame"]
    input_file = targeted_input_files[0]
    source_file = os.path.join(os.path.abspath('..\\xslt_mapping\\output'), input_file) + '.rdf'
    
    with open(source_file, encoding='utf8') as fd:
        doc = xmltodict.parse(fd.read())
    
    #Get a list of concept schemes    
    concept_scheme_list = get_concept_schemes(doc)
    
    #Create a new .rdf file with the concept schemes added and write the analysis file
    write_concept_schemes(doc,input_file,concept_scheme_list)
    write_analysis(doc,input_file,concept_scheme_list)

def create_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output')    

def write_concept_schemes(doc,input_file,concept_scheme_list):
    doc = add_concept_schemes(doc,concept_scheme_list)
    output_file = os.path.abspath('output/') + input_file + '_with_schemes.rdf' 
    
    fd = open(output_file, "w", encoding='utf8')
    fd.write(xmltodict.unparse(doc, pretty=True))
    fd.close()
    
    print('\n' + str(len(concept_scheme_list)) + ' concepts succesfully added to:\n' + output_file + '\n')

def add_concept_schemes(doc,concept_scheme_list):
    #Update the doc to also include the concept schemes in the rdf:Description dictionary
    description_list = doc['rdf:RDF']['rdf:Description']
    
    for scheme in concept_scheme_list:
        scheme_dict = OrderedDict([("@rdf:about",scheme),("rdf:type",OrderedDict([("@rdf:resource","http://www.w3.org/2004/02/skos/core#ConceptScheme")]))])
        description_list.append(scheme_dict)
    
    return(doc)

def get_concept_schemes(doc):
    concept_scheme_list = []
    for concept in doc['rdf:RDF']['rdf:Description']:
        if 'skos:inScheme' in concept:
            if type(concept['skos:inScheme']) is list:
                for scheme in concept['skos:inScheme']:
                    if scheme['@rdf:resource'] not in concept_scheme_list:
                        concept_scheme_list.append(scheme['@rdf:resource'])
            else:
                if concept['skos:inScheme']['@rdf:resource'] not in concept_scheme_list:
                    concept_scheme_list.append(concept['skos:inScheme']['@rdf:resource'])
    return(concept_scheme_list)

def write_analysis(doc,input_file,concept_scheme_list):
    #Initialize output text file
    ANALYSIS_FILENAME = os.path.join('output/', 'Scheme_analysis_') + input_file + '.txt'
    f = open(ANALYSIS_FILENAME, 'w', encoding="utf8")
    write_string = ""
    write_string += 'Analysis report for: ' + str(input_file) + '.rdf'
    
    #Write the different concept schemes
    write_string += '\n\nUnique concept schemes: ' + str(len(concept_scheme_list))
    for scheme in concept_scheme_list:
        write_string += '\n' + scheme
    
    #Write the rdf tags of the different concept schemes (this is essentially what has been added to the .rdf)
    write_string += '\n\n.rdf copy paste: \n\n'
    for scheme in concept_scheme_list:
        write_string += '<rdf:Description rdf:about="' + scheme + '">\n\t<rdf:type rdf:resource=\"http://www.w3.org/2004/02/skos/core#ConceptScheme\"/>\n</rdf:Description>\n'  
    
    f.write(write_string)
    f.close()
    
    print('Analysis completed and placed in the output folder')

if __name__ == "__main__":
    main()
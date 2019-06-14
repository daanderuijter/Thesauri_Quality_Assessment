How to use this project:

Make sure that the following files are placed in the folder "xslt_mapping/data" :

"authexport_TOPIC_20181213.xml"
"rma-skos-materials.rdf"
"rma-skos-thesaurus.rdf"

Given the correct source files are in place, execute the commands in "xslt_mapping/run_commands.txt"

After that, the scripts can be run in the following order :

thesaurus/reconstruct.py
skosify/skosify_logger.py
tree_analysis/tree_analysis-lib_MARC.py
tree_analysis/tree-analysis-lib_SKOS.py
tree_analysis/tree-analysis-lib_SKOS_skosified.py
tree_analysis/tree-analysis-add-schemes.py

The files a script uses are found in the list object "targeted_input_files" at the top of the main() functions
all outputs of the scripts are placed in the "output" folder of the folder the script is found in
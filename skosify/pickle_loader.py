# -*- coding: utf-8 -*-
"""
@author: Daan

This file has no real purpose except loading in an output file created by "reconstruct.py"
"""

import pickle
import os

def main():
    create_output_dir()
    targeted_input_files = ["rma-skos-lib_dictionary"]
    input_file = targeted_input_files[0]
    source_file = os.path.join(os.path.abspath('..\\thesaurus\\output'), input_file) + '.pkl'
    
    with open(source_file, 'rb') as f:
        data = pickle.load(f) 

def create_output_dir():
    if not os.path.exists('output'):
        os.mkdir('output')
        
if __name__ == "__main__":
    main()
    
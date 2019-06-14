#!/usr/bin/env python
# coding: utf-8

# In[1]:


import lxml.etree as ET
import os.path

xml_filename = os.path.abspath('..\data\\') + "authexport_TOPIC_20181213.xml"
dom = ET.parse(xml_filename)


# In[2]:


def get_last_modified_date(root):
    # returns a tuple with (yyyy, mm, dd, hh, mm, ss)
    return tuple([root.text[:4]] + [root.text[i:i+2] for i in range(4, 14, 2)])

def get_creation_date(root):
    # returns the date as a string (yyyy-mm-dd)
    # Added a temporary hack to fix creation dates like 2093-03-05
    d = root.text[:6]
    if int(d[:1]) in [0,1]:
        return f"20{d[:2]}-{d[2:4]}-{d[4:]}"
    else:
        return f"19{d[:2]}-{d[2:4]}-{d[4:]}"

def get_550_text(root):
    w_code = None
    id_text = None
    a_text = None
    for child in root:
        text = child.text.strip()
        if text == 'h' or text == 'w' or text == 'g':
            w_code = text
        elif 'AmRIJ' in text:
            start = text.find(")") + 1
            id_text = text[start:].strip()
        else:
            a_text = text

    return w_code, id_text, a_text

def get_a_code_text(root):
    for child in root:
        if child.attrib['code'] == 'a':
            return child.text.strip()
        
def get_i_code_text(root):
    for child in root:
        if child.attrib['code'] == 'i':
            return child.text.strip()


# In[3]:


# todo add namespace
XML_NS = "http://www.w3.org/XML/1998/namespace"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
SKOS_NS = "http://www.w3.org/2004/02/skos/core#"
DCT_NS = "http://purl.org/dc/terms/"
RML_NS = "http://library.rijksmuseum.nl/"

XML = "{http://www.w3.org/XML/1998/namespace}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS = "{http://www.w3.org/2004/02/skos/core#}"
DCT = "{http://purl.org/dc/terms/}"
RML = "{http://library.rijksmuseum.nl/}"

ET.register_namespace('xml', XML_NS)
ET.register_namespace('skos', SKOS_NS)
ET.register_namespace('dct', DCT_NS)
ET.register_namespace('rdf', RDF_NS)
# ET.register_namespace('rml', RML_NS)


# In[4]:


rdf = ET.Element(RDF + "RDF")
tree = ET.ElementTree(rdf)

# set and delete attribs so namespace ends up on top
rdf.set(DCT + "example", "0")
rdf.set(SKOS + "example", "0")

for attrib in rdf.attrib:
    del rdf.attrib[attrib]

i = -1
for record in dom.getroot():
    
    concept = ET.SubElement(rdf, SKOS + "Concept")
    i += 1
    
    for field in record:
        
        if not 'tag' in field.attrib:
            continue
            
        tag = field.attrib['tag']
        
        if tag == '001':
            concept.set(RDF + "about", RML_NS + field.text)
        
        if tag == '005':
            # extract last modified date
            # dcterms:modified 
            label = ET.SubElement(concept, DCT + "modified")
            year, month, day, hour, minute, secconds = get_last_modified_date(field)
            text = f"{year}-{month}-{day}T{hour}:{minute}:{secconds}"
            label.text = text
        
        elif tag == '008':
            # extract creation date
            # dcterms:created
            label = ET.SubElement(concept, DCT + "created")
            label.text = get_creation_date(field)
        
        elif tag == '150':
            # extract topical term
            # skos:prefLabel
            label = ET.SubElement(concept, SKOS + "prefLabel")
            label.set(XML + "lang", "nl")
            label.text = get_a_code_text(field)
            
        elif tag == '450':
            # extract Tracing
            # skos:altLabel
            label = ET.SubElement(concept, SKOS + "altLabel")
            label.set(XML + "lang", "nl")
            label.text = get_a_code_text(field)
            
        elif tag == '550':
            # extract Tracing
            # skos:Broader (g), skos:Narrower (h), skos:Related (w)
            w_code, id_text, a_text = get_550_text(field)
            
            if w_code == 'g':
                label = ET.SubElement(concept, SKOS + "broader")
            elif w_code == 'h':
                label = ET.SubElement(concept, SKOS + "narrower")
            elif w_code == 'w':
                label = ET.SubElement(concept, SKOS + "related")
            else:
                label = ET.SubElement(concept, SKOS + "related")
            
            if id_text:
                label.set(RDF + "resource", RML_NS + id_text)
            else:
                label.set(XML + "lang", "nl")
                label.text = a_text
            
        elif tag == '680':
            # extract note
            # skos:definition (Omschrijving), skos:altLabel (Vertaling) 
            # (Volledige term) can be ignored
            text = get_i_code_text(field)
            
            if 'Omschrijving' in text:
                label = ET.SubElement(concept, SKOS + "definition")
                label.set(XML + "lang", "nl")
                label.text = text[14:]
            elif 'Vertaling' in text:
                label = ET.SubElement(concept, SKOS + "prefLabel")
                label.set(XML + "lang", "en")
                label.text = text[11:]
            elif 'Volledige term' in text:
                pass
    
# ET.dump(rdf)        


# In[5]:


with open(os.path.abspath('..\data\\') + "DdR_lib.rdf", "wb") as f:
    f.write(b'<?xml version="1.0" ?>\n')
    f.write(ET.tostring(tree, pretty_print=True))

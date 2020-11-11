# author: ETH Zurich, gta digital, Zoé Reinke
# license: please refer to the license.txt file in our git repository (https://github.com/gtadigital/ProfileParser)

import os
import lxml.etree as ET
import argparse
import rdflib
#from rdflib import Graph
 


sourceXML = "C:\\Users\\Zoe\\Documents\\Arbeit gta\\Python Code\\sourceFilesParser"
sourceX3ML = "C:\\Users\\Zoe\\Documents\\Arbeit gta\\Python Code\\sourceFilesParser"
generatorPolicy = "C:\\Users\\Zoe\\Documents\\Arbeit gta\\Python Code\\groupTransform.xsl"

f = open("C:\\Users\\Zoe\\Documents\\Arbeit gta\\Python Code\\targetFilesParser\\output.rdf", "w")

# read in X3ML file
tree = ET.parse(sourceX3ML)
root = tree.getroot()

#create rdf graph
g = Graph()


#define namespaces
rdf= Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ulan= Namespace("http://vocab.getty.edu/page/ulan/")
crm= Namespace("http://www.cidoc-crm.org/cidoc-crm/")
rdfs= Namespace("http://www.w3.org/2000/01/rdf-schema#")
crmdig= Namespace("http://www.ics.forth.gr/isl/CRMdig/")
gnd= Namespace("https://d-nb.info/")
frbr= Namespace("http://iflastandards.info/ns/fr/frbr/frbroo/")
crmpc= Namespace("http://www.cidoc-crm.org/crmpc/")
wikidata= Namespace("https://www.wikidata.org/wiki/")
sikart= Namespace("http://www.sikart.ch/")
skos= Namespace("http://www.w3.org/2004/02/skos/core#")
cpr= Namespace("https://www.schema.swissartresearch.net/cpr/")
sari= Namespace("https://resource.swissartresearch.net/")


#create node for the person the xml input file is about



#fill graph
for x in root.iter("link")


#write graph data in output file
f.write(g.serialize(format='pretty-xml'))
f.close()
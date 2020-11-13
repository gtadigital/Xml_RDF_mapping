# author: ETH Zurich, gta digital, Zoé Reinke
# license: please refer to the license.txt file in our git repository (https://github.com/gtadigital/ProfileParser)

import os
import lxml.etree as ET
import argparse
import rdflib
from rdflib import Graph
from rdflib import Namespace
from rdflib import *
 


sourceXML = "C:\\Users\\Zoe\\Documents\\Arbeit gta\\x3ml rdf transformation\\sourceXMLPerson.xml"
sourceX3ML = "C:\\Users\\Zoe\\Documents\\Arbeit gta\\x3ml rdf transformation\\x3mlMapping.xml"
generatorPolicy = "C:\\Users\\Zoe\\Documents\\Arbeit gta\\x3ml rdf transformation\\generator-policy.xml"

f = open("C:\\Users\\Zoe\\Documents\\Arbeit gta\\x3ml rdf transformation\\output.rdf", "wb")

# read in X3ML file
treeM = ET.parse(sourceX3ML)
rootM = treeM.getroot()

#read in source XML file
treeS = ET.parse(sourceXML)
rootS = treeS.getroot()

#read in generator policy
treeG = ET.parse(generatorPolicy)
rootG = treeG.getroot()

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

g.bind("ulan", ulan)
g.bind("crm", crm)
g.bind("rdfs", rdfs)
g.bind("crmdig", crmdig)
g.bind("gnd", gnd)
g.bind("frbr", frbr)
g.bind("crmpc", crmpc)
g.bind("wikidata", wikidata)
g.bind("sikart", sikart)
g.bind("skos", skos)
g.bind("cpr", cpr)
g.bind("sari", sari)



#create node for the person the xml input file is about
#get type (e.g. crm:E21_person)
concept_namespace = rootM.find("./mappings/mapping/domain/target_node/entity/type").text.split(":", maxsplit=1)[0]
concept_type = rootM.find("./mappings/mapping/domain/target_node/entity/type").text.split(":", maxsplit=1)[1]

#get identifier (i.e. uuid)
uuid_search = ".//" + rootM.find("./mappings/mapping/domain/target_node/entity/instance_generator/arg").text[3:-7]
uuid = rootS.find(uuid_search).text

#create node and insert it into graph
urn = Namespace("urn:uuid:")
person = URIRef(urn[uuid])

g.add((person, RDF.type, getattr(crm, concept_type)))



#fill graph
#for x in rootM.iter("link")


#write graph data in output file
f.write(g.serialize(format='pretty-xml'))
f.close()

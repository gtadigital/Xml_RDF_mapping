# author: ETH Zurich, gta digital, Zoé Reinke
# license: please refer to the license.txt file in our git repository (https://github.com/gtadigital/ProfileParser)

import os
import lxml.etree as ET
import argparse
import rdflib
import re
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

#create namespace dictionary
namespace_dict={}
namespace_dict["rdf"]= "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
namespace_dict["ulan"]= "http://vocab.getty.edu/page/ulan/"
namespace_dict["crm"]= "http://www.cidoc-crm.org/cidoc-crm/"
namespace_dict["rdfs"]= "http://www.w3.org/2000/01/rdf-schema#"
namespace_dict["crmdig"]= "http://www.ics.forth.gr/isl/CRMdig/"
namespace_dict["gnd"]= "https://d-nb.info/"
namespace_dict["frbr"]= "http://iflastandards.info/ns/fr/frbr/frbroo/"
namespace_dict["crmpc"]= "http://www.cidoc-crm.org/crmpc/"
namespace_dict["wikidata"]= "https://www.wikidata.org/wiki/"
namespace_dict["sikart"]= "http://www.sikart.ch/"
namespace_dict["skos"]= "http://www.w3.org/2004/02/skos/core#"
namespace_dict["cpr"]= "https://www.schema.swissartresearch.net/cpr/"
namespace_dict["sari"]= "https://resource.swissartresearch.net/"



#create node for the person the xml input file is about
#get type (e.g. crm:E21_person)
concept_namespace = rootM.find("./mappings/mapping/domain/target_node/entity/type").text.split(":", maxsplit=1)[0]
concept_type = rootM.find("./mappings/mapping/domain/target_node/entity/type").text.split(":", maxsplit=1)[1]
path_1 = rootM.find("./mappings/mapping/domain/source_node").text.split("root", maxsplit=1)[1]


#get identifier (i.e. uuid)
uuid_search = ".//" + rootM.find("./mappings/mapping/domain/target_node/entity/instance_generator/arg").text[3:-7]
uuid = rootS.find(uuid_search).text

#create node and insert it into graph
urn = Namespace("urn:uuid:")
person = URIRef(urn[uuid])

g.add((person, RDF.type, getattr(crm, concept_type)))



#fill graph
for x in rootM.iter("link"):

    #find predicate (i.e. namespace and relation type) of RDF triple (e.g. crm, P107)
    relation_namespace = x.find("path/target_relation[1]/relationship").text.split(":", maxsplit=1)[0]
    relation = x.find("path/target_relation[1]/relationship").text.split(":", maxsplit=1)[1]

    #find object (i.e. namespace and entity type) of RDF triple (e.g. crm, E21)
    target_entity_namespace = x.find("range/target_node/entity/type").text.split(":", maxsplit=1)[0]
    target_entity_type = x.find("range/target_node/entity/type").text.split(":", maxsplit=1)[1]


    #get current xpath for xml input file given by current position in x3ml input file
    path_2= x.find("path/source_relation/relation").text
    path= "."+ path_1 +"/"+ path_2

    value= ""      #value of current xpath in xml file
    if rootS.find(path) is not None:
        value= rootS.find(path).text


    #find identifier of the object of the current RDF triple  (e.g. "https://resource.swissartresearch.net/person/debb2cce-9ab9-4f68-8782-efea2ed5e152/birth")
    #from instance_generator tag in X3ML file and from corresponding generator tag in generator policy
    generator_node = x.find("range/target_node/entity/instance_generator")
    generator_name = x.find("range/target_node/entity/instance_generator").get("name")
    generator_args = {}

    for y in generator_node.iter("arg"):
        arg_name= y.attrib['name']
        arg_type= y.attrib['type']
        arg_value= y.text         #value of the arg tag in XML input file
        arg_final_value= y.text   #value to be passed to generator_args[]

        #if arg_type is xpath the value to be passed to the generator is not arg_value
        if arg_type == "xpath":
            if arg_value.startswith("text", 0):
                arg_final_value = value
            
            else:
                arg_value= arg_value.replace("/text()", "", 1)
                arg_value= arg_value.replace("..", "./entry", 1)

                if rootS.find(arg_value) is not None:
                    arg_final_value = rootS.find(arg_value).text
        
        generator_args[arg_name]= arg_final_value

    generator = rootG.find(".//generator[@name= '"+generator_name+"']")
    generator_pattern= rootG.find(".//generator[@name= '"+generator_name+"']/pattern")
    triple_object_identifier=""
    
    if ((generator_pattern is not None) and (generator is not None)):
        prefix = generator.attrib['prefix']
        generator_namespace= namespace_dict[prefix]
        generator_pattern_value = generator_pattern.text

        generator_variables = re.findall(r'{(.*?)}', generator_pattern_value)

        for v in generator_variables:
            generator_pattern_value= generator_pattern_value.replace("{"+v+"}", generator_args[v])
        
        triple_object_identifier=generator_namespace+generator_pattern_value
    

    #create RDF triple and add it to graph
    #triple_object_identifier="abc"+ str(counter)
    triple_object= URIRef(triple_object_identifier)

    g.add((triple_object, RDF.type, getattr(crm, target_entity_type)))
    g.add((person, getattr(crm, relation), triple_object))
    




#write graph data in output file
f.write(g.serialize(format='pretty-xml'))
f.close()



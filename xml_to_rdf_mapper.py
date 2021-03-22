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
 


sourceXML = ""
sourceX3ML = ""
generatorPolicy = ""

f = open("", "wb")

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

def create_node(gen_ancestor_node, gen_node, count, path_2_value, current_subject, relation_namespace, relation, target_entity_namespace, target_entity_type, val, with_rel):
    generator_name = ""
    triple_object_identifier= ""
    literal_value=""
    generator_pattern_value=""
    generator_namespace="crm"

    if gen_node is not None:
        generator_name= gen_ancestor_node.findall(".//instance_generator")[count].get("name")

    if generator_name == "UUID":

        if gen_node.find("arg") is not None:
            path_2= gen_ancestor_node.find(path_2_value).text
            if rootS.find("./"+path_1+"/"+path_2) is not None:
                triple_object_identifier= rootS.find("./"+path_1+"/"+path_2).text
        else:
            uuid= rootS.find("./entry/_uuid").text
            triple_object_identifier=uuid+"-"+target_entity_type
            generator_namespace= "urn"

    elif generator_name == "URIorUUID":

        if (gen_node.find("arg") is not None) and (gen_node.find("arg").get("type") == "constant"):
            triple_object_identifier= gen_node.find("arg").text
            generator_namespace="sari"

        elif (gen_node.find("arg") is not None) and (gen_node.find("arg").get("type") == "xpath"):
            path_2= gen_ancestor_node.find(path_2_value).text
            if rootS.find("./"+path_1+"/"+path_2) is not None:
                triple_object_identifier= rootS.find("./"+path_1+"/"+path_2).text

    elif generator_name == "Literal":
        path_2= gen_ancestor_node.find(path_2_value).text
        if rootS.find("./"+path_1+"/"+path_2) is not None:
                literal_value= rootS.find("./"+path_1+"/"+path_2).text
    
    #standard case with generator_name matching to a generator in the generator policy
    elif gen_node is not None:
        generator_args = {}           #dictionary containing the argument names and values for the generator

        for w in gen_node.iter("arg"):
            arg_name= w.attrib['name']
            arg_type= w.attrib['type']
            arg_value= w.text         #value of the arg tag in XML input file
            arg_final_value= w.text   #value to be passed to generator_args[]

            #if arg_type is xpath the value to be passed to the generator is not arg_value
            if arg_type == "xpath":
                if arg_value.startswith("text", 0):
                    arg_final_value = val
                
                elif arg_value.startswith(".", 0):
                    arg_value= arg_value.replace("/text()", "", 1)
                    arg_value= arg_value.replace("..", "./entry", 1)

                    if rootS.find(arg_value) is not None:
                        arg_final_value = rootS.find(arg_value).text

                else:
                    arg_value= arg_value.replace("/text()", "", 1)
                    #path= "."+ path_1 +"/"+ path_2
                    arg_value= path+"/"+arg_value

                    if rootS.find(arg_value) is not None:
                        arg_final_value = rootS.find(arg_value).text

            
            generator_args[arg_name]= arg_final_value

        generator = rootG.find(".//generator[@name= '"+generator_name+"']")
        generator_pattern= rootG.find(".//generator[@name= '"+generator_name+"']/pattern")
        
        if ((generator_pattern is not None) and (generator is not None)):
            generator_namespace = generator.attrib['prefix']
            generator_pattern_value = generator_pattern.text

            generator_variables = re.findall(r'{(.*?)}', generator_pattern_value)

            for v in generator_variables:
                generator_pattern_value= generator_pattern_value.replace("{"+v+"}", generator_args[v])
            
            generator_pattern_value= generator_pattern_value.replace(" ", "_")
            triple_object_identifier= generator_pattern_value


    #create RDF triple and add it to graph
    if (target_entity_type!= "") and (triple_object_identifier!= "") and (generator_name != "Literal"):
        triple_object= URIRef(eval(generator_namespace)[triple_object_identifier])

        g.add((triple_object, RDF.type, getattr(eval(target_entity_namespace), target_entity_type)))
        
        if with_rel:
         
            g.add((current_subject, getattr(eval(relation_namespace), relation), triple_object))

        return triple_object
    
    elif (target_entity_type!= "") and (literal_value!= "") and (generator_name == "Literal"):
        triple_object= Literal(literal_value)
        g.add((current_subject, getattr(eval(relation_namespace), relation), triple_object))
        return triple_object
    
    return

def create_label(gen_ancestor_node, label_gen_node, path_2_value, triple_object):
    label_text=""
    lang_text=""
    
    if (label_gen_node is not None) and (label_gen_node.tag == "label_generator"):
        
        #check if tag <arg name="text"> extsists, if yes retrieve necessary information from tag
        if label_gen_node.find("./arg[@name='text']") is not None:
            if label_gen_node.find("./arg[@name='text']").attrib['type'] == "xpath":
                path_2= ""
                if path_2_value!= "":
                    path_2= gen_ancestor_node.find(path_2_value).text
                
                path_3= label_gen_node.find("./arg[@name='text']").text
                path= "."+path_1+"/"+path_2+ "/"+ path_3
                path= path.replace("/text()", "", 1)
                #print("PATHHHHHHHH:"+ path)
                if rootS.find(path) is not None:
                    label_text= rootS.find(path).text
            else: #else type attribute is "constant"
                label_text= label_gen_node.find("./arg[@name='text']").text
        
        #check if tag <arg name="language"> extsists, if yes retrieve necessary information from tag
        if label_gen_node.find("./arg[@name='language']") is not None:
            if label_gen_node.find("./arg[@name='language']").attrib['type'] == "xpath":
                path_2= ""
                if path_2_value!="":
                    path_2= gen_ancestor_node.find(path_2_value).text
                path_3= label_gen_node.find("./arg[@name='language']").text
                path= "./"+path_1+"/"+path_2+ "/"+ path_3
                path= path.replace("/text()", "", 1)
                if rootS.find(path) is not None:
                    lang_text= rootS.find(path).text
            else: #else type attribute is "constant"
                lang_text= label_gen_node.find("./arg[@name='language']").text
        
        #add label to graph
        g.add((triple_object, rdfs.label, Literal(label_text, lang= lang_text)))


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
outer_counter=0
for q in rootM.iter("mapping"):
    
    #xpath of soure node of current mapping
    path_1= q.find("./domain/source_node").text.split("root", maxsplit=1)[1]
    path_2= ""
    path= path_1.replace("/", "./", 1)

    current_mapping = person
    
    if outer_counter>0:
        domain_node = q.find("./domain")
        mapping_generator_node = q.find("./domain/target_node/entity/instance_generator")
        entity_namespace= domain_node.find("./target_node/entity/type").text.split(":", maxsplit=1)[0]
        entity_type= domain_node.find("./target_node/entity/type").text.split(":", maxsplit=1)[1]
        current_mapping = create_node(domain_node, mapping_generator_node , 0, "", None, "", "", entity_namespace, entity_type, "", False)

        label_generator_node= q.find("./domain/target_node/entity/label_generator")
        create_label(domain_node, label_generator_node, "", current_mapping)

    for x in q.iter("link"):

        counter=0
        current_subj= current_mapping

        for y in x.iter("relationship"):

            #find predicate (i.e. namespace and relation type) of RDF triple (e.g. crm, P107)
            rel_namespace = y.text.split(":", maxsplit=1)[0]
            rel = y.text.split(":", maxsplit=1)[1]
            #print("relation: "+rel)


            #find object (i.e. namespace and entity type) of RDF triple (e.g. crm, E21)
            target_entity_node= x.findall(".//entity")[counter]
            targ_entity_namespace="crm"
            targ_entity_type= ""
            #print("counter: "+str(counter))
            #print(target_entity_node)
            if (target_entity_node is not None) and (target_entity_node.find("./type") is not None):
                targ_entity_namespace = target_entity_node.find("./type").text.split(":", maxsplit=1)[0]
                targ_entity_type = target_entity_node.find("./type").text.split(":", maxsplit=1)[1]
            #print("target_entity_namespace: "+targ_entity_namespace)
            #print("target_entity_type: "+targ_entity_type)


            #get current xpath for xml input file given by current position in x3ml input file
            path_2= x.find("path/source_relation/relation").text
            path= "."+ path_1 +"/"+ path_2

            value= ""      #value of current xpath in xml file
            if rootS.find(path) is not None:
                value= rootS.find(path).text


            #find identifier of the object of the current RDF triple  (e.g. "https://resource.swissartresearch.net/person/debb2cce-9ab9-4f68-8782-efea2ed5e152/birth")
            #from instance_generator tag in X3ML file and from corresponding generator tag in generator policy
            #add new node to the graph
            generator_node = x.findall(".//instance_generator")[counter]
            triple_obj = create_node(x, generator_node, counter, "./range/source_node", current_subj, rel_namespace, rel, targ_entity_namespace, targ_entity_type, value, True)
            

            #add lebels
            #check if there is a label generator for the current triple_object, if yes gather necessary information for label 
            label_generator_node= generator_node.getnext()
            create_label(x, label_generator_node, "./range/source_node", triple_obj)
            
            #update current_subj and counter
            current_subj= triple_obj
            counter+=1
            print()
    
    outer_counter+=1
            




#write graph data in output file
f.write(g.serialize(format='pretty-xml'))
f.close()



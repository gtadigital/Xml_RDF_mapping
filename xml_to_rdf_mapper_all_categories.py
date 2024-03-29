# author: ETH Zurich, gta digital, Zoé Reinke
# license: please refer to the license.txt file in our git repository (https://github.com/gtadigital/ProfileParser)

#run the code by calling the transform(sourceXML, sourceX3ML, generatorPolicy, output_path, uuid_xpath) function
#the first 4 arguments denote the paths to the desired input and output files
#the last argument denotes the xpath to the uuid tag in the source xml file. This argument depends on the category (AO, BW, group, person or place) and should have one of the following values
#AO: "./entry/ao_record_uuid" BW: "./entry/oeu_nc_uuid" group: "./entry/_uuid" person: "./entry/_uuid" place: "./entry/plIdentifier_uuid"

import logging
import os
import lxml.etree as ET
import argparse
import rdflib
import re
from rdflib import Graph
from rdflib import Namespace
from rdflib import *


#this is a helper function that joins together an absolute and a relative xpath into one coherent absolute xpath
def concat_path(path_pt1, path_pt2):
    path_w = ""
    occ = path_pt2.count("../")

    for i in range(0, occ):
        path_pt2 = path_pt2.replace("../", "", 1)
        path_pt1 = path_pt1.rsplit("/", 1)[0]
    
    path_pt2 = path_pt2.replace("/text()", "", 1)
    path_pt2 = path_pt2.replace("text()", "", 1)
    
    if path_pt2=="":
        path_w = path_pt1
    else:
        path_w = path_pt1+"/"+path_pt2
    
    return path_w


#This function adds a new rdf node to the rdf graph.
#To do so, it uses values provided directly by the function arguments (e.g. relation_namespace ("crm"), relation_name ("P2_has_type",...)) and values based on the current instance of the <instance_generator...> tag which are computed during the function call.
#The current instance/node of the instance_generator tag is handed over to the function in the argument "gen_node". 
#The attribute "name" of the instance_generator node (stored in variable "generator_name") tells us which generator to use from the generator policy.
#The generators from the generator policy provide us with a specific pattern (stored in variable "generator_patterm") denoting how the URI identifier of the new node (later stored in the variable "triple_object_identifier") should be structured (e.g. "place/{place_id}/appellation/{appellation_id}")
#The placeholder strings in the curly braces {} in the pattern are to be replaced with values specific to the new node which is to be created.
#The values to be inserted into these placeholders are derived from the <arg ...> tags subordinated to the current <instance_generator...> tag. 
#The values are provided either via a constant value or via an xpath leading to some value in the source xml file
#Once obtained from the input files, these values are stored in the dictionary "generator_args" and inserted into the URI pattern in ll. 170-181
#There are some instance_generator tags to whose name no generator of the generator policy corresponds, namely "UUID", "URIorUUID" and "Literal".
#For these tags the URI identifier (var "triple_object_identifier") is created in a different way
#In the end, the function creates the new rdf node and adds it to the graph
def create_node(gen_ancestor_node, gen_node, count, current_subject, relation_namespace, relation, target_entity_namespace, target_entity_type, val, with_rel, path, tag_num, uuid_xpath):
    generator_name = ""
    triple_object_identifier= ""
    literal_value=""
    literal_lang=""
    generator_pattern_value=""
    generator_namespace="crm"

    if gen_node is not None:
        generator_name= gen_ancestor_node.findall(".//instance_generator")[count].get("name")

    #create the URI identifier of the node
    #handle the three "edge case" generators UUID, URIorUUID and Literal
    if generator_name == "UUID":

        if (gen_node.find("arg") is not None) and (gen_node.find("arg").get("type") == "xpath"):
            generator_namespace="uuid"
            path_3= gen_node.find("./arg").text
            path_whole= concat_path(path, path_3)

            if rootS.find(path_whole) is not None:
                triple_object_identifier= rootS.find(path).text
        else:
            uuid_local= rootS.find(uuid_xpath).text
            triple_object_identifier=uuid_local+"-"+target_entity_type
            generator_namespace= "uuid"

    elif generator_name == "URIorUUID":

        if (gen_node.find("arg") is not None) and (gen_node.find("arg").get("type") == "constant"):
            triple_object_identifier= gen_node.find("arg").text
            generator_namespace="uuid"

        elif (gen_node.find("arg") is not None) and (gen_node.find("arg").get("type") == "xpath"):
            generator_namespace="uuid"
            path_3= gen_node.find("./arg").text

            if path_3.startswith("text", 0):
                triple_object_identifier = val
            else:
                path_whole= concat_path(path, path_3)
                if rootS.find(path_whole) is not None:
                    triple_object_identifier= rootS.find(path_whole).text

    elif generator_name == "Literal":
        if gen_node.find("./arg[@name='text']") is not None:
            if gen_node.find("./arg[@name='text']").attrib['type'] == "xpath":
                
                path_3= gen_node.find("./arg[@name='text']").text
                path_whole= concat_path(path, path_3)
                
                if rootS.find(path_whole) is not None and rootS.find(path_whole).text is not None:
                    literal_value= rootS.find(path_whole).text
            
            elif gen_node.find("./arg[@name='text']").text is not None:
                #else we presume the attribute type is "constant"
                literal_value= gen_node.find("./arg[@name='text']").text

        
        if gen_node.find("./arg[@name='language']") is not None:
            if gen_node.find("./arg[@name='language']").attrib['type'] == "xpath":

                path_3= gen_node.find("./arg[@name='language']").text

                path_whole= concat_path(path, path_3)

                if len(rootS.findall(path_whole)) >= tag_num+1:
                    if rootS.findall(path_whole)[tag_num] is not None:
                        literal_lang= rootS.findall(path_whole)[tag_num].text
                elif rootS.find(path_whole) is not None:
                    literal_lang= rootS.find(path_whole).text

            else:
                #else we presume the attribute type is "constant"
                literal_lang= gen_node.find("./arg[@name='language']").text
    
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
                
                else:
                    path_whole= concat_path(path, arg_value)

                    if len(rootS.findall(path_whole)) >= tag_num+1:
                        if rootS.findall(path_whole)[tag_num] is not None:
                            arg_final_value= rootS.findall(path_whole)[tag_num].text
                    elif rootS.find(path_whole) is not None:
                        arg_final_value= rootS.find(path_whole).text


            elif arg_type== "constant":
                arg_final_value= w.text

            generator_args[arg_name]= arg_final_value


        generator = rootG.find(".//generator[@name= '"+generator_name+"']")
        generator_pattern= rootG.find(".//generator[@name= '"+generator_name+"']/pattern")
        
        if ((generator_pattern is not None) and (generator is not None)):
            #the generators "coordinates_alternative" and "coordinates" are edge cases as they do not posses a "prefix" attribute denoting the namespace
            if generator_name == "coordinates_alternative" or generator_name == "coordinates":
                generator_namespace= "nonamesp"
            else:
                generator_namespace = generator.attrib['prefix']
            
            generator_pattern_value = generator_pattern.text

            generator_variables = re.findall(r'{(.*?)}', generator_pattern_value)

            for v in generator_variables:
                if generator_args[v] is not None:
                    generator_pattern_value= generator_pattern_value.replace("{"+v+"}", generator_args[v])
                else:
                    return None #if generator_args[v] is None, there is an <if><exists> text() <\exists><\if> condition in the x3ml mapping and we abort the function call
        
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
        triple_object= Literal(literal_value, lang= literal_lang)
        g.add((current_subject, getattr(eval(relation_namespace), relation), triple_object))
        return triple_object
    
    return


#This function adds a mew rdf label to the rdf graph. To do so it uses one of the <label_generator...> tags in the X3ML mapping schema
#The current instance/node of the label_generator tag is handed over to the function in the argument "label_gen_node". 
#An rdf label contains a text <rdfs:label>xyz</rdfs:label> and may have a language attribute <rdfs:label lang="en">
#The values of both the text and the language attribute can be obtained via the <arg...> tags subordinated to the label_generator tag.
#Either they are provided by a constant value enclosed in the arg tags (<arg...>constant</arg>) or by an xpath leading to some value in the source xml file
#Once obtained, these values are stored in the variables "label_text" and "lang_text"
#In the end, the function creates the new rdf label based on the values computed in the function
def create_label(label_gen_node, path, triple_object, tag_num):
    label_text=""
    lang_text=""
    path_whole=""
    
    if (label_gen_node is not None) and (label_gen_node.tag == "label_generator"):
        
        #check if tag <arg name="text"> extsists, if yes retrieve necessary information from tag
        if label_gen_node.find("./arg[@name='text']") is not None:
            if label_gen_node.find("./arg[@name='text']").attrib['type'] == "xpath":
                
                path_3= label_gen_node.find("./arg[@name='text']").text

                path_whole= concat_path(path, path_3)
                if len(rootS.findall(path_whole)) >= tag_num+1:
                    if rootS.findall(path_whole)[tag_num] is not None:
                        label_text= rootS.findall(path_whole)[tag_num].text
                elif rootS.find(path_whole) is not None:
                    label_text= rootS.find(path_whole).text
            else: #else type attribute is "constant"
                label_text= label_gen_node.find("./arg[@name='text']").text
        
        #check if tag <arg name="language"> extsists, if yes retrieve necessary information from tag
        if label_gen_node.find("./arg[@name='language']") is not None:
            if label_gen_node.find("./arg[@name='language']").attrib['type'] == "xpath":

                path_3= label_gen_node.find("./arg[@name='language']").text

                path_whole= concat_path(path, path_3)

                if len(rootS.findall(path_whole)) >= tag_num+1:
                    if rootS.findall(path_whole)[tag_num] is not None:
                        lang_text= rootS.findall(path_whole)[tag_num].text
                elif rootS.find(path_whole) is not None:
                    lang_text= rootS.find(path_whole).text
            else: #else type attribute is "constant"
                lang_text= label_gen_node.find("./arg[@name='language']").text
        
        #add label to graph

        g.add((triple_object, rdfs.label, Literal(label_text, lang= lang_text)))

    #print(logging.info())


#This function does the main part of the xml to rdf transformation process.
#First, we read in the input files and create a new empty rdf graph which will be filled in the course of the function call and define the necessary namespaces
#Then, in order to create the new rdf nodes with the correct dependency structure, we loop through the x3ml mapping schema by the tags <mapping>, <link> and <relationship>:
#For each <mapping> tag a "top-level" rdf node should be added to the graph which depends only on the root rdf node.
#Each <link> tag defines a cascade of nodes which is dependent on the current mapping.
#Within a <link>...</link> tag, each <relationship> tag defines a new node. These nodes have a top-down dependency structure where each node depends on the node defined by the <relationship> tag above it.
#We store the node on which the new node to be created in the current iteration is dependent in the variable "current_subj_list"
#To create the node we have to extract some necessary values from the x3ml mapping, namely:
#the entity type (e.g. "E21_Person")(stored in variable "entity_type"), the entity namespace (e.g. "sari")(var "entity_namespece"),
#the type of relation (e.g. "P2_has_type")(var "rel"), the relation namespace (e.g. "crm")(var "rel_namespace") and
#the xpath leading to the corresponding values in the source xml file which is contained in the <source_node> tags of the x3ml mapping
#Finally, with all this information gathered, we access the <instance_generator> tag belonging to the current <relationship> tag (i.e. the next instance_generator tag below the rel. tag)
#and create the new rdf node by calling the create_node() function
#If there are <label_generator> tags belonging to the current relationship tag, we create a rdf label for each of them by calling the create_label() function

#the for loops "for n in range(0, num_nodes):..." and "for i in range(0, num_nodes):..." serve the following purpose:
#sometimes when creating a new rdf node, there is more than one tag in the source xml file corresponding to the current xpath denoted in the x3ml mapping.
#In this case, we want to create a new node for each of the tags in the source xml file. Therefore we count the number of occurrences of the current xpath in the source xml file and do the node creation procedure for each of them
def transform(sourceXML, sourceX3ML, generatorPolicy, output_path, uuid_xpath):
    f = open(output_path, "wb")

    # read in X3ML file
    global treeM
    treeM = ET.parse(sourceX3ML)
    global rootM
    rootM = treeM.getroot()

    #read in source XML file
    global treeS 
    treeS= ET.parse(sourceXML)
    global rootS 
    rootS= treeS.getroot()

    #read in generator policy
    global treeG 
    treeG= ET.parse(generatorPolicy)
    global rootG 
    rootG= treeG.getroot()

    #create rdf graph
    global g 
    g = Graph()


    #define namespaces
    global rdf
    rdf= Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    global ulan
    ulan= Namespace("http://vocab.getty.edu/page/ulan/")
    global crm
    crm= Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    global rdfs
    rdfs= Namespace("http://www.w3.org/2000/01/rdf-schema#")
    global crmdig
    crmdig= Namespace("http://www.ics.forth.gr/isl/CRMdig/")
    global gnd
    gnd= Namespace("https://d-nb.info/")
    global frbr
    frbr= Namespace("http://iflastandards.info/ns/fr/frbr/frbroo/")
    global crmpc
    crmpc= Namespace("http://www.cidoc-crm.org/crmpc/")
    global wikidata
    wikidata= Namespace("https://www.wikidata.org/entity/")
    global sikart
    sikart= Namespace("http://www.sikart.ch/")
    global skos
    skos= Namespace("http://www.w3.org/2004/02/skos/core#")
    global cpr
    cpr= Namespace("https://www.schema.swissartresearch.net/cpr/")
    global sari
    sari= Namespace("https://resource.swissartresearch.net/")
    global tu
    tu = Namespace("https://resources.gta.arch.ethz.ch/terminology/transurbicide/")
    global uuid
    uuid = Namespace("")
    global tgn
    tgn = Namespace("http://vocab.getty.edu/tgn/")
    global geonames
    geonames= Namespace("https://www.geonames.org/")
    global dbpedia
    dbpedia= Namespace("http://dbpedia.org/resource/")
    global viaf
    viaf= Namespace("http://viaf.org/viaf/")
    global nonamesp
    nonamesp = Namespace("")
    global http
    http=Namespace("http")

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
    g.bind("tu", tu)
    g.bind("uuid", uuid)
    g.bind("tgn", tgn)
    g.bind("geonames", geonames)
    g.bind("dbpedia", dbpedia)
    g.bind("viaf", viaf)
    g.bind("nonamesp", nonamesp)
    g.bind("http", http)


    #fill the graph
    for q in rootM.iter("mapping"):
        
        #xpath of source node of current mapping
        path_1= q.find("./domain/source_node").text.split("root", maxsplit=1)[1]
        path_2= ""
        path= path_1.replace("/", "./", 1)
        
        
        #if there are more than one tags with the current path in the input xml file, we create a rdf node for each of them
        num_nodes = int(rootS.xpath('count('+path+')'))

        for n in range(0, num_nodes):
            #after the first iteration we have to set the path value back to the initial value
            path_1= q.find("./domain/source_node").text.split("root", maxsplit=1)[1]
            path_2= ""
            path= path_1.replace("/", "./", 1)
            
            #get the entity namespace (e.g. "crm") and the entity type (e.g. "E21_Person") of the top-level node
            domain_node = q.find("./domain")
            mapping_generator_node = q.find("./domain/target_node/entity/instance_generator")
            entity_namespace= domain_node.find("./target_node/entity/type").text.split(":", maxsplit=1)[0]
            entity_type= domain_node.find("./target_node/entity/type").text.split(":", maxsplit=1)[1]

            outer_value= ""
            if rootS.findall(path)[n] is not None:
                outer_value= rootS.findall(path)[n].text

            #create the new top-level node and add it to thegraph. In order to access it later on, when we create nodes dependent on it, we store it in the variable current_mapping
            current_mapping = create_node(domain_node, mapping_generator_node, 0, None, "", "", entity_namespace, entity_type, outer_value, False, path, n, uuid_xpath)

            label_generator_node= q.find("./domain/target_node/entity/label_generator")
            create_label(label_generator_node, path, current_mapping, n)

            #save xpath of current node in variable path_1
            path_1= treeS.getpath(rootS.findall(path)[n])
            path_1=path_1.replace("/root", ".", 1)


            for x in q.iter("link"):

                counter=0
                current_subj_list=[] #in this list we store the nodes on which the nodes created in the inner for loops are dependent
                current_subj_list.append(current_mapping)

                for y in x.iter("relationship"):
                    triple_obj_list=[] #in this list we store the nodes created in the inner for loops in order to be able to access them later on

                    #find predicate (i.e. namespace and relation type) of RDF triple (e.g. crm, P107)
                    rel_namespace = y.text.split(":", maxsplit=1)[0]
                    rel = y.text.split(":", maxsplit=1)[1]


                    #find object (i.e. namespace and entity type) of RDF triple (e.g. crm, E21)
                    target_entity_node= x.findall(".//entity")[counter]
                    targ_entity_namespace="crm" #default namespace
                    targ_entity_type= "" #default entity type
                    if (target_entity_node is not None) and (target_entity_node.find("./type") is not None):
                        targ_entity_namespace = target_entity_node.find("./type").text.split(":", maxsplit=1)[0]
                        targ_entity_type = target_entity_node.find("./type").text.split(":", maxsplit=1)[1]


                    #get current xpath for xml input file given by current position in x3ml input file
                    path_2= x.find("path/source_relation/relation").text
                    path= path_1 +"/"+ path_2

                    num_nodes = len(rootS.findall(path))

                    #if there are more than one tags with with the current path in the input xml file, we create a rdf node for each of them
                    for i in range(0, num_nodes):

                        #check if there is a violated <if><exists>...</exists></if> condition which tells us not to create rdf nodes from the current relationship tag
                        if rootS.findall(path)[i] is None and ((y.getprevious() is not None and y.getprevious().tag == "if") or (target_entity_node.getprevious() is not None and target_entity_node.getprevious().tag== "if")):
                            break

                        #value of current xpath in xml file
                        value=""
                        if rootS.findall(path)[i] is not None:
                            value= rootS.findall(path)[i].text
                        


                        #find identifier of the object of the current RDF triple  (e.g. "https://resource.swissartresearch.net/person/debb2cce-9ab9-4f68-8782-efea2ed5e152/birth")
                        #from instance_generator tag in X3ML file and from corresponding generator tag in generator policy
                        generator_node = x.findall(".//instance_generator")[counter]
                        
                        for subject in current_subj_list:
                            #add new node to the graph
                            triple_obj = create_node(x, generator_node, counter, subject, rel_namespace, rel, targ_entity_namespace, targ_entity_type, value, True, path, i, uuid_xpath)
                            if triple_obj is None:
                                break
                                #if triple_obj is None a <if><exists>...<\exists><\if> was violated during the function call; therefore we end the current iteration of the for loop

                            #add lebels
                            #check if there are one or two label generators for the current triple_object, if yes gather necessary information for label 
                            label_generator_node= generator_node.getnext()
                            create_label(label_generator_node, path, triple_obj, i)

                            if label_generator_node is not None:
                                label_generator_node= generator_node.getnext().getnext()
                                create_label(label_generator_node, path, triple_obj, i)

                            triple_obj_list.append(triple_obj)
                    
                    #update current_subj and counter
                    current_subj_list= triple_obj_list
                    counter+=1
            
                
    #write graph data in output file
    f.write(g.serialize(format='pretty-xml'))
    f.close()


import os
import rdflib
from rdflib import Graph

base_directory = ""
output_directory =""

counter=0

list_sub_dirs = [x[0] for x in os.walk(base_directory)]

for sub_dir in list_sub_dirs:
    graph = Graph()
    graph_is_empty= True

    for file in os.listdir(sub_dir):
        if file.endswith(('.rdf')):
            graph_is_empty= False
            file_name= sub_dir+"/"+file
            graph.parse(file_name)

    #we only create a new rdf file if the current subdirectory actually conatained an rdf file
    if not graph_is_empty:
        output_file= open(output_directory +"/"+ "output"+ str(counter) +".rdf", "wb")

        output_file.write(graph.serialize(format='pretty-xml'))
        output_file.close()
    counter+=1

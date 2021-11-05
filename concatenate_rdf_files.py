import argparse
import os
import rdflib
from rdflib import Graph


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='run concatenate_rdf_files.py')
    parser.add_argument('--base_directory', dest="base_directory",help='path of the folder containing the rdf files to be concatenated')
    parser.add_argument('--output_directory', dest="output_directory", help='path of the folder which is to contain the output foilder')

    args = parser.parse_args()
    base_directory = args.base_directory
    output_directory = args.output_directory

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
    
    print("done")

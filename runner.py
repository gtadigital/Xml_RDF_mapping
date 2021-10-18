import argparse
import os
import xml_to_rdf_mapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='run xml to rdf transformation')
    parser.add_argument('--source_XML', dest="source_XML",help='path of the folder containing the source XML files')
    parser.add_argument('--gen_pol', dest="gen_pol", help='path of the generator policy file')
    parser.add_argument('--x3ml_mapping', dest="x3ml_mapping", help='path of the X3ML mapping file')
    parser.add_argument('--out_path', dest="out_path", help='path of the folder which will contain the output files' )
    parser.add_argument('--path_to_uuid', dest="path_to_uuid", help='path to the uuid tag in the source XML file')

    args = parser.parse_args()
    source_XML = args.source_XML
    gen_pol = args.gen_pol
    x3ml_mapping = args.x3ml_mapping
    out_path = args.out_path
    path_to_uuid = args.path_to_uuid

    counter = 0
    for root, dirs, files in os.walk(source_XML):

        for item in files:
            if item.endswith(('.xml')):
                whole_input_path = root+"/"+ item
                modified_output_path= out_path+"/file"+str(counter)+"_entry.rdf"
                xml_to_rdf_mapper.transformAll(whole_input_path, x3ml_mapping, gen_pol, modified_output_path, path_to_uuid)
                counter+=1
    
    print("done")
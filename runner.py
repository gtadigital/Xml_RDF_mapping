import argparse

import xml_to_rdf_mapper_final_with_arguments
from xml_to_rdf_mapper_final_with_arguments import transform

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='run xml to rdf transformation')
    parser.add_argument('--source_XML', dest="source_XML",help='path of the source XML file')
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

    xml_to_rdf_mapper_final_with_arguments.transformAll(source_XML, x3ml_mapping, gen_pol, out_path, path_to_uuid)
    print("done")

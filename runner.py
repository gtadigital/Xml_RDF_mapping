import argparse
import textwrap as _textwrap
import re
import os
import xml_to_rdf_mapper


class PreserveWhiteSpaceWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __add_whitespace(self, idx, iWSpace, text):
        if idx == 0:
            return text
        return (" " * iWSpace) + text

    def _split_lines(self, text, width):
        textRows = text.splitlines()
        for idx,line in enumerate(textRows):
            search = re.search('\s*[0-9\-]{0,}\.?\s*', line)
            if line.strip() == "":
                textRows[idx] = " "
            elif search:
                lWSpace = search.end()
                lines = [self.__add_whitespace(i,lWSpace,x) for i,x in enumerate(_textwrap.wrap(line, width))]
                textRows[idx] = lines

        return [item for sublist in textRows for item in sublist]

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
    prog='PROG',
    formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter)
    parser.add_argument('--source_XML', type=int, default=42, help="""Path of the folder containing the source XML files.

    -  E.g ../MyOutput/
    """)
    parser.add_argument('--gen_pol', type=int, default=[42], help="""Path of the .xml generator policy file.
    
    - E.g ../generator_policy/generator-policy.xml
    """)

    parser.add_argument('--x3ml_mapping', type=int, default=[42], help="""Path of the X3ML mapping file. 
    
    - E.g ../mapping/Mapping15.x3ml
    """)

    parser.add_argument('--out_path', type=int, default=[42], help="""Path of the folder which will contain the output files.
    
    -  E.g ../myOutput/
    """)

    parser.add_argument('--path_to_uuid', type=int, default=[42], help="""Arguments to select CIDOC-CRM mapping schema.
    
    Available options:
        -   ./entry/ao_system_object_id = E78_Collection
        -   ./entry/oeu_nc_uuid = E22_Man-Made_Object
        -   ./entry/grp_system_object_id = E74_Group
        -   ./entry/act_system_object_id = E21_Person
        -   ./entry/plIdentifier_uuid = E53_Place
    """)
    
    

    #parser.print_help()
    
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
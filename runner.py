import xml_to_rdf_mapper
from xml_to_rdf_mapper import transformAll

xml_to_rdf_mapper.transformAll("..\\xml_source.xml", "..x3ml_mapping.xml", "..\\generator-policy.xml", "..\\output_BW_new.rdf", "./entry/oeu_nc_uuid")
print("done")

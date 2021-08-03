import xml_to_rdf_mapper_all_categories
from xml_to_rdf_mapper_all_categories import transform

xml_to_rdf_mapper_all_categories.transform("input/sourceXMLPerson.xml", 
	"mapping_schema/x3mlMapping.xml", 
	"generator_policy/generator-policy.xml", 
	"output/person.rdf", 
	"./entry/_uuid")
print("done")
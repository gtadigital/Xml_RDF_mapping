# Xml_RDF_mapping


## What the code does
The xml_to_rdf_mapper.py file provides the function transformAll() which takes as arguments a source XML file, an x3ml mapping schema in xml format and a generator policy also in XML format and transforms the data provided in the source XML file to an rdf graph according to the schema defined in the x3ml mapping and the generator policy.
The test_runner.py file is a helper file which makes it easy to run the transformAll()-function from the xml_to_rdf_mapperpy file directly from the terminal.

## How to run the code

- save xml_to_rdf_mapper.py and test_ruunner.py in the same directory
- in the test_runner.py file (l.4), provide the correct paths to yout input files to the xml_to_rdf_mapper.transformAll(...) function
- run test_runner.py in your terminal : Windows: C:\yourDirectory> test_runner.py

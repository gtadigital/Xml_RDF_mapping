# Xml_RDF_mapping


The xml_to_rdf_mapper.py file provides the function transformAll(), which takes as arguments a source XML file, an x3ml mapping schema in XML format, a generator policy also in XML format and a string value denoting the xpath from the root to the uuid in the source xml file, and transforms the data provided in the source XML file to an rdf graph according to the schema defined in the x3ml mapping and the generator policy.

The test_runner.py file is a helper file which makes it easy to run the transformAll()-function from the xml_to_rdf_mapperpy file directly from the terminal.

The concatenate_rdf_files.py file concatenates all rdf files which are in the directory whose path is saved in the base_directory variable (l.5) and saves the newly generated, big rdf graph in the directory whose path is saved in the output_directory variable (l.6.)

## Installation

* Clone the repository and go into the directory

```bash
# Clone the repository:
$ git clone https://github.com/gtadigital/Xml_RDF_mapping.git
```
 A new folder ```Xml_RDF_mapping``` will be created

* Go into the new folder:

```bash
# Go into the repository
$ cd Xml_RDF_mapping
```
* Install Virtual Environment

```bash
# Type the command 
$ python3 -m venv .venv
```
* Activate the Virtual Environment

```bash
# Type the command
$ source .venv/bin/activate
```

* Install the dependencies

```bash
# Type the command
$ pip install -r requirements.txt
```
   
* Run the scripts:

  Transform an XML file to an RDF file according to a certain X3ML mapping schema and a corresponding generator policy:

    In the test_runner.py file (l.4), provide the correct arguments to the xml_to_rdf_mapper.transformAll(...) function. the first 4 arguments denote the paths to the desired input and output files. The last argument denotes the xpath to the uuid tag in the source xml file. This argument depends on the category (AO, BW, group, person or place) and should have one of the following values: 
      - AO: "./entry/ao_record_uuid" 
      - BW: "./entry/oeu_nc_uuid" 
      - group: "./entry/_uuid" 
      - person: "./entry/_uuid" 
      - place: "./entry/plIdentifier_uuid"

    Then run test_runner.py 
    ```bash
    # Run the script
    $ python3 python test_runner.py
    ```
  

  Concatenate all rdf files in a certain directory:
  
    Save the path to the directory containing the rdf files in the variable base_directory (l.5) and save the path to the directory which will contain the newly generated big rdf file in the variable output_directory (l.6)

    Then run concatenate_rdf_files.py
    ```bash
    # Run the script
    $ python3 python concatenate_rdf_files.py
    ```

## Release History

The project has not been released yet.

## Credits

Institute for the History and Theory of Architecture, gta digital, ETH Zurich

## License

Xml_RDF_mapping (c) by Institute for the History and Theory of Architecture, gta digital, ETH Zurich

Xml_RDF_mapping is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.

This file is subject to the terms and conditions defined in file 'LICENSE.txt', which is part of this source code package.

# Xml_RDF_mapping

The goal of this tool is to transform XML into RDF graph(s) according to CIDOC-CRM ontology.
The transformation is done by using the X3M mapping schema.

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

    Then run test_runner.py 
    ```bash
    # Run the script
    $ python3 python test_runner.py
    ```
  

* Concatenate all rdf files in a certain directory:
  
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

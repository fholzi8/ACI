Configuring the APIC From Cisco XLS

The Cisco format xls for data collection is used with these tools. The directory structure should be maintained
as it is used by each of the python scripts. The directory scripts is the root for all script work.

The sub-directories are as follows:
./input - Contains the CSV files exported from the Cisco XLS
./py 	- Contains the python conversion scripts from CSV to XML
./xml	- Contains the final XML to be posted to the APIC.

You may delete all the files in ./input and ./xml as they will be recreated by the scripts.

There are 3 python scripts in the root scripts directory.

1. export_excel_to_csv.py - This script takes the Cisco XLS and converts the selected worksheets to individual CSV files.
							This script uses a hardcoded Cisco XLS name and absolute path, you must change this to the
							path and filename of the Cisco XLS you are using.

2. convert_csv_to_xml.py  - This script converts the CSV files to XML. It calls each specific script in ./py to convert
							each CSV file to a corresponding XML file. You can run each conversion script directly from
							the ./py directory if required.

3. post_xml_to_apic.py	  - Helper script, this will provide a menu list of all the xml files in the ./xml directory.
							Selecting a file number will post this file to the APIC. This script requires cmd line params
							of username and password. The DIV APIC IP is hard coded and can be changed or introduced into
							the cmd line if required with small modifications.
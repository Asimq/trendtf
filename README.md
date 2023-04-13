# TRENDTF 

The repository contains the following subprojects;


1. Dspace: (Python)

Dspace contains scripts to import DC metadata into Dspace 7.5 (backend)
It contains a modular (classes based) and a function based script. Both has the same functionality and can be extended to bring new functionalities in the project.
Read importDcMetadata.py for easy understanding.

2.  Metadata: (Python)

Metadata has scripts for retrieval and converting Metadata
It can retrieve metadata from TIB's OAI API

Conversion has scripts for the following:
a) FTX to JSON
b) JSON to DC JSON
c) JSON to XML
d) XML to DC JSON

3. RabbitMQ: (Python, Ansible)

RabbitMQ has Ansible scripts for copying the template project as well as for running and stopping them. It also has modified files (projects) to template project for different processes.

4. Termsuite: (Java, Sh, Python)

It includes the sh, python scripts along with the libraries that are essential for running it on Java 11.

5. TrendtfSearch (Python - Flask 8)
Full text based search web-app based on Elastic index. Entry point wsgi.py

6. Elastic (Python)

It contains the script for importing data into ElasticSearch

7. TopicModeling (Python)

It contains the code and template project for two techinques of topic modeling used in DTF project.

8. API (Python - FastAPI) 
FileDownload API offering various kinds of text files and metadata as downloadable files from a mounted drive for DTF
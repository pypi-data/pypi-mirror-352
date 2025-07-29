# OpenTLDR-Core
An Open Framework for Generating an Tailored Daily Report
This repository contains the OpenTLDR package. You can 'pip install opentldr' to get the contents of this repository as a python package in your virtaul env.

![overview image](https://opentldr.org/images/opentldr.png)

The latest OpenTLDR-Core library is availible as a Pip Package:
<pre>
python3 -m pip install opentldr
</pre>

## Introduction to OpenTLDR

OpenTLDR is an open source framework written in Python to implement the process of creating a Tailored Daily Report from a series of news-like articles. This repository contains the Core classes used as a library by OpenTLDR implementations, like the example notebooks you can find in the OpenTLDR-Example repo on GitHub.

OpenTLDR is composed of Python modules:
- A **KnowledgeGraph** module that has been implemented as a layer on top of the Neo4j Graph Database
- A module with a set of **Domain** classes that implement the nodes and edges in a TLDR-focused knowledge graph
- A **Workflow** module and tool that wraps the execution of a series of Python Notebooks to make them behave like components
- A **DataRepo** module that abstracts the data ingest from Python Notebooks using a config parameter for either S3 or Files

This GitHub repo handles the back-end code that is only required if you wish to modify this functionality directly. Otherwise, you should use the OpenTDLR-Example repository, which implements analytic pieces of the process in a series of Jupyter Notebooks. All of the code in this repo is available to Python code as a pip library using a command like `python3 -m pip install opentldr` please make sure that you need to modify this library directly before using this codebase.

## KnowledgeGraph

OpenTLDR uses a Neo4j graph database as the storage layer of its KnowledgeGraph. The default (and easiest) way to do this is to run the Community Edition neo4j Server in a Docker container on the local machine that you execute OpenTLDR workflows. A linux shell script (start_neo4j.sh) and docker-compose configuraiton file (scripts/Neo4j/docker-compose) automate this process. The default container does not require authentication but only connects to localhost loopback interface. You can change all of this and use .env or system environment variables to direct the OpenTLDR library to use the desired neo4j server and user credientials.

OpenTLDR uses the KnowledgeGraph's API to build up a series of objects and relationships (see the Domain module) over a series of steps in the automated workflow (see the Workflow module). This includes loading content (e.g., news articles), which means that the graph database can become large. The KnowledgeGraph API is designed to be verb-oriented and functional, with the Domain classes being the nouns and providing useful data objects. The primary reason for this API design was to keep the Notebooks simple, clean, and transactional to the KnowledgeGraph. The default query methods return either a single or list of objects defined by a Domain class.

## Domain

The OpenTLDR library includes class definitions for all of the objects represented in the KnowledgeGraph. This standardizes the graph, so that multiple analytic workflows can easily achieve compatability.

Each Domain class includes the following properties:
- uid - a text string that acts as a unique identifier that is created the first time the data object is saved and can be queried.
- meta - a json object that can be used to decorate any node or edge with additional properties that your workflow might use (but that are not expected to be implemented by others)

The schema of the KnowledgeGraph is represented graphically to indicate how the different node and edge types interconnect. As long as the Domain objects and KnowledgeGraph API are used, it should be difficult to end up with incorrect connections. Every edge type is also a uniquely named Domain object with a uid and meta properties. 

![schema image](https://opentldr.org/images/schema.png)

The colors in this image can be replicated in the neo4j interface using the `scripts/neo4j_styles.grass` file, which can be drag and dropped on the main neo4j webpage. Note that the naming convention for neo4j suggests that nodes be labeled with upper camel case capitalization without spaces (which is the same as the naming of the python Domain classes) and edges are all caps with underlines as spaces (which can sometimes be confusing when switching between the python Domain class names and the labels in the graph and cypher code).

## Workflow

The OpenTLDR Workflow uses PaperMill to execute the sequences of analytic notebooks and parameterize them. This should not impede the notebooks from  being run manually when desired, but it does enforce the expected workflow order of execution that should be used when running evaluation scoring for an end-to-end analytic workflow.

### The Default Workflow Parameters

There are a few paramters that are used throughout the standard workflow.

#### Output Folder
This indicates where the automated workflow should place the outputed Notebooks. Note that these are copies of the original notebooks that show the execution results.  They copies are overwritten each time the workflow is executed. The original notebooks should always be treated as read-only copies.

<pre>
output_folder = "./READ_ONLY_OUTPUT"
</pre>

#### Notebook Order
This parameter is a list of strings, where each string is the relative path of a Notebook file to run. We tend to name these with the order that they are executed manually, but the `Workflow` class always executes in the order they appear in this list. 

<pre>
notebook_order = [
    "Step_0_Initialize.ipynb",
  ...
    "Step_6_Evaluate.ipynb"
    ]
</pre>

If you wish to change the running order or add/remove steps, you can do so by editing this list.

#### Variables to Set
This parameter is of type dict that is converted into additional parameters that are injected into the notebooks at run-time. The key value will become the variable name.

<pre>
variables_to_set={
    "message": "Successfully passed in parameters from Workflow.ipynb!",
   ...
    "repo_config": {'repo_type': 'files', 'path': './sample_data'}
    }
</pre>

Note that this format is likely to change to better support passing different parameters into individual steps.

## DataRepo
The DataRepo class provides an abstraction for locating data to use within the steps of the workflow. For example, in the above `variables_to_set` specification, there is a config json string `repo_config` that indicates to pull data from a directory of files located at the given path. At this time, only files and S3 buckets are implemented:

Config for using files, in this case from the local sample_data folder:
<pre>
repo_config = {
        'repo_type': 'files',
        'path': './sample_data'
        }
</pre>

Config for using S3 Bucket where the bucket name, access key id, and s3 secret are pulled from environment variables:
<pre>
repo_config = {
        'repo_type': 's3',
        'bucket': os.getenv("S3_BUCKET"),
        'aws_access_key_id': os.getenv("S3_ACCESS_KEY_ID"),
        'aws_secret_access_key': os.getenv("S3_SECRET_KEY")
        }
</pre>

Below is an example of using the DataRepo to load news content from either of the above:
<pre>
from opentldr import KnowledgeGraph, DataRepo

kg = KnowledgeGraph()
cr = DataRepo(kg, repo_config)

for uid in cr.importContentData():
    print ("Loaded Content: {uid}".format(uid=uid))
</pre>
This will create a DataRepo `cr` that writes to the KnowledgeGraph `kg` from the parsed Content configured above. The return value is a list of the uids of Content nodes created (note Source nodes would be created if needed but not returned here).


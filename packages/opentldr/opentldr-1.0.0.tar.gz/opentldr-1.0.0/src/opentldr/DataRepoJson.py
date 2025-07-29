from .DataRepo import AbstractDataRepo
from .KnowledgeGraph import KnowledgeGraph
from .Domain import *
from .log import log

import os
import json

class DataRepoJsonFiles(AbstractDataRepo):
    '''
    Reads a single .json text file from the path and populates the KG using it.
    This is a great way to export checkpoints for a KG and re-import them later.
    '''

    def __init__(self, kg:KnowledgeGraph, filename:str):
        self.kg=kg
        self.filename = filename
        self.verify()


    def verify(self):

        path = self.filename

        # ensure path points to a readable file
        if not os.path.exists(path):
            raise ValueError ("Cannot reach path: {path}".format(path=path))
        
        if os.path.isdir(path):
            raise ValueError ("Path ({path}) is a directory, looking for a .json file.".format(path=path))

        if not os.access(path,os.R_OK):
            raise ValueError("Cannot read file at {path}".format(path=path))
        
        with open(path) as f:
            self.data = json.load(f)


    def describe(self) -> str:
        return "JSON File (path = '{path}')".format(path=self.ingest_path)  


    def importAll(self) -> dict:
        out:dict={}
        out.update(self.importReferenceData())
        out.update(self.importActiveData())
        out.update(self.importRequestData())
        out.update(self.importFeedbackData())
        out.update(self.importEvaluationData())
        return out
    

    def importReferenceData(self) -> dict:
        log.info("Importing Reference Data from JSON File...")
        node_look_up:dict={}

        # Import Reference Nodes
        node_uids:list[str] = []
        for ref_node_json in self.data['reference']['nodes']:
            ref_node = ReferenceNode.from_json(ref_node_json)
            ref_node.save()
            node_uids.append(ref_node.uid)
            node_look_up[ref_node.uid]=ref_node
        log.info("Imported {c} Reference Nodes.".format(len(node_uids)))

        # Import Reference Edges
        edge_uids:list[str] = []
        for ref_edge_json in self.data['reference']['edges']:
            ref_edge = ReferenceEdge.from_json(ref_edge_json)
            # TODO: set the to/from uids into neomodel object
            ref_edge.save()
            edge_uids.append(ref_edge.uid)
        log.info("Imported {c} Reference Edges.".format(len(edge_uids)))

        return {"ReferenceNodes":node_uids, "ReferenceEdges":edge_uids}
    

    def importRequestData(self) -> list[str]:
        log.info("Importing Requests from File System...")

        path = self.ingest_path
        alt_path = os.path.join(self.ingest_path,"requests")
        if os.path.exists(alt_path) and os.path.isdir(alt_path) and os.access(alt_path,os.R_OK):
            log.debug("Found data type directory in specified repo path.")
            path=alt_path

        default_source_name = "File System Directory:{path}".format(path=path)      # TODO: Never used.  Delete.
        list_of_uids = []

        # read in each text file from directory
        for filename in os.listdir(path):

            # ignore anything but files that end in .txt
            if os.path.splitext(filename)[1] != ".txt" or not os.path.isfile(os.path.join(path, filename)):
                continue

            full_path=os.path.join(path, filename)
            with open(full_path) as f:
                text = f.read()
                request=self.importTextRequest(kg=self.kg, text=text)       # TODO: importTextRequest never defined
                list_of_uids.append(request.uid)
                log.info("Imported: {data}".format(data=request.to_text()))

        return list_of_uids

    def importActiveData(self) -> list[str]:
        log.info("Importing Active Data from File System...")
        path = self.ingest_path
        alt_path = os.path.join(self.ingest_path,"active")
        if os.path.exists(alt_path) and os.path.isdir(alt_path) and os.access(alt_path,os.R_OK):
            log.debug("Found data type directory in specified repo path.")
            path=alt_path
        default_source_name = "File System Directory:{path}".format(path=path)
        list_of_uids = []

        # read in each text file from directory
        for filename in os.listdir(path):
            full_path=os.path.join(path, filename)

            # ignore anything but files that end in .txt
            if os.path.splitext(filename)[1] != ".txt" or not os.path.isfile(full_path):
                continue

            with open(full_path) as f:
                text = f.read()
                url="file://{path}".format(path=os.path.abspath(full_path))
                content=self.importTextContent(kg=self.kg, text=text, url=url, default_source_name=default_source_name)  # TODO: importTextRequest never defined
                list_of_uids.append(content.uid)
                log.info("Imported: {data}".format(data=content.to_text()))

        return list_of_uids
    
    def importFeedbackData(self) -> list[str]:
        message:str = "Importing MongoDB Feedback Data is not implemented yet."
        log.error(message)
        raise NotImplementedError(message)

    def importEvaluationData(self) -> list[str]:
        message:str = "Importing MongoDB Evaluation Data is not implemented yet."
        log.error(message)
        raise NotImplementedError(message)
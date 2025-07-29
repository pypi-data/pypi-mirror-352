from .AbstractDataRepo import AbstractDataRepo
from .Domain import jsonToKg, dictToKg
from .KnowledgeGraph import KnowledgeGraph
from .log import log

import os
import json


class FileSystemDataRepo(AbstractDataRepo):
    '''
    Reads all the text files in the provided directory path. Creates a Source node for the directory and parses the text files.
    This extracts lines with property definitions (e.g., "date: 05/14/1960 08:00PM") and puts the rest into the text body.
    Creates a Content node, for each file and adds it to the knowledge graph.
    '''

    def __init__(self, kg:KnowledgeGraph, ingest_path="."):     # TODO: "." seems like a bad default. "files" would be better.
        self.kg=kg
        self.ingest_path = ingest_path
        self.files=self.getAllFiles(ingest_path)


    def describe(self) -> str:
        return "File system at ('{path}') contains {n} files.".format(path=self.ingest_path, n=len(self.files))  

    @classmethod
    def getAllFiles(cls,current:str) -> list[str]:
        if os.path.exists(current) and os.access(current,os.R_OK):
            if os.path.isdir(current):
                list=[]
                for child in os.listdir(current):
                    full_path=os.path.join(current, child)
                    #print(full_path)
                    list.extend(cls.getAllFiles(full_path))
                return list
            else:
                return [current]
        else:
            if not os.path.exists(current):
                log.debug("Doesn't exist: {name}.".format(name=current))
            
            if not os.access(current,os.R_OK):
                log.warning("Cannot read: {name}.".format(name=current))
            return []    

    # TODO: Move repeated method to superclass
    def _importByClass(self,raw:dict,clazz:str) -> list[str]:
        list_of_uids=[]
        if clazz in raw:
            for item in raw[clazz]:
                item['class']=clazz
                o = dictToKg(self.kg,item)
                list_of_uids.append(o.uid)
        return list_of_uids

    def importData(self) -> list[str]:
        log.info("Importing Data from File System...")
        list_of_uids=[]

        # load files by dependency order but each file only once
        imported=[]
        for c in [*self.import_order, ""]:
            if c !="":
                log.debug("Finding files for type {type}.".format(type=c))
            else:
                log.debug("Finding remaining files of unknown class types.")

            for fullpath in self.files:  
                if fullpath not in imported:
                    if c == "" or c in fullpath or c.lower() in fullpath or c.capitalize() in fullpath:
                        imported.append(fullpath)
                        try:
                            extension = os.path.splitext(fullpath)[-1]
                            match extension:

                                case '.txt' | '.text':
                                    log.info("Importing Text File: {path}".format(path=fullpath))
                                    with open(fullpath) as f:
                                        raw=f.read().split('\n---\n')
                                        for part in raw:
                                            ann, text = self.parseAnnotatedText(part)
                                            if not 'class' in ann:
                                                ann['class'] = self.inferDomainClass(fullpath,ann)
                                            if len(text) > 0 and not 'text' in ann:
                                                ann['text']=text
                                            o = dictToKg(self.kg,ann)
                                            list_of_uids.append(o.uid)
                                
                                case '.cql' | '.cypher':
                                    log.info("Importing Cypher File: {path}".format(path=fullpath))
                                    self.kg.cypher_import(fullpath)
                                    list_of_uids.extend(self.clean_up_nodes())
                                
                                case '.json':
                                    log.info("Importing JSON File: {path}".format(path=fullpath))
                                    with open(fullpath) as f:
                                        raw:dict= json.load(f)
                                        for c2 in self.import_order:
                                            added_list=self._importByClass(raw,c2)
                                            list_of_uids.extend(added_list)
                                
                                case _:
                                    log.warning("Skipping unknown-type file: {path}".format(path=fullpath))
                                    continue
                        except Exception as e:
                            log.error("Failed to import file: {}".format(fullpath))
                            log.error("Caused by {}".format(e))
                            
        return list_of_uids

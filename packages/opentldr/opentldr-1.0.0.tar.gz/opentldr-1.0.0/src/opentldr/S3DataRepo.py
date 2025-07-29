from .DataRepo import AbstractDataRepo
from .KnowledgeGraph import KnowledgeGraph
from .Domain import jsonToKg, dictToKg
from .log import log

import boto3
import json
import os
import tempfile

class S3DataRepo(AbstractDataRepo):

    files:list = []

    def __init__(self, kg:KnowledgeGraph, bucket_name:str, aws_access_key_id:str, aws_secret_access_key:str, prefix:str=None) :
        self.kg=kg
        session = boto3.Session( aws_access_key_id, aws_secret_access_key)
        s3 = session.resource('s3')
        self.bucket_name = bucket_name
        self.bucket = s3.Bucket(bucket_name)
        self.prefix = prefix
        for o in self.bucket.objects.all():
            if prefix is None or o.key.startswith(prefix):
                if not o.key.endswith("/"): #skip directories
                    self.files.append(o)


    def describe(self) -> str:
        return "S3 Bucket Content ('{bucket}')".format(bucket=self.bucket_name)

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
        log.info("Importing Data from S3 Bucket...")
        default_source_name = "S3 Bucket:{path}".format(path=self.bucket_name)
        list_of_uids = []

        # load objects by dependency order but each file only once
        imported=[]
        for c in [*self.import_order, ""]:
            if c !="":
                log.debug("Finding objects for type {type}.".format(type=c))
            else:
                log.debug("Finding remaining files of unknown class types.")

            for summary in self.files: 
                if summary.key not in imported:
                    if c == "" or c in summary.key or c.lower() in summary.key or c.capitalize() in summary.key:
                        imported.append(summary.key)
                        extension = "."+summary.key.rsplit(".",1)[-1]
                        url="https://{bucket_name}.s3.amazonaws.com/{object_name}".format(bucket_name=self.bucket_name, object_name=summary.key)
                        text=summary.get()['Body'].read().decode()
                        
                        match extension:
                            case '.txt' | '.text':
                                log.info("Importing Text Object: {path}".format(path=summary.key))
                                raw=text.split('\n---\n')
                                for part in raw:
                                    ann, text = self.parseAnnotatedText(part)
                                    if not 'class' in ann:
                                        ann['class'] = self.inferDomainClass(summary.key,ann)
                                    if len(text) > 0 and not 'text' in ann:
                                        ann['text']=text
                                    o = dictToKg(self.kg,ann)
                                    list_of_uids.append(o.uid)
                            
                            case '.cql' | '.cypher':
                                log.info("Importing Cypher Object: {path}".format(path=summary.key))
                                with tempfile.NamedTemporaryFile(delete=False) as fp:
                                    fp.write(text.encode())  # this should be cypher
                                    fp.close()      # don't delete on close
                                    self.kg.cypher_import(fp.name)
                                    # deletes when exiting block
                                list_of_uids.extend(self.clean_up_nodes())
                            
                            case '.json':
                                log.info("Importing JSON Object: {path}".format(path=summary.key))
                                raw:dict= json.loads(text)
                                for c in self.import_order:
                                    added_list=self._importByClass(raw,c)
                                    list_of_uids.extend(added_list)
                            
                            case _:
                                log.warning("Skipping unknown-type file: {path}".format(path=summary.key))
                                continue
                            
        return list_of_uids

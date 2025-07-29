import os
import re
from abc import ABC, abstractmethod 
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from .KnowledgeGraph import KnowledgeGraph

from .AbstractDataRepo import AbstractDataRepo
from .FileSystemDataRepo import FileSystemDataRepo
from .S3DataRepo import S3DataRepo

from .log import log

class DataRepo(AbstractDataRepo):
    '''
    Factory class to setup any type of DataRepo from the configuration inputs.
    '''
    repo:AbstractDataRepo


    def _configOrEnv(self, key:str, config:dict) -> str:
        value:str=config.get(key)

        # setting in environment to override configurations for automation
        if os.getenv("OVERRIDE_CONTENT_REPO_CONFIGS") is not None:
            value=None

        if value is None:
            value = config.get(key.capitalize())
        if value is None:
            value = os.getenv(key)
        if value is None:
            value = os.getenv(key.capitalize())
        if value is None:
            raise TypeError("No value found for '{key}', which is required.".format(key=key))
        return value


    def __init__(self, kg:KnowledgeGraph, config:dict):
        if config is None:
            log.warn("No config file passed to DataRepo, defaulting to using environment variables.")
            config="{}"

        type = self._configOrEnv("repo_type",config);
        # TODO: The s3/files check here make the "case _" branch unreachable.
        # I recommend deleting the check here.  Making it easier to expand cases below in the future.
        if type is None or type not in ['s3','files']:
            message=("DataRepo factory requires a dictionary structure as a parameter that includes at least a 'repo_type' entry set to one of 's3' or 'files'.")
            log.error(message)
            raise TypeError(message)
        
        match type:
            case "s3":
                bucket_name=self._configOrEnv("bucket",config)
                aws_access_key_id=self._configOrEnv("aws_access_key_id",config)
                aws_secret_access_key=self._configOrEnv("aws_secret_access_key",config)
                prefix=self._configOrEnv("prefix",config)
                self.repo= S3DataRepo(kg,bucket_name=bucket_name, aws_access_key_id=aws_access_key_id, 
                                      aws_secret_access_key=aws_secret_access_key, prefix=prefix)
            case "files":
                ingest_path=self._configOrEnv("path",config)
                self.repo= FileSystemDataRepo(kg,ingest_path=ingest_path)
            case _:
                message:str = "Invalid 'type' config ('{type}').".format(type=type)
                log.error(message)
                raise NotImplementedError(message)

    def importData(self) -> list[str]:
        if self.repo is None:
            log.error("No DataRepo was configured.")
        return self.repo.importData()

    def describe(self) -> str:
        if self.repo is None:
            log.error("No DataRepo was configured.")
        return self.repo.describe()
    
 
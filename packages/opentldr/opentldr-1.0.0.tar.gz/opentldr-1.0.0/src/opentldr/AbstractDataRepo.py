from abc import ABC, abstractmethod 
import re
import json

from .KnowledgeGraph import KnowledgeGraph
from .log import log

class AbstractDataRepo:
    '''
    baseclass for all Data Repositories, includes shared methods and ingest ordering.
    '''
    # knowledgegraph for import/export
    kg:KnowledgeGraph=None

    # order content should be imported to ensure dependencies.
    import_order=[
            "ReferenceNode",
            "ReferenceEdge",
            "Source",
            "Content",
            "User",
            "Request",
            "Feedback",
            "EvalKey"
        ]
  
    @abstractmethod
    def importData(self) -> list[str]:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass

    def __init__(self, kg:KnowledgeGraph):
        self.kg=kg

    @classmethod
    def parseAnnotatedText(cls,text:str ) -> tuple[dict, str]:
        '''
        Parses a string from an annotated text file, extracts the annotations, and
        returns a tuple (dict of metadata , string of non annotation text block).

        Annotations are commented property key : value pairs, such as:
            # uid = 1234\n
            This is a text block.\n
            # name = Chris\n
            Another line.\n
            And one at the end.\n

        Will return ({'uid': '1234', 'name':'Chris}, 'This is a text block.\nAnother line.\nAnd one at the end')    
        '''
        # Identifies a property key
        property_regex=re.compile(r'^#\s*[a-z_]+\s*\:\s*')
        
        content_text=""
        properties={}

        for line in text.splitlines():
            match= property_regex.search(line)
            if match:
                # This line is an annotation
                key = re.sub(r'[#:\s]',"",match.group()).lower()
                value = ''.join(re.split(property_regex,line)).strip()
                properties[key]=value
            else:
                # This line is a text block
                content_text='\n'.join([content_text,line])

        return (properties, content_text.strip())
    
    @classmethod
    def inferDomainClass(cls,full_path:str,annotations:dict) -> str:
        if 'class' in annotations:
            return annotations["class"]
        log.debug("Class was not specified in annotations, attempting to infer from path ({path}).".format(path=full_path))
        path = full_path.lower()
        if 'reference' in path:
            return "ReferenceNode"
        if 'active' in path or 'content' in path or 'article' in path:
            return "Content"
        if 'request' in path or 'query' in path or 'user' in path:
            if 'text' in annotations:
                return "Request"
            if 'name' in annotations:
                return "User"
            # TODO: Nothing is returned if no text and no name
        if 'eval' in path or 'evalkey' in path or 'evaluation' in path:
            return "EvalKey"
        if 'feedback' in path:
            return "Feedback"
        return "UNKNOWN"

    def clean_up_nodes(self) -> list[str]:
        out:list[str]=[]
        for tag in self.import_order:
            log.info("Cleaning up {tag}:".format(tag=tag))
            node_list = self.kg.get_all_nodes_by_tag(tag)
            if node_list is None:
                continue
            for node in node_list:
                node.save() # Updates properties, including uid
                out.append(node.uid)
        log.info("Cleaned {n} nodes.".format(n=len(out)))
        return out

    def exportData(self, path:str):
        pass
import json
from time import perf_counter

from .log import log

# Pull environment variables from .env or os
from dotenv import load_dotenv
load_dotenv()

# disable warning for debugging of frozen packages
# seems to only matter when running under Jupyter
import os
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"]="1"

# For setting the output notebooks to read-only
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWRITE

import papermill as pm

class Workflow:

    def __init__(self, workflow: dict):
        self.workflow=workflow
        self.verify()

    @classmethod
    def from_json(cls,j:str):
        wf:Workflow = cls(json.loads(j))
        return wf
        
    @classmethod
    def from_file(cls,filepath:str):
        j=json.load(open(filepath))
        return cls(j)

    @classmethod
    def from_vars(cls,output_folder:str, notebook_order:list[str], variables:dict):
        workflow = {}
        workflow["Output"] = output_folder
        nblist = []
        for notebook in notebook_order:
            nblist.append([notebook, variables])
        workflow["Notebooks"] = nblist
        return cls(workflow)

    def verify(self):
        '''
        Walk thru the structure of the workflow and ensure it is setup correctly.
        '''
        has_errors:bool=False
        errors:str=""

        # Verify Output
        path=self.workflow["Output"]
        if path is None:
            log.error("'Output' path is set to None.")
            has_errors=True
        elif not os.path.exists(path):
            log.info("'Output' path ({path}) does not exist, creating it...".format(path=path))
            self.ensure_path(path) 
        elif not os.path.isdir(path):
            log.error("'Output' path ({path}) is not a directory.".format(path=path))  
            has_errors=True 
        elif not os.access(path, os.W_OK):
            log.error("'Output' path ({path}) is not writable.".format(path=path))
            has_errors=True

        log.debug("Output config verified.")

        # Verify Common Settings
        if "Common" in self.workflow:
            common_dict=self.workflow["Common"]
            log.debug("Common config exists.")    

        # Verify Notebooks    
        nblist=self.workflow["Notebooks"]
        if nblist is None:
            log.error("'Notebooks' is set to None.")
            has_errors=True

        c = 1
        for step in nblist:
            notebook:str=step[0]
            if not os.path.isfile(notebook):
                log.error("'Notebooks' #{c}: '{notebook}' not exist.".format(c=c,notebook=notebook))
                has_errors=True
            elif not os.access(notebook,os.R_OK):
                log.error("'Notebooks' #{c}: '{notebook}' is not readable.".format(c=c,notebook=notebook))  
                has_errors=True

            params=step[1]
            if params is None:
                log.error("'Notebooks' #{c}: '{notebook}' does not have parameters set.".format(c=c,notebook=notebook))
                has_errors=True
            p=1
            for key, value in params.items():
                if not type(key) == str:
                    log.error("'Notebooks' #{c}: {notebook} Variable #{p}: name '{var}' is not a string value.".format(c=c,notebook=notebook,p=p,var=key))
                    has_errors=True
                p=p+1
            c=c+1
        
        if has_errors:
            raise ValueError("Error in Workflow specification (see errors in log).")
        else:
            log.debug("No errors in verification of workflow specification, exporting a copy to output directory.")
            self.export_workflow(os.path.join(self.workflow["Output"],"workflow.json"))

    def export_workflow(self, filepath:str) ->json:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.workflow, f, ensure_ascii=False, indent=4)

    def ensure_path(self,path):
        '''
        Ensure_path(path) simply creates a directory if it is not there already.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
            log.info("Created output directory: "+path)

    def execute_notebook(self, notebook:str, variables:dict, output_path:str) -> float:
        '''
        Execute_notebook runs a single notebook file in PaperMill returns the run time in seconds
        '''
        try:
            out_notebook:str = os.path.join(output_path,notebook.replace('/',"_"))
            log.debug("Now executing notebook '{notebook}' with params '{params}' and output '{output}'.".format(notebook=notebook,params=variables,output=output_path))

            notebook_working_dir = os.path.dirname(notebook)
            if notebook_working_dir == '': # no directory given
                notebook_working_dir=os.getcwd()

            log.debug("CWD for notebook '{notebook}' set to '{cwd}'.".format(notebook=notebook,cwd=notebook_working_dir))

            step_start=perf_counter()
            pm.execute_notebook(notebook, out_notebook, variables, cwd=notebook_working_dir)
            step_end=perf_counter()

            return (step_end-step_start)
        
        except Exception as e:
            log.error("There was an error executing the notebook ({nb}), please verify the parameters and that the notebook runs successfully on its own.".format(nb=notebook))
            raise e

    def run(self):
        '''
        Run the defined workflow files in order in PaperMill
        '''
        output_path=self.workflow["Output"]
        self.ensure_path(output_path)

        common_params = None
        if "Common" in self.workflow:
            common_params=self.workflow["Common"]

        workflow_start=perf_counter()
        c=1
        for step in self.workflow["Notebooks"]:
            notebook:str=step[0]
            params=step[1]

            if common_params is not None:
                params = params | common_params
                log.debug("Common config exists, combined to {}".format(params)) 


            print("\nStarting Notebook #{c}: {name}".format(c=c,name=notebook))
            time=self.execute_notebook(notebook,params,output_path)
            print("Completed #{c}: {name} in {time} seconds.".format(c=c,name=notebook,time=round(time,2)))

            c=c+1
        workflow_end=perf_counter()
        print("Workflow completed successfully in {time} seconds.".format(time=round(workflow_end-workflow_start,2)))


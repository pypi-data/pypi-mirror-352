import sys

import pytest
from neo4j.exceptions import ClientError

sys.path.insert(0, 'src')

from opentldr import Workflow
from opentldr.Domain import ReferenceNode


NOTEBOOK_DIR = "tests"

def test_create_missing_output():
    with pytest.raises(Exception):
        wf = Workflow({})


def test_create_missing_notebooks():
    with pytest.raises(Exception):
        wf = Workflow({
            "Output": "./temp",
        })


def test_create_missing_vars():
    with pytest.raises(Exception):
        wf = Workflow({
            "Output": "./temp",
            "Notebooks": [f"{NOTEBOOK_DIR}/Step_0.ipynb"],
        })


def test_create_1_step():
    wf = Workflow({
        "Output": "./temp",
        "Notebooks": [(f"{NOTEBOOK_DIR}/Step_0.ipynb", {})],
    })


def test_create_2_steps():
    wf = Workflow({
        "Output": "./temp",
        "Notebooks": [
            (f"{NOTEBOOK_DIR}/Step_0.ipynb", {}),
            (f"{NOTEBOOK_DIR}/Step_1.ipynb", {}),
        ],
    })




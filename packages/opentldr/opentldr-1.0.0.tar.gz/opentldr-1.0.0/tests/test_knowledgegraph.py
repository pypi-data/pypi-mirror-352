import sys

import pytest
from neo4j.exceptions import ClientError

sys.path.insert(0, 'src')

from opentldr import KnowledgeGraph
from opentldr.Domain import ReferenceNode


def test_default_connection():
    kg = KnowledgeGraph()
    assert kg.connect()


def test_run_query():
    kg = KnowledgeGraph()

    rn = kg.add_reference_node(ReferenceNode(text="this is a test"), type="TEST")
    list = kg.cypher_query("MATCH (n:ReferenceNode) return n", "n")
    assert rn in list

    kg.delete_reference_node(rn)
    list = kg.cypher_query("MATCH (n:ReferenceNode) return n", "n")
    assert rn not in list




def test_run_query_params():
    kg = KnowledgeGraph()

    rn = kg.add_reference_node(ReferenceNode(text="this is a test"), type="TEST")
    uid = rn.uid
    list = kg.cypher_query("MATCH (n:ReferenceNode) WHERE n.uid = $uid RETURN n", "n",
                           params={"uid": uid})
    assert rn in list

    kg.delete_reference_node(rn)
    list = kg.cypher_query("MATCH (n:ReferenceNode) WHERE n.uid = $uid RETURN n", "n",
                           params={"uid": uid})
    assert rn not in list


def test_run_query_missing_params():
    kg = KnowledgeGraph()

    rn = kg.add_reference_node(ReferenceNode(text="this is a test"), type="TEST")
    with pytest.raises(ClientError):
        list = kg.cypher_query("MATCH (n:ReferenceNode) WHERE n.uid = $uid RETURN n", "n",
                               params={})           # uid is NOT defined in params


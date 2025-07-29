import os
from dotenv import load_dotenv

import datetime

from neo4j import GraphDatabase
import neomodel as nm

from opentldr.Domain import *
from opentldr.ContentEnrichment import *
from .log import log

load_dotenv()
load_dotenv("{d}/.env".format(d=os.getcwd()))
load_dotenv("{d}/../.env".format(d=os.getcwd()))


def _getenv(variable: str, default: str):
    """
    _getenv(variable, default) attempts to resolve the value of the environment variable specified.
    If it cannot find the variable in the OS or .env (from dotenv package) it will fail over to the
    provided default value while giving a warning to the logging system.
    """
    value: str = os.getenv(variable)
    if value == None:
        log.warning(
            "No environment variable '"
            + variable
            + "' so defaulting to '"
            + default
            + "'."
        )
        return default
    return value


class KnowledgeGraph:
    """
    KnowledgeGraph is the API for OpenTLDR's interface to Neo4j graph database. It attempts to make the
    driver connection using OS, .env, and then default values for connections. This API maps neo4j
    nodes/edges to types specified in the Domain module (using Neomodel OGM and some custom cypher).

    In order to be successful, you will need to have a neo4j server running, reachable on the network,
    and with environment variables (either in OS or .env files) similar to these:

        NEO4J_CONNECTION='neo4j://localhost:7687'
        NEO4J_USERNAME=neo4jUser
        NEO4J_PASSWORD=neo4jPassword
        NEO4J_DATABASE=neo4j

    This class can be used in several different ways, including:
        (1) import opentldr.KnowledgeGraph ... kg=KnowledgeGraph() ... (use kg here) ... kg.close()
        (2) with opentldr.KnowledgeGraph as kg: ... (use kg here, and then it will autoclose)

    """

    # -----------------
    # Setup Methods
    # -----------------

    # Default values come from first of: (1) .env file, (2) os environment, or (3) these hardcoded values
    connection = _getenv("NEO4J_CONNECTION", "neo4j://localhost:7687")
    user = _getenv("NEO4J_USERNAME", "neo4j")
    password = _getenv("NEO4J_PASSWORD", "neo4j")
    database = _getenv("NEO4J_DATABASE", "neo4j")
    driver = GraphDatabase.driver(connection, auth=(user, password))
    nm.config.DRIVER = driver

    def __init__(
        self,
        neo4j_driver=None,
        connection=None,
        user=None,
        password=None,
        database=None,
    ):
        if connection is not None:
            self.connection = connection
        if user is not None:
            self.user = user
        if password is not None:
            self.password = password
        if database is not None:
            self.database = database

        if neo4j_driver is None:
            log.info("Connecting to Neo4J using environment specification.")
            log.info("\tconnection:\t{v}".format(v=self.connection))
            log.info("\tuser:\t\t{v}".format(v=self.user))
            # log.info("\tpassword:\t{v}".format(v=self.password))           # don't display sensitive information
            log.info("\tdatabase:\t{v}".format(v=self.database))
            self.connect()
        else:
            log.info("Using Neo4j driver passed into initialization.")
            self.connect(neo4j_driver)

    def __del__(self):
        if self.driver is not None:
            self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        if self.driver is not None:
            self.driver.close()

    # -----------------
    # General Utility Methods
    # -----------------

    def neo4j_query(self, cql):
        """
        Performs a cypher call to the knowledge base and returns results in the standard neo4j driver format.
        Use this if you are following neo4j documentation, otherwise use cypher_query().
        """
        if self.driver == None:
            self.connect()

        try:
            records, summary, keys = self.driver.execute_query(
                cql,
                database_=self.database,
            )
            log.debug(
                "The query `{query}` returned {records_count} records in {time} ms.".format(
                    query=summary.query,
                    records_count=len(records),
                    time=summary.result_available_after,
                )
            )
            return records, summary
        except Exception as e:
            log.error(e)

    def neomodel_query(self, cypher_query, params: dict = {}):
        """
        Performs a cypher query in the standard neomodel method, which will return a list of lists of neomodel.
        Use this if you are following Neomodel documentation, otherwise use cypher_query().
        """
        if self.driver == None:
            self.connect()

        return nm.db.cypher_query(cypher_query, resolve_objects=True, params=params)

    def connect(self, driver=None):
        """
        Ensures that a connection to Neo4j has been established and is functioning.
        """
        try:
            if driver is None:
                if self.driver is None:
                    driver = GraphDatabase.driver(
                        self.connection, auth=(self.user, self.password)
                    )
                else:
                    driver = self.driver

            log.info("Testing Neo4j Connectivity...")
            driver.verify_connectivity()

            if driver.verify_connectivity:
                log.info("Successfully connected to Neo4J server for KnowledgeGraph.")
            else:
                log.error(
                    "Unable to connect to Neo4J for KnowledgeGraph. Check that Neo4j server is running."
                )
                return False

            log.info("Testing Neo4j Authentication...")
            driver.verify_authentication()

            if driver.verify_authentication:
                log.info("Successfully logged into Neo4J server for KnowledgeGraph.")
            else:
                log.error(
                    "Unable to log in to Neo4J for KnowledgeGraph. Check that your user and password are correct."
                )
                return False

            self.driver = driver
            nm.config.DRIVER = self.driver
            nm.db.set_connection(driver=self.driver)

            return True

        except Exception as e:
            log.error(e)
            log.error(
                "There was an issue connecting to Neo4J server, please verify that it is running and configured correctly."
            )
            raise e

    def getNeo4jDriver(self):
        """
        Returns the Neo4j driver class being used (usually neo4j.GraphDatabase.driver) so that direct neo4j calls can be
        made or it can be passed into other libraries.
        """
        if self.driver is None:
            self.connect()
        return self.driver

    def close(self):
        """
        Shuts down the current connection to neo4j. This should be done at the end of each program / notebook.
        If you use the "with statement" context control, this will be called automatically when the code block ends.
        """
        if self.driver is not None:
            self.driver.close()
        self.driver = None

    def _ensure_saved(self, node: OpenTldrMeta):
        """
        OpenTLDR objects all inherit from the OpenTldrMeta mixin class. They will be assigned a "uid" when they are saved.
        So, we can use this to determine if an object has been saved or not and respond appropriately.
        """
        if node.uid is None:
            log.warning(
                "Nodes must be persisted with node.save() before being connected. Forcing this now."
            )
            return node.save()
        return node

    def get_all_node_uids_by_tag(self, tag: str) -> list[str]:
        """
        Returns the list of uids for the tag specified as a string.
        """
        return self.cypher_query("MATCH (n:{tag}) RETURN n.uid".format(tag=tag))

    def get_all_nodes_by_tag(self, tag: str):
        """
        Returns the list of uids for the tag specified as a string.
        """
        return self.cypher_query("MATCH (n:{tag}) RETURN n".format(tag=tag), "n")

    # -----------------
    # KnowedgeGraph API
    # -----------------

    def cypher_query(
        self, cypher_query, extract_variable=None, params: dict = {}
    ) -> list:
        """
        Performs a cypher query and returns a single simple list of Neomodel objects based on the variable indicated (or first).
        Use this for most OpenTLDR queries because it is much simpler to process for iterating on the results.
        For example: cypher_query("MATCH (a)-[b]->(c) RETURN a,b,c","a") only returns a list of only the "a" results.
        So, cypher_query("MATCH (a)-[b]->(c) RETURN a","a") would give the same result list by dropping the "b" and "c" results.
        Reduce the risk of Cypher injection attacks by passing Cypher parameters in params.
        """
        if self.driver is None:
            log.debug(
                "Cypher Query made before driver created, creating connection driver."
            )
            self.connect()

        results, meta = nm.db.cypher_query(
            cypher_query, resolve_objects=True, params=params
        )

        index = 0
        if extract_variable is not None:
            index = meta.index(extract_variable)
        else:
            if len(meta) > 1:
                log.warning(
                    "cypher_query is defaulting to return the first element of multiple return values in results."
                )

        return [item[index] for item in results]

    def cypher_query_one(self, cypher_query, extract_variable=None, params: dict = {}):
        """
        Performs a query that is intended to LIMIT the return values to one single Neomodel object. This simplifies the processing
        of the query results to consistently only get a single object for the extract_variable, it is undefined which unless you sort them.
        For example: cypher_query_one("MATCH (a)-[b]->(c) RETURN a,b,c","a") returns the FIRST object of result "a".
        So, cypher_query_one("MATCH (a)-[b]->(c) RETURN a LIMIT 1","a") gives the same result (faster).
        Reduce the risk of Cypher injection attacks by passing Cypher parameters in params.
        """
        results = self.cypher_query(cypher_query, extract_variable, params=params)

        # Limits the output to the first actual object (i.e., not a list)
        if results is not None and len(results) > 0:
            return results[0]
        else:
            return None

    def cypher_import(self, filename):
        """
        Processes a text file containing cypher commands and executes them on the KnowledgeGraph.
        """
        count = 0
        with open(filename) as fp:
            lines = fp.readlines()
            for line in lines:
                if len(line.strip()) == 0:
                    continue
                with self.driver.session() as session:
                    session.run(line)
                count = count + 1
        log.info(
            "Imported {count} lines of Cypher from {filename}".format(
                count=count, filename=filename
            )
        )

    def delete_all(self):
        """
        Clears the neo4j graph database.
        """
        self.cypher_query("MATCH(x) DETACH DELETE x")

    def shortest_path(self, start: OpenTldrMeta, end: OpenTldrMeta):
        """
        This is a special cypher command to run neo4j's shortest path algorithm and return the path (list of edges) found.
        We remove EvalKey, Recommendation, Tldr, Source, and User nodes to avoid irrelevant paths that circumvent Reference Data.
        """
        results, meta = self.neomodel_query(
            """
            MATCH path=shortestPath((s)-[*..10]-(e))
            WHERE s.uid='{start_id}'
            AND e.uid='{end_id}'                         
            AND NONE(n IN nodes(path) WHERE 'Recommendation' IN LABELS(n))
            AND NONE(n IN nodes(path) WHERE 'Tldr' IN LABELS(n))
            AND NONE(n IN nodes(path) WHERE 'Source' IN LABELS(n))
            AND NONE(n IN nodes(path) WHERE 'User' IN LABELS(n))
            AND NONE(n IN nodes(path) WHERE 'EvalKey' IN LABELS(n))
            RETURN path
            """.format(start_id=start.uid, end_id=end.uid)
        )

        if len(results) == 0:
            return None
        else:
            return results[0][meta.index("path")]

    def get_by_uid(self, uid: str):
        return self.cypher_query_one(
            "MATCH (n) WHERE n.uid=$uid RETURN n", params={"uid": uid}
        )

    # -----------------
    # Reference Data API
    # -----------------

    ## Reference Nodes in KG are labeled as ReferenceNode

    def add_reference_node(
        self, text: str, type: str, hypothesized: bool = False
    ) -> ReferenceNode:
        """
        Creates a new ReferenceNode object in KG.
        """
        return ReferenceNode(text=text, type=type, hypothesized=hypothesized).save()

    def get_reference_node_by_uid(self, uid: str) -> ReferenceNode:
        """
        Returns a single ReferenceNode as indicated by the uid or None if it does not exist in KG.
        """
        return ReferenceNode.nodes.get_or_none(uid=uid)

    def get_all_reference_nodes(self) -> list[ReferenceNode]:
        """
        Returns a list of all the ReferenceNodes in the KG.
        """
        return self.cypher_query("MATCH (n:ReferenceNode) RETURN n", "n")

    def update_reference_node(self, node: ReferenceNode) -> ReferenceNode:
        """
        Updates the KG with changes to a ReferenceNode properties
        """
        return node.save()

    def delete_reference_node(self, node: ReferenceNode):
        """
        Removes the passed ReferenceNode and the edges connected to them.
        """
        self.cypher_query(
            "MATCH (n:ReferenceNode) WHERE n.uid=$uid DETACH DELETE n",
            params={"uid": node.uid},
        )

    def delete_all_reference_nodes(self):
        """
        Removes all of the ReferenceNode and the edges connected to them.
        """
        self.cypher_query("MATCH (n:ReferenceNode) DETACH DELETE n")

    def get_reference_node_by_uid(self, uid: str) -> ReferenceNode:
        """
        Returns a single ReferenceNode as indicated by the uid or None if it does not exist in KG.
        """
        return ReferenceNode.nodes.get_or_none(uid=uid)

    def get_all_reference_nodes(self) -> list[ReferenceNode]:
        """
        Returns a list of all the ReferenceNodes in the KG.
        """
        return self.cypher_query("MATCH (n:ReferenceNode) RETURN n", "n")

    ## Reference Edges - in KG these are labeled as REFERENCE_EDGE but Neomodel classes are ReferenceEdge

    def add_reference_edge(
        self,
        from_node: ReferenceNode,
        to_node: ReferenceNode,
        text: str,
        type: str,
        hypothesized: bool = False,
    ):
        """
        Adds a ReferenceEdge between two ReferenceNodes. Note these edges are only between ReferenceNodes.
        """
        from_node = self._ensure_saved(from_node)
        to_node = self._ensure_saved(to_node)
        edge = from_node.edges.connect(
            to_node, {"type": type, "text": text, "hypothesized": hypothesized}
        )
        return edge.save()

    def get_reference_edge_by_uid(self, uid: str) -> ReferenceEdge:
        """
        Returns a single ReferenceEdge as indicated by the uid or None if it does not exist in KG.
        """
        return self.cypher_query_one(
            "MATCH (a)-[r:REFERENCE_EDGE]->(b) WHERE r.uid=$uid RETURN r",
            params={"uid": uid},
        )

    def get_all_reference_edges(self) -> list[ReferenceEdge]:
        """
        Returns a list of all of the ReferenceEdges in the KG.
        """
        return self.cypher_query("MATCH (a)-[n:REFERENCE_EDGE]->(b) RETURN n", "n")

    def update_reference_edge(self, edge: ReferenceEdge) -> ReferenceEdge:
        """
        Updates the KG with changes to a ReferenceEdge's properties
        """
        return edge.save()

    def delete_reference_edge(self, edge: ReferenceEdge):
        """
        Removes the ReferenceEdge.
        """
        self.cypher_query(
            "MATCH (a)-[r:REFERENCE_EDGE]->(b) WHERE r.uid=$uid DETACH DELETE r",
            params={"uid": edge.uid},
        )

    def delete_all_reference_edges(self):
        """
        Removes all of the ReferenceEdges from KG.
        """
        self.cypher_query("MATCH (a)-[r:REFERENCE_EDGE]->(b) DETACH DELETE r")

    # =================
    # Active Data
    # =================

    # -----------------
    # Source Nodes - refer to the origin of content
    # -----------------

    def add_source(self, name: str) -> Source:
        """
        Creates new Source node, or if one by the same name already exists it reuses it.
        """
        source = Source.nodes.get_or_none(name=name)
        if source is None:
            source = Source(name=name).save()
        else:
            log.warning(
                "Found existing Source node for name {name}, returning pre-existing node.".format(
                    name=name
                )
            )
        return source

    def get_source_by_uid(self, uid: str) -> Source:
        """
        Gets an existing Source node by uid or None if it does not exist
        """
        return Source.nodes.get_or_none(uid=uid)

    def get_source_by_name(self, name: str) -> Source:
        """
        Gets an existing Source node by name or None if it does not exist
        """
        return Source.nodes.get_or_none(name=name)

    def get_all_sources(self) -> list[Source]:
        return Source.nodes

    def update_source(self, node: Source) -> Source:
        """
        Updates the KG with changes to a Source's properties.
        """
        return node.save()

    def delete_source(self, source: Source):
        """
        Removes the passed Source node, its content nodes, and the edges connected to it.
        """
        for c in self.get_content_by_source(source):
            self.delete_content(c)
        return self.delete_source_by_uid(source.uid)

    def delete_source_by_uid(self, uid: str):
        return self.cypher_query(
            """
            MATCH (s:Source) WHERE s.uid=$uid
            DETACH DELETE s""",
            params={"uid": uid},
        )

    def delete_all_sources(self):
        """
        Removes all of the Sources, their content, and the edges connected to them.
        """
        for s in self.get_all_sources():
            self.delete_source(s)

    # -----------------
    # Content Nodes - contain article content and link to their Source
    # -----------------

    def add_content(
        self,
        source: Source,
        type: str,
        url: str,
        date: datetime.date,
        title: str,
        text: str,
    ) -> Content:
        content = Content.nodes.get_or_none(url=url)
        if content is None:
            content = Content(
                url=url, date=date, title=title, text=text, type=type
            ).save()
            content.is_from.connect(source)
        else:
            log.warning(
                "Found existing Content node for url {url}, returning pre-existing node.".format(
                    url=url
                )
            )
        return content

    def get_content_by_uid(self, uid: str) -> Content:
        content = Content.nodes.get_or_none(uid=uid)
        return content

    def get_content_by_title(self, title: str) -> Request:
        return self.cypher_query_one(
            """
            MATCH (c:Content) WHERE c.title=$title 
            RETURN c """,
            "c",
            params={"title": title},
        )

    def get_content_by_url(self, url: str) -> Content:
        content = Content.nodes.get_or_none(url=url)
        return content

    def get_content_by_date(self, date: datetime.date) -> list[Content]:
        content = Content.nodes.get_or_none(date=date)
        return content

    def get_content_by_source(self, source: Source) -> list[Content]:
        return self.get_content_by_source_uid(source.uid)

    def get_content_by_source_uid(self, uid: str) -> list[Content]:
        return self.cypher_query(
            """
            MATCH (s:Source) WHERE s.uid=$uid
            MATCH (c:Content)
            MATCH (c)-[y:IS_FROM]->(s)
            RETURN c """,
            "c",
            params={"uid": uid},
        )

    def get_content_by_recommendation(
        self, recommendation: Recommendation
    ) -> list[Content]:
        return recommendation.get_recommends()

    def get_all_content(self) -> list[Content]:
        content = Content.nodes
        return content

    def delete_content(self, content: Content):
        for e in self.get_entities_by_content(content):
            self.delete_entity(e)
        for k in self.get_evalkeys_by_content(content):
            self.delete_evalkey(k)
        return self.delete_content_by_uid(content.uid)

    def delete_content_by_uid(self, uid: str):
        return self.cypher_query(
            """
            MATCH (c:Content) WHERE c.uid=$uid
            DETACH DELETE c """,
            params={"uid": uid},
        )

    def delete_all_content(self):
        for c in self.get_all_content():
            self.delete_content(c)

    # -----------------
    # Active Data / Entity
    # -----------------

    def add_entity(self, node: Content | Request, text: str, type: str) -> Entity:
        entity = Entity(text=text, type=type).save()
        entity.mentioned_in.connect(node)
        return entity

    def add_refers_to_edge(
        self, entity: Entity, reference: ReferenceNode, confidence=1.0
    ):
        entity.refers_to.connect(reference, {"confidence": confidence})

    def get_entity_by_uid(self, uid: str) -> Entity:
        entities = Entity.nodes.get_or_none(uid=uid)
        return entities

    def get_entity_by_url(self, url: str) -> Entity:
        entities = Entity.nodes.get_or_none(url=url)
        return entities

    def get_entities_by_content(self, content: Content) -> list[Entity]:
        return self.cypher_query(
            """
            MATCH (c:Content) WHERE c.uid=$content_uid
            MATCH (e:Entity)
            MATCH (e)-[y:MENTIONED_IN]->(c)
            RETURN e """,
            "e",
            params={"content_uid": content.uid},
        )

    def get_entities_by_content_uid(self, uid: str) -> list[Entity]:
        return self.cypher_query(
            """
            MATCH (c:Content) WHERE c.uid=$content_uid
            MATCH (e:Entity)
            MATCH (e)-[y:MENTIONED_IN]->(c)
            RETURN e """,
            "e",
            params={"content_uid": uid},
        )

    def get_entities_by_request(self, request: Request) -> list[Entity]:
        return self.cypher_query(
            """
            MATCH (r:Request) WHERE r.uid=$request_uid
            MATCH (e:Entity)
            MATCH (e)-[y:MENTIONED_IN]->(r)
            RETURN e """,
            "e",
            params={"request_uid": request.uid},
        )

    def get_all_entities(self) -> list[Entity]:
        entities = Entity.nodes
        return entities

    def delete_entity(self, node: Entity):
        return self.delete_entity_by_uid(node.uid)

    def delete_entity_by_uid(self, uid: str):
        return self.cypher_query(
            """
            MATCH (e:Entity) WHERE e.uid=$uid
            DETACH DELETE e """,
            params={"uid": uid},
        )

    def delete_all_entities(self):
        return self.cypher_query("""
            MATCH (e:Entity)
            DETACH DELETE e """)

    # -----------------
    # Requests API
    # -----------------

    # -----------------
    # Users
    # -----------------

    def add_user(self, name: str, email: str) -> User:
        user = User.nodes.get_or_none(name=name)
        if user is None:
            user = User(name=name, email=email).save()
        else:
            log.warning(
                "Found existing User node for name {name}, returning pre-existing node.".format(
                    name=name
                )
            )
        return user

    def get_user_by_uid(self, uid: str) -> User:
        user = User.nodes.get_or_none(uid=uid)
        return user

    def get_user_by_name(self, name: str) -> User:
        user = User.nodes.get_or_none(name=name)
        return user

    def get_all_users(self) -> list[User]:
        users = User.nodes
        return users

    def delete_user(self, user: User):
        for r in self.get_requests_by_user(user):
            self.delete_request(r)
        return self.delete_user_by_uid(user.uid)

    def delete_user_by_uid(self, uid: str):
        return self.cypher_query(
            """
            MATCH (u:User) WHERE u.uid=$uid
            DETACH DELETE u""",
            params={"uid": uid},
        )

    def delete_all_users(self):
        for u in self.get_all_users():
            self.delete_user(u)

    # -----------------
    # Requests
    # -----------------

    def add_request(self, title: str, text: str, user: User) -> Request:
        request = Request.nodes.get_or_none(title=title)
        if request is None or request.requested_by.single().uid != user.uid:
            request = Request(title=title, text=text).save()
            request.requested_by.connect(user)
        else:
            log.warning(
                "Found existing Request node for {title}, returning pre-existing node.".format(
                    title=title
                )
            )
        return request

    def get_request_by_uid(self, uid: str) -> Request:
        request = Request.nodes.get_or_none(uid=uid)
        return request

    def get_requests_by_user(self, user: User) -> list[Request]:
        return self.get_requests_by_user_uid(user.uid)

    def get_requests_by_user_uid(self, uid: str) -> list[Request]:
        return self.cypher_query(
            """
            MATCH (u:User) WHERE u.uid=$user_id
            MATCH (q:Request)
            MATCH (q)-[y:REQUESTED_BY]->(u)
            RETURN q """,
            "q",
            params={"user_id": uid},
        )

    def get_request_by_title(self, title: str) -> Request:
        return self.cypher_query_one(
            """
            MATCH (q:Request) WHERE q.title=$title
            RETURN q """,
            "q",
            params={"title": title},
        )

    def get_all_requests(self) -> list[Request]:
        requests = Request.nodes
        return requests

    def delete_request(self, request: Request):
        for e in self.get_entities_by_request(request):
            self.delete_entity(e)
        for t in self.get_tldr_by_request(request):
            self.delete_tldr(t)
        for k in self.get_evalkeys_by_request(request):
            self.delete_evalkey(k)
        return self.delete_request_by_uid(request.uid)

    def delete_request_by_uid(self, uid: str):
        return self.cypher_query(
            """
            MATCH (r:Request) WHERE r.uid=$uid
            DETACH DELETE r """,
            params={"uid": uid},
        )

    def delete_all_requests(self):
        for r in self.get_all_requests():
            self.delete_request(r)

    def get_requests_by_tldr_entry(self, entry: TldrEntry) -> Request:
        return self.cypher_query_one(
            """
            MATCH (e:TldrEntry) WHERE e.uid=$uid
            MATCH (t:Tldr)
            MATCH (q:Request)
            MATCH (e)<-[x:CONTAINS]-(t)-[y:RESPONSE_TO]->(q)
            RETURN q """,
            "q",
            params={"uid": entry.uid},
        )

    # -----------------
    # Workflow Products API
    # -----------------

    # -----------------
    # Recommendations
    # -----------------

    def add_recommendation(
        self, score: float, content: Content, request: Request
    ) -> Recommendation:
        if content.uid is None or request.uid is None:
            log.error(
                "Adding Recommendation requires an existing and saved Content and Request node. Attempting to save them..."
            )
            content.save()
            request.save()

        recommendation = self.get_recommendation(content, request)
        if recommendation is None:
            recommendation = Recommendation(score=score).save()
            recommendation.recommends.connect(content)
            recommendation.relates_to.connect(request)
        else:
            log.warning(
                "Found existing Recommendation node between content and request, returning pre-existing node."
            )
        return recommendation

    def get_recommendation(self, content: Content, request: Request) -> Recommendation:
        return self.cypher_query_one(
            """
            MATCH (q:Request) WHERE q.uid=$request_id
            MATCH (a:Content) WHERE a.uid=$content_id
            MATCH (r:Recommendation)
            MATCH (r)-[x:RECOMMENDS]->(a)
            MATCH (r)-[y:RELATES_TO]->(q)
            RETURN r LIMIT 1 """,
            "r",
            params={"request_id": request.uid, "content_id": content.uid},
        )

    def get_recommendation_by_id(self, uid: str) -> Recommendation:
        recommendation = Recommendation.nodes.get_or_none(uid=uid)
        return recommendation

    def get_recommendations_by_request(self, request: Request) -> list[Recommendation]:
        return self.cypher_query(
            """
            MATCH (q:Request) WHERE q.uid=$request_id
            MATCH (r:Recommendation)
            MATCH (r)-[y:RELATES_TO]->(q)
            RETURN r ORDER BY r.score DESC """,
            "r",
            params={"request_id": request.uid},
        )

    def get_all_recommendations(self) -> list[Recommendation]:
        recommendations = Recommendation.nodes
        return recommendations

    def delete_recommendation(self, recommendation: Recommendation):
        recommendation.delete()

    def delete_all_recommendations(self):
        self.cypher_query("MATCH (r:Recommendation) DETACH DELETE (r)")

    # -----------------
    # Summaries
    # -----------------

    def add_summary(
        self, text: str, content: Content, recommendation: Recommendation = None
    ) -> Summary:
        summary = self.get_summary(content, recommendation)
        if summary is None:
            summary = Summary(text=text).save()
            summary.summarizes.connect(content)
            if recommendation is not None:
                summary.focus_on.connect(recommendation)
        else:
            log.warning("Found existing Summary node, returning pre-existing node.")
        return summary

    def get_summary(
        self, content: Content, recommendation: Recommendation = None
    ) -> Summary:
        # Summaries without recommendations should explictly NOT have recommendations associated with them
        if recommendation is None:
            return self.cypher_query_one(
                """
                MATCH (a:Content) WHERE a.uid=$content_id
                MATCH (s:Summary)
                MATCH (s)-[x:SUMMARIZES]->(a)
                WHERE NOT (s)-[:FOCUS_ON]->()
                RETURN s """,
                "s",
                params={"content_id": content.uid},
            )
        else:
            return self.cypher_query_one(
                """
                MATCH (r:Recommendation) WHERE r.uid=$recommendation_id
                MATCH (a:Content) WHERE a.uid=$content_id
                MATCH (s:Summary)
                MATCH (s)-[x:SUMMARIZES]->(a)
                MATCH (s)-[y:FOCUS_ON]->(r)
                RETURN s """,
                "s",
                params={
                    "recommendation_id": recommendation.uid,
                    "content_id": content.uid,
                },
            )

    def get_summary_by_id(self, uid: str) -> Summary:
        summary = Summary.nodes.get_or_none(uid=uid)
        return summary

    def get_summaries_by_content(self, content: Content) -> list[Summary]:
        return self.cypher_query(
            """
            MATCH (a:Content) WHERE a.uid=$content_id
            MATCH (s:Summary)
            MATCH (s)-[x:SUMMARIZES]->(a)
            RETURN s """,
            params={"content_id": content.uid},
        )

    def get_summaries_by_recommendation(
        self, recommendation: Recommendation
    ) -> list[Summary]:
        return self.cypher_query(
            """
            MATCH (r:Recommendation) WHERE r.uid=$recommendation_id
            MATCH (s:Summary)
            MATCH (s)-[x:FOCUS_ON]->(r)
            RETURN s """,
            "s",
            params={"recommendation_id": recommendation.uid},
        )

    def get_all_summary(self) -> list[Summary]:
        summary = Summary.nodes
        return summary

    def delete_summary(self, summary: Summary):
        summary.delete()

    def delete_all_summaries(self):
        self.cypher_query("MATCH (s:Summary) DETACH DELETE (s)")

    # -----------------
    # Tldr
    # -----------------

    def add_tldr(self, request: Request, date: datetime.date) -> Tldr:
        tldr = self.get_tldr(request, date)
        if tldr is None:
            tldr = Tldr(date=date).save()
            tldr.response_to.connect(request)
        else:
            log.warning(
                "Found existing Tldr node for request on given date, returning pre-existing node."
            )
        return tldr

    def get_tldr(self, request: Request, date: datetime.date) -> Tldr:
        return self.get_tldr_by_uid_and_date(request.uid, date)

    def get_tldr_by_uid(self, uid: str) -> Tldr:
        tldr = Tldr.nodes.get_or_none(uid=uid)
        return tldr

    def get_tldrs_by_date(self, date: datetime.date):
        results = self.cypher_query(
            """
            MATCH (t:Tldr) WHERE t.date=$date
            RETURN t """,
            "t",
            params={"date": date},
        )
        if results is None:
            return None
        else:
            return results[0]

    def get_tldrs_before_date(self, date: datetime.date):
        return self.cypher_query(
            """
            MATCH (t:Tldr) WHERE t.date<$date
            RETURN t """,
            "t",
            params={"date": date},
        )

    def get_tldr_by_request(self, request: Request) -> list[Tldr]:
        return self.get_tldr_by_request_uid(request.uid)

    def get_tldr_by_request_uid(self, request_uid: str) -> list[Tldr]:
        return self.cypher_query(
            """
            MATCH (q:Request) WHERE q.uid=$request_uid
            MATCH (t:Tldr)
            MATCH (t)-[y:RESPONSE_TO]->(q)
            RETURN t """,
            "t",
            params={"request_uid": request_uid},
        )

    def get_tldr_by_uid_and_date(self, request_uid: str, date: datetime.date) -> Tldr:
        return self.cypher_query_one(
            """
            MATCH (q:Request) WHERE q.uid=$request_uid
            MATCH (t:Tldr) where t.date=$date
            MATCH (t)-[y:RESPONSE_TO]->(q)
            RETURN t """,
            "t",
            params={"date": date, "request_uid": request_uid},
        )

    def get_all_tldrs(self) -> list[Tldr]:
        tldrs = Tldr.nodes
        return tldrs

    def delete_tldr(self, tldr: Tldr):
        self.delete_tldr_entries_by_tldr(tldr)
        tldr.delete()

    def delete_all_tldrs(self):
        for tldr in Tldr.nodes:
            self.delete_tldr(tldr)

    # -----------------
    # Tldr Entries
    # -----------------

    def add_entry_to_tldr(
        self,
        tldr: Tldr,
        score: float,
        recommendation: Recommendation,
        summary: Summary,
        content: Content,
    ) -> TldrEntry:
        tldr_entry = TldrEntry(
            link=content.url,
            title=content.title,
            type=content.type,
            score=recommendation.score,
            summary=summary.text,
        ).save()
        tldr_entry.includes.connect(summary)
        tldr_entry.based_on.connect(recommendation)
        tldr.contains.connect(tldr_entry, {"score": score})
        return tldr_entry

    def get_tldr_entry_by_uid(self, uid: str) -> TldrEntry:
        return self.get_entry_by_uid(uid)
    
    def get_entry_by_uid(self, uid: str) -> TldrEntry:
        tldr_entry = TldrEntry.nodes.get_or_none(uid=uid)
        return tldr_entry

    def get_entries_by_tldr(self, tldr: Tldr) -> list[TldrEntry]:
        return self.cypher_query(
            """
            MATCH (t:Tldr) WHERE t.uid=$tldr_id
            MATCH (e:TldrEntry)
            MATCH (t)-[x:CONTAINS]->(e)
            RETURN e ORDER BY e.score DESC""",
            "e",
            params={"tldr_id": tldr.uid},
        )

    def delete_tldr_entry(self, tldr_entry: TldrEntry):
        tldr_entry.delete()

    def delete_tldr_entries_by_tldr(self, tldr: Tldr):
        for tldr_entry in tldr.contains.all():
            self.delete_tldr_entry(tldr_entry)

    # -----------------
    # Feedback
    # -----------------

    def add_feedback_click(self, entry: TldrEntry, date: datetime.date) -> Feedback:
        feedback = self.get_feedback_by_tldr_entry(entry)
        if feedback is None:
            feedback = Feedback(click=date).save()
            feedback.about_entry.connect(entry)
            request = self.get_requests_by_tldr_entry(entry)
            feedback.from_request.connect(request)
        else:
            feedback.click_date = date
            feedback.save()
            log.warning("Updated click date of existing Feedback.")

        return feedback

    def add_feedback_rating(self, entry: TldrEntry, score: float) -> Feedback:
        feedback = self.get_feedback_by_tldr_entry(entry)
        if feedback is None:
            feedback = Feedback(score=score).save()
            feedback.about_entry.connect(entry)
            request = self.get_requests_by_tldr_entry(entry)
            feedback.from_request.connect(request)
        else:
            feedback.score = score
            feedback.save()
            log.warning("Updated scoring of existing Feedback.")

        return feedback

    def get_feedback_by_tldr_entry(self, entry: TldrEntry) -> Feedback:
        return self.cypher_query_one(
            """
            MATCH (f:Feedback)
            MATCH (e:TldrEntry) WHERE e.uid=$uid
            MATCH (f)-[x:ABOUT]->(e)
            RETURN f """,
            "f",
            params={"uid": entry.uid},
        )

    def get_feedback_by_request(self, request: Request) -> list[Feedback]:
        return self.cypher_query(
            """
            MATCH (f:Feedback)
            MATCH (r:Request) WHERE r.uid=$uid
            MATCH (f)-[x:FROM]->(r)
            RETURN f """,
            "f",
            params={"uid": request.uid},
        )

    # -----------------
    # EvalKey Nodes - rubric for evaluation metrics
    # -----------------

    def add_evalkey(
        self, content: Content, request: Request, score: float, text: str
    ) -> EvalKey:
        key = EvalKey(text=text, score=score).save()
        key.key_for_content.connect(content)
        key.key_for_request.connect(request)
        return key

    def get_evalkey_by_uid(self, uid: str) -> EvalKey:
        key = EvalKey.nodes.get_or_none(uid=uid)
        return key

    def get_evalkeys_by_request(self, request: Request) -> list[EvalKey]:
        return self.cypher_query(
            """
            MATCH (q:Request) WHERE q.uid=$request_id
            MATCH (e:EvalKey)-[eq:KEY_FOR_REQUEST]->(q)
            RETURN e """,
            "e",
            params={"request_id": request.uid},
        )

    def get_evalkeys_by_content(self, content: Content) -> list[EvalKey]:
        return self.cypher_query(
            """
            MATCH (c:Content) WHERE c.uid=$content_id
            MATCH (c)<-[ec:KEY_FOR_CONTENT]-(e:EvalKey)
            RETURN e """,
            "e",
            params={"content_id": content.uid},
        )

    def get_evalkey_by_content_and_request(
        self, content: Content, request: Request
    ) -> EvalKey:
        return self.cypher_query_one(
            """
            MATCH (c:Content) WHERE c.uid=$content_id
            MATCH (q:Request) WHERE q.uid=$request_id
            MATCH (c)<-[ec:KEY_FOR_CONTENT]-(e:EvalKey)-[eq:KEY_FOR_REQUEST]->(q)
            RETURN e """,
            "e",
            params={"content_id": content.uid, "request_id": request.uid},
        )

    def get_all_evalkeys(self) -> list[EvalKey]:
        evalkeys = EvalKey.nodes
        return evalkeys

    def delete_evalkey(self, evalKey: EvalKey):
        return self.delete_evalkey_by_uid(evalKey.uid)

    def delete_evalkey_by_uid(self, uid: str):
        return self.cypher_query(
            """
            MATCH (k:EvalKey) WHERE k.uid=$uid
            DETACH DELETE k""",
            params={"uid": uid},
        )

    def delete_all_evalkeys(self):
        for k in self.get_all_evalkeys():
            self.delete_evalkey(k)

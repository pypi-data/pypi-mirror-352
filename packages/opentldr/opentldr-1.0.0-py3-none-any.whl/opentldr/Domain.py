import json
from abc import ABC, abstractmethod 
from datetime import datetime,date

# All of the OpenTLDR Domain classes build on Neomodel as an OGM for Neo4j
import neomodel as nm

# Note change in NeoModel 5.3.0
# from neomodel.cardinality import One, ZeroOrOne, ZeroOrMore, OneOrMore
from neomodel.sync_.cardinality import One, ZeroOrOne, ZeroOrMore, OneOrMore

from .log import log

def jsonToKg(kg,json_string):
    '''
    Hydrate a json string to a Domain object. This requires the "class" attribute to
    determine the correct class type, so it only works on these classes.
    '''
    raw = json.loads(json)
    log.info("Ingesting JSON into an OpenTLDR Domain object and then the KG.")
    print("JSON: ",raw)
    if isinstance(raw,list):
        for item in raw:
            dictToKg(kg,item)
    elif isinstance(raw,dict):
        dictToKg(kg,raw)
    

def dictToKg(kg,data:dict):

    if "class" in data:
        clazz = data["class"]
        data.pop("class")
        obj= globals()[clazz].from_json(kg,json.dumps(data))
        return obj
    else:
        raise TypeError("Cannot detect a class specification in this data. Unable to instantiate object.")


def inferDateFormat(date_string:str) -> date:
    formats=['%m/%d/%y', '%m/%d/%Y', '%m-%d-%y', '%m-%d-%Y', '%Y-%m-%d']
    d:date = None
    for f in formats:
        try:
            d=datetime.strptime(date_string,f)
            return d
        except:
            pass # try try again
    # give up with a nicely formatted date, even if wrong
    log.error("Unable to parse date out of '{date}'.  Returning now.".format(date=date))
    return datetime.now() 


# UTILITY MIX-IN CLASSES

class OpenTldrMeta():
    '''
    OpenTldrMeta is a mixin class that adds a unique id (uid) and JSON property (metadata)
    to a Node or Edge. This is used in every Edge and Node in OpenTLDR and provides an
    interface for PyDantic for data manipulation and JSON.
    '''
    uid=nm.UniqueIdProperty()
    metadata=nm.JSONProperty()
       
    def to_text(self) -> str:
        '''
        to_text() returns a unique, user readable string representing the object.
        '''
        return "uid: {uid}".format(uid=self.uid)


class OpenTldrNode():
    '''
    OpenTldrNode is mixed in to each node class to support json import/export.
    '''
    @classmethod
    def from_json(cls, kg, json_string):
        json_dict=json.loads(json_string)
        if "class" in json_dict:
            json_dict.pop("class")
        if "date" in json_dict:
            json_dict["date"]=inferDateFormat(json_dict["date"])
        node = cls(**json_dict)
        node.from_json_connect(kg, json_dict)
        node.save()
        return node
        
    def to_json(self,kg) -> str:
        data = self.__properties__.copy()
        if "date" in data:
            data["date"]=data["date"].strftime("%m/%d/%Y")
        data["class"]=type(self).__name__
        if "element_id_property" in data:
            data.pop("element_id_property")
        connection = self.to_json_connect(kg, data)
        if connection is not None:
            data.update(connection)
        return json.dumps(data)

    def to_json_connect(self, kg, json_dict) -> dict:
        '''
        Override to_json_connect to insert edge data into the node.
        '''
        return None

    def from_json_connect(self, kg, json_dict):
        '''
        Override from_json_connect to rebuild edge data from serialized node.
        '''
        return None



class OpenTldrEdge():
    '''
    OpenTldrEdge is mixed in to each edge class to support json import/export
    '''

    @abstractmethod
    def get_connection_json(cls) -> dict:
        pass

    @classmethod
    def from_json(cls, kg, json_string):
        json_dict=json.loads(json_string)
        if "class" in json_dict:
            json_dict.pop("class")
        if "date" in json_dict:
            json_dict["date"]=inferDateFormat(json_dict["date"])
        node = cls(**json_dict)
        node.from_json_connect(kg, json_dict)
        node.save()
        return node
        
    def to_json(self,kg) -> str:
        data = self.__properties__.copy()
        if "date" in data:
            data["date"]=data["date"].strftime("%m/%d/%Y")
        data["class"]=type(self).__name__
        if "element_id_property" in data:
            data.pop("element_id_property")
        connection = self.to_json_connect(kg, data)
        if connection is not None:
            data.update(connection)
        return json.dumps(data)

    def to_json_connect(self, kg, json_dict) -> dict:
        '''
        Override to_json_connect to insert edge data into the node.
        '''
        return None


    def from_json_connect(self, kg, json_dict):
        '''
        Override from_json_connect to rebuild edge data from serialized node.
        '''
        return None


    @classmethod
    def from_json(cls, kg, json_string):
        json_dict=json.loads(json_string)
        if "connection" in json_dict:
            connection=json_dict["connection"]

            from_node=kg.get_by_uid(connection["start"])
            #print("FROM: {type}\t{uid}\t{desc}".format(type=type(from_node),uid=from_node.uid,desc=from_node.to_text()))
            
            to_node=kg.get_by_uid(connection["end"])
            #print("to: {type}\t{uid}\t{desc}".format(type=type(to_node),uid=to_node.uid,desc=to_node.to_text()))

            rel=getattr(from_node,connection["relation"])
            if "class" in json_dict:
                json_dict.pop("class")
            json_dict.pop("connection")
            edge= rel.connect(to_node,json_dict)
            edge.save()
            return edge
        else:
            raise TypeError("OpenTldrEdge requires connection data stored in json.")

        
    def to_json(self,kg) -> str:
        data = self.__properties__.copy()
        data["class"]=type(self).__name__
        data["connection"]=self.get_connection_json()
        if "element_id_property" in data:
            data.pop("element_id_property")
        return json.dumps(data)


class OpenTldrText():
    '''
    OpenTldrText is a mixin class that adds the properties of text and type (both are Strings)
    to any Node or Edge. This is used whenever the client stores text in the knowledge graph.
    '''
    text = nm.StringProperty(required=True)
    type = nm.StringProperty(required=True)

    def to_text(self) -> str:
        return "type: {type}\t text: {text}".format(type=self.type,text=self.text)


class CitableNode(nm.StructuredNode):
    '''
    CitableNode is a baseclass for any Node from which we extract entities (e.g., NER),
    we can add a topic embedding, and we need to refer back to the Node from where they were detected.
    '''
    embedding = nm.ArrayProperty(required=False)
    

class Uncertain():
    '''
    Uncertain is a mixin class that adds a confidence value (0.0-1.0) to a Node or Edge.
    This is implemented to store the float value and generate description qualitative
    text clauses for the ranges of this confidence value.
    '''
    confidence = nm.FloatProperty(default=1.0)
    def uncertainty_to_text(self) -> str:
        if self.confidence < 0.05:
            return "with almost no chance"
        if self.confidence >= 0.05 and self.confidence < 0.20:
            return "very unlikely"
        if self.confidence >= 0.2 and self.confidence < 0.45:
            return "unlikely"
        if self.confidence >= 0.45 and self.confidence < 0.55:
            return "with roughly even chance"
        if self.confidence >= 0.55 and self.confidence < 0.8:
            return "likely"
        if self.confidence >= 0.8 and self.confidence < 0.95:
            return "very likely"
        if self.confidence >= 0.55 and self.confidence < 1.0:
            return "with almost certainty"
        return "with certainty"

class Scored():
    '''
    Scored is a mixin class that adds a score value (0.0-1.0) to a Node or Edge.
    This is implemented to store the float value and generate descriptive qualitative
    text clauses for the ranges of this score value.
    '''
    score = nm.FloatProperty(default=-1.0)
    def score_to_text(self) -> str:
        if self.score < 0.0:
            return "unknown"
        if self.score < 0.15:
            return "very low"
        if self.score >= 0.15 and self.score < 0.40:
            return "low"
        if self.score >= 0.4 and self.score < 0.6:
            return "medium"
        if self.score >= 0.6 and self.score < 0.85:
            return "high"
        if self.score >= 0.85 and self.score < 1.0:
            return "very high"
        return "perfect"



# REFERENCE KNOWLEDGE


class ReferenceEdge(nm.StructuredRel, OpenTldrText, OpenTldrMeta, OpenTldrEdge):
    '''
    ReferenceEdge allows for general reference data relationships to be introduced into the 
    knowledge graph and used abstractly (e.g., ontological distance using path finding).
    This uses the OpenTldrText mixin to implement text and type properties.
    '''
    hypothesized = nm.BooleanProperty(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_hypothesized(self) -> bool:
        return self.hypothesized

    def set_hypothesized(self, is_hypothesized:bool):
        self.hypothesized=is_hypothesized

    def get_connection_json(self) -> dict:
        return {
            "start": self.start_node().uid,
            "relation": "edges",
            "end": self.end_node().uid
        }

    def to_text(self) -> str:
        left:ReferenceNode = self.start_node()
        right:ReferenceNode = self.end_node()
        return "{left} -[{relationship}:{type}]-> {right}".format(left=left.text,
                                                           right=right.text,
                                                           relationship=self.text,
                                                           type=self.type)


class ReferenceNode(nm.StructuredNode, OpenTldrText, OpenTldrMeta, OpenTldrNode):
    '''
    ReferenceNode allows for general reference data nodes to be introduced into the
    knowledge graph and used abstractly (e.g., to relate extracted entities to known things).
    This uses the OpenTldrText mixin to implement text and type properties.
    The hypothesized property is a boolean that indicates if this was inferred (e.g., discovered)
    or provided as fact via external reference data (e.g., imported). 
    '''
    hypothesized = nm.BooleanProperty(default=False)

    edges = nm.RelationshipTo('ReferenceNode','REFERENCE_EDGE', model=ReferenceEdge, cardinality=ZeroOrMore)

    def is_hypothesized(self) -> bool:
        return self.hypothesized

    def set_hypothesized(self, is_hypothesized:bool):
        self.hypothesized=is_hypothesized

    def connect_to(self, to_node:'ReferenceNode') -> ReferenceEdge:
        return self.edges.connect(to_node)
    
    def connect(self, to_node:'ReferenceNode', edge:ReferenceEdge):
        self.edges.connect()

    def to_text(self) -> str:
        return "'{text}' of type {type}".format(text=self.text,type=self.type)
    


# Active Data


class Source(nm.StructuredNode, OpenTldrMeta, OpenTldrNode):
    '''
    Source nodes indicate the generator of various content. This may be an author or distributor
    of information. The name property is used to uniquely identify the Source.
    '''
    name = nm.StringProperty(unique_index=True, required=True)


class IsFrom(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    IsFrom edges connect Content nodes to the Source nodes in the knowledge graph.
    '''
    def to_text(self) -> str:
        return "The {content_type} '{content_title}' is from the source {end}.".format(
            content_type= self.start_node().type,
            content_title=self.start_node().title,
            end=self.end_node().name)


class Content(CitableNode, OpenTldrMeta, OpenTldrText, OpenTldrNode):
    '''
    Content nodes represent text-based information, such as a news article or message.
    They include properties for title (String), date (datetime.date), and url (String).
    In OpenTldr Content node urls are used for hyperlinks back to the original material.
    '''
    title = nm.StringProperty(required=True)
    date = nm.properties.DateProperty(required=True)
    url = nm.StringProperty(required=True)

    is_from = nm.RelationshipTo(Source, 'IS_FROM', model=IsFrom, cardinality=One)

    def get_is_from(self) -> Source:
        return self.is_from.single()

    def to_text(self) -> str:
        return "A {content_type} content titled '{content_title}' from {date}.".format(
            content_type= self.type,
            content_title=self.title,
            date=self.date)
    
    def to_json_connect(self, kg, json_dict) -> dict:
        out:dict= {}
        if "source" not in json_dict:
            out["source"]=self.is_from.single().name
        return out

    def from_json_connect(self, kg, json_dict):
        # Ensure there is an is_from relation
        if "source" in json_dict:
            source=kg.get_source_by_name(json_dict["source"])
            if source is None:
                source=kg.add_source(json_dict["source"])
            self.save()
            self.is_from.connect(source)

class MentionedIn(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    MentionedIn edges connects an extracted Entity node to the CitableNode (e.g., Content 
    or Request) that included the reference.
    '''
    def to_text(self) -> str:
        return "The entity '{entity}' is mentioned in the '{title}'.".format(
            entity=self.start_node().text,
            title=self.end_node().title)


class RefersTo(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge, Uncertain):
    '''
    RefersTo edges connects an extracted Entity node to the ReferenceNode that it is believed
    to represent with the uncertainity value provided. 
    '''
    def to_text(self) -> str:
        return "The entity '{entity}' {uncertainty} refers to '{ref}'.".format(
            entity=self.start_node().text,
            ref=self.end_node().text,
            uncertainty=self.uncertainty_to_text())


class Entity(nm.StructuredNode, OpenTldrText, OpenTldrMeta, OpenTldrNode):
    '''
    Entity nodes represent specific things that are "mentioned_in" in Citable nodes 
    (e.g., Content or Requests) that "refers_to" some ReferenceNode information. The text property
    contains the text for the entity identified and the type property expresses what it is.
    The "refers_to" edge can be uncertain (e.g., sematic similarity of text and type consistency). 
    '''
    refers_to=nm.RelationshipTo(ReferenceNode,'REFERS_TO', model = RefersTo, cardinality=ZeroOrMore)  
    mentioned_in = nm.RelationshipTo("CitableNode", 'MENTIONED_IN', model=MentionedIn, cardinality=OneOrMore)

    def get_refers_to(self) -> list[Source]:
        return self.refers_to
    
    def get_mentioned_in(self) -> Source:
        return self.mentioned_in.single()


# Information Request


class User(nm.StructuredNode, OpenTldrMeta, OpenTldrNode):
    '''
    User node represents a client of the OpenTLDR system and has name and email properties (Stings).
    Similar to a Content connecting to a Source, Requests connect to a User (see RequestedBy edge).
    '''
    name = nm.StringProperty(required=True)
    email = nm.StringProperty(required=True)

    def to_text(self) -> str:
        return "The User '{name}' with email '{email}'.".format(
            name=self.name, email=self.email)


class RequestedBy(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    RequestedBy edges connect Request nodes to the User node to reflect who made the request.
    '''

    def to_text(self) -> str:
        return "The request '{request}' was requested by {user}.".format(
            request=self.start_node().title,
            user=self.end_node().name)


class Request(CitableNode, OpenTldrMeta, OpenTldrNode):
    '''
    Request nodes information requests that are made by users to indicate what information they
    are interested in and how to tailor that information for them. A "text" property (String) 
    holds the text of the information request and the "title" property (String) provides a 
    short labels for the request to avoid repeating long request text. The "requested_by" edge
    links each request to one User node.
    '''
    title=nm.StringProperty(required=True)
    text = nm.StringProperty(required=True)

    requested_by = nm.RelationshipTo(User, 'REQUESTED_BY', model=RequestedBy, cardinality=One)

    def get_requested_by(self) -> User:
        return self.requested_by.single()

    def to_text(self) -> str:
        return "The request titled '{title}'.".format(title=self.title)

    def to_json_connect(self, kg, json_dict) -> dict:
        out:dict= {}
        user:User = self.requested_by.single()
        
        if "user" not in json_dict:
            out["user"]=user.name
        if "email" not in json_dict:
            out["email"]=user.email

        return out

    def from_json_connect(self, kg, json_dict):
        # Ensure there is a requested_by relation
        if "user" in json_dict:
            user=kg.get_user_by_name(json_dict["user"])
            if user is None:
                email="unknown"
                if "email" in json_dict:
                    email = json_dict["email"]
                user=kg.add_user(json_dict["user"],email)
            self.save()
            self.requested_by.connect(user)

# Workflow Products | Recommendations and Summaries


class Recommends(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    Recommends edge connects a Recommendation node to the Content node that is being recommended.
    '''
    def to_text(self) -> str:
        return "This has {score} relevance for {content_type} '{content_title}'.".format(
            content_title=self.end_node().title,
            content_type= self.end_node().type,
            score=self.start_node.score_to_text())


class RelatesTo(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    RelatesTo edge connects a Recommendation node to the Request on which it is based.
    '''
    def to_text(self) -> str:
        return "This has {score} relevance to the request '{request}'.".format(
            request= self.end_node().title,
            score=self.start_node().score_to_text())


class Recommendation(nm.StructuredNode, OpenTldrMeta, OpenTldrNode, Scored):
    '''
    Recommendation nodes represent the assertion that a Content node (pointed to by Recommends edge)
    is believed to be relevant to a Request node (pointed to by the RelatesTo edge). The score
    property (float 0.0 - 1.0) indicates how relevant and thus how strong the recommendation.
    '''
    recommends = nm.RelationshipTo(Content, 'RECOMMENDS', model=Recommends, cardinality=One)
    relates_to = nm.RelationshipTo(Request, 'RELATES_TO', model=RelatesTo, cardinality=One)

    def get_recommends(self) -> Content:
        return self.recommends.single()
    
    def get_relates_to(self) -> Request:
        return self.relates_to.single()

    def to_text(self) -> str:
        return "The {content_type} '{content_title}' has {score} relevance to the request '{request}'.".format(
            content_title=self.recommends.single().text,
            content_type= self.recommends.single().type,
            request= self.relates_to.single().title,
            score=self.score_to_text())


class Summarizes(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    Summerizes edges connect a Summary node to the Content node that they summarize.
    '''
    pass


class FocusOn(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge, Uncertain):
    '''
    FocusOn edges connect a Summary node to the Recommendation node that may help inform what
    the most relevant parts of the Summary are with respect to that Recommendation / Request.
    '''
    pass


class Summary(nm.StructuredNode, OpenTldrMeta, OpenTldrNode):
    '''
    Summary node contains text (String property) that is a shortened (ideally tailored) version
    of the Content node connect with the "summaries" edge. The "focus_on" edge connects to the
    Recommendation that may inform how this summary is tailored.
    '''
    text = nm.StringProperty(required=True)
    summarizes = nm.RelationshipTo(Content, 'SUMMARIZES', model=Summarizes, cardinality=One)
    focus_on = nm.RelationshipTo(Recommendation, 'FOCUS_ON', model=FocusOn, cardinality=ZeroOrOne)

    def get_summarizes(self) -> Content:
        return self.summarizes.single()
    
    def get_focus_on(self) -> Recommendation:
        return self.focus_on.single()


# Workflow Products | TLDR


class Includes(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    Includes edges connect a TldrEntry node to a Summary node to indicate that the Summary is
    to be used in that part of the TLDR.
    '''
    pass


class BasedOn(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    BasedOn edges connect a TldrEntry node to a Recommendation node to indicate why that
    entry is being included in the TLDR and may be used for things like ordering the entries
    to show the most recommended first.
    '''
    pass


class TldrEntry(nm.StructuredNode, OpenTldrMeta, OpenTldrNode, Scored):
    '''
    TldrEntry is one record within a TLDR. In general, there is a one-to-one relationship
    between each TldrEntry, Recommendation, and Summary such that each record within a TLDR
    has a score for the Recommendation, a text blurb from the Summary, and a connection back
    to the original Content (from both the Recommendation and Summary).
    '''
    link = nm.StringProperty(required=True)
    title = nm.StringProperty(required=True)
    type = nm.StringProperty(required=False)
    summary=nm.StringProperty(required=True)

    includes = nm.RelationshipTo(Summary, 'INCLUDES', model=Includes, cardinality=ZeroOrOne)
    based_on = nm.RelationshipTo(Recommendation, 'BASED_ON', model=BasedOn, cardinality=ZeroOrOne)

    def get_includes(self) -> Summary:
        return self.includes.single()
    
    def get_based_on(self) -> Recommendation:
        return self.based_on.single()

    def to_text(self) -> str:
        return "The entry summarizes {content_type} '{content_title}' and {score} relevance to the request.".format(
            content_title=self.title,
            content_type= self.type,
            score=self.score_to_text())


class Contains(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge, Scored):
    '''
    Connects a Tldr to each of the TldrEntry objects that makes it up. The assumption
    here is that the score property (float 0.0 - 1.0) on the edge provides a descending ordering for
    the entries connected by these links.
    '''
    pass


class ResponseTo(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    ResponseTo edges connect a Tldr to the Request for which it was generated.
    '''
    pass


class Tldr(nm.StructuredNode, OpenTldrMeta, OpenTldrNode):
    '''
    Tldr nodes represent an instance of the TLDR report for the date (in 'date' property of type
    datetime.date). It is connected to the Request by the ResponseTo edge and a set of TldrEntries
    by "Entries" edges.
    '''
    date = nm.DateProperty(required=True)

    contains = nm.RelationshipTo(TldrEntry, 'CONTAINS', model=Contains, cardinality=ZeroOrMore)
    response_to = nm.RelationshipTo(Request, 'RESPONSE_TO', model=ResponseTo, cardinality=One)

    def get_contains(self) -> list[TldrEntry]:
        return self.contains

    def get_response_to(self) -> Request:
        return self.response_to.single()

    def to_text(self) -> str:
        out:str = "The TLDR for request '{request}' on date {date} includes: ".format(
            request= self.response_to.single().title,
            date=self.date)
        for tldr_entry in self.includes:
            out += "\t{text}\n".format(text=tldr_entry.to_text())
        return out



# FEEDBACK


class FeedbackForEntry(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    Edges connect a Feedback to the TLDR Entry for which it was generated.
    '''
    pass #TODO: complete this methods


class FeedbackForRequest(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    Edges connect a Feedback to the Request for which it was generated.
    '''
    pass #TODO: complete this method


class Feedback(nm.StructuredNode, OpenTldrMeta, OpenTldrNode, Scored):
    '''
    Feedback relates events back to a Request node to TldrEntry node to provide a method for
    storing events (for example giving it stars or logging accessing the source article)
    
    Feedback score ("score" property is float with expected range of 0.0 - 1.0) indicating
    how relevant that entry is with respect to the request. These edges are generally created
    by the UI when the user rates an entry (e.g., clicking on a star rating).

    Feedback clicked ("clicked" property is a date) indicates when the last time the source
    link for the TLDR entry was clicked by the user.
    '''
    click_date = nm.DateProperty(required=False)

    about_entry = nm.RelationshipTo(TldrEntry, 'ABOUT', model=FeedbackForEntry, cardinality=One)
    from_request = nm.RelationshipTo(Request, 'FROM', model=FeedbackForRequest, cardinality=One)
    
    def to_text(self) -> str:   
        click_status = "not clicked"
        if self.click_date is not None:
            click_status= "clicked on {date}".format(date=self.click_date.strftime("%m/%d/%Y"))
        
        rate_status = "unrated"
        if self.score is not None:
            rate_status = "rated as {rate}".format(rate=self.score_to_text())

        return "The feedback is that entry '{entry}' was {rate_status} and {click_status}.".format(
                entry = self.key_for_content.single().to_text(),
                rate_status = rate_status,
                click_status = click_status);
       

# EVALUATION 


class KeyForContent(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    Edges connect a EvaluationKey to a Content node.
    '''
    pass #TODO: complete this method


class KeyForRequest(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    '''
    Edges connect a EvaluationKey to a Request.
    '''
    pass #TODO: complete this method


class EvalKey(nm.StructuredNode, OpenTldrMeta, OpenTldrNode, Scored):
    '''
    EvalKey is an indication of the relationship between a Content (e.g., a news article) and a
    Request (i.e., what the user is interested in). This represents a "correct" tailoring pair.
    This also includes a score and text to help identify what was most relevant in the pair.
    '''
    text = nm.StringProperty(required=True)
    key_for_content = nm.RelationshipTo(Content, 'KEY_FOR_CONTENT', model=KeyForContent, cardinality=One)
    key_for_request = nm.RelationshipTo(Request, 'KEY_FOR_REQUEST', model=KeyForRequest, cardinality=One)

    def to_json_connect(self, kg, json_dict) -> dict:
        out:dict= {}
        if "request" not in json_dict:
            out["request"]=self.key_for_request.single().title
        if "content" not in json_dict:
            out["content"]=self.key_for_content.single().title
        return out

    def from_json_connect(self, kg, json_dict):
        
        request:Request = None
        if "request" in json_dict:
            request=kg.get_request_by_title(json_dict["request"])
            if request is None:
                raise ValueError("Request titled '{req}' was not found in KG, but is required for EvalKey.".format(req=json_dict["request"]))
        else:
            raise ValueError("EvalKey requires a 'request' entry.")
        
        content:Content = None
        if "content" in json_dict:
            content=kg.get_content_by_title(json_dict["content"])
            if content is None:
                raise ValueError("Content titled '{req}' was not found in KG, but is required for EvalKey.".format(req=json_dict["content"]))
        else:
            raise ValueError("EvalKey requires a 'request' entry.")
        
        self.save()
        self.key_for_request.connect(request)
        self.key_for_content.connect(content)


    def to_text(self) -> str:
        return "The relevance of the content '{content}' to the request '{request}' is {amount}, and can be tailored down to '{text}'.".format(
            content = self.key_for_content.single().title,
            request = self.key_for_request.single().title,
            text = self.text,
            amount = self.score_to_text())

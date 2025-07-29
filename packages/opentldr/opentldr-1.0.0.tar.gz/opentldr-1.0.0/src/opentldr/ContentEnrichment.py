from .Domain import *
#from .KnowledgeGraph import KnowledgeGraph

import neomodel as nm

# Document Content

class OrderedEdges(nm.StructuredRel):
    order = nm.IntegerProperty(required=False, default=0)

class SubsectionOf(OpenTldrMeta, OpenTldrEdge, OrderedEdges):
    pass

class AuthoredBy(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge, Uncertain):
    pass

class Enriches(nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    pass
   
class Enrichment(nm.StructuredNode, OpenTldrMeta, OpenTldrNode):
    contains = nm.RelationshipTo('Enrichment','CONTAINS', model=SubsectionOf, cardinality=ZeroOrMore)

class TechnicalPaper(Enrichment):
    title = nm.StringProperty(required=False)
    link = nm.StringProperty(required=False)
    publish_date = nm.DateProperty(required=False)
    author = nm.RelationshipTo(ReferenceNode, 'AUTHORED_BY', model=AuthoredBy, cardinality=ZeroOrMore)
    enriches = nm.RelationshipTo(Content, 'Enriches', model=Enriches, cardinality=ZeroOrOne)

class Section(Enrichment):
    title = nm.StringProperty(required=True)
    url = nm.StringProperty(required=False)

class TextChunk(Entity, Enrichment):
    index = nm.IntegerProperty(required=False)

class Table(Enrichment):
    pass


class Formula(Enrichment):
    pass


class Figure(Enrichment):
    caption = nm.StringProperty(required=False)
    title = nm.StringProperty(required=True)
    description = nm.StringProperty(required=False)
    url = nm.StringProperty(required=False)

# Image Content

class Image(Enrichment):
    title = nm.StringProperty(required=True)
    description = nm.StringProperty(required=False)
    url = nm.StringProperty(required=False)

class ImageSequence(Enrichment):
    pass


# Audio Content

class AudioChunk(Enrichment):
    pass


class AudioSequence(Enrichment):
    pass


# Video Content

class Scene():
    time:int = 0
    frame:Image = None
    audio:AudioChunk = None


class Video(ImageSequence, AudioSequence):
    pass


# Similarity Matrix

class SimilarTo (nm.StructuredRel, OpenTldrMeta, OpenTldrEdge):
    pass

class Similarity (nm.StructuredNode, OpenTldrMeta, OpenTldrNode, Scored):
    similar_to = nm.Relationship(Content,'SIMILAR_TO', model=SimilarTo, cardinality=ZeroOrMore)
    
    def to_text(self) -> str:
        nodes=""
        for node in self.similar_to:
            if len(nodes)!=0:
                nodes=nodes+" AND "
            nodes= nodes + node.title.replace("\n","")
        return "There is a {score} similarity between: {nodes}".format(score=self.score_to_text(),nodes=nodes)
    

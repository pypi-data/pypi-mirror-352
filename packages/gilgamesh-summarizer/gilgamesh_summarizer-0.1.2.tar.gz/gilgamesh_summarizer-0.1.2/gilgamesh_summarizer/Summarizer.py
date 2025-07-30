from rdflib import Graph, Namespace, RDF, RDFS, OWL, term
from unsloth import FastLanguageModel
from transformers import AutoTokenizer
import torch
from typing import List, Dict, Tuple
import rdflib


class Summarizer:
    def __init__(self,kg):
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name="Kwts/OntologySummarizer",
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
        )

        self.kg = kg
        self.results = []
        self.kvpairs = set()
        self.model.eval()
        self.template = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Determine whether the given RDF triple set represents a KeyValuePair. Prove which predicate is the key and which the value. Your answer must have the following form:
Yes/No:<key>:<value>

### Input:
{}

### Response:
"""

    def format_triples(self, node: rdflib.term.URIRef, triples: List[Tuple]) -> str:
        lines = []
        for predicate, obj in triples:
            pred_str = f"<{predicate}>"
            obj_str = f"<{obj}>" if isinstance(obj, rdflib.term.URIRef) else f'"{obj}"'
            lines.append(f"<{node}> {pred_str} {obj_str} .")
        return "\n".join(lines)

    def classify_node(self, triples: str) -> str:
        prompt = self.template.format(triples) + self.tokenizer.eos_token
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=20, do_sample=False)
        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Parse only the last response segment
        if "### Response:" in decoded:
            response = decoded.split("### Response:")[-1].strip().split("\n")[0]
        else:
            response = decoded.strip()
        return response

    def classify_clusters(
        self,
        clusters: List[List[rdflib.term.URIRef]],
        triples_dict: Dict[rdflib.term.URIRef, List[Tuple]]
    ):
        results = {}
        for cluster in clusters:
            for node in cluster:
                if node in triples_dict:
                    if triples_dict.get(node,-1)!=-1:
                        formatted = self.format_triples(node, triples_dict[node])
                        classification = self.classify_node(formatted)
                        results[str(node)] = classification

        for (k,v) in results.items():
            if 'yes' in str(v.lower()) or 'yes'==str(v.lower()):
                tokens = v.split(":")
                key = tokens[1]
                value = tokens[2]
                type = self.__find_type(term.URIRef(k),key,value,triples_dict)
                if type != None:
                    self.kvpairs.add(type)


        self.results = results
        return self.kvpairs

    def remove_classes_and_collect_range_predicates(self, target_uris: set):
        removed_predicates = set()
        graph = self.kg.ontology

        for uri_str in target_uris:
            class_uri = term.URIRef(uri_str[0])

            # Find predicates where the class is used as a range
            for pred in graph.subjects(RDFS.range, class_uri):
                if isinstance(pred, term.URIRef):
                    removed_predicates.add(pred)
                    for triple in list(graph.triples((pred, None, None))):
                        graph.remove(triple)

            # Remove the class definition and related triples
            for triple in list(graph.triples((class_uri, None, None))):
                graph.remove(triple)

            for triple in list(graph.triples((None, None, class_uri))):
                graph.remove(triple)

        return removed_predicates


    def __find_type(self,node,key,value,triples_dict):
        edges = triples_dict.get(node,-1)
        if edges==-1:
            return None
        else:
            type=""
            k=""
            v=""
            for (p,o) in edges:
                if p == RDF.type:
                    type = o
                if key==str(o):
                    k = p
                if value==str(o):
                    v = p

            return (type,k,v)


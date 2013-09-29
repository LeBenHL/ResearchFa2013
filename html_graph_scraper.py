import re

from html5lib.constants import *
from pygraph.classes.digraph import digraph, AdditionError
from pygraph.algorithms.searching import depth_first_search
from pygraph.algorithms.minmax import heuristic_search

state_node_pattern = "[\s]*def ([^\s]*State)\("
#edge_label_pattern = "[\s]*(elif|if) [^\s]* (in|==|is) ([^\s:]*( \| [^:]*)?)"
edge_label_pattern = "[\s]*(elif|if) [^\s]* (in|==|is) ([^:]*):"
else_pattern = "[\s]*else:"
end_node_pattern = "[\s]*self\.state = self\.([^\s]*)"
parse_error_pattern = '.*tokenTypes\["ParseError"\].*'

class UndoFile(file):
  
  def __init__ (self, fileObj):
    self.file = fileObj
    self.prevPos = None

  def readline(self):
    self.prevPos = self.file.tell()
    return self.file.readline()

  def undoReadLine(self):
    self.file.seek(self.prevPos)


def parseGraph():
  graph = digraph()
  parseNodes(graph)
  parseEdges(graph)
  return graph

def parseNodes(graph):
  f = open("tokenizer.py", "r")
  for line in f:
    match = re.match(state_node_pattern, line)
    if match:
      state_node = match.group(1)
      graph.add_node(state_node)

def parseEdges(graph):
  f = UndoFile(open("tokenizer.py", "r"))
  line = f.readline()
  while line:
    match = re.match(state_node_pattern, line)
    if match:
      outgoing_node = match.group(1)
      if outgoing_node == "bogusCommentState":
        #Weird case for bogus Comment State. A '>' character is needed to return to the dataState
        edge = (outgoing_node, "dataState")
        addEdge(graph, edge, ">")
      elif outgoing_node == "markupDeclarationOpenState":
        #If we are doing markup declaration state, just add an edge to the comment state.
        #We probably don't want to go near DOCTYPE and CDATA state
        edge = (outgoing_node, "commentState")
        addEdge(graph, edge, "--")
      elif outgoing_node == "cdataSectionState":
        #Weird Case as well.
        edge = (outgoing_node, "dataState")
        addEdge(graph, edge, "]]>")
      else:
        _parseEdgeLabels(graph, outgoing_node, f)

    line = f.readline()

def _parseEdgeLabels(graph, outgoing_node, f):
  line = f.readline()
  while line:
    match = re.match(state_node_pattern, line)
    if match:
      #We see a new state node! We need to parse new edges
      f.undoReadLine()
      break

    if "self.consumeEntity()" in line:
      #Weird case where we consume an entity and then return back to the corresponding data state
      if outgoing_node == "entityDataState":
        edge = (outgoing_node, "dataState")
        addEdge(graph, edge, "entity;")
      elif outgoing_node == "characterReferenceInRcdataState":
        edge = (outgoing_node, "rcdataState")
        addEdge(graph, edge, "entity;")
      else:
        print "WARNING: Unexpected consume entity for " + outgoing_node

      line = f.readline()
      continue

    match = re.match(edge_label_pattern, line)
    if match:
      label = match.group(3)
      if label.startswith('"') and label.endswith('"'):
        #Evaluate the string if we detect it as a string to strip the quotes and escape chars 
        label = eval(label)
      _parseEdgeEndNodes(graph, outgoing_node, label, f)

      line = f.readline()
      continue

    match = re.match(else_pattern, line)
    if match:
      label = "Anything Else"
      _parseEdgeEndNodes(graph, outgoing_node, label, f)

      line = f.readline()
      continue

    line = f.readline()


def _parseEdgeEndNodes(graph, outgoing_node, label, f):
  line = f.readline()
  while line:
    match = re.match(parse_error_pattern, line)
    if match:
      #Parse Error! We don't want parse errors
      #break
      pass

    match = re.match(edge_label_pattern, line)
    if match:
        #We see a new edge label node! We need to parse new edge end nodes
        f.undoReadLine()
        break

    match = re.match(state_node_pattern, line)
    if match:
      #We see a new state node! Bubble this discovery Up!
      f.undoReadLine()
      break

    if "self.emitCurrentToken()" in line:
      #Weird case where we emit current token and return to the data state
      edge = (outgoing_node, "dataState")
      addEdge(graph, edge, label)

      line = f.readline()
      continue
      

    match = re.match(end_node_pattern, line)
    if match:
      #We see an end node! We found our edge!
      end_node = match.group(1)
      edge = (outgoing_node, end_node)
      addEdge(graph, edge, label)

      line = f.readline();
      continue

    line = f.readline()

def addEdge(graph, edge, label):
  print label
  if graph.has_edge(edge):
    new_label = graph.edge_label(edge) + ", " + label
    graph.set_edge_label(edge, new_label)
  else:
    try:
      graph.add_edge(edge, label=label)
    except AdditionError as e:
      #Something state is not in our graph. Probably random entity things though.
      #Just print error message to log and double check if we should consider entity states
      print "WARNING: " + e.message

def shortestPathToDataState(graph, node):

  def zeroHeuristic(neighbor, goal):
    return 0 

  return heuristic_search(graph, node, "dataState", zeroHeuristic)

def shortestPathFromDataState(graph, node):

  def zeroHeuristic(neighbor, goal):
    return 0 

  return heuristic_search(graph, "dataState", node, zeroHeuristic)

def generateActionList(graph, path):
  prev_node = None
  action_list = []
  for node in path:
    if prev_node:
      label = graph.edge_label((prev_node, node))
      label = label.split(", ")
      action_list.append(label)

    prev_node = node

  return action_list


if __name__ == "__main__":
    graph = parseGraph()
    reachable_nodes = depth_first_search(graph, "dataState")[1]
    for node in reachable_nodes:
      path = shortestPathToDataState(graph, node)
      #print node, generateActionList(graph, path)
    #print "******************************"
    #print "******************************"
    for node in reachable_nodes:
      path = shortestPathFromDataState(graph, node)
      #print node, generateActionList(graph, path)





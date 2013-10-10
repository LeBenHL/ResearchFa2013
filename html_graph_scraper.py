import re
from collections import namedtuple

from html5lib.constants import *
from pygraph.classes.digraph import digraph, AdditionError
from pygraph.algorithms.searching import depth_first_search
from pygraph.algorithms.minmax import heuristic_search

state_node_pattern = "[\s]*def ([^\s]*State)\("
edge_label_pattern = "[\s]*(elif|if) data (in|==|is) ([^:]*):"
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
      if outgoing_node == "markupDeclarationOpenState":
        #If we are doing markup declaration state, just add an edge to the comment state.
        #We probably don't want to go near DOCTYPE and CDATA state
        #TODO BETTER MARKUPDECLARATION STATE
        edge = (outgoing_node, "commentState")
        addEdge(graph, edge, "--")
        edge = (outgoing_node, "markupDeclarationOpenState")
        addEdge(graph, edge, "Anything Else")
      elif outgoing_node == "cdataSectionState":
        #Parsing this is quite difficult, I rather add the edges in by hand
        addEdge(graph, ("cdataSectionState", "dataState"), "]]>")
        addEdge(graph, ("cdataSectionState", "dataState"), "Anything Else")
      elif outgoing_node == "bogusCommentState":
        #Bogus Comment State weirdly formatted too
        addEdge(graph, ("bogusCommentState", "dataState"), ">")
        addEdge(graph, ("bogusCommentState", "dataState"), "Anything Else")
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
        edge = (outgoing_node, "entityDataState")
        addEdge(graph, edge, "Anything Else")
      elif outgoing_node == "characterReferenceInRcdataState":
        edge = (outgoing_node, "rcdataState")
        addEdge(graph, edge, "entity;")
        edge = (outgoing_node, "characterReferenceInRcdataState")
        addEdge(graph, edge, "Anything Else")
      else:
        print "WARNING: Unexpected consume entity for " + outgoing_node

      line = f.readline()
      continue

    match = re.match(edge_label_pattern, line)
    if match:
      label = match.group(3)
      if not label == "EOF": 
        label = _sanitize(label)
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

def _sanitize(label):
  and_appropriate_pattern = '(.*) and appropriate'
  match = re.match(and_appropriate_pattern, label)


  if (label.startswith('"') and label.endswith('"')) or (label.startswith("'") and label.endswith("'")):
    #Evaluate the string if we detect it as a string to strip the quotes and escape chars 
    label = eval(label)
  elif label.startswith('(') and label.endswith(')'):
    if label == '(spaceCharacters | frozenset(("/", ">")))':
      #Hacky. I will just manually set the label when it looks like the above string
      label = "spaceCharacters, '/', ''>'"
    else:
      #If in parens, evaluate it to get the value as a tuple or frozenset and covert it to a string delimited by commas
      label = ', '.join(eval(label))
  elif match:
    #If ends with and appropriate, get rid of the and appropriate line. We don't give a shit about it
    label = match.group(1)

  return label


def _parseEdgeEndNodes(graph, outgoing_node, label, f):
  line = f.readline()
  found_end_node = False
  while line:
    match = re.match(parse_error_pattern, line)
    if match:
      #Parse Error! We don't want parse errors
      #break
      pass

    match = re.match(edge_label_pattern, line)
    if match:
        #We see a new edge label node! We need to parse new edge end nodes
        if not found_end_node:
          #Probably is self edge
          edge = (outgoing_node, outgoing_node)
          addEdge(graph, edge, label)
          #print outgoing_node, label

        f.undoReadLine()
        break

    match = re.match(else_pattern, line)
    if match:
        #We see a new edge label node! We need to parse new edge end nodes
        if not found_end_node:
          #Probably is self edge
          edge = (outgoing_node, outgoing_node)
          addEdge(graph, edge, label)
          #print outgoing_node, label

        f.undoReadLine()
        break

    match = re.match(state_node_pattern, line)
    if match:
      #We see a new state node! Bubble this discovery Up!
      if not found_end_node:
        #Probably is self edge
        edge = (outgoing_node, outgoing_node)
        addEdge(graph, edge, label)
        #print outgoing_node, label
      f.undoReadLine()
      break

    if "self.emitCurrentToken()" in line:
      #Weird case where we emit current token and return to the data state
      edge = (outgoing_node, "dataState")
      addEdge(graph, edge, label)
      found_end_node = True

      line = f.readline()
      continue
      

    match = re.match(end_node_pattern, line)
    if match:
      #We see an end node! We found our edge!
      end_node = match.group(1)
      edge = (outgoing_node, end_node)
      addEdge(graph, edge, label)
      found_end_node = True

      line = f.readline();
      continue

    line = f.readline();

def addEdge(graph, edge, label):
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

Node = namedtuple('Node', ['state', 'path'], verbose=False)
class Queue:
  def __init__(self):
      self.list = []

  def push(self,item):
      self.list.insert(0,item)

  def pop(self):
      return self.list.pop()

  def isEmpty(self):
      return len(self.list) == 0

class Search:

  @staticmethod
  def breadthFirstSearch(problem):
    return Search._generalSearch(problem, Queue());
  
  @staticmethod
  def _generalSearch(problem, fringe):    
    closedSet = set()
    moveList = []
    cost = 0
    fringe.push(problem.getStartState())
    while not fringe.isEmpty():
      node = fringe.pop()
      if (problem.isGoalState(node)):
        path = list(node.path)
        path.reverse()
        print path
      state_tuple = tuple(node.state)
      if state_tuple not in closedSet:
          closedSet.add(state_tuple)
          successors = problem.getSuccessors(node)
          for successor in successors:
              tuple_successor = tuple(successor.state)
              if tuple_successor not in closedSet:
                  fringe.push(successor)
    return node

class IllegalCharacterException(Exception):
  pass

class IllegalActionException(Exception):
  pass


class CommonStringSearchDict(dict):

  def __init__(self, *args):
    dict.__init__(self, args)

  def __getitem__(self, key):
    try:
      return dict.__getitem__(self, key)
    except KeyError:
      raise IllegalCharacterException()

class CommonStringSearchProblem:

  def __init__(self, graph, start_nodes, end_node):
    self.graph = graph
    self.reverse_graph = graph.reverse()
    self.start_nodes = set(start_nodes)
    self.end_node = end_node
    self.html_charset = allActions(graph)

    self.anything_else_characters = dict()
    for node in graph.nodes():
      actions = set()
      for neighbor in self.reverse_graph.neighbors(node):
        actions = actions.union(self.graph.edge_label((node, neighbor)).split(", "))
      self.anything_else_characters[node] = self.html_charset.difference(actions)

  def getStartState(self):
    return Node(set([end_node]), [])

  def isGoalState(self, node):
    return self.start_nodes.issubset(node.state)

  def getSuccessors(self, node):
    successors = []
    for action in self._findAllActions(node.state):
      successors.append(self._takeAction(node, action))
    return successors

  def _takeAction(self, node, action):
    new_state = []
    for html_state in node.state:
      for neighbor in self.reverse_graph.neighbors(html_state):
        edge_label = self.reverse_graph.edge_label((html_state, neighbor))
        actions = set(edge_label.split(", "))
        if "Anything Else" in actions:
          actions.remove("Anything Else")
          actions = actions.union(self.anything_else_characters[neighbor])

        if self._contains(action, actions):
          new_state.append(neighbor)

    return Node(set(new_state), node.path + [action])

  def _contains(self, action, actions):
    return action in actions

  def _findAllActions(self, state):
    actions = set()
    for html_state in state:
      for neighbor in self.reverse_graph.neighbors(html_state):
        edge_label = self.reverse_graph.edge_label((html_state, neighbor))
        action_list = set(edge_label.split(", "))
        if "Anything Else" in action_list:
          action_list.remove("Anything Else")
          action_list = action_list.union(self.anything_else_characters[neighbor])
        actions = actions.union(action_list)

    return actions


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

def allActions(graph):
  actions = []
  for edge in graph.edges():
    if '\'"\'' in graph.edge_label(edge):
      print edge
      print graph.edge_label(edge)
    actions += graph.edge_label(edge).split(", ")

  return set(actions)


if __name__ == "__main__":
    graph = parseGraph()
    #print graph.edge_label(("dataState", "dataState"))
    print allActions(graph)

    reachable_nodes = depth_first_search(graph, "dataState")[1]
    print reachable_nodes
    end_node = "dataState"
    problem = CommonStringSearchProblem(graph, reachable_nodes, end_node)
    Search.breadthFirstSearch(problem).path

    """
    print "SHORTEST PATHS TO DATA STATES"
    reachable_nodes = depth_first_search(graph, "dataState")[1]
    for node in reachable_nodes:
      path = shortestPathToDataState(graph, node)
      print node, generateActionList(graph, path)
    print "******************************"
    print "******************************"
    print "SHORTEST PATHS FROM DATA STATE"
    for node in reachable_nodes:
      path = shortestPathFromDataState(graph, node)
      print node, generateActionList(graph, path)
    """





from pygraph.readwrite.dot import read
from pygraph.algorithms.searching import depth_first_search
from pygraph.algorithms.filters.null import null
import pygraph.classes.digraph

action_to_characters_dict = dict()
action_to_characters_dict["'\\t' U+0009"] = "\\t"
action_to_characters_dict["'\\n' U+000A"] = "\\n"
action_to_characters_dict["'!' U+0021"] = "!"
action_to_characters_dict['charref'] = "charref"
action_to_characters_dict["' ' U+0020"] = " "
action_to_characters_dict["'?' U+003F"] = "?"
action_to_characters_dict['EOF'] = "EOF"
action_to_characters_dict["'/' U+002F"] = "/"
action_to_characters_dict["'\\x0c' U+000C"] = "\\x0c"
action_to_characters_dict["'&lt;' U+003C"] = "<"
action_to_characters_dict["'=' U+003D"] = "="
action_to_characters_dict["'`' U+0060"] = "`"
action_to_characters_dict['lowercase-ascii-letters'] = "a"
action_to_characters_dict["'\\x00' U+0000"] = "'\\x00' U+0000"
action_to_characters_dict['uppercase-ascii-letters'] = "A"
action_to_characters_dict["'&gt;' U+003E"] = ">"
action_to_characters_dict["&quot;'&quot; U+0027"] = "'"
action_to_characters_dict['--'] = "--"
action_to_characters_dict["'&' U+0026"] = "&"
action_to_characters_dict["'-' U+002D"] = "-"
action_to_characters_dict["'&quot;' U+0022"] = '"'


def get_all_characters():
	return action_to_characters_dict.values()

def get_all_actions():
	return action_to_characters_dict.keys()

class StateFilter(null):

	def __call__(self, node, parent):
		if "state" in node:
			return True
		else:
			return False

class PathNeverTraversedException(Exception):
	pass

class IllegalCharacterException(Exception):
	pass

class CommonPathDict(dict):

	def __init__(self, *args):
		dict.__init__(self, args)

	def __getitem__(self, key):
		try:
			return dict.__getitem__(self, key)
		except KeyError:
			raise IllegalCharacterException()


class CommonPathSearch:

	def __init__(self, start_states, graph):
		self.graph = graph
		self.start_states = start_states
		self.paths_traversing = [[]]
		self.end_states = dict()
		for node in graph.nodes():

			anything_else = False
			anything_else_state = None
			all_actions = get_all_actions()

			char_to_end_state_dict = CommonPathDict()
			for neighbor in graph.neighbors(node):

				#Current Input Character emits the character and leaves the state machine in the original state
				if neighbor == '"current-input-character"':
					end_state = node
				else:
					end_state = neighbor

				for action in graph.edge_label((node, neighbor)).replace('"', '').split(","):
					action = action.strip()
					if action == "Anything else":
						anything_else = True
						anything_else_state = end_state
					else:
						try:
							all_actions.remove(action)
						except ValueError:
							print "Tried to remove action:" + action
						char = action_to_characters_dict[action]
						char_to_end_state_dict[char] = end_state

			if anything_else:
				for action in all_actions:
					char = action_to_characters_dict[action]
					char_to_end_state_dict[char] = anything_else_state

			#print node,char_to_end_state_dict
			self.end_states[node] = char_to_end_state_dict


	def find_common_paths(self, number_of_paths):
		searches = []
		for start_state in self.start_states:
			searches.append(CommonPathTraversal(start_state, self))

		while number_of_paths > 0 and len(self.paths_traversing) > 0:
			current_path = self.paths_traversing.pop(0)
			print current_path
			end_state = self.end_state(searches, current_path)
			if not end_state:

				all_chars = get_all_characters()
				for char in all_chars:
					try:
						for search in searches:
							search.process_char(current_path, char)
						self.paths_traversing.append(current_path + [char])
					except IllegalCharacterException:
						continue

			else:
				print current_path, end_state
				number_of_paths -= 1

	def get_end_state(self, start_state, action):
		try:
			return self.end_states[start_state][action]
		except IllegalCharacterException as e:
			#print start_state, action
			raise e


	@staticmethod
	def find_all_actions(traversals, path):
		actions = set()
		for traversal in traversals:
			actions = actions.union(traversal.possible_actions(path))
		return actions

	@staticmethod
	def end_state(searches, path):
		end_states = set()
		for search in searches:
			end_states.add(search.end_state(path))
		if len(end_states) == 1 and '"parse-error"' not in end_states and '"current-input-character"' not in end_states:
			return end_states.pop()
		else:
			return ""

class CommonPathTraversal:

	def __init__(self, start_state, common_path_search):
		self.path_to_end_state_dict = dict()
		self.path_to_end_state_dict[tuple([])] = start_state
		self.common_path_search = common_path_search
		self.start_state = start_state

	def possible_actions(self, path):
		try:
			actions = []
			end_state = self.path_to_end_state_dict[tuple(path)]
			for neighbor in self.get_graph().neighbors(end_state):
				for action in self.get_graph().edge_label((end_state, neighbor)).replace('"', '').split(","):
					actions.append(action.strip())
			return actions
		except KeyError:
			raise PathNeverTraversedException()

	def end_state(self, path):
		try:
			return self.path_to_end_state_dict[tuple(path)]
		except KeyError:
			raise PathNeverTraversedException()

	def process_char(self, path, char):
		start_state = self.path_to_end_state_dict[tuple(path)]
		end_state = self.common_path_search.get_end_state(start_state, char)
		self.path_to_end_state_dict[tuple(path + [char])] = end_state
		print start_state, end_state, char

	def get_graph(self):
		return self.common_path_search.graph


if __name__ == "__main__":
    graph =  read('html-tokenizer.dot')

    #Only find node reachable from the data-state that are state nodes.
    start_states = depth_first_search(graph, '"data-state"', StateFilter())[1]
    
    print start_states
    cps = CommonPathSearch(start_states, graph)
    cps.find_common_paths(1000)



    
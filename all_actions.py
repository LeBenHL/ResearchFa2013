from pygraph.readwrite.dot import read

if __name__ == "__main__":
    graph =  read('html-tokenizer.dot')

    actions = set()

    for edge in graph.edges():
    	for action in graph.edge_label(edge).replace('"', '').split(","):
    		actions.add(action.strip())

    print actions


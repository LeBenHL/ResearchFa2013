from pygraph.readwrite.dot import read
from pygraph.algorithms.searching import depth_first_search
from pygraph.algorithms.filters.null import null

from tokenizer import HTMLTokenizer
from html5lib.constants import tokenTypes

#html_charset = ["\t", "\n", "!", "comma;", " ", "?", "/", "\x0c", "<", "=", "`", "a", "A", ">", "'", "&", "-", '"']
html_charset = ["!", "<", ">", "'", "-", '"']

parser_state_to_state_function_map = dict()
parser_state_to_state_function_map['"after-attribute-name-state"'] = "afterAttributeNameState"
parser_state_to_state_function_map['"after-attribute-value-(quoted)-state"'] = "afterAttributeValueState"
parser_state_to_state_function_map['"after-doctype-name-state"'] = "afterDoctypeNameState"
parser_state_to_state_function_map['"after-doctype-public-identifier-state"'] = "afterDoctypePublicIdentifierState"
parser_state_to_state_function_map['"after-doctype-public-keyword-state"'] = "afterDoctypePublicKeywordState"
parser_state_to_state_function_map['"after-doctype-system-identifier-state"'] = "afterDoctypeSystemIdentifierState"
parser_state_to_state_function_map['"after-doctype-system-keyword-state"'] = "afterDoctypeSystemKeywordState"
parser_state_to_state_function_map['"attribute-name-state"'] = "attributeNameState"
parser_state_to_state_function_map['"attribute-value-(double-quoted)-state"'] = "attributeValueDoubleQuotedState"
parser_state_to_state_function_map['"attribute-value-(single-quoted)-state"'] = "attributeValueSingleQuotedState"
parser_state_to_state_function_map['"attribute-value-(unquoted)-state"'] = "attributeValueUnQuotedState"
parser_state_to_state_function_map['"before-attribute-name-state"'] = "beforeAttributeNameState"
parser_state_to_state_function_map['"before-attribute-value-state"'] = "beforeAttributeValueState"
parser_state_to_state_function_map['"before-doctype-name-state"'] = "beforeDoctypeNameState"
parser_state_to_state_function_map['"before-doctype-public-identifier-state"'] = "beforeDoctypePublicIdentifierState"
parser_state_to_state_function_map['"before-doctype-system-identifier-state"'] = "beforeDoctypeSystemIdentifierState"
parser_state_to_state_function_map['"between-doctype-public-and-system-identifiers-state"'] = "betweenDoctypePublicAndSystemIdentifiersState"
parser_state_to_state_function_map['"bogus-comment-state"'] = "bogusCommentState"
parser_state_to_state_function_map['"bogus-doctype-state"'] = "bogusDoctypeState"
parser_state_to_state_function_map['"character-reference-in-data-state"'] = "entityDataState"
parser_state_to_state_function_map['"character-reference-in-attribute-value-state"'] = "processEntityInAttribute"
parser_state_to_state_function_map['"character-reference-in-rcdata-state"'] = "characterReferenceInRcdata"
parser_state_to_state_function_map['"comment-end-bang-state"'] = "commentEndBangState"
parser_state_to_state_function_map['"comment-end-dash-state"'] = "commentEndDashState"
parser_state_to_state_function_map['"comment-end-state"'] = "commentEndState"
parser_state_to_state_function_map['"comment-start-dash-state"'] = "commentStartDashState"
parser_state_to_state_function_map['"comment-start-state"'] = "commentStartState"
parser_state_to_state_function_map['"comment-state"'] = "commentState"
parser_state_to_state_function_map['"data-state"'] = "dataState"
parser_state_to_state_function_map['"doctype-name-state"'] = "doctypeNameState"
parser_state_to_state_function_map['"doctype-public-identifier-(double-quoted)-state"'] = "doctypePublicIdentifierDoubleQuotedState"
parser_state_to_state_function_map['"doctype-public-identifier-(single-quoted)-state"'] = "doctypePublicIdentifierSingleQuotedState"
parser_state_to_state_function_map['"doctype-state"'] = "doctypeState"
parser_state_to_state_function_map['"doctype-system-identifier-(double-quoted)-state"'] = "doctypeSystemIdentifierDoubleQuotedState"
parser_state_to_state_function_map['"doctype-system-identifier-(single-quoted)-state"'] = "doctypeSystemIdentifierSingleQuotedState"
parser_state_to_state_function_map['"end-tag-open-state"'] = "closeTagOpenState"
parser_state_to_state_function_map['"markup-declaration-open-state"'] = "markupDeclarationOpenState"
parser_state_to_state_function_map['"plaintext-state"'] = "plaintextState"
parser_state_to_state_function_map['"rawtext-end-tag-name-state"'] = "rawtextEndTagNameState"
parser_state_to_state_function_map['"rawtext-end-tag-open-state"'] = "rawtextEndTagOpenState"
parser_state_to_state_function_map['"rawtext-less-than-sign-state"'] = "rawtextLessThanSignState"
parser_state_to_state_function_map['"rawtext-state"'] = "rawtextState"
parser_state_to_state_function_map['"rcdata-end-tag-name-state"'] = "rcdataEndTagNameState"
parser_state_to_state_function_map['"rcdata-end-tag-open-state"'] = "rcdataEndTagOpenState"
parser_state_to_state_function_map['"rcdata-less-than-sign-state"'] = "rcdataLessThanSignState"
parser_state_to_state_function_map['"rcdata-state"'] = "rcdataState"
parser_state_to_state_function_map['"script-data-double-escape-end-state"'] = "scriptDataDoubleEscapeEndState"
parser_state_to_state_function_map['"script-data-double-escape-start-state"'] = "scriptDataDoubleEscapeStartState"
parser_state_to_state_function_map['"script-data-double-escaped-dash-dash-state"'] = "scriptDataDoubleEscapedDashDashState"
parser_state_to_state_function_map['"script-data-double-escaped-dash-state"'] = "scriptDataDoubleEscapedDashState"
parser_state_to_state_function_map['"script-data-double-escaped-less-than-sign-state"'] = "scriptDataDoubleEscapedLessThanSignState"
parser_state_to_state_function_map['"script-data-double-escaped-state"'] = "scriptDataDoubleEscapedState"
parser_state_to_state_function_map['"script-data-end-tag-name-state"'] = "scriptDataEndTagNameState"
parser_state_to_state_function_map['"script-data-end-tag-open-state"'] = "scriptDataEndTagOpenState"
parser_state_to_state_function_map['"script-data-escape-start-dash-state"'] = "scriptDataEscapeStartDashState"
parser_state_to_state_function_map['"script-data-escape-start-state"'] = "scriptDataEscapeStartState"
parser_state_to_state_function_map['"script-data-escaped-dash-dash-state"'] = "scriptDataEscapedDashDashState"
parser_state_to_state_function_map['"script-data-escaped-dash-state"'] = "scriptDataEscapedDashState"
parser_state_to_state_function_map['"script-data-escaped-end-tag-name-state"'] = "scriptDataEscapedEndTagNameState"
parser_state_to_state_function_map['"script-data-escaped-end-tag-open-state"'] = "scriptDataEscapedEndTagOpenState"
parser_state_to_state_function_map['"script-data-escaped-less-than-sign-state"'] = "scriptDataEscapedLessThanSignState"
parser_state_to_state_function_map['"script-data-escaped-state"'] = "scriptDataEscapedState"
parser_state_to_state_function_map['"script-data-less-than-sign-state"'] = "scriptDataLessThanSignState"
parser_state_to_state_function_map['"script-data-state"'] = "scriptDataState"
parser_state_to_state_function_map['"self-closing-start-tag-state"'] = "selfClosingStartTagState"
parser_state_to_state_function_map['"tag-name-state"'] = "tagNameState"
parser_state_to_state_function_map['"tag-open-state"'] = "tagOpenState"

state_to_current_token_map = dict();
state_to_current_token_map['"tag-name-state"'] = {"type": tokenTypes["StartTag"],
                                 "name": "", "data": [],
                                 "selfClosing": False,
                                 "selfClosingAcknowledged": False}
state_to_current_token_map['"before-attribute-name-state"'] = {"type": tokenTypes["EndTag"],
                                 "name": "",
                                 "data": [], "selfClosing": False}
state_to_current_token_map['"self-closing-start-tag-state"'] = {"type": tokenTypes["EndTag"],
                                 "name": "",
                                 "data": [], "selfClosing": False}
state_to_current_token_map['"data-state"'] = {"type": tokenTypes["EndTag"],
                                 "name": "",
                                 "data": [], "selfClosing": False}
state_to_current_token_map['"comment-start-state"'] = {"type": tokenTypes["Comment"], "data": ""}
state_to_current_token_map['"doctype-state"'] = {"type": tokenTypes["Doctype"],
                                     "name": "",
                                     "publicId": None, "systemId": None,
                                     "correct": True}


class StateFilter(null):

	def __call__(self, node, parent):
		if "state" in node:
			return True
		else:
			return False

class CommonStringToSameEndState:

	def __init__(self, start_states):
		self.start_states = start_states
		self.html_strings = [""]

	def find_common_strings(self, number_of_strings):
		parsers = []
		for start_state in self.start_states:
			parsers.append(HTMLParsers(start_state))
		while number_of_strings > 0 and len(self.html_strings) > 0:
			html_string = self.html_strings.pop(0)
			print html_string

			end_state = self.end_state(parsers, html_string)
			if end_state and end_state != "parseError":
				pass
				if html_string == '<!-- "><!-- -->':
					print end_state, html_string
					return

			for char in html_charset:
				self.html_strings.append(html_string + char)


	@staticmethod
	def end_state(parsers, html_string):
		end_states = set()
		for parser in parsers:
			end_state = parser.state_after_parse(html_string)
			end_states.add(end_state)
		if len(end_states) == 1:
			return end_states.pop()
		else:
			return ""


class HTMLParsers:

	def __init__(self, start_state):
		self.start_state = parser_state_to_state_function_map[start_state]

	def state_after_parse(self, string):
		tokenizer = HTMLTokenizer(string)
		tokenizer.state = getattr(tokenizer, self.start_state)
		#print tokenizer.state.__name__
		for token in tokenizer:
			if token and token["type"] == tokenTypes["ParseError"]:
				return "parseError"
		#print
		return tokenizer.state.__name__


if __name__ == "__main__":
    graph =  read('html-tokenizer.dot')

    #Only find node reachable from the data-state that are state nodes.
    #start_states = depth_first_search(graph, '"data-state"', StateFilter())[1]
    #print start_states
    start_states = ['"attribute-value-(double-quoted)-state"', '"data-state"']
    c = CommonStringToSameEndState(start_states)
    c.find_common_strings(10)



    
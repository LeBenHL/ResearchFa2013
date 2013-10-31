from tokenizer import HTMLTokenizer
from html5lib.constants import tokenTypes

start_state_to_string_prefix = dict()
start_state_to_string_prefix['dataState'] = ""
start_state_to_string_prefix['entityDataState'] = "&"
start_state_to_string_prefix['tagOpenState'] = "<"
start_state_to_string_prefix['markupDeclarationOpenState'] = "<!"
start_state_to_string_prefix['commentState'] = "<!--"
start_state_to_string_prefix['commentEndDashState'] = "<!-- Comment -"
start_state_to_string_prefix['commentEndState'] = "<!-- Comment --"
start_state_to_string_prefix['commentEndBangState'] = "<!-- Comment --!"
start_state_to_string_prefix['closeTagOpenState'] = "</"
start_state_to_string_prefix['tagNameState'] = "<img"
start_state_to_string_prefix['beforeAttributeNameState'] = "<img "
start_state_to_string_prefix['attributeNameState'] = "<img src"
start_state_to_string_prefix['beforeAttributeValueState'] = "<img src="
start_state_to_string_prefix['attributeValueDoubleQuotedState'] = '<img src="'
start_state_to_string_prefix['afterAttributeValueState'] = '<img src=""'
start_state_to_string_prefix['selfClosingStartTagState'] = '<img src=""/'
start_state_to_string_prefix['attributeValueUnQuotedState'] = '<img src=Hi'
start_state_to_string_prefix['attributeValueSingleQuotedState'] = "<img src='"
start_state_to_string_prefix['afterAttributeNameState'] = "<img src "
start_state_to_string_prefix['bogusCommentState'] = "<?"


class HTMLParser:

  def __init__(self, start_state):
    self.start_state = start_state


  def state_after_parse(self, html_string):
    full_string = start_state_to_string_prefix[self.start_state] + html_string
    tokenizer = HTMLTokenizer(full_string)
    for token in tokenizer:
      pass
    return tokenizer.lastState.__name__

def print_end_states(start_states, html_string):
  parsers = []
  for start_state in start_states:
    parsers.append(HTMLParser(start_state))
  for parser in parsers:
    print "Start State: %s, End State: %s" % (parser.start_state, parser.state_after_parse(html_string))


if __name__ == "__main__":
    #start_states = ['dataState', 'entityDataState', 'tagOpenState', 'markupDeclarationOpenState', 'commentState', 'commentEndDashState', 'commentEndState', 'commentEndBangState', 'closeTagOpenState', 'tagNameState', 'beforeAttributeNameState', 'attributeNameState', 'beforeAttributeValueState', 'attributeValueDoubleQuotedState', 'afterAttributeValueState', 'selfClosingStartTagState', 'attributeValueUnQuotedState', 'attributeValueSingleQuotedState', 'afterAttributeNameState', 'bogusCommentState']
    #html_string = "hey--\'\"-->nbsp;"
    #print_end_states(start_states, html_string)
    tokenizer = HTMLTokenizer("<textarea>Hey Ben</junk>")
    iter = tokenizer.__iter__()
    print iter.next()
    tokenizer.state = tokenizer.rcdataState
    print iter.next()
    print tokenizer.state.__name__
    print iter.next()




    
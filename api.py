from jsonrpc import dispatcher
import time
import pexpect
from collections import defaultdict
import re


def parse_parser_results(response_byte):
    # """ 
    # Process the result returned by Stanford NLP Toolkit
    # """
    # example:
    # > I love you
    # > Sentence #1 (3 tokens):
    # > i love you
    # > [Text=i CharacterOffsetBegin=0 CharacterOffsetEnd=1 PartOfSpeech=FW]
    # > [Text=love CharacterOffsetBegin=2 CharacterOffsetEnd=6 PartOfSpeech=VBP]
    # > [Text=you CharacterOffsetBegin=7 CharacterOffsetEnd=10 PartOfSpeech=PRP]
    # > (ROOT
    # >   (S
    # >     (NP (FW i))
    # >     (VP (VBP love)
    # >       (NP (PRP you)))))
    # > root(ROOT-0, love-2)
    # > nsubj(love-2, i-1)
    # > dobj(love-2, you-3)
    result = {}
    response = response_byte.decode('utf-8').strip().split('\n')
    raw_sentence = response[2]
    length = len(raw_sentence.split(' '))
    parsetree_str = " ".join([node.strip() for node in response[3+length:-length-1]])
    result["parsetree"] = parsetree_str

    return result


class StanfordCoreNLP(object):
    """
    Command-line interaction with Stanford's CoreNLP java utilities.
    Can be run as a JSON-RPC server or imported as a module.
    """
    def __init__(self):
        """
        Checks the location of the jar files.
        Spawns the server as a process.
        """

        java_path = "/usr/lib/jvm/java-1.8.0-sun-1.8.0.91/bin/java"
        classname = "edu.stanford.nlp.pipeline.StanfordCoreNLP"
        annotators = "tokenize,ssplit,parse"
        
        # spawn the server
        start_corenlp = '{java_path} -cp "*" -Xmx2g {classname} -annotators {annotators}'.format(java_path=java_path, classname=classname, annotators=annotators)
        print("initiating NLP:", start_corenlp)
        self.corenlp = pexpect.spawn(start_corenlp)
        self.corenlp.expect("NLP>")
    
    def _parse(self, text):
        """
        This is the core interaction with the parser.
        
        It returns a Python data-structure, while the parse()
        function returns a JSON object
        """
        while True:
            try:
                self.corenlp.read_nonblocking (4000, 0.3)
            except pexpect.TIMEOUT:
                break
        self.corenlp.sendline(text)
        self.corenlp.expect("NLP>")
        # bytes to utf-8
        return self.corenlp.before

    def parse(self, text):
        """ 
        This function takes a text string, sends it to the Stanford parser,
        reads in the result, parses the results and returns a list
        with one dictionary entry for each parsed sentence, in JSON format.
        """
        response = self._parse(text)
        response_json = parse_parser_results(response)
        return response_json


nlp = StanfordCoreNLP()
@dispatcher.add_method
def parse(text):
    result = nlp.parse(text)
    return result

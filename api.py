from jsonrpc import dispatcher
import time
import pexpect
from collections import defaultdict
import re
import sys


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
    response = response_byte.decode('utf-8').strip()
    response = response.replace('\r\n', '\n')
    PATTERN = "\(ROOT\n[\w\W]+\)\n\n"
    parsertree = re.search(PATTERN, response).group(0)
    parsertree = re.sub(" +", " ", parsertree)
    parsertree = parsertree.replace("\n", "")
    result["parsetree"] = parsertree

    return result


def parse_lemma_results(response_byte):
    # """ 
    # Process the result returned by Stanford NLP Toolkit
    # """
    # example:
    # > I ate apple
    # > Sentence #1 (3 tokens):
    # > I ate apple
    # > [Text=i CharacterOffsetBegin=0 CharacterOffsetEnd=1 PartOfSpeech=LS Lemma=i]
    # > [Text=eat CharacterOffsetBegin=2 CharacterOffsetEnd=5 PartOfSpeech=VB Lemma=eat]
    # > [Text=apple CharacterOffsetBegin=6 CharacterOffsetEnd=11 PartOfSpeech=NN Lemma=apple]
    result = {}
    response = response_byte.decode('utf-8').strip()
    response = response.replace('\r\n', '\n')
    PATTERN = "Lemma=(.*?)\]"
    lemma = re.findall(PATTERN, response)
    result["lemma"] = " ".join(lemma)

    return result


class StanfordCoreNLP(object):
    """
    Command-line interaction with Stanford's CoreNLP java utilities.
    Can be run as a JSON-RPC server or imported as a module.
    """
    def __init__(self, mode):
        """
        Checks the location of the jar files.
        Spawns the server as a process.
        """

        java_path = "/usr/lib/jvm/java-1.8.0-sun-1.8.0.91/bin/java"
        classname = "edu.stanford.nlp.pipeline.StanfordCoreNLP"
        if mode == "parse":
            prop_file = "parse.properties"
        elif mode == "lemma":
            prop_file = "lemma.properties"
        else:
            print("only support parse and lemma, %s not supported" % mode)
            sys.exit(1)

        # spawn the server
        start_corenlp = '{java_path} -cp "*" -Xmx2g {classname} -props {propsfile}'.format(java_path=java_path, classname=classname, propsfile=prop_file)
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

    def lemma(self, text):
        """ 
        This function takes a text string, sends it to the Stanford parser,
        reads in the result, parses the results and returns a list
        with one dictionary entry for each parsed sentence, in JSON format.
        """
        response = self._parse(text)
        response_json = parse_lemma_results(response)
        return response_json

thismodule = sys.modules[__name__]
thismodule.nlp = None
@dispatcher.add_method
def parse(text):
    nlp = thismodule.nlp
    result = nlp.parse(text)
    return result

@dispatcher.add_method
def lemma(text):
    thismodule.nlp
    result = nlp.lemma(text)
    return result

def init_nlp(mode):
    thismodule.nlp = StanfordCoreNLP(mode)

# Generated from Joda.g4 by ANTLR 4.13.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,7,41,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,1,0,1,0,1,0,1,0,1,1,1,1,5,1,22,8,1,10,1,12,1,25,9,1,1,2,1,
        2,1,3,1,3,1,4,1,4,1,5,1,5,1,6,4,6,36,8,6,11,6,12,6,37,1,6,1,6,0,
        0,7,1,1,3,2,5,3,7,4,9,5,11,6,13,7,1,0,4,3,0,65,90,95,95,97,122,5,
        0,43,43,45,57,65,90,95,95,97,122,1,0,48,57,3,0,9,10,13,13,32,32,
        42,0,1,1,0,0,0,0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,
        11,1,0,0,0,0,13,1,0,0,0,1,15,1,0,0,0,3,19,1,0,0,0,5,26,1,0,0,0,7,
        28,1,0,0,0,9,30,1,0,0,0,11,32,1,0,0,0,13,35,1,0,0,0,15,16,5,85,0,
        0,16,17,5,84,0,0,17,18,5,67,0,0,18,2,1,0,0,0,19,23,7,0,0,0,20,22,
        7,1,0,0,21,20,1,0,0,0,22,25,1,0,0,0,23,21,1,0,0,0,23,24,1,0,0,0,
        24,4,1,0,0,0,25,23,1,0,0,0,26,27,5,43,0,0,27,6,1,0,0,0,28,29,5,45,
        0,0,29,8,1,0,0,0,30,31,5,58,0,0,31,10,1,0,0,0,32,33,7,2,0,0,33,12,
        1,0,0,0,34,36,7,3,0,0,35,34,1,0,0,0,36,37,1,0,0,0,37,35,1,0,0,0,
        37,38,1,0,0,0,38,39,1,0,0,0,39,40,6,6,0,0,40,14,1,0,0,0,3,0,23,37,
        1,6,0,0
    ]

class JodaLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    UTC_KEYWORD = 1
    LONG_TZ_IDENTIFIER = 2
    PLUS = 3
    MINUS = 4
    COLON = 5
    DIGIT = 6
    WS = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'UTC'", "'+'", "'-'", "':'" ]

    symbolicNames = [ "<INVALID>",
            "UTC_KEYWORD", "LONG_TZ_IDENTIFIER", "PLUS", "MINUS", "COLON", 
            "DIGIT", "WS" ]

    ruleNames = [ "UTC_KEYWORD", "LONG_TZ_IDENTIFIER", "PLUS", "MINUS", 
                  "COLON", "DIGIT", "WS" ]

    grammarFileName = "Joda.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None



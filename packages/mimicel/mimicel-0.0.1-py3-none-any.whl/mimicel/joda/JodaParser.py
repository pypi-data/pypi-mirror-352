# Generated from Joda.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,7,21,2,0,7,0,2,1,7,1,2,2,7,2,1,0,1,0,1,0,3,0,10,8,0,1,1,1,1,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,0,0,3,0,2,4,0,1,1,0,3,4,19,0,9,1,
        0,0,0,2,11,1,0,0,0,4,13,1,0,0,0,6,10,5,1,0,0,7,10,3,2,1,0,8,10,3,
        4,2,0,9,6,1,0,0,0,9,7,1,0,0,0,9,8,1,0,0,0,10,1,1,0,0,0,11,12,5,2,
        0,0,12,3,1,0,0,0,13,14,7,0,0,0,14,15,5,6,0,0,15,16,5,6,0,0,16,17,
        5,5,0,0,17,18,5,6,0,0,18,19,5,6,0,0,19,5,1,0,0,0,1,9
    ]

class JodaParser ( Parser ):

    grammarFileName = "Joda.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'UTC'", "<INVALID>", "'+'", "'-'", "':'" ]

    symbolicNames = [ "<INVALID>", "UTC_KEYWORD", "LONG_TZ_IDENTIFIER", 
                      "PLUS", "MINUS", "COLON", "DIGIT", "WS" ]

    RULE_timeZone = 0
    RULE_longTZ = 1
    RULE_fixedTZ = 2

    ruleNames =  [ "timeZone", "longTZ", "fixedTZ" ]

    EOF = Token.EOF
    UTC_KEYWORD=1
    LONG_TZ_IDENTIFIER=2
    PLUS=3
    MINUS=4
    COLON=5
    DIGIT=6
    WS=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class TimeZoneContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def UTC_KEYWORD(self):
            return self.getToken(JodaParser.UTC_KEYWORD, 0)

        def longTZ(self):
            return self.getTypedRuleContext(JodaParser.LongTZContext,0)


        def fixedTZ(self):
            return self.getTypedRuleContext(JodaParser.FixedTZContext,0)


        def getRuleIndex(self):
            return JodaParser.RULE_timeZone

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTimeZone" ):
                return visitor.visitTimeZone(self)
            else:
                return visitor.visitChildren(self)




    def timeZone(self):

        localctx = JodaParser.TimeZoneContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_timeZone)
        try:
            self.state = 9
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 6
                self.match(JodaParser.UTC_KEYWORD)
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 7
                self.longTZ()
                pass
            elif token in [3, 4]:
                self.enterOuterAlt(localctx, 3)
                self.state = 8
                self.fixedTZ()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LongTZContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LONG_TZ_IDENTIFIER(self):
            return self.getToken(JodaParser.LONG_TZ_IDENTIFIER, 0)

        def getRuleIndex(self):
            return JodaParser.RULE_longTZ

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLongTZ" ):
                return visitor.visitLongTZ(self)
            else:
                return visitor.visitChildren(self)




    def longTZ(self):

        localctx = JodaParser.LongTZContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_longTZ)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 11
            self.match(JodaParser.LONG_TZ_IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FixedTZContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self, i:int=None):
            if i is None:
                return self.getTokens(JodaParser.DIGIT)
            else:
                return self.getToken(JodaParser.DIGIT, i)

        def COLON(self):
            return self.getToken(JodaParser.COLON, 0)

        def PLUS(self):
            return self.getToken(JodaParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(JodaParser.MINUS, 0)

        def getRuleIndex(self):
            return JodaParser.RULE_fixedTZ

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFixedTZ" ):
                return visitor.visitFixedTZ(self)
            else:
                return visitor.visitChildren(self)




    def fixedTZ(self):

        localctx = JodaParser.FixedTZContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_fixedTZ)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            _la = self._input.LA(1)
            if not(_la==3 or _la==4):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 14
            self.match(JodaParser.DIGIT)
            self.state = 15
            self.match(JodaParser.DIGIT)
            self.state = 16
            self.match(JodaParser.COLON)
            self.state = 17
            self.match(JodaParser.DIGIT)
            self.state = 18
            self.match(JodaParser.DIGIT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






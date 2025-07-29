# Generated from CelDuration.g4 by ANTLR 4.13.2
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
        4,1,11,47,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,1,0,1,0,1,0,1,1,3,1,19,8,1,1,1,1,1,5,1,23,8,1,10,1,12,1,26,9,1,
        1,1,3,1,29,8,1,1,1,3,1,32,8,1,1,2,1,2,1,2,1,3,1,3,1,4,1,4,3,4,41,
        8,4,1,5,1,5,1,6,1,6,1,6,0,0,7,0,2,4,6,8,10,12,0,3,1,0,9,10,1,0,1,
        6,1,0,7,8,44,0,14,1,0,0,0,2,31,1,0,0,0,4,33,1,0,0,0,6,36,1,0,0,0,
        8,38,1,0,0,0,10,42,1,0,0,0,12,44,1,0,0,0,14,15,3,2,1,0,15,16,5,0,
        0,1,16,1,1,0,0,0,17,19,3,12,6,0,18,17,1,0,0,0,18,19,1,0,0,0,19,20,
        1,0,0,0,20,24,3,4,2,0,21,23,3,4,2,0,22,21,1,0,0,0,23,26,1,0,0,0,
        24,22,1,0,0,0,24,25,1,0,0,0,25,32,1,0,0,0,26,24,1,0,0,0,27,29,3,
        12,6,0,28,27,1,0,0,0,28,29,1,0,0,0,29,30,1,0,0,0,30,32,3,8,4,0,31,
        18,1,0,0,0,31,28,1,0,0,0,32,3,1,0,0,0,33,34,3,6,3,0,34,35,3,10,5,
        0,35,5,1,0,0,0,36,37,7,0,0,0,37,7,1,0,0,0,38,40,3,6,3,0,39,41,5,
        3,0,0,40,39,1,0,0,0,40,41,1,0,0,0,41,9,1,0,0,0,42,43,7,1,0,0,43,
        11,1,0,0,0,44,45,7,2,0,0,45,13,1,0,0,0,5,18,24,28,31,40
    ]

class CelDurationParser ( Parser ):

    grammarFileName = "CelDuration.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'h'", "'m'", "'s'", "'ms'", "<INVALID>", 
                     "'ns'", "'+'", "'-'" ]

    symbolicNames = [ "<INVALID>", "HOURS", "MINUTES", "SECONDS", "MILLIS", 
                      "MICROS", "NANOS", "PLUS", "MINUS", "DECIMAL", "INT", 
                      "WS" ]

    RULE_parse = 0
    RULE_duration_input = 1
    RULE_component = 2
    RULE_amount = 3
    RULE_zero_value_with_optional_s = 4
    RULE_unit = 5
    RULE_sign = 6

    ruleNames =  [ "parse", "duration_input", "component", "amount", "zero_value_with_optional_s", 
                   "unit", "sign" ]

    EOF = Token.EOF
    HOURS=1
    MINUTES=2
    SECONDS=3
    MILLIS=4
    MICROS=5
    NANOS=6
    PLUS=7
    MINUS=8
    DECIMAL=9
    INT=10
    WS=11

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ParseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def duration_input(self):
            return self.getTypedRuleContext(CelDurationParser.Duration_inputContext,0)


        def EOF(self):
            return self.getToken(CelDurationParser.EOF, 0)

        def getRuleIndex(self):
            return CelDurationParser.RULE_parse

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParse" ):
                return visitor.visitParse(self)
            else:
                return visitor.visitChildren(self)




    def parse(self):

        localctx = CelDurationParser.ParseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_parse)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 14
            self.duration_input()
            self.state = 15
            self.match(CelDurationParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Duration_inputContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def component(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CelDurationParser.ComponentContext)
            else:
                return self.getTypedRuleContext(CelDurationParser.ComponentContext,i)


        def sign(self):
            return self.getTypedRuleContext(CelDurationParser.SignContext,0)


        def zero_value_with_optional_s(self):
            return self.getTypedRuleContext(CelDurationParser.Zero_value_with_optional_sContext,0)


        def getRuleIndex(self):
            return CelDurationParser.RULE_duration_input

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDuration_input" ):
                return visitor.visitDuration_input(self)
            else:
                return visitor.visitChildren(self)




    def duration_input(self):

        localctx = CelDurationParser.Duration_inputContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_duration_input)
        self._la = 0 # Token type
        try:
            self.state = 31
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 18
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==7 or _la==8:
                    self.state = 17
                    self.sign()


                self.state = 20
                self.component()
                self.state = 24
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==9 or _la==10:
                    self.state = 21
                    self.component()
                    self.state = 26
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 28
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==7 or _la==8:
                    self.state = 27
                    self.sign()


                self.state = 30
                self.zero_value_with_optional_s()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComponentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def amount(self):
            return self.getTypedRuleContext(CelDurationParser.AmountContext,0)


        def unit(self):
            return self.getTypedRuleContext(CelDurationParser.UnitContext,0)


        def getRuleIndex(self):
            return CelDurationParser.RULE_component

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComponent" ):
                return visitor.visitComponent(self)
            else:
                return visitor.visitChildren(self)




    def component(self):

        localctx = CelDurationParser.ComponentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_component)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.amount()
            self.state = 34
            self.unit()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AmountContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DECIMAL(self):
            return self.getToken(CelDurationParser.DECIMAL, 0)

        def INT(self):
            return self.getToken(CelDurationParser.INT, 0)

        def getRuleIndex(self):
            return CelDurationParser.RULE_amount

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAmount" ):
                return visitor.visitAmount(self)
            else:
                return visitor.visitChildren(self)




    def amount(self):

        localctx = CelDurationParser.AmountContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_amount)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
            _la = self._input.LA(1)
            if not(_la==9 or _la==10):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Zero_value_with_optional_sContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def amount(self):
            return self.getTypedRuleContext(CelDurationParser.AmountContext,0)


        def SECONDS(self):
            return self.getToken(CelDurationParser.SECONDS, 0)

        def getRuleIndex(self):
            return CelDurationParser.RULE_zero_value_with_optional_s

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitZero_value_with_optional_s" ):
                return visitor.visitZero_value_with_optional_s(self)
            else:
                return visitor.visitChildren(self)




    def zero_value_with_optional_s(self):

        localctx = CelDurationParser.Zero_value_with_optional_sContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_zero_value_with_optional_s)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 38
            self.amount()
            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 39
                self.match(CelDurationParser.SECONDS)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UnitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def HOURS(self):
            return self.getToken(CelDurationParser.HOURS, 0)

        def MINUTES(self):
            return self.getToken(CelDurationParser.MINUTES, 0)

        def SECONDS(self):
            return self.getToken(CelDurationParser.SECONDS, 0)

        def MILLIS(self):
            return self.getToken(CelDurationParser.MILLIS, 0)

        def MICROS(self):
            return self.getToken(CelDurationParser.MICROS, 0)

        def NANOS(self):
            return self.getToken(CelDurationParser.NANOS, 0)

        def getRuleIndex(self):
            return CelDurationParser.RULE_unit

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnit" ):
                return visitor.visitUnit(self)
            else:
                return visitor.visitChildren(self)




    def unit(self):

        localctx = CelDurationParser.UnitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_unit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 42
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 126) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SignContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PLUS(self):
            return self.getToken(CelDurationParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(CelDurationParser.MINUS, 0)

        def getRuleIndex(self):
            return CelDurationParser.RULE_sign

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSign" ):
                return visitor.visitSign(self)
            else:
                return visitor.visitChildren(self)




    def sign(self):

        localctx = CelDurationParser.SignContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_sign)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            _la = self._input.LA(1)
            if not(_la==7 or _la==8):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






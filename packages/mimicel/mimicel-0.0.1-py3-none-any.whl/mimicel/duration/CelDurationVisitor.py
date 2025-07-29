# Generated from CelDuration.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .CelDurationParser import CelDurationParser
else:
    from CelDurationParser import CelDurationParser

# This class defines a complete generic visitor for a parse tree produced by CelDurationParser.

class CelDurationVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CelDurationParser#parse.
    def visitParse(self, ctx:CelDurationParser.ParseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CelDurationParser#duration_input.
    def visitDuration_input(self, ctx:CelDurationParser.Duration_inputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CelDurationParser#component.
    def visitComponent(self, ctx:CelDurationParser.ComponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CelDurationParser#amount.
    def visitAmount(self, ctx:CelDurationParser.AmountContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CelDurationParser#zero_value_with_optional_s.
    def visitZero_value_with_optional_s(self, ctx:CelDurationParser.Zero_value_with_optional_sContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CelDurationParser#unit.
    def visitUnit(self, ctx:CelDurationParser.UnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CelDurationParser#sign.
    def visitSign(self, ctx:CelDurationParser.SignContext):
        return self.visitChildren(ctx)



del CelDurationParser
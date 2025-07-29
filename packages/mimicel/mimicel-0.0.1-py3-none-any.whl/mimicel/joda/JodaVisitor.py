# Generated from Joda.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .JodaParser import JodaParser
else:
    from JodaParser import JodaParser

# This class defines a complete generic visitor for a parse tree produced by JodaParser.

class JodaVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by JodaParser#timeZone.
    def visitTimeZone(self, ctx:JodaParser.TimeZoneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JodaParser#longTZ.
    def visitLongTZ(self, ctx:JodaParser.LongTZContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JodaParser#fixedTZ.
    def visitFixedTZ(self, ctx:JodaParser.FixedTZContext):
        return self.visitChildren(ctx)



del JodaParser
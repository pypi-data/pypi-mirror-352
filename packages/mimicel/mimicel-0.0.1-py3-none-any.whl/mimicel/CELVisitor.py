# Generated from CEL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .CELParser import CELParser
else:
    from CELParser import CELParser

# This class defines a complete generic visitor for a parse tree produced by CELParser.

class CELVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CELParser#start.
    def visitStart(self, ctx:CELParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#expr.
    def visitExpr(self, ctx:CELParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#conditionalOr.
    def visitConditionalOr(self, ctx:CELParser.ConditionalOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#conditionalAnd.
    def visitConditionalAnd(self, ctx:CELParser.ConditionalAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#relation.
    def visitRelation(self, ctx:CELParser.RelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#calc.
    def visitCalc(self, ctx:CELParser.CalcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#MemberExpr.
    def visitMemberExpr(self, ctx:CELParser.MemberExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#LogicalNot.
    def visitLogicalNot(self, ctx:CELParser.LogicalNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Negate.
    def visitNegate(self, ctx:CELParser.NegateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#MemberCall.
    def visitMemberCall(self, ctx:CELParser.MemberCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Select.
    def visitSelect(self, ctx:CELParser.SelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#PrimaryExpr.
    def visitPrimaryExpr(self, ctx:CELParser.PrimaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Index.
    def visitIndex(self, ctx:CELParser.IndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Ident.
    def visitIdent(self, ctx:CELParser.IdentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#GlobalCall.
    def visitGlobalCall(self, ctx:CELParser.GlobalCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Nested.
    def visitNested(self, ctx:CELParser.NestedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#CreateList.
    def visitCreateList(self, ctx:CELParser.CreateListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#CreateStruct.
    def visitCreateStruct(self, ctx:CELParser.CreateStructContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#CreateMessage.
    def visitCreateMessage(self, ctx:CELParser.CreateMessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#ConstantLiteral.
    def visitConstantLiteral(self, ctx:CELParser.ConstantLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#exprList.
    def visitExprList(self, ctx:CELParser.ExprListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#listInit.
    def visitListInit(self, ctx:CELParser.ListInitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#fieldInitializerList.
    def visitFieldInitializerList(self, ctx:CELParser.FieldInitializerListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#optField.
    def visitOptField(self, ctx:CELParser.OptFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#mapInitializerList.
    def visitMapInitializerList(self, ctx:CELParser.MapInitializerListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#SimpleIdentifier.
    def visitSimpleIdentifier(self, ctx:CELParser.SimpleIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#EscapedIdentifier.
    def visitEscapedIdentifier(self, ctx:CELParser.EscapedIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#optExpr.
    def visitOptExpr(self, ctx:CELParser.OptExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Int.
    def visitInt(self, ctx:CELParser.IntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Uint.
    def visitUint(self, ctx:CELParser.UintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Double.
    def visitDouble(self, ctx:CELParser.DoubleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#String.
    def visitString(self, ctx:CELParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Bytes.
    def visitBytes(self, ctx:CELParser.BytesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#BoolTrue.
    def visitBoolTrue(self, ctx:CELParser.BoolTrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#BoolFalse.
    def visitBoolFalse(self, ctx:CELParser.BoolFalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CELParser#Null.
    def visitNull(self, ctx:CELParser.NullContext):
        return self.visitChildren(ctx)



del CELParser
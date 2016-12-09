# Generated from PCRE.g4 by ANTLR 4.5.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .PCREParser import PCREParser
else:
    from PCREParser import PCREParser

# This class defines a complete listener for a parse tree produced by PCREParser.
class PCREListener(ParseTreeListener):

    # Enter a parse tree produced by PCREParser#parse.
    def enterParse(self, ctx:PCREParser.ParseContext):
        pass

    # Exit a parse tree produced by PCREParser#parse.
    def exitParse(self, ctx:PCREParser.ParseContext):
        pass


    # Enter a parse tree produced by PCREParser#alternation.
    def enterAlternation(self, ctx:PCREParser.AlternationContext):
        pass

    # Exit a parse tree produced by PCREParser#alternation.
    def exitAlternation(self, ctx:PCREParser.AlternationContext):
        pass


    # Enter a parse tree produced by PCREParser#expr.
    def enterExpr(self, ctx:PCREParser.ExprContext):
        pass

    # Exit a parse tree produced by PCREParser#expr.
    def exitExpr(self, ctx:PCREParser.ExprContext):
        pass


    # Enter a parse tree produced by PCREParser#element.
    def enterElement(self, ctx:PCREParser.ElementContext):
        pass

    # Exit a parse tree produced by PCREParser#element.
    def exitElement(self, ctx:PCREParser.ElementContext):
        pass


    # Enter a parse tree produced by PCREParser#quantifier.
    def enterQuantifier(self, ctx:PCREParser.QuantifierContext):
        pass

    # Exit a parse tree produced by PCREParser#quantifier.
    def exitQuantifier(self, ctx:PCREParser.QuantifierContext):
        pass


    # Enter a parse tree produced by PCREParser#quantifier_type.
    def enterQuantifier_type(self, ctx:PCREParser.Quantifier_typeContext):
        pass

    # Exit a parse tree produced by PCREParser#quantifier_type.
    def exitQuantifier_type(self, ctx:PCREParser.Quantifier_typeContext):
        pass


    # Enter a parse tree produced by PCREParser#character_class.
    def enterCharacter_class(self, ctx:PCREParser.Character_classContext):
        pass

    # Exit a parse tree produced by PCREParser#character_class.
    def exitCharacter_class(self, ctx:PCREParser.Character_classContext):
        pass


    # Enter a parse tree produced by PCREParser#backreference.
    def enterBackreference(self, ctx:PCREParser.BackreferenceContext):
        pass

    # Exit a parse tree produced by PCREParser#backreference.
    def exitBackreference(self, ctx:PCREParser.BackreferenceContext):
        pass


    # Enter a parse tree produced by PCREParser#backreference_or_octal.
    def enterBackreference_or_octal(self, ctx:PCREParser.Backreference_or_octalContext):
        pass

    # Exit a parse tree produced by PCREParser#backreference_or_octal.
    def exitBackreference_or_octal(self, ctx:PCREParser.Backreference_or_octalContext):
        pass


    # Enter a parse tree produced by PCREParser#capture.
    def enterCapture(self, ctx:PCREParser.CaptureContext):
        pass

    # Exit a parse tree produced by PCREParser#capture.
    def exitCapture(self, ctx:PCREParser.CaptureContext):
        pass


    # Enter a parse tree produced by PCREParser#non_capture.
    def enterNon_capture(self, ctx:PCREParser.Non_captureContext):
        pass

    # Exit a parse tree produced by PCREParser#non_capture.
    def exitNon_capture(self, ctx:PCREParser.Non_captureContext):
        pass


    # Enter a parse tree produced by PCREParser#comment.
    def enterComment(self, ctx:PCREParser.CommentContext):
        pass

    # Exit a parse tree produced by PCREParser#comment.
    def exitComment(self, ctx:PCREParser.CommentContext):
        pass


    # Enter a parse tree produced by PCREParser#option.
    def enterOption(self, ctx:PCREParser.OptionContext):
        pass

    # Exit a parse tree produced by PCREParser#option.
    def exitOption(self, ctx:PCREParser.OptionContext):
        pass


    # Enter a parse tree produced by PCREParser#option_flags.
    def enterOption_flags(self, ctx:PCREParser.Option_flagsContext):
        pass

    # Exit a parse tree produced by PCREParser#option_flags.
    def exitOption_flags(self, ctx:PCREParser.Option_flagsContext):
        pass


    # Enter a parse tree produced by PCREParser#option_flag.
    def enterOption_flag(self, ctx:PCREParser.Option_flagContext):
        pass

    # Exit a parse tree produced by PCREParser#option_flag.
    def exitOption_flag(self, ctx:PCREParser.Option_flagContext):
        pass


    # Enter a parse tree produced by PCREParser#look_around.
    def enterLook_around(self, ctx:PCREParser.Look_aroundContext):
        pass

    # Exit a parse tree produced by PCREParser#look_around.
    def exitLook_around(self, ctx:PCREParser.Look_aroundContext):
        pass


    # Enter a parse tree produced by PCREParser#subroutine_reference.
    def enterSubroutine_reference(self, ctx:PCREParser.Subroutine_referenceContext):
        pass

    # Exit a parse tree produced by PCREParser#subroutine_reference.
    def exitSubroutine_reference(self, ctx:PCREParser.Subroutine_referenceContext):
        pass


    # Enter a parse tree produced by PCREParser#conditional.
    def enterConditional(self, ctx:PCREParser.ConditionalContext):
        pass

    # Exit a parse tree produced by PCREParser#conditional.
    def exitConditional(self, ctx:PCREParser.ConditionalContext):
        pass


    # Enter a parse tree produced by PCREParser#backtrack_control.
    def enterBacktrack_control(self, ctx:PCREParser.Backtrack_controlContext):
        pass

    # Exit a parse tree produced by PCREParser#backtrack_control.
    def exitBacktrack_control(self, ctx:PCREParser.Backtrack_controlContext):
        pass


    # Enter a parse tree produced by PCREParser#newline_convention.
    def enterNewline_convention(self, ctx:PCREParser.Newline_conventionContext):
        pass

    # Exit a parse tree produced by PCREParser#newline_convention.
    def exitNewline_convention(self, ctx:PCREParser.Newline_conventionContext):
        pass


    # Enter a parse tree produced by PCREParser#callout.
    def enterCallout(self, ctx:PCREParser.CalloutContext):
        pass

    # Exit a parse tree produced by PCREParser#callout.
    def exitCallout(self, ctx:PCREParser.CalloutContext):
        pass


    # Enter a parse tree produced by PCREParser#atom.
    def enterAtom(self, ctx:PCREParser.AtomContext):
        pass

    # Exit a parse tree produced by PCREParser#atom.
    def exitAtom(self, ctx:PCREParser.AtomContext):
        pass


    # Enter a parse tree produced by PCREParser#cc_atom.
    def enterCc_atom(self, ctx:PCREParser.Cc_atomContext):
        pass

    # Exit a parse tree produced by PCREParser#cc_atom.
    def exitCc_atom(self, ctx:PCREParser.Cc_atomContext):
        pass


    # Enter a parse tree produced by PCREParser#shared_atom.
    def enterShared_atom(self, ctx:PCREParser.Shared_atomContext):
        pass

    # Exit a parse tree produced by PCREParser#shared_atom.
    def exitShared_atom(self, ctx:PCREParser.Shared_atomContext):
        pass


    # Enter a parse tree produced by PCREParser#literal.
    def enterLiteral(self, ctx:PCREParser.LiteralContext):
        pass

    # Exit a parse tree produced by PCREParser#literal.
    def exitLiteral(self, ctx:PCREParser.LiteralContext):
        pass


    # Enter a parse tree produced by PCREParser#cc_literal.
    def enterCc_literal(self, ctx:PCREParser.Cc_literalContext):
        pass

    # Exit a parse tree produced by PCREParser#cc_literal.
    def exitCc_literal(self, ctx:PCREParser.Cc_literalContext):
        pass


    # Enter a parse tree produced by PCREParser#shared_literal.
    def enterShared_literal(self, ctx:PCREParser.Shared_literalContext):
        pass

    # Exit a parse tree produced by PCREParser#shared_literal.
    def exitShared_literal(self, ctx:PCREParser.Shared_literalContext):
        pass


    # Enter a parse tree produced by PCREParser#number.
    def enterNumber(self, ctx:PCREParser.NumberContext):
        pass

    # Exit a parse tree produced by PCREParser#number.
    def exitNumber(self, ctx:PCREParser.NumberContext):
        pass


    # Enter a parse tree produced by PCREParser#octal_char.
    def enterOctal_char(self, ctx:PCREParser.Octal_charContext):
        pass

    # Exit a parse tree produced by PCREParser#octal_char.
    def exitOctal_char(self, ctx:PCREParser.Octal_charContext):
        pass


    # Enter a parse tree produced by PCREParser#octal_digit.
    def enterOctal_digit(self, ctx:PCREParser.Octal_digitContext):
        pass

    # Exit a parse tree produced by PCREParser#octal_digit.
    def exitOctal_digit(self, ctx:PCREParser.Octal_digitContext):
        pass


    # Enter a parse tree produced by PCREParser#digits.
    def enterDigits(self, ctx:PCREParser.DigitsContext):
        pass

    # Exit a parse tree produced by PCREParser#digits.
    def exitDigits(self, ctx:PCREParser.DigitsContext):
        pass


    # Enter a parse tree produced by PCREParser#digit.
    def enterDigit(self, ctx:PCREParser.DigitContext):
        pass

    # Exit a parse tree produced by PCREParser#digit.
    def exitDigit(self, ctx:PCREParser.DigitContext):
        pass


    # Enter a parse tree produced by PCREParser#name.
    def enterName(self, ctx:PCREParser.NameContext):
        pass

    # Exit a parse tree produced by PCREParser#name.
    def exitName(self, ctx:PCREParser.NameContext):
        pass


    # Enter a parse tree produced by PCREParser#alpha_nums.
    def enterAlpha_nums(self, ctx:PCREParser.Alpha_numsContext):
        pass

    # Exit a parse tree produced by PCREParser#alpha_nums.
    def exitAlpha_nums(self, ctx:PCREParser.Alpha_numsContext):
        pass


    # Enter a parse tree produced by PCREParser#non_close_parens.
    def enterNon_close_parens(self, ctx:PCREParser.Non_close_parensContext):
        pass

    # Exit a parse tree produced by PCREParser#non_close_parens.
    def exitNon_close_parens(self, ctx:PCREParser.Non_close_parensContext):
        pass


    # Enter a parse tree produced by PCREParser#non_close_paren.
    def enterNon_close_paren(self, ctx:PCREParser.Non_close_parenContext):
        pass

    # Exit a parse tree produced by PCREParser#non_close_paren.
    def exitNon_close_paren(self, ctx:PCREParser.Non_close_parenContext):
        pass


    # Enter a parse tree produced by PCREParser#letter.
    def enterLetter(self, ctx:PCREParser.LetterContext):
        pass

    # Exit a parse tree produced by PCREParser#letter.
    def exitLetter(self, ctx:PCREParser.LetterContext):
        pass



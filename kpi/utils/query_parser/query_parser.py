# -*- coding: utf-8 -*-

from django.db.models import Q

DEFAULT_FIELD_NAME = 'summary'

from .grammar import parse as grammar_parse

class Actions(object):

    def __init__(self, model):
        self.model = model
    def process_value(self, field, value):
        # If all we're doing when we have a type mismatch with a field
        # is returning an empty set, then we don't need to do type validation.
        # Django compares between field values and string versions just fine.
        # But there's no magic string for null, so we're adding one.
        if value == 'null':
            return None
        else:
            return value

    def query(self, text, a, b, elements):
        exp = elements[1]
        if hasattr(exp, 'text') and exp.text == '':
            # Handle the empty query case with an empty Q object, returning all
            return Q()
        else:
            #fallthrough
            return exp
    def orexp(self, text, a, b, elements):
        # fallthrough if singular
        if elements[1].text == '':
            return elements[0]
        # else, combine full sequence of ORs into flattened expression
        else:
            # Start with the first Q object
            orgroup = elements[0]
            # Loop through the repeated clauses and OR the subexpressions.
            for clause in elements[1].elements:
                orgroup |= clause.expr
            return orgroup
    def andexp(self, text, a, b, elements):
        # fallthrough if singular
        if elements[1].text == '':  # gotta make sure this is working
            return elements[0]
        # else, combine full sequence of ANDs into flattened expression
        else:
            # Start with the first Q object
            andgroup = elements[0]
            # Loop through the repeated clauses and AND the subexpressions.
            for clause in elements[1].elements:
                andgroup &= clause.expr
            return andgroup
    def parenexp(self, text, a, b, elements):
        # fallthrough to subexpression
        exp = elements[2]
        return exp
    def notexp(self, text, a, b, elements):
        # negate subexpression (Q object)
        exp = elements[2]
        return ~exp
    def term(self, text, a, b, elements):
        if elements[0].text == '':
            # A search term by itself without a specified field
            # Search the default field with case-insensitive "contains"
            field = DEFAULT_FIELD_NAME + "__icontains"
            value = elements[1]
            return Q(**{field: value})
        else:
            # A field+colon, and a value [[field,':'],value]
            field = elements[0].elements[0]
            value = elements[1]
            # Process the value with as much type-validation as necessary
            value = self.process_value(field, value)
            return Q(**{field: value})
    def word(self, text, a, b, elements):
        return text[a:b]
    def string(self, text, a, b, elements):
        return text[a+1:b-1]
    def name(self, text, a, b, elements):
        return text[a:b]  

def parse(query='', model=None):
    return grammar_parse(query, actions=Actions(model))
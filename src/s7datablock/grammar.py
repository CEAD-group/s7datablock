"""Grammar definitions for parsing TIA Portal DB exports."""
from functools import reduce
from operator import or_

from pyparsing import CaselessKeyword, Combine, Dict, Forward, Group, OneOrMore
from pyparsing import Opt as Optional  # workaround for mypy bug
from pyparsing import Regex, Suppress, Word, ZeroOrMore, alphanums, alphas, nums

from s7datablock.constants import S7_ALL_TYPES

# Basic tokens
QUOTE = Suppress(Word("'\""))
UNQUOTED_IDENT = Word(f"{alphas}_", f"{alphanums}_")
QUOTED_IDENT = QUOTE + Word(f"{alphanums}_. ") + QUOTE
IDENT = QUOTED_IDENT | UNQUOTED_IDENT
REAL = Regex(r"\d+\.\d*")
INT = Regex(r"\d+")
LBRACE, RBRACE, SEMI, COLON = map(Suppress, "{};:")
EQUALS = Suppress(":=")
BOOLEAN = CaselessKeyword("True") | CaselessKeyword("False")
COMMENT = Suppress("//" + Regex(r".*"))
POINT = Suppress(".")
hex_prefix = Combine(Word(nums) + "#")
hex_digits = Word(nums + "ABCDEFabcdef")
HEX = Combine(hex_prefix + hex_digits)
VALUE = BOOLEAN | HEX | REAL | INT

# S7 specific grammar
S7_DTYPE = reduce(or_, map(CaselessKeyword, S7_ALL_TYPES))
DURATION = Regex(r"T#\d+[sMHmsdh]")

# Attribute assignments and values
optional_attribute_assignments = Suppress(
    Optional(
        LBRACE + ZeroOrMore(IDENT + EQUALS + QUOTE + (BOOLEAN | S7_DTYPE | REAL) + QUOTE + Optional(SEMI)) + RBRACE
    )
)

date = IDENT + optional_attribute_assignments
value_assignment = EQUALS + (REAL | BOOLEAN | INT | DURATION)
optional_default_value = Suppress(Optional(expr=value_assignment, default=None))

# Structure definitions
struct_def = Forward()

struct_element = Dict(
    Group(
        Optional(date)
        + Optional(IDENT)
        + optional_attribute_assignments
        + COLON
        + Optional((S7_DTYPE + optional_default_value + SEMI) | (QUOTED_IDENT + SEMI) | struct_def)
    )
    + Optional(COMMENT)
)

struct_def <<= (
    Suppress(CaselessKeyword("STRUCT"))
    + Optional(COMMENT)
    + Group(OneOrMore(struct_element))
    + Suppress(CaselessKeyword("END_STRUCT"))
    + SEMI
)

# Type and variable definitions
type_def = Dict(
    Group(
        Suppress("TYPE")
        + IDENT
        + Suppress("VERSION")
        + COLON
        + Suppress(REAL("version"))
        + struct_def
        + Suppress("END_TYPE")
    )
)

var_def = Dict(
    Group(
        Suppress(CaselessKeyword("VAR"))
        + ZeroOrMore(struct_element)
        + Group(OneOrMore(struct_element))
        + Suppress("END_VAR")
    )
)

# Default values and data block definitions
default_value_element = Group(ZeroOrMore(IDENT + POINT) + IDENT + Suppress(EQUALS) + VALUE + Suppress(SEMI)) + Group(
    ZeroOrMore(Suppress(EQUALS) + VALUE + Suppress(SEMI))
)

defaults_values_block = Dict(
    Group(Suppress(CaselessKeyword("BEGIN")) + ZeroOrMore(default_value_element) + Suppress("END_DATA_BLOCK"))
)("BEGIN")

data_block_def = Dict(
    Group(
        Suppress("DATA_BLOCK")
        + QUOTE
        + IDENT
        + QUOTE
        + optional_attribute_assignments
        + Suppress("VERSION")
        + COLON
        + Suppress(REAL)
        + Suppress(Optional(CaselessKeyword("NON_RETAIN")))
        + (var_def | struct_def | QUOTED_IDENT)
    )
)("DATA_BLOCK")

# Complete program grammar
program = Group(ZeroOrMore(type_def))("TYPES") + data_block_def + defaults_values_block

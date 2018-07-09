import copy
from typing import NewType, Sequence, Tuple, Text

import ply.yacc
from . lexer import tokens


# A SAMoS script is a series of statements.  We represent the script as
# a sequence of tuples.
Parsed = Tuple[Tuple]


def p_program(p):
    """ program : statement
                | program statement
    """
    if len(p) == 2:
        if len(p[1]) == 0:      # Newline or comment.
            p[0] = p[1]
        else:
            p[0] = (p[1],)
    else:
        if len(p[2]) == 0:      # Newline or comment.
            p[0] = p[1]
        else:
            p[0] = p[1] + (p[2],)


# This catch-all rule is used for any catastrophic errors.  In this case, we simply return nothing.
def p_program_error(p):
    """ program : error """
    p[0] = []
    p.parser.error = 1


# Statements.

# Format of all XPP statements.
def p_statement(p):
    """ statement : command NEWLINE """
    p[0] = p[1]

# Blank line.
def p_statement_newline(p):
    """ statement : NEWLINE """
    p[0] = ()


# Commands.

def p_command_messages(p):
    """ command : MESSAGES str """
    p[0] = ('messages', p[2])


def p_command_config(p):
    """ command : CONFIG str exprset """
    p[0] = ('config', p[2], p[3])
    

def p_command_box(p):
    """ command : BOX str exprset """
    p[0] = ('box', p[2], p[3])


def p_command_input(p):
    """ command : INPUT str """
    p[0] = ('input', p[2])
    

def p_command_nlist(p):
    """ command : NLIST exprset """
    p[0] = ('nlist', p[2])


def p_command_pair_potential(p):
    """ command : PAIR_POTENTIAL str exprset """
    p[0] = ('pair_potential', p[2], p[3])
        

def p_command_pair_param(p):
    """ command : PAIR_PARAM str exprset """
    p[0] = ('pair_param', p[2], p[3])


def p_command_external(p):
    """ command : EXTERNAL str exprset """
    p[0] = ('external', p[2], p[3])


def p_command_population(p):
    """ command : POPULATION str exprset """
    p[0] = ('population', p[2], p[3])
        

def p_command_log(p):
    """ command : LOG str exprset """
    p[0] = ('log', p[2], p[3])


def p_command_dump(p):
    """ command : DUMP str exprset """
    p[0] = ('dump', p[2], p[3])


def p_command_integrator(p):
    """ command : INTEGRATOR str exprset """
    p[0] = ('integrator', p[2], p[3])


def p_command_run(p):
    """ command : RUN NUMBER """
    p[0] = ('run', p[2])


def p_command_disable(p):
    """ command : DISABLE str exprset """
    p[0] = ('disable', p[2], p[3])


def p_command_read_cell_boundary(p):
    """ command : READ_CELL_BOUNDARY str """
    p[0] = ('read_cell_boundary', p[2])


def p_command_constraint(p):
    """ command : CONSTRAINT str exprset """
    p[0] = ('constraint', p[2], p[3])


def p_command_timestep(p):
    """ command : TIMESTEP NUMBER """
    p[0] = ('timestep', p[2])


# Expressions.


def p_exprlist(p):
    """ exprlist : expr
                 | exprlist SEMI expr
    """
    if len(p) == 2:
        # p[0] = [p[1]]
        p[0] = p[1]
    else:
        # p[0] = p[1] + [p[3]]
        p[0] = {**p[1], **p[3]}


def p_expr_assignment(p):
    """ expr : assignment """
    p[0] = p[1]


def p_expr_str(p):
    """ expr : str """
    p[0] = {p[1]: True}


# Assignments.
def p_assignment(p):
    """ assignment : str EQUALS str
                   | str EQUALS NUMBER
    """
    p[0] = {p[1]: p[3]}


# Expressions sepparated by semicolon.

def p_exprset(p):
    """ exprset : LBRACE exprlist RBRACE 
                | LBRACE exprlist SEMI RBRACE
    """
    p[0] = (p[2])



# A string.        
def p_str(p):
    """ str : ID """
    p[0] = p[1]


# Catastrophic error handler.
def p_error(p):
    if not p:
        print("SYNTAX ERROR AT EOF")


def parse(data: str) -> Parsed:
    """ Parse data. """
    parser = ply.yacc.yacc(debug=True)
    return parser.parse(data)


def parse_file(fname: str) -> Parsed:
    """ Parse configuration file."""
    with open(fname, 'r') as f:
        return parse(f.read())

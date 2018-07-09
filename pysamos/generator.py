from typing import Tuple, Union, NewType, List, Sequence
import typing
import numbers

from . import parser
from . import lexer


def write(cfg: parser.Parsed, fname: str) -> None:
    """ Write config. """
    cmds = g_program(cfg)
    with open(fname, 'w') as f:
        f.writelines(cmd+'\n' for cmd in cmds)


def g_program(cfg: parser.Parsed) -> List[str]:
    """ Read full config from parser and return generated commands. """
    cmds = tuple([g_command(cmd) for cmd in cfg])
    return cmds


# COMMANDS.

def g_command(cmd: Tuple) -> str:
    """ Generate a command. """
    uid = cmd[0]
    if uid.upper() in lexer.simple_cmd_tokens:
        return g_command_simple(cmd)
    elif uid.upper() in lexer.options_cmd_tokens:
        return g_command_options(cmd)
    else:
        return g_command_nlist(cmd)


def g_command_simple(cmd: Tuple[str, str]) -> str:
    """ Generate a simple command with one argument and no options. """
    return f'{g_expr(cmd[0])} {g_expr(cmd[1])}'


def g_command_options(cmd: Tuple[str, str, List]) -> str:
    """ Generate a long command with options. """
    return f'{g_expr(cmd[0])} {g_expr(cmd[1])} {g_opts(cmd[2])}'


def g_command_nlist(cmd: Tuple[str, List]) -> str:
    """ Generate a command for nlist. """
    return f'{cmd[0]} {g_opts(cmd[1])}'

# OPTIONS.

def g_opts(opt: dict) -> str:
    """ Generate an options. """
    assignments = [g_expr({key: val}) for key, val in opt.items()]
    exprlist = ';'.join(assignments)
    return f'{{{exprlist}}}'


# EXPRESSIONS.

def g_expr(expr) -> str:
    """ Generate an expression. """
    if type(expr) is dict:
        return g_expr_assignment(expr)
    elif type(expr) is str:
        return g_expr_str(expr)
    elif type(expr) is bool:
        return g_expr_bool(expr)
    else:
        return g_expr_num(expr)


def g_expr_assignment(expr: dict) -> str:
    """ Generate an assignment expression. """
    var = g_expr(list(expr.keys())[0])
    rhs = g_expr(list(expr.values())[0])
    if rhs is True:
        return f'{var}'
    else:
        return f'{var}={rhs}'


def g_expr_num(expr: float) -> str:
    """ Generate a number expression. """
    return str(expr)


def g_expr_str(expr: str) -> str:
    """ Generate a string expression. """
    return expr


def g_expr_bool(expr: bool) -> str:
    """ Generate a boolean expression. """
    return expr
    

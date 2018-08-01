# Simple lexer for samos config file.

import ply.lex


# Simple tokens which don't define a command.
literal_tokens = ('ID',
                  'LBRACE',
                  'RBRACE',
                  'SEMI',
                  'NUMBER',
                  'EQUALS',
                  'NEWLINE') 

# Simple commands without additional options.
simple_cmd_tokens = ('MESSAGES',
                     'INPUT',
                     'READ_CELL_BOUNDARY',
                     'TIMESTEP',
                     'RUN')

# Commands with additional options.
options_cmd_tokens = ('BOX',
                      'CONFIG',
                      'CONSTRAINT',
                      'DISABLE',
                      'DUMP',
                      'INTEGRATOR',
                      'LOG',
                      'PAIR_POTENTIAL',
                      'PAIR_PARAM',
                      'EXTERNAL',
                      'POPULATION')

# Remaining tokens.
other_tokens = ('NLIST',)

# All tokens.
tokens = literal_tokens + simple_cmd_tokens + options_cmd_tokens + other_tokens


t_EQUALS = r'='
t_SEMI = r';'
t_LBRACE = r'{'
t_RBRACE = r'}'


def t_DISABLE(t):
    r'(?m)^disable'
    return t


def t_TIMESTEP(t):
    r'(?m)^timestep'
    return t


def t_MESSAGES(t):
    r'(?m)^messages'
    return t


def t_CONFIG(t):
    r'(?m)^config'
    return t


def t_BOX(t):
    r'(?m)^box'
    return t


def t_INPUT(t):
    r'(?m)^input'
    return t


def t_READ_CELL_BOUNDARY(t):
    r'(?m)^read_cell_boundary'
    return t


def t_NLIST(t):
    r'(?m)^nlist'
    return t


def t_CONSTRAINT(t):
    r'(?m)^constraint'
    return t


def t_PAIR_POTENTIAL(t):
    r'(?m)^pair_potential'
    return t


def t_PAIR_PARAM(t):
    r'(?m)^pair_param'
    return t


def t_EXTERNAL(t):
    r'(?m)^external'
    return t


def t_POPULATION(t):
    r'(?m)^population'
    return t


def t_LOG(t):
    r'(?m)^log'
    return t


def t_DUMP(t):
    r'(?m)^dump'
    return t


def t_INTEGRATOR(t):
    r'(?m)^integrator'
    return t


def t_RUN(t):
    r'(?m)^run'
    return t


# Signed number.
def t_NUMBER(t):
    r'-?(\d+\.\d*|\d*\.\d+|\d+)'
    num = float(t.value)
    t.value = int(num) if float(num).is_integer() else num
    return t


def t_ID(t):
    r'[a-zA-Z\-0-9\_\/\.]+'
    return t


def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'

lexer = ply.lex.lex()


def lex_file(fname: str) -> list:
    """Lex configuration file into tokens."""
    with open(fname, 'r') as f:
        lexer.input(f.read())
        # Tokenize.
        tokens = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens.append(tok)
    return tokens

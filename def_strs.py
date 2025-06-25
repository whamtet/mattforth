from util import maplast_lines

def defstr(s):
    if s.startswith('STRING '):
        [a, b] = s[7:].split(': ')
        return f"""
{a}: .asciz "{b}\\n"
"""

def defstr0(s):
    if s.startswith('STRING0 '):
        [a, b] = s[8:].split(': ')
        return f"""
{a}: .asciz "{b}"
"""

VAR_COUNTER = 0

def str_line(is_last, str):
    if is_last:
        return f""".asciz "{str}" """
    else:
        return f""".ascii "{str}\\n" """

def defprint(s):
    global VAR_COUNTER
    # s has already been split on <?
    lines = s.split('\n')
    VAR_COUNTER += 1

    return [
        f"""var{VAR_COUNTER}:
        {maplast_lines(str_line, lines)}
        """,
        f""".var{VAR_COUNTER} """
    ]
import re
from if_compiler import emit_if, emit_else, emit_then
from func_compiler import get_commands, add_command, is_recording

def keep(f, s):
    return filter(lambda x: x, map(f, s))

def mapcat(f, s):
    out = []
    for x in s:
        for y in f(x):
            out.append(y)
    return out

def defstr(s):
    if s.startswith('STRING '):
        [a, b] = s[7:].split(': ')
        return f"""
{a}: .asciz "{b}\\n"
"""

def push_stack(value):
    return f"""
mov X3, #{value}
str X3, [X19], #8
"""

prefix_funcs = [
(".", lambda s: f"""
ldr X0, ={s}
bl printf
"""), 
("@@", lambda var: f"""
ldr X1, ={var}
ldr X0, [X1]
str X0, [X19], #8
"""), 
("@", lambda var: f"""
ldr X0, ={var}
str X0, [X19], #8
"""),
("!", lambda var: f"""
ldr X0, [X19, #-8]!
ldr X1, ={var}
str X0, [X1]
""")]

def op_maker(s):
    return f"""
ldr X0, [X19, #-8]!
ldr X1, [X19, #-8]
{s} X0, X0, X1
str X0, [X19, #-8]
"""

def comp_maker(s):
    return f"""
ldr X0, [X19, #-8]!
ldr X1, [X19, #-8]
cmp X1, X0
cset X2, {s}
str X2, [X19, #-8]
"""

def not_maker(s):
    return f"""
ldr X0, [X19, #-8]
cmp X0, #0
cset X2, {s}
str X2, [X19, #-8]
"""

plain_args = {
"+": op_maker("add"),
"-": op_maker("sub"),
"*": op_maker("mul"),
".": """
ldr     X0, =format
ldr X1, [X19, #-8]!
bl      printf
""",
"..": """
ldr X0, [X19, #-8]!
bl printf
""",
"?": """
mov X8, #63
mov X0, #0
ldr X1, [X19, #-8]!
ldr X2, [X19, #-8]
svc #0
str X1, [X19, #-8]
""",
"dup": """
ldr X0, [X19, #-8]
str X0, [X19], #8
""",
"not": not_maker("eq"),
"pos?": not_maker("gt"),
"neg?": not_maker("lt"),
"<": comp_maker("lt"),
"<=": comp_maker("le"),
"==": comp_maker("eq"),
">=": comp_maker("ge"),
">": comp_maker("gt"),
"!=": comp_maker("ne"),
"inc": """
ldr X0, [X19, #-8]
add X0, X0, #1
str X0, [X19, #-8]
""",
"dec": """
ldr X0, [X19, #-8]
sub X0, X0, #1
str X0, [X19, #-8]
"""
}

def clean_line(line):
    if 'VARIABLE' in line:
        return ''

    if line.startswith('ARR '):
        return ''

    if line.startswith('STRING '):
        return ''

    return line.split('\\')[0]

def bss(var):
    return f"""
{var}: .skip 8
"""

def bss_array(var):
    [name, size] = var
    return f"""
{name}: .skip {size}
"""


def compile_sym(s):

    commands = get_commands(s)
    if commands != None:
        return mapcat(compile_sym, commands)

    if len(s) > 1 and s != '..':
        for prefix, f in prefix_funcs:
            if s.startswith(prefix):
                t = s[len(prefix):]
                return [f(t)]

    if symbol == 'IF':
        return [emit_if()]
    if symbol == 'ELSE':
        return [emit_else()]
    if symbol == 'THEN':
        return [emit_then()]

    asm = plain_args.get(s)
    if asm:
        return [asm]

    return [push_stack(s)]

with open("index.mf", "r") as file_src:

    src = file_src.read()
    variables = re.findall(r"VARIABLE (\w+)", src)
    arrays = re.findall(r"ARR (\w+) (\d+)", src)

    assembly = []
    lines = src.split('\n')

    for line_src_ in lines:
        line_src = clean_line(line_src_)
        for symbol in re.findall(r"\S+", line_src):
            if is_recording():
                # don't add any steps
                add_command(symbol)
            else:
                for step in compile_sym(symbol):
                    assembly.append(step)

    # format
    with open("h.template.s") as file_template:
        template = file_template.read()
        strs = ''.join(keep(defstr, lines))
        text = '\n'.join(assembly)
        bss_defs = ''.join(map(bss, variables)) + ''.join(map(bss_array, arrays))

        out = template.format(strs, text, bss_defs)

        with open("h.s", "w") as file_out:
            file_out.write(out)
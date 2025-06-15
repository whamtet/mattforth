import re
from if_compiler import emit_if, emit_else, emit_then

def keep(f, s):
    return filter(lambda x: x, map(f, s))

def defstr(s):
    if s.startswith('STRING '):
        [a, b] = s[7:].split(': ')
        return f"""
{a}: .asciz "{b}\\n"
"""

def pr_str(s):
    return f"""
ldr X0, ={s}
bl printf
"""

def push_stack(value):
    return f"""
mov X3, #{value}
str X3, [X19], #8
"""

def store(var):
    return f"""

"""

func_args = {
"!": lambda var: f"""
ldr X0, [X19, #-8]!
ldr X1, ={var}
str X0, [X1]
""",
"@": lambda var: f"""
ldr X1, ={var}
ldr X0, [X1]
str X0, [X19], #8
"""
}

plain_args = {
"+": """
ldr X0, [X19, #-8]!
ldr X1, [X19, #-8]!
add X0, X0, X1
str X0, [X19], #8
""",
"-": """
ldr X0, [X19, #-8]!
ldr X1, [X19, #-8]!
sub X0, X0, X1
str X0, [X19], #8
""",
"*": """
ldr X0, [X19, #-8]!
ldr X1, [X19, #-8]!
mul X0, X0, X1
str X0, [X19], #8
""",
".": """
ldr     X0, =format
ldr X1, [X19, #-8]!
bl      printf
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
    size = int(size) * 8
    return f"""
{name}: .skip {size}
"""


def compile_sym(s, curr_variable):

    if symbol.startswith('.') and symbol != '.':
        return [pr_str(symbol[1:])]

    if symbol == 'IF':
        return [emit_if()]
    if symbol == 'ELSE':
        return [emit_else()]
    if symbol == 'THEN':
        return [emit_then()]

    asm = plain_args.get(s)
    if asm:
        return [asm] 

    f = func_args.get(s)
    if f:
        return [f(curr_variable)]

    return [push_stack(s)]

with open("index.mf", "r") as file_src:

    src = file_src.read()
    variables = re.findall(r"VARIABLE (\w+)", src)
    arrays = re.findall(r"ARR (\w+) (\d+)", src)

    symbols = set(variables)
    for array in arrays:
        symbols.add(array[0])

    curr_variable = None

    assembly = []
    lines = src.split('\n')

    for line_src_ in lines:
        line_src = clean_line(line_src_)
        for symbol in re.findall(r"\S+", line_src):
            if symbol in symbols:
                curr_variable = symbol
            elif symbol.startswith('.') and symbol != '.':
                assembly.append(pr_str(symbol[1:]))
            else:
                for step in compile_sym(symbol, curr_variable):
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
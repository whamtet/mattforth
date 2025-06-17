import re
from if_compiler import emit_if, emit_else, emit_then
from func_compiler import get_commands, add_command, is_recording
from loop_compiler import emit_loop, emit_loop_end
from map_compiler import emit_assoc, emit_get
from parser_compiler import emit_parser
from util import mapcat, keep

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

def print_maker(i):
    r = 'X' + str(21 + i * 2)
    return f"""
ldr X0, =format
mov X1, {r}
bl printf
"""

plain_args = {
"+": op_maker("add"),
"-": op_maker("sub"),
"*": op_maker("mul"),
"&": op_maker("and"),
".": """
ldr     X0, =format
ldr X1, [X19, #-8]!
bl      printf
""",
".i": print_maker(0),
".j": print_maker(1),
"..": """
ldr X0, [X19, #-8]!
bl printf
""",
# usage: 10 @x ?
"?": """
mov X8, #63
mov X0, #0
ldr X1, [X19, #-8]! // buffer
ldr X2, [X19, #-8] // count
// put the buffer back on the stack
str X1, [X19, #-8]
svc #0
// append zero at the end of the string
add X0, X0, X1
str xzr, [X0]
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
""",
"=str": """
ldr X0, [X19, #-8]!
ldr X1, [X19, #-8]
bl strcmp
str X0, [X19, #-8]
""",
"alloc-sm": """
ldr X0, [X19, #-8]
lsl X0, X0, #3
str X20, [X19, #-8]
add X20, X20, X0
""",
"alloc": """
    mov x0, #0                  // addr = NULL (let kernel choose)
    mov x1, #1048576            // length = 1 MiB
    mov x2, #3                  // prot = PROT_READ | PROT_WRITE (1|2 = 3)
    mov x3, #0x22               // flags = MAP_PRIVATE | MAP_ANONYMOUS (2|0x20 = 0x22)
    mov x4, #-1                 // fd = -1 (no file)
    mov x5, #0                  // offset = 0
    mov x8, #222                 // syscall number: mmap
    svc #0                       // make syscall
    str X0, [X19], #8 // address of region
""",
"getenv": """
ldr X0, [X19, #-8]
bl getenv
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

    if line.startswith('STRING0 '):
        return ''

    if line.startswith('CONST '):
        return ''

    return line.split('//')[0]

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

skip_prefix = set(['..', '.i', '.j', '.k'])

def compile_sym(s, constants):

    commands = get_commands(s)
    if commands != None:
        return mapcat(lambda x: compile_sym(x, constants), commands)

    if len(s) > 1 and s not in skip_prefix:
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

    if symbol == 'LOOP':
        return [emit_loop(0)]
    if symbol == 'LOOP2':
        return [emit_loop(1)]

    if symbol == 'LOOPEND':
        return [emit_loop_end(0)]
    if symbol == 'LOOPEND2':
        return [emit_loop_end(1)]

    if symbol == 'assoc':
        return [emit_assoc()]
    if symbol == 'get':
        return [emit_get()]

    if symbol == 'parse':
        return [emit_parser()]

    asm = plain_args.get(s)
    if asm:
        return [asm]

    v = constants.get(s)

    return [push_stack(v or s)]

with open("index.mf", "r") as file_src:

    src = file_src.read()
    variables = re.findall(r"VARIABLE (\w+)", src)
    arrays = re.findall(r"ARR (\w+): (\d+)", src)
    constants = dict(re.findall(r"CONST (\w+): (\d+)", src))

    assembly = []
    lines = src.split('\n')

    for line_src_ in lines:
        line_src = clean_line(line_src_)
        for symbol in re.findall(r"\S+", line_src):
            if is_recording():
                # don't add any steps
                add_command(symbol)
            else:
                for step in compile_sym(symbol, constants):
                    assembly.append(step)

    # format
    with open("h.template.s") as file_template:
        template = file_template.read()
        strs = ''.join(keep(defstr, lines)) + ''.join(keep(defstr0, lines))
        text = '\n'.join(assembly)
        bss_defs = ''.join(map(bss, variables)) + ''.join(map(bss_array, arrays))

        out = template.format(strs, text, bss_defs)

        with open("h.s", "w") as file_out:
            file_out.write(out)
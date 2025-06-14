import re

def push_stack(value):
    return f"""
mov X3, #{value}
str X3, [X19], #8
"""

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
    return line.split('\\')[0]


def compile_sym(s):
    asm = plain_args.get(s)
    if asm:
        return [asm] 

    return [push_stack(s)]

with open("index.mf", "r") as file_src:

    assembly = []

    for line_src_ in file_src:
        line_src = clean_line(line_src_)
        for symbol in re.findall(r"\S+", line_src):
            for step in compile_sym(symbol):
                assembly.append(step)

    # format
    with open("h.template.s") as file_template:
        template = file_template.read()
        out = template.format('\n'.join(assembly))

        with open("h.s", "w") as file_out:
            file_out.write(out)
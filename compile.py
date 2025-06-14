import re

def push_stack(value):
    return f"""
mov X3, #{value}
str X3, [X19]
add X19, X19, #64
"""

pop_stack = """
sub X19, X19, #64
ldr X1, [X19]
"""

print_c = """
ldr     x0, =format
bl      printf
"""

def clean_line(line):
    return line.split('\\')[0]

def compile_sym(s):
    if s == '.':
        return [pop_stack, print_c]

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
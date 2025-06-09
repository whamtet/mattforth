import re

def push_stack(value):
    return f"""
mov X3, #{value}
str X3, [X4]
add X4, X4, #64
"""

save_pointer = """
ldr X5, =pointer
str X4, [X5]
"""

load_pointer = """
ldr X4, =pointer
"""

def clean_line(line):
    return line.split('\\')[0]

def compile_sym(s):
    return push_stack(s)

with open("index.mf", "r") as file_src:

    assembly = []

    for line_src_ in file_src:
        line_src = clean_line(line_src_)
        for symbol in re.findall(r"\S+", line_src):
            assembly.append(compile_sym(symbol))

    assembly.append(save_pointer)
    assembly.append(load_pointer)

    # format
    with open("h.template.s") as file_template:
        template = file_template.read()
        out = template.format('\n'.join(assembly))

        with open("h.s", "w") as file_out:
            file_out.write(out)
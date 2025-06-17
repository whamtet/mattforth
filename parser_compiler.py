COUNTER = 0

# X0 base addr
# X1 offset
# X2 value
# X3 sum

def emit_parser():
    global COUNTER
    COUNTER += 1

    return f"""
ldr X0, [X19, #-8]
mov X1, #0
mov X3, #0
mov X4, #10

parse{COUNTER}:
ldrb W2, [X0, X1]
cmp W2, #0
b.eq parse_end{COUNTER}
cmp W2, #10 // newline
b.eq parse_end{COUNTER}
sub X2, X2, #48
mul X3, X3, X4
add X3, X3, X2
add X1, X1, #1
b parse{COUNTER}
parse_end{COUNTER}:
str X3, [X19, #-8]
"""
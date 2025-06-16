# hash = ((hash << 5) + hash) + c;

COUNTER = 0

def emit_hash():
    global COUNTER
    COUNTER += 1

# X0 base address
# X1 offset
# X2 char
# X3 sum
# X4 left shifted

    return f"""
ldr X0, [X19, #-8] // going to put it back
mov X1, #0
mov X3, #5381
hash{COUNTER}:
ldrb W2, [X0, X1]
cmp W2, #0
b.eq hash_end{COUNTER}
// body of the loop
lsl X4, X3, #5
add X3, X3, X4
add W3, W3, W2
add X1, X1, #1
b hash{COUNTER}
hash_end{COUNTER}:
str X3, [X19, #-8]
"""
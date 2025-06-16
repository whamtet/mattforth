from util import repeat_lines
# hash = ((hash << 5) + hash) + c;

COUNTER = 0

def bucket_check():
    return f"""
mov X0, X25
mov X1, X26
bl strcmp
cmp X0, #0
b.eq bucket_end{COUNTER}
add X26, X26, #16
"""

def emit_assoc():
    global COUNTER
    COUNTER += 1

# X25 address of k
# X1 offset
# X2 char
# X3 sum
# X4 left shifted
# X26 array

    return f"""
ldr X25, [X19, #-16] // going to put it back
mov X1, #0
mov X3, #5381
hash{COUNTER}:
ldrb W2, [X25, X1]
cmp W2, #0
b.eq hash_end{COUNTER}
// body of the loop
lsl X4, X3, #5
add X3, X3, X4
add W3, W3, W2
add X1, X1, #1
b hash{COUNTER}
hash_end{COUNTER}:
and X3, X3, #0xFF // get lowest byte
lsl X3, X3, #4 // 8 slots and two
ldr X26, [X19, #-24] // address of array
add X26, X26, X3 // check here
// now we can hardcode the equality check

{repeat_lines(7, bucket_check())}
bucket_end{COUNTER}:
add X26, X26, #8
ldr X0, [X19, #-8]
str X0, [X26]
// lastly pop two off the stack
sub X19, X19, #16
"""
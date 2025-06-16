from util import repeatedly_lines
# hash = ((hash << 5) + hash) + c;

COUNTER = 0

def bucket_check_assoc(i):
    return f"""

ldr X0, [X26]
cmp X0, #0 // if we're at a zero bucket
b.eq bucket_end{COUNTER} // we've found our spot

mov X1, X25
bl strcmp
cmp X0, #0 // if we've matched the key
b.eq bucket_end{COUNTER} // also found our spot
add X26, X26, #16 // try the next spot
"""

def bucket_check_get(i):
    return f"""

ldr X0, [X26]
cmp X0, #0 // if we're at a zero bucket
b.eq bucket_failure{COUNTER} // we've found our spot

mov X1, X25
bl strcmp
cmp X0, #0 // if we've matched the key
b.eq bucket_success{COUNTER} // also found our spot

add X26, X26, #16 // try the next spot
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
cmp W2, #0 // when we reach the null char
b.eq hash_end{COUNTER} // we have finished calculating the hash
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

{repeatedly_lines(7, bucket_check_assoc)}
bucket_end{COUNTER}:

str X25, [X26] // store k
ldr X0, [X19, #-8] // copy from top of the stack (v)
str X0, [X26, #8] // to one above X26

// lastly pop two off the stack
sub X19, X19, #16
"""

def emit_get():
    global COUNTER
    COUNTER += 1

# X25 address of k
# X1 offset
# X2 char
# X3 sum
# X4 left shifted
# X26 array

    return f"""
ldr X25, [X19, #-8] // going to put it back
mov X1, #0
mov X3, #5381
hash{COUNTER}:
ldrb W2, [X25, X1]
cmp W2, #0 // when we reach the null char
b.eq hash_end{COUNTER} // we have finished calculating the hash
// body of the loop
lsl X4, X3, #5
add X3, X3, X4
add W3, W3, W2
add X1, X1, #1
b hash{COUNTER}
hash_end{COUNTER}:
and X3, X3, #0xFF // get lowest byte
lsl X3, X3, #4 // 8 slots and two

ldr X26, [X19, #-16] // address of array
add X26, X26, X3 // check here
// now we can hardcode the equality check

{repeatedly_lines(7, bucket_check_get)}

// for get we have failure and success
bucket_failure{COUNTER}:
// simply store 0 at the top of stack
str xzr, [X19, #-8]
b bucket_end{COUNTER}

bucket_success{COUNTER}:
ldr X0, [X26, #8] // v
str X0, [X19, #-8]
bucket_end{COUNTER}:
"""
LOOP_COUNTER = 0

def emit_loop(offset):
    global LOOP_COUNTER

    if offset == 0:
        LOOP_COUNTER += 3

    counter = LOOP_COUNTER + offset
    r1 = 'X' + str(20 + offset * 2)
    r2 = 'X' + str(20 + offset * 2 + 1)

    return f"""
ldr {r2}, [X19, #-8]!
ldr {r1}, [X19, #-8]!

cmp {r1}, {r2}
b.eq loop_end{counter}
loop{counter}:
"""

def emit_loop_end(offset):

    counter = LOOP_COUNTER + offset
    r1 = 'X' + str(20 + offset * 2)
    r2 = 'X' + str(20 + offset * 2 + 1)

    return f"""
add {r1}, {r1}, #1
cmp {r1}, {r2}
b.ne loop{counter}
loop_end{counter}:
"""
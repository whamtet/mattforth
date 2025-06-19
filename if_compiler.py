IF_COUNTER = 0
IF_STACK = []

def push_if():
    IF_STACK.append((IF_COUNTER, False))
def push_else(counter):
    IF_STACK.append((counter, True))

def emit_if():
    global IF_COUNTER

    push_if()
    label = IF_COUNTER
    IF_COUNTER += 1 # for next time

    return f"""
ldr X0, [X19, #-8]!
cmp X0, #0
b.eq z{label}
"""

def emit_else():
    [counter, _] = IF_STACK.pop()
    push_else(counter)

    return f"""
b then{counter}
z{counter}:
"""

def emit_then():
    [counter, has_else] = IF_STACK.pop()
    end_label = "then" if has_else else "z"
    return end_label + str(counter) + ':'
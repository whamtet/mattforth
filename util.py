def keep(f, s):
    return filter(lambda x: x, map(f, s))

def mapcat(f, s):
    out = []
    for x in s:
        for y in f(x):
            out.append(y)
    return out

def repeat(n, x):
    return map(lambda _: x, range(n))

def repeat_lines(n, x):
    return '\n'.join(repeat(n, x))

def repeatedly(n, f):
    return map(f, range(n))

def repeatedly_lines(n, f):
    return '\n'.join(repeatedly(n, f))
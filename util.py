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

def maplast(f, s):
    out = []
    i = 0
    for x in s:
        i += 1
        out.append(f(i == len(s), x))

    return out

def maplast_lines(f, s):
    return '\n'.join(maplast(f, s))

def split2(a, b):
    x = a.split(b, 1)
    if len(x) == 1:
        return x[0], None
    else:
        return x[0], x[1]
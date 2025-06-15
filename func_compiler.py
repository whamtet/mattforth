FUNCS = {}

CURR_NAME = None
CURR_ASSEMBLY = None
ACCEPTING = False
RECORDING = False

def get_assembly(sym):
    global CURR_NAME, CURR_ASSEMBLY, ACCEPTING, RECORDING

    if ACCEPTING:
        CURR_NAME = sym
        ACCEPTING = False
        RECORDING = True
        CURR_ASSEMBLY = []

        return []

    elif sym == ':':
        ACCEPTING = True

        return []

    elif sym == ';':
        RECORDING = False
        FUNCS[CURR_NAME] = CURR_ASSEMBLY

        return []

    return FUNCS.get(sym)

def add_assembly(assembly):
    CURR_ASSEMBLY.append(assembly)

def is_recording():
    return RECORDING
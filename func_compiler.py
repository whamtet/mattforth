FUNCS = {}

CURR_NAME = None
CURR_COMMANDS = None
ACCEPTING = False
RECORDING = False

def get_commands(sym):
    global CURR_NAME, CURR_COMMANDS, ACCEPTING, RECORDING

    if ACCEPTING:
        CURR_NAME = sym
        ACCEPTING = False
        RECORDING = True
        CURR_COMMANDS = []

        return []

    elif sym == ':':
        ACCEPTING = True

        return []

    return FUNCS.get(sym)

def add_command(command):
    global RECORDING
    if command == ';':
        RECORDING = False
        FUNCS[CURR_NAME] = CURR_COMMANDS
    else:
        CURR_COMMANDS.append(command)

def is_recording():
    return RECORDING
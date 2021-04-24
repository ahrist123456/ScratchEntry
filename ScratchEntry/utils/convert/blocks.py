import utils.idgen as idgen

def convert(origin: dict, libs):
    blockids = {}
    header = []

    for i in origin:
        blockids[i] = idgen.getID()

        block = origin[i]
        try:
            if block["parent"] == None:
                header.append(i)
        except: pass

    ret = []
    for i in header:
        ret.append(chunkTrace(i, blockids, origin, libs))

    return ret

reps = {
    "event_whenflagclicked": 0,
    "event_whenkeypressed": 1,
    "event_whenthisspriteclicked": 2,
    "event_whenbroadcastreceived": 3,
    "control_wait": 4,
    "control_repeat": 5,
    "control_forever": 6,
    "control_if": 7,
    "control_if_else": 8,
    "control_wait_until": 9,
    "control_repeat_until": 10,
    "control_start_as_clone": 11,
    "control_create_clone_of": 12,
    "control_delete_this_clone": 13,

    "operator_add": 14, "operator_subtract": 15, 
    "operator_multiply": 16, "operator_divide": 17,

    "control_forever": 18, "control_repeat": 19,
}

rets = [
    "when_run_button_click",
    "when_some_key_pressed",
    "when_object_click",
    "when_message_cast",
    "wait_second",
    "repeat_basic",
    "repeat_inf",
    "_if",
    "if_else",
    "wait_until_true",
    "repeat_while_true",
    "when_clone_start",
    "create_clone",
    "delete_clone",

    #사칙연산자
    "calc_basic", "calc_basic", "calc_basic", "calc_basic",

    #반복
    "repeat_inf", "repeat_basic",
]

def chunkTrace(cur, blockids, origin, libs):
    ret = []
    while True:
        found = libs.find(origin[cur]["opcode"])
        if found != None:
            params = []
            for x in found["params"]:
                if x[0] == '"':
                    params.append(x[1:])
                elif x == '&VARIABLE':
                    params.append(libs.get_var(origin[cur]["fields"]["VARIABLE"][1]))
                else:
                    params.append(paramTrace(origin[cur]["inputs"][x], blockids, origin, libs))

            if found["type"] == "direct" or found["type"] == "operator":
                ret.append(getblock(blockids[cur], found["code"], params + [None]))

            elif found["type"] == "substk":
                substk = paramTrace(origin[cur]["inputs"]["SUBSTACK"], blockids, origin, libs)
                ret.append(getblock(blockids[cur], found["code"], params + [None], statement = [substk]))

        else:
            try: opcode = reps[origin[cur]["opcode"]]
            except: pass
            else:
                if opcode == 0:
                    ret.append(getblock(blockids[cur], rets[opcode], [None]))

                if opcode == 4:
                    param = paramTrace(origin[cur]["inputs"]["DURATION"], blockids, origin, libs)
                    ret.append(getblock(blockids[cur], rets[opcode], [param, None]))

        print(f"Converted: Block '{cur}'")

        if origin[cur]["next"] == None: break
        cur = origin[cur]["next"]

    return ret

def paramTrace(inputs, blockids, origin, libs):
    if inputs[0] == 1:
        return getblock(idgen.getID(), "text", [str(inputs[1][1])])
    elif inputs[0] == 3:
        if inputs[1][0] == 12:
            ret = getblock(idgen.getID(), "get_variable", [libs.get_var(inputs[1][2]), None])
            return ret
        else:
            ret = chunkTrace(inputs[1], blockids, origin, libs)
            return ret[0]
    elif inputs[0] == 2:
        ret = chunkTrace(inputs[1], blockids, origin, libs)
        return ret
    else:
        #todo
        pass

def getblock(id, type, params, statement = []):
    block = {
        "id": id, "type": type,
        "x": 0, "y": 0, "statements": [],
        "movable": None,
        "deletable": 1,
        "emphasized": False,
        "readOnly": None,
        "copyable": True,
        "statements": statement,
        "extensions": [],
        "params": params
    }
    return block
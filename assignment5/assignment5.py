#we are mostly interested in decompiled/dtu/compute/exec
from pathlib import Path
import json

dc = Path("course-02242-examples/decompiled/")
classes = {}
methods = {}

def find_method(am):
    return methods[(am)]

def print_bytecode(am):
    m = find_method(am)
    assert m is not None
    print(m["code"]["bytecode"])

def bytecode_interpr(am, log):
    memory = {} 
    mstack = [([], [], (am,  0))]
    for i in range(0, 10):
        log("->", mstack, end="")
        (localVar, operateStack, (am_, i))  = mstack[-1]
        b = find_method(am)["code"]["bytecode"][i]
        # print(b) 
        if b["opr"] == "return":
            if b["type"] == None:
                log("(return)")
                return None
            elif b["type"] == "int":
                log("(return)")
                return operateStack[-1]
            else:
                log("unsupported operation", b)
                return None
        elif b["opr"] == "push":
            log("(push)")
            v = b["value"]
            _ = mstack.pop()
            mstack.append((localVar, operateStack + [v["value"]], (am_, i+1))) 
        else:
            log("unsupported operation ", b)
            return None

     

    
     

if __name__ == '__main__':
    for f in dc.glob("**/*.json"):
        with open(f) as p:
            doc = json.load(p)
            classes[doc["name"]] = doc
    # print(classes)
    for cls in classes.values():
        for mtd in cls["methods"]:
            methods[(cls["name"], mtd["name"])] = mtd
    # for m in cases:
    #     print(m)
    print_bytecode(("dtu/compute/exec/Simple", "noop"))
    print('inter ')
    cases = [
        ("dtu/compute/exec/Simple", "noop"),
        ("dtu/compute/exec/Simple", "zero")
    ]
    for c in cases:
        print("---", c, "---")
        s = bytecode_interpr(c, print)
        print(s)
        print("---done---")
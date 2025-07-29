
from Instructions import *

#dict of valid instructions, extend from Instruction.py
instruction_dict = {
    "wait": wait,
    "jump": jump,
    "ramp": ramp,
}

#interpret instructions of the form (instr, target, duration) to voltages, base
def interpret_instructions(orders):
    base = 0.0 #voltage
    ans = []

    for (i, (instr, target, duration)) in enumerate(orders):
        if instr not in instruction_dict:
            raise ValueError(f'Instruction {i+1} type: "{instr}" is not one of {list(instruction_dict.keys())}')
        vals, base = instruction_dict[instr](i, base, target, duration) 
        
        ans += map(lambda x: round(4* x, 5) / 4, vals) #round to closest 2.5 microvolts      

    ans.append(0) #Reset to 0
    return ans
"""
File for any instructions, to have them in use, put them in the instruction_dict in Translator
All instructions must take 
    (
    Instruction number, 
    Base value for instrument in volts, 
    Target in volts, 
    Duration in seconds
    )
and return (
    [outputs in volts], 
    new base value
)
Target and duration must be None if unused

Technically less efficient than just having them in an if-else but this is far more extensible if you want that
Also could have None/Duration-unused checks be decorators but that seems excessive 
"""

def wait(i, base, target, duration): #Repeat base value over duration
    if target != None:
        raise ValueError(f'Intruction {i+1}: wait has target {target}, should be None')
    if duration == None:
        raise ValueError(f'Intruction {i+1}: wait has duration None, should be set')
    return [base] * safeInt(duration * 1000, i), base

def ramp(i, base, target, duration): #Smoothly change to base to target over duration
    if duration == None:
        raise ValueError(f'Intruction {i+1}: ramp has duration None, should be set')
    if target == None:
        raise ValueError(f'Intruction {i+1}: ramp has target None, should be set')
    
    #not including base but including target
    ret = [base + i * (target - base) / (duration * 1000) for i in range(1, safeInt(duration * 1000, i) + 1)] 
    base = target
    return ret, base

def jump(i, base, target, duration): #set base to target
    if duration != None:
        raise ValueError(f'Intruction {i+1}: jump has duration {target}, should be None')
    if target == None:
        raise ValueError(f'Intruction {i+1}: jump has target None, should be set')
    base = target
    return [base], base

def safeInt(n, i): #Check instructions are a whole number of milliseconds, i is for error handling
    ret = int(n)
    if ret != n:
        raise ValueError(f'Intruction {i+1}: duration is {n} milliseconds, instuctions must be in whole numbers of milliseconds')
    return ret

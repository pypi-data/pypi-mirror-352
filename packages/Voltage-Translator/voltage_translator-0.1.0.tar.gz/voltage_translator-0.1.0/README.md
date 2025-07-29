# Voltage-Translator

This module should be used for the instrument to translate instructions into voltages.

The only public function in this module is interpret_instructions. It takes an ordered collection of instructions and returns the output of those instructions as a list of voltages measured every millisecond.

Instructions are of the form: (instruction type, target voltage in Volts, duration in seconds)
There are 3 instruction types:
  "wait": Do nothing over the specified time (i.e. hold the voltage constant). The target voltage must be None.
  “ramp”: Ramp to the target voltage over the specified timeframe. This means that the instrument should increase the voltage in 1 ms increments over the specified time period, and end up at the value of the target voltage.
  “jump”: Go to the target voltage immediately. Duration must be None, as the operation will always take 1 ms.

For testing, we will need to test error handling and edge cases mostly. 
For error handling, we need try except clauses to check instruction and type errors. 
For the actual functionality, some simple examples will be needed and then ones that check empty inputs, less than millisecond time (and negative) and a check that return values are iterable. We will also probably want some sort of rounding beforehand on the tests to avoid floaing point errors and bit length issues. 

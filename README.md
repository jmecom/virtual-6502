# Virtual6502
An emulator of the NES 6502 CPU written in Python.

## Running
To enter interactive mode, run with `python3 main.py`.

To run a program you've written, pass the filename as an argument: `python3 main.py example.vsp`.

## Testing
You can test the CPU by running `python3 test_nestest.py`. This creates
a virtual Gamepak from the nestest ROM in test/ and compares the output
of the CPU to the log from nestest. Currently, the CPU does not complete
the test and thus is not yet suitable for use in an NES emulator. However, 
this should not affect your usage of the program, as the known issues don't
arise when used from the command line interface. 
If they do, please let me know!

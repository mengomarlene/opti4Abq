This directory contains example files for the opti4Abq toolbox.

./exampleTools contains python tools used in the 3 examples.
Each example directory (scalar1Param, 1D2Param, and xy2Param) contain 1 python model (which uses 1 inp file) and the associated experimental data.

Easiest way to run the examples (without changing much) is to copy the associated runOpti_xxx.py file in the root of the opti4Abq toolbox directory and run it with python (either double click or type "python runOpti_xxx.py" in the command line)
Note that the example files are set with absolute paths to search for external modules/files that need setting up and that all use the postPro4Abq toolbox to post-process the data!
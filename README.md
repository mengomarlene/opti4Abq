# opti4Abq
 An optimisation method in Python 2.X that runs on a set of abaqus models to minimise the difference (in a least square sense) between the FEA output and the a correspondong set of data — Edit 

The optimisation is done with the L-BFGS-B implementation in SciPy
The following Python modules are used: scipy.optimize, subprocess, numpy, and importlib if run with Python 2.X, X<7

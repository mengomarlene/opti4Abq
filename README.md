# opti4Abq
 An optimisation method in Python 2.X that runs on a set of abaqus models to minimise the difference (in a least square sense) between the FEA output and a corresponding set of data

The following Python modules are used: scipy.optimize, subprocess, numpy, and importlib if run with Python 2.7

The module **opti4AbqScalar** defines a residuals function which is minimised by the `scipy.optimize.minimize_scalar` method.
That residuals function copmutes FE models defined in python files stored in a given directory (modelsDir) and compare the output of those models with experimental data stored in a directory (expDir) - expDir and modelsDir can be the same directory.

## data and model preparation

The experimental data has to be stored for each model in a .ascii file whose name is the same as the name of the python file defining the corresponding model: if modelsDir contain `modelNumber1.py` and `modelNumber2.py` then expDir should contain `modelNumber1.ascii` and `modelNumber2.ascii`

Currently ([commit 05/03/15](https://github.com/mengomarlene/opti4Abq/commit/d52fb5bafc5eb999945969ccae9ff44282064711)), only data consisting of one single scalar values are supported.

The python files defining the abaqus models must define a model, a job, and a job analysis (with the `job.submit()` and `job.waitForCompletion()` commands).
The abaqus model must be function of the scalar parameter to optimise.
That scalar is passed to the abaqus model as a system argument.
A typical python file will contain the following block:
```python
import sys
optiParam = float(sys.argv[-1]) #reads the string argument as a float
job = parametrisedTests(optiParam) #defines the job through a function taking as argument the parameter to optimise
job.submit() #submit the abaqus job
job.waitForCompletion() # waits for the job to complete before allowing the system to do anything else
```

The post-processing of the FEA model must also be defined in this python file with a function called `postPro` and taking as arguments the name of the abaqus odb: def postPro(odbName). The values of interest (i.e. those similar to the experimental data) must be recoreded in a file called file `output.ascii` in the same format the experimental data is
A typical `postPro` function will open the odb, read some output values, do some mathematical operations on those values and write  the outcome into `output.ascii`

## how to use and what it does

The `opti4AbqScalar` module has to be called through its `main` function: main(modelDir,expdir)
A typical example using the module is defined in `runScalarOpti.py`

The `main` function also takes as optional arguments `pBounds`, a tuple of two floats/integers defining the boundaries of research of the parameter to optimize, and `options`, a dictionary of optimisation options as described in the exemple file

The `main` function returns the value of the parameter after optimisation, the value of the residual function for that parameter, the number of evaluations of the residuals function, and an optimisation message.

At each iteration of the optimisation process, a `verboseValues_X.ascii` (X being the iteration number) file is written in the working directory. It contains the iteration number, the value of the parameter at that iteration, the value of the residuals function at that iteration as well as a list of the values of each model output.

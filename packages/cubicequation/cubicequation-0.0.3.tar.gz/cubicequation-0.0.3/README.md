# Python cubic equation solver for exact values

A Python module for the exact solutions of a cubic equation: a x^3 + b x^2 + c x + d = 0

## Usage

### Calculate cubic solution
The solutions are three symexpress3 objects: x1Optimized, x2Optimized, x3Optimized
```py
>>> import cubicequation
>>> objCubic = cubicequation.CubicEquation()
>>> objCubic.a = "1"
>>> objCubic.b = "2"
>>> objCubic.c = "3"
>>> objCubic.d = "4"
>>> objCubic.calcSolutions()
>>> print( f"x1: {objCubic.x1Optimized}\nx2: {objCubic.x2Optimized}\nx3: {objCubic.x3Optimized}\n" )
x1: (-2/3) + (15 * 6^^(1/2) + 35)^^(1/3) * (-1/3) + (1/3) * (15 * 6^^(1/2) + (-35))^^(1/3)
x2: (-2/3) + (1/6) * (15 * 6^^(1/2) + 35)^^(1/3) + (-1/6) * (15 * 6^^(1/2) + 35)^^(1/3) * i * 3^^(1/2) + (-1/6) * i * 3^^(1/2) * (15 * 6^^(1/2) + (-35))^^(1/3) + (-1/6) * (15 * 6^^(1/2) + (-35))^^(1/3)
x3: (-2/3) + (15 * 6^^(1/2) + 35)^^(1/3) * (1/6) + (15 * 6^^(1/2) + 35)^^(1/3) * i * 3^^(1/2) * (1/6) + (1/6) * i * 3^^(1/2) * (15 * 6^^(1/2) + (-35))^^(1/3) + (-1/6) * (15 * 6^^(1/2) + (-35))^^(1/3)
```

### Numeric input values
The parameters may be real numbers or symexpress3 strings
```py
>>> import cubicequation
>>> objCubic = cubicequation.CubicEquation()
>>> objCubic.a = 1.10
>>> objCubic.b = 2.25
>>> objCubic.c = "2 + 1 + 3"
>>> objCubic.d = "4/2"
>>> objCubic.calcSolutions()
>>> print( f"x1: {objCubic.x1Optimized}\nx2: {objCubic.x2Optimized}\nx3: {objCubic.x3Optimized}\n" )
x1: (-15/22) + (-5/11) * ((11/25) * (3373/2)^^(1/2) + (-1349/200))^^(1/3) + (5/11) * ((11/25) * (3373/2)^^(1/2) + (1349/200))^^(1/3)
x2: (-15/22) + (5/22) * ((11/25) * (3373/2)^^(1/2) + (-1349/200))^^(1/3) + (-5/22) * i * 3^^(1/2) * ((11/25) * (3373/2)^^(1/2) + (-1349/200))^^(1/3) + (-5/22) * i * 3^^(1/2) * ((11/25) * (3373/2)^^(1/2) + (1349/200))^^(1/3) + (-5/22) * ((11/25) * (3373/2)^^(1/2) + (1349/200))^^(1/3)
x3: (-15/22) + (5/22) * ((11/25) * (3373/2)^^(1/2) + (-1349/200))^^(1/3) + (5/22) * i * 3^^(1/2) * ((11/25) * (3373/2)^^(1/2) + (-1349/200))^^(1/3) + (5/22) * i * 3^^(1/2) * ((11/25) * (3373/2)^^(1/2) + (1349/200))^^(1/3) + (-5/22) * ((11/25) * (3373/2)^^(1/2) + (1349/200))^^(1/3)
```

### Calculate real values
```py
>>> import cubicequation
>>> objCubic = cubicequation.CubicEquation()
>>> objCubic.a = 1.10
>>> objCubic.b = 2.25
>>> objCubic.c = "2 + 1 + 3"
>>> objCubic.d = "4/2"
>>> objCubic.calcSolutions()
>>> print( f"x1: {objCubic.x1Value}\nx2: {objCubic.x2Value}\nx3: {objCubic.x3Value}\n" )
x1: -0.3767589142748171
x2: (-0.8343478155898642-2.0321695851742962j)
x3: (-0.8343478155898642+2.0321695851742962j)
```

### Example optimized exact values
```py
>>> import cubicequation
>>> objCubic = cubicequation.CubicEquation()
>>> objCubic.a = 1
>>> objCubic.b = 6
>>> objCubic.c = 11
>>> objCubic.d = 6
>>> objCubic.calcSolutions()
>>> print( f"x1: {objCubic.x1Optimized}\nx2: {objCubic.x2Optimized}\nx3: {objCubic.x3Optimized}\n" )
x1: (-3)
x2: (-1)
x3: (-2)
```

### Command line
python -m cubicequation

- *Help*: python -m cubicequation  -h
- *Cubic solution*: python -m cubicequation 1 2 3 4

### Graphical user interface
https://github.com/SWVandenEnden/websym3

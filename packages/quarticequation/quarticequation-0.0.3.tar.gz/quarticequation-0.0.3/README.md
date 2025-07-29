# Python quartic equation solver for exact values

A Python module for the exact solutions of a quartic equation: a x^4 + b x^3 + c x^2 + d x + e = 0

## Usage

### Calculate quartic solution
The solutions are four symexpress3 objects: x1Optimized, x2Optimized, x3Optimized, x4Optimized
```py
>>> import quarticequation
>>> objQuartic = quarticequation.QuarticEquation()
>>> objQuartic.a = "1"
>>> objQuartic.b = "2"
>>> objQuartic.c = "3"
>>> objQuartic.d = "4"
>>> objQuartic.e = "5"
>>> objQuartic.calcSolutions()
>>> print( f"x1: {objQuartic.x1Optimized}\nx2: {objQuartic.x2Optimized}\nx3: {objQuartic.x3Optimized}\nx4: {objQuartic.x4Optimized}\n" )
x1: (-1/2) + ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(1/2) * (-1/2) + (1/2) * ((-2) + ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(-1/2) * 4 +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ))^^(1/2)
x2: (-1/2) + ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(1/2) * (-1/2) + ((-2) + ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(-1/2) * 4 +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ))^^(1/2) * (-1/2)
x3: (-1/2) + (1/2) * ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(1/2) + (1/2) * ((-2) + (-4) * ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(-1/2) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ))^^(1/2)
x4: (-1/2) + (1/2) * ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(1/2) + ((-2) + (-4) * ((-1) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ) * (-1))^^(-1/2) +  cos( (1/3) *  atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) *  sin( (1/3) *  atan( (1/2) ) ))^^(1/2) * (-1/2)```
```

### Numeric input values
The parameters may be real numbers or symexpress3 strings
```py
>>> import quarticequation
>>> objQuartic = quarticequation.QuarticEquation()
>>> objQuartic.a = 1.0
>>> objQuartic.b = -28
>>> objQuartic.c = "200 + 66"
>>> objQuartic.d = "-1028"
>>> objQuartic.e = "2730 / 2"
>>> objQuartic.calcSolutions()
>>> print( f"x1: {objQuartic.x1Optimized}\nx2: {objQuartic.x2Optimized}\nx3: {objQuartic.x3Optimized}\nx4: {objQuartic.x4Optimized}\n" )
x1: 5
x2: 3
x3: 13
x4: 7
```

### Calculate real values
```py
>>> import quarticequation
>>> objQuartic = quarticequation.QuarticEquation()
>>> objQuartic.a = 1
>>> objQuartic.b = 2
>>> objQuartic.c = 3
>>> objQuartic.d = 4
>>> objQuartic.e = 5
>>> objQuartic.calcSolutions()
>>> print( f"x1: {objQuartic.x1Value}\nx2: {objQuartic.x2Value}\nx3: {objQuartic.x3Value}\nx4: {objQuartic.x4Value}\n" )
x1: (-1.287815479557648+0.8578967583284903j)
x2: (-1.287815479557648-0.8578967583284903j)
x3: (0.2878154795576482+1.4160930801719078j)
x4: (0.28781547955764797-1.4160930801719078j)
```


### Command line
python -m quarticequation

- *Help*: python -m quarticequation  -h
- *Quartic solution*: python -m quarticequation 1 2 3 4 5

### Graphical user interface
https://github.com/SWVandenEnden/websym3

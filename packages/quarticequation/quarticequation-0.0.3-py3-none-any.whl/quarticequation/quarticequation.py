#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Quartic root calculation

    Copyright (C) 2024 Gien van den Enden - swvandenenden@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Calculations based on:
      https://en.wikipedia.org/wiki/Quartic_equation


"""

import symexpress3

class QuarticEquation():
  """
  Quartic equation solver, a x^4 + b x^3 + c x^2 + d x + e = 0
  Give the calculated values and the exact values in symexpress3 format.
  It gives the exact values from the standard quartic equation and the optimized expressions.
  """

  def __init__( self ):
    # defaults
    self._a           = '1'  # symexpress3
    self._b           = '0'
    self._c           = '0'
    self._d           = '0'
    self._e           = '0'
    self._output      = None # symexpress3.SymToHtml object
    self._realCalc    = True # boolean True = calculate real values
    # calculated values
    self._x1          = None # the solutions with the standard quartic equation
    self._x2          = None
    self._x3          = None
    self._x4          = None
    self._x1Optimized = None # the optimized solutions
    self._x2Optimized = None
    self._x3Optimized = None
    self._x4Optimized = None
    self._x1Value     = None # the calculated values
    self._x2Value     = None
    self._x3Value     = None
    self._x4Value     = None

  @property
  def a(self):
    """
    Parameter a
    """
    return self._a

  @a.setter
  def a(self, val):
    self._a = symexpress3.ConvertToSymexpress3String( val )

  @property
  def b(self):
    """
    Parameter b
    """
    return self._b

  @b.setter
  def b(self, val):
    self._b = symexpress3.ConvertToSymexpress3String( val )

  @property
  def c(self):
    """
    Parameter c
    """
    return self._c

  @c.setter
  def c(self, val):
    self._c = symexpress3.ConvertToSymexpress3String( val )

  @property
  def d(self):
    """
    Parameter d
    """
    return self._d

  @d.setter
  def d(self, val):
    self._d = symexpress3.ConvertToSymexpress3String( val )

  @property
  def e(self):
    """
    Parameter e
    """
    return self._e

  @e.setter
  def e(self, val):
    self._e = symexpress3.ConvertToSymexpress3String( val )

  @property
  def htmlOutput(self):
    """
    Set html output object
    """
    return self._output

  @htmlOutput.setter
  def htmlOutput(self, val):
    if val != None and ( not isinstance( val, symexpress3.SymToHtml )) :
      raise NameError( f'htmlOutput is incorrect: {type(val)}, expected SymToHtml object ' )
    self._output = val

  @property
  def realCalc(self):
    """
    Calc the real values of the solutions
    """
    return self._realCalc

  @realCalc.setter
  def realCalc(self, val):
    if not isinstance( val, bool ):
      raise NameError( f'realCalc is incorrect: {type(val)}, expected bool value' )
    self._realCalc = val

  #
  # read only properties
  #
  @property
  def x1(self):
    """
    The first solution
    """
    return self._x1

  @property
  def x2(self):
    """
    The second solution
    """
    return self._x2

  @property
  def x3(self):
    """
    The third solution
    """
    return self._x3

  @property
  def x4(self):
    """
    The fourth solution
    """
    return self._x4

  @property
  def x1Optimized(self):
    """
    The first solution, optimized
    """
    return self._x1Optimized

  @property
  def x2Optimized(self):
    """
    The second solution, optimized`
    """
    return self._x2Optimized

  @property
  def x3Optimized(self):
    """
    The third solution, optimized
    """
    return self._x3Optimized

  @property
  def x4Optimized(self):
    """
    The fourth solution, optimized
    """
    return self._x4Optimized

  @property
  def x1Value(self):
    """
    The calculated value of the first solution
    """
    return self._x1Value

  @property
  def x2Value(self):
    """
    The calculated value of the second solution
    """
    return self._x2Value

  @property
  def x3Value(self):
    """
    The calculated value of the third solution
    """
    return self._x3Value

  @property
  def x4Value(self):
    """
    The calculated value of the fourth solution
    """
    return self._x4Value


  #
  # Calculate the 4 solutions of the quartic equation
  #
  def calcSolutions(self):
    """
    Determined the four solutions of the quartic equation
    Based on https://en.wikipedia.org/wiki/Quartic_equation
    """

    #
    # based on https://en.wikipedia.org/wiki/Quartic_equation
    #
    self._x1Value    = None
    self._x2Value    = None
    self._x3Value    = None
    self._x4Value    = None

    fourthPowerStr  = "A x^^4 + B x^^3 + C x^^2 + D x + E"
    fourthpower2Str = "x^^4 + B / A x^^3 + C / A x^^2 + D / A x + E / A"
    xStr            = "u - B / 4A"

    uStr    = "(u -B/(4A))^^4 + (B/A)(4- B/(4A))^^3 + (C/A)(u - B/(4A))^^2 + (D/A)(4-B/(4A) + E/A"
    uOprStr = "u^^4 + ( (-3 B^^2 ) / (8 A^^2) + C/A) u^^2 + ( (B^^3)/(8 A^^3) - (B C)/(2 A^^2) + D/A) u + ( (-3 B^^4) / (256 A^^4) + (C B^^2)/(16 A^^3) - (B D )/(4 A^^2) + E/A)"

    aLittleStr = "(-3 B^^2)/(8 A^^2) + C/A"
    bLittleStr = "(B^^3)/(8 A^^3) - (B C )/(2 A^^2) + D/A"
    cLittleStr = "(-3 B^^4 )/(256 A^^4) + (C B^^2)/(16 A^^3) - (B D)/(4 A^^2) + E/A"

    # uResultStr = "u^^4 + a u^^2 + b u + c"

    # ySolStr ="2 y^^3 - a y^^2 - 2 c y + (a c - 1/4 b^^2) = (2 y - a )(y^^2 - c) - 1/4 b^^2 = 0"

    u1Str = "1/2 ( -1 (2 y -a )^^(1/2) + ( -2 y - a + (2 b)/( (2 y - a)^^(1/2) ))^^(1/2) )"
    u2Str = "1/2 ( -1 (2 y -a )^^(1/2) - ( -2 y - a + (2 b)/( (2 y - a)^^(1/2) ))^^(1/2) )"
    u3Str = "1/2 (    (2 y -a )^^(1/2) + ( -2 y - a - (2 b)/( (2 y - a)^^(1/2) ))^^(1/2) )"
    u4Str = "1/2 (    (2 y -a )^^(1/2) - ( -2 y - a - (2 b)/( (2 y - a)^^(1/2) ))^^(1/2) )"

    yStr = "a / 6 + w - p / ( 3 * w )"
    wStr = "(-q / 2 + (q^^2 / 4 + (p^^3)/27)^^(1/2) )^^(1/3)"
    pStr = "-1 (a^^2 / 12 ) - c"
    qStr = "-1 (a^^3 / 108) + ( a c ) / 3 - (b^^2) /8"

    x1Str = "u1 - B / (4 A)"
    x2Str = "u2 - B / (4 A)"
    x3Str = "u3 - B / (4 A)"
    x4Str = "u4 - B / (4 A)"

    dVars = {}
    dVars[ 'A' ] = self._a
    dVars[ 'B' ] = self._b
    dVars[ 'C' ] = self._c
    dVars[ 'D' ] = self._d
    dVars[ 'E' ] = self._e

    dVarsCalc = {}

    if self._output != None:
      self._output.writeVariables( dVars )
      self._output.writeLine( '' )

      fourthPowerExp = symexpress3.SymFormulaParser( fourthPowerStr )
      fourthPowerExp.optimize()
      fourthPowerExp.replaceVariable( dVars )
      fourthPowerExp.optimize( "setOnlyOne" )
      fourthPowerExp.optimize()

      self._output.writeSymExpress( fourthPowerExp, "Start expression" )
      self._output.writeLine( str( fourthPowerExp ) )
      self._output.writeLine( '' )

      self._output.writeLine( 'Based on <a href="https://en.wikipedia.org/wiki/Quartic_equation">https://en.wikipedia.org/wiki/Quartic_equation</a>' )
      self._output.writeLine( '' )


      fourthpower2Exp = symexpress3.SymFormulaParser( fourthpower2Str )
      fourthpower2Exp.optimize()
      self._output.writeSymExpress( fourthpower2Exp, "Expression with A eliminated" )
      self._output.writeLine( str( fourthpower2Exp ) )
      self._output.writeLine( '' )

      helpExpr = symexpress3.SymFormulaParser( xStr )
      helpExpr.optimize()
      self._output.writeSymExpress( helpExpr, "Substitute u for x" )
      self._output.writeLine( str( helpExpr ) )
      self._output.writeLine( '' )

      helpExpr = symexpress3.SymFormulaParser( uStr )
      helpExpr.optimize()
      self._output.writeSymExpress( helpExpr, "Expression in u" )
      self._output.writeLine( str( helpExpr ) )
      self._output.writeLine( '' )

      helpExpr = symexpress3.SymFormulaParser( uOprStr )
      helpExpr.optimize()
      self._output.writeSymExpress( helpExpr, "Expression in u optimized" )
      self._output.writeLine( str( helpExpr ) )
      self._output.writeLine( '' )


    aLittleExp = symexpress3.SymFormulaParser( aLittleStr )
    bLittleExp = symexpress3.SymFormulaParser( bLittleStr )
    cLittleExp = symexpress3.SymFormulaParser( cLittleStr )

    if self._output != None:
      dVarsCalc[ 'A' ] = symexpress3.SymFormulaParser(self._a).getValue()
      dVarsCalc[ 'B' ] = symexpress3.SymFormulaParser(self._b).getValue()
      dVarsCalc[ 'C' ] = symexpress3.SymFormulaParser(self._c).getValue()
      dVarsCalc[ 'D' ] = symexpress3.SymFormulaParser(self._d).getValue()
      dVarsCalc[ 'E' ] = symexpress3.SymFormulaParser(self._e).getValue()

    aLittleExp.optimize()
    bLittleExp.optimize()
    cLittleExp.optimize()

    if self._output != None:
      self._output.writeSymExpress( aLittleExp, "Variable a" )
      self._output.writeLine( str( aLittleExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( aLittleExp, dVarsCalc )
      self._output.writeLine( '' )

      self._output.writeSymExpress( bLittleExp, "Variable b" )
      self._output.writeLine( str( bLittleExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( bLittleExp, dVarsCalc )
      self._output.writeLine( '' )

      self._output.writeSymExpress( cLittleExp, "Variable c" )
      self._output.writeLine( str( cLittleExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( cLittleExp, dVarsCalc )
      self._output.writeLine( '' )

    pExp = symexpress3.SymFormulaParser( pStr )
    qExp = symexpress3.SymFormulaParser( qStr )
    wExp = symexpress3.SymFormulaParser( wStr )
    yExp = symexpress3.SymFormulaParser( yStr )

    pExp.optimize()
    qExp.optimize()
    wExp.optimize()
    yExp.optimize()

    u1Exp = symexpress3.SymFormulaParser( u1Str )
    u2Exp = symexpress3.SymFormulaParser( u2Str )
    u3Exp = symexpress3.SymFormulaParser( u3Str )
    u4Exp = symexpress3.SymFormulaParser( u4Str )

    x1Exp = symexpress3.SymFormulaParser( x1Str )
    x2Exp = symexpress3.SymFormulaParser( x2Str )
    x3Exp = symexpress3.SymFormulaParser( x3Str )
    x4Exp = symexpress3.SymFormulaParser( x4Str )

    u1Exp.optimize()
    u2Exp.optimize()
    u3Exp.optimize()
    u4Exp.optimize()

    x1Exp.optimize()
    x2Exp.optimize()
    x3Exp.optimize()
    x4Exp.optimize()

    if self._output != None and self._realCalc == True:
      try:
        # by 4 the same answers (x+2)^^4 you get error: 0.0 cannot be raised to a negative power
        # but you can optimize further for the correct answer
        # so we ignore this error
        dVarsCalc[ 'a' ] = aLittleExp.getValue( dVarsCalc )
        dVarsCalc[ 'b' ] = bLittleExp.getValue( dVarsCalc )
        dVarsCalc[ 'c' ] = cLittleExp.getValue( dVarsCalc )

        dVarsCalc[ 'p' ] = pExp.getValue( dVarsCalc )
        dVarsCalc[ 'q' ] = qExp.getValue( dVarsCalc )
        dVarsCalc[ 'w' ] = wExp.getValue( dVarsCalc )
        dVarsCalc[ 'y' ] = yExp.getValue( dVarsCalc )

      except Exception as exceptAll: # pylint: disable=broad-exception-caught
        self._output.writeLine( str( exceptAll ) )


    if self._output != None:
      self._output.writeSymExpress( u1Exp, "Variable u1" )
      self._output.writeLine( str( u1Exp ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( u2Exp, "Variable u2" )
      self._output.writeLine( str( u2Exp ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( u3Exp, "Variable u3" )
      self._output.writeLine( str( u3Exp ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( u4Exp, "Variable u4" )
      self._output.writeLine( str( u4Exp ) )
      self._output.writeLine( '' )


      self._output.writeSymExpress( x1Exp, "Variable x1" )
      self._output.writeLine( str( x1Exp ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x2Exp, "Variable x2" )
      self._output.writeLine( str( x2Exp ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x3Exp, "Variable x3" )
      self._output.writeLine( str( x3Exp ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x4Exp, "Variable x4" )
      self._output.writeLine( str( x4Exp ) )
      self._output.writeLine( '' )


    aLittleExp.replaceVariable( dVars )
    bLittleExp.replaceVariable( dVars )
    cLittleExp.replaceVariable( dVars )

    aLittleExp.optimize( "setOnlyOne" )
    bLittleExp.optimize( "setOnlyOne" )
    cLittleExp.optimize( "setOnlyOne" )

    aLittleExp.optimizeNormal()
    bLittleExp.optimizeNormal()
    cLittleExp.optimizeNormal()

    if self._output != None:
      self._output.writeSymExpress( pExp, "Variable p" )
      self._output.writeLine( str( pExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( pExp, dVarsCalc )
      self._output.writeLine( '' )

      self._output.writeSymExpress( qExp, "Variable q" )
      self._output.writeLine( str( qExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( qExp, dVarsCalc )
      self._output.writeLine( '' )

      self._output.writeSymExpress( wExp, "Variable w" )
      self._output.writeLine( str( wExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( wExp, dVarsCalc )
      self._output.writeLine( '' )

      self._output.writeSymExpress( yExp, "Variable y" )
      self._output.writeLine( str( yExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( yExp, dVarsCalc )
      self._output.writeLine( '' )

    if self._output != None:
      self._output.writeSymExpress( aLittleExp, "Variable a calculated" )
      self._output.writeLine( str( aLittleExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( aLittleExp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( bLittleExp, "Variable b calculated" )
      self._output.writeLine( str( bLittleExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( bLittleExp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( cLittleExp, "Variable c calculated" )
      self._output.writeLine( str( cLittleExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( cLittleExp )
      self._output.writeLine( '' )

    dVars[ 'a' ] = str( aLittleExp )
    dVars[ 'b' ] = str( bLittleExp )
    dVars[ 'c' ] = str( cLittleExp )

    pExp.replaceVariable( dVars )
    pExp.optimize( "setOnlyOne" )
    pExp.optimizeNormal()
    dVars[ 'p' ] = str( pExp )

    if self._output != None:
      self._output.writeSymExpress( pExp, "Variable p calculated" )
      self._output.writeLine( str( pExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( pExp )
      self._output.writeLine( '' )


    qExp.replaceVariable( dVars )
    qExp.optimize( "setOnlyOne" )
    qExp.optimizeNormal()
    dVars[ 'q' ] = str( qExp )

    if self._output != None:
      self._output.writeSymExpress( qExp, "Variable q calculated" )
      self._output.writeLine( str( qExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( qExp )
      self._output.writeLine( '' )


    wExp.replaceVariable( dVars )
    wExp.optimize( "setOnlyOne" )
    wExp.optimizeNormal()
    dVars[ 'w' ] = str( wExp )

    if self._output != None:
      self._output.writeSymExpress( wExp, "Variable w calculated" )
      self._output.writeLine( str( wExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( wExp )
      self._output.writeLine( '' )


    yExp.replaceVariable( dVars )
    yExp.optimize( "setOnlyOne" )
    yExp.optimizeNormal()
    dVars[ 'y' ] = str( yExp )

    if self._output != None:
      self._output.writeSymExpress( yExp, "Variable y calculated" )
      self._output.writeLine( str( yExp ) )
      if self._realCalc == True:
        self._output.writeGetValues( yExp )
      self._output.writeLine( '' )


    u1Exp.replaceVariable( dVars )
    u2Exp.replaceVariable( dVars )
    u3Exp.replaceVariable( dVars )
    u4Exp.replaceVariable( dVars )

    u1Exp.optimize( "setOnlyOne" )
    u2Exp.optimize( "setOnlyOne" )
    u3Exp.optimize( "setOnlyOne" )
    u4Exp.optimize( "setOnlyOne" )

    u1Exp.optimizeNormal()
    u2Exp.optimizeNormal()
    u3Exp.optimizeNormal()
    u4Exp.optimizeNormal()

    if self._output != None:
      self._output.writeSymExpress( u1Exp, "Variable u1 calculated" )
      self._output.writeLine( str( u1Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( u1Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( u2Exp, "Variable u2 calculated" )
      self._output.writeLine( str( u2Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( u2Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( u3Exp, "Variable u3 calculated" )
      self._output.writeLine( str( u3Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( u3Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( u4Exp, "Variable u4 calculated" )
      self._output.writeLine( str( u4Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( u4Exp )
      self._output.writeLine( '' )


    dVars[ 'u1' ] = str( u1Exp )
    dVars[ 'u2' ] = str( u2Exp )
    dVars[ 'u3' ] = str( u3Exp )
    dVars[ 'u4' ] = str( u4Exp )

    x1Exp.replaceVariable( dVars )
    x2Exp.replaceVariable( dVars )
    x3Exp.replaceVariable( dVars )
    x4Exp.replaceVariable( dVars )

    x1Exp.optimize( "setOnlyOne" )
    x2Exp.optimize( "setOnlyOne" )
    x3Exp.optimize( "setOnlyOne" )
    x4Exp.optimize( "setOnlyOne" )

    x1Exp.optimizeNormal()
    x2Exp.optimizeNormal()
    x3Exp.optimizeNormal()
    x4Exp.optimizeNormal()

    if self._output != None:
      self._output.writeSymExpress( x1Exp, "Variable x1 calculated" )
      self._output.writeLine( str( x1Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x1Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x2Exp, "Variable x2 calculated" )
      self._output.writeLine( str( x2Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x2Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x3Exp, "Variable x3 calculated" )
      self._output.writeLine( str( x3Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x3Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x4Exp, "Variable x4 calculated" )
      self._output.writeLine( str( x4Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x4Exp )
      self._output.writeLine( '' )


    self._x1 = x1Exp.copy()
    self._x2 = x2Exp.copy()
    self._x3 = x3Exp.copy()
    self._x4 = x4Exp.copy()

    x1Exp.optimizeExtended()
    x2Exp.optimizeExtended()
    x3Exp.optimizeExtended()
    x4Exp.optimizeExtended()

    self._x1Optimized = x1Exp
    self._x2Optimized = x2Exp
    self._x3Optimized = x3Exp
    self._x4Optimized = x4Exp

    if self._realCalc == True:
      self._x1Value = self._x1Optimized.getValue()
      self._x2Value = self._x2Optimized.getValue()
      self._x3Value = self._x3Optimized.getValue()
      self._x4Value = self._x4Optimized.getValue()

    if self._output != None:
      self._output.writeSymExpress( x1Exp, "Variable x1 optimized calculated" )
      self._output.writeLine( str( x1Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x1Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x2Exp, "Variable x2 optimized calculated" )
      self._output.writeLine( str( x2Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x2Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x3Exp, "Variable x3 optimized calculated" )
      self._output.writeLine( str( x3Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x3Exp )
      self._output.writeLine( '' )

      self._output.writeSymExpress( x4Exp, "Variable x4 optimized calculated" )
      self._output.writeLine( str( x4Exp ) )
      if self._realCalc == True:
        self._output.writeGetValues( x4Exp )
      self._output.writeLine( '' )

    if self._realCalc == True and self._output != None:
      self._output.writeLine( f'x1: {self._x1Value}' )
      self._output.writeLine( f'x2: {self._x2Value}' )
      self._output.writeLine( f'x3: {self._x3Value}' )
      self._output.writeLine( f'x4: {self._x4Value}' )

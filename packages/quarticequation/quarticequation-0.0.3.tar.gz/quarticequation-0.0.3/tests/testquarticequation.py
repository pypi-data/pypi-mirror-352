#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Test quartic equation

    Copyright (C) 2021 Gien van den Enden - swvandenenden@gmail.com

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

"""

from datetime import datetime

import symexpress3
import quarticequation

testData = [ # 1   x^^4 + 10 * x^^3 + 35 * x^^2 + 50 * x + 24  = (x+1)(x+2)(x+3)(x+4)
             { 'a' : '1'
             , 'b' : '10'
             , 'c' : '35'
             , 'd' : '50'
             , 'e' : '24'
             , 'x1opt' : '-3'
             , 'x2opt' : '-4'
             , 'x3opt' : '-1'
             , 'x4opt' : '-2'
             }
           , # 2   x^^4 + x^^3 * 8 + x^^2 * 24 + x * 32 + 16  = (x+2)(x+2)(x+2)(x+2)
             { 'a' : '1'
             , 'b' : '8'
             , 'c' : '24'
             , 'd' : '32'
             , 'e' : '16'
             , 'x1opt' : '-2'
             , 'x2opt' : '-2'
             , 'x3opt' : '-2'
             , 'x4opt' : '-2'
             }
           , # 3   x^^4 + (-28) * x^^3 + 266 * x^^2 + (-1028) * x + 1365  = (x-3)(x-7)(x-5)(x-13)
             { 'a' :     1
             , 'b' :   -28
             , 'c' :   266
             , 'd' : -1028
             , 'e' :  1365
             , 'x1opt' :  '5'
             , 'x2opt' :  '3'
             , 'x3opt' : '13'
             , 'x4opt' :  '7'
             }
           , # 4   x^^4 + 2 * x^^3 + 3 * x^^2 + 4 * x + 5 
             { 'a' : 1
             , 'b' : 2
             , 'c' : 3
             , 'd' : 4
             , 'e' : 5
             , 'x1opt' : '(-1/2) + ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(1/2) * (-1/2) + (1/2) * ((-2) + ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(-1/2) * 4 + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ))^^(1/2)'
             , 'x2opt' : '(-1/2) + ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(1/2) * (-1/2) + ((-2) + ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(-1/2) * 4 + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ))^^(1/2) * (-1/2)'
             , 'x3opt' : '(-1/2) + (1/2) * ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(1/2) + (1/2) * ((-2) + (-4) * ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(-1/2) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ))^^(1/2)'
             , 'x4opt' : '(-1/2) + (1/2) * ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(1/2) + ((-2) + (-4) * ((-1) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ) * (-1))^^(-1/2) + cos( (1/3) * atan( (1/2) ) ) * 15^^(1/2) * (-1) + 5^^(1/2) * sin( (1/3) * atan( (1/2) ) ))^^(1/2) * (-1/2)'
             }
           ]

startTime = datetime.now()

# test quartic equation
iTests = 0
iGood  = 0
iBad   = 0

clsQuartic = quarticequation.QuarticEquation()
clsQuartic.realCalc = False

for dData in testData :
  iTests += 1
  print( f"Test: {iTests}", end='\r')

  clsQuartic.a = dData.get( 'a' )
  clsQuartic.b = dData.get( 'b' )
  clsQuartic.c = dData.get( 'c' )
  clsQuartic.d = dData.get( 'd' )
  clsQuartic.d = dData.get( 'd' )
  clsQuartic.e = dData.get( 'e' )

  clsQuartic.calcSolutions()

  clsCheck1 = symexpress3.SymFormulaParser( dData.get( 'x1opt' )  )
  clsCheck2 = symexpress3.SymFormulaParser( dData.get( 'x2opt' )  )
  clsCheck3 = symexpress3.SymFormulaParser( dData.get( 'x3opt' )  )
  clsCheck4 = symexpress3.SymFormulaParser( dData.get( 'x4opt' )  )

  clsCheck1.optimizeNormal()
  clsCheck2.optimizeNormal()
  clsCheck3.optimizeNormal()
  clsCheck4.optimizeNormal()

  if ( (not clsCheck1.isEqual( clsQuartic.x1Optimized )) or
       (not clsCheck2.isEqual( clsQuartic.x2Optimized )) or
       (not clsCheck3.isEqual( clsQuartic.x3Optimized )) or
       (not clsCheck4.isEqual( clsQuartic.x4Optimized ))   ):
    iBad += 1

    print( f'Entry {iTests} not equal'  )
    print( f' x1 : {clsQuartic.x1Optimized}, expected: {clsCheck1}' )
    print( f' x2 : {clsQuartic.x2Optimized}, expected: {clsCheck2}' )
    print( f' x3 : {clsQuartic.x3Optimized}, expected: {clsCheck3}' )
    print( f' x4 : {clsQuartic.x4Optimized}, expected: {clsCheck4}' )

  else:
    iGood += 1

endTime   = datetime.now()
timeInSec = ( endTime - startTime ).total_seconds()

print( f"Number of tests: {iTests}, passed: {iGood}, failed; {iBad}, total time: {timeInSec} (sec)" )

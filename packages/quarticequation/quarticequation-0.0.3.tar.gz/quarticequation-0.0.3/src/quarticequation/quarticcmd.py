#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Command line interface

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

"""

import symexpress3
import quarticequation


def CalcSolutions( quarticVars, outputFormat ):
  """
  Calculate the quartic solutions
  """
  if len( quarticVars ) == 0:
    print( "No parameters are given, nothing to calculate" )
    return

  if len( quarticVars ) > 5:
    print( f"Only the first 5 parameters are used, found {len( quarticVars )} parameters" )

  # default output format, solutions as string and calculated values
  if outputFormat in( "", None ):
    outputFormat = "sc"

  try:

    clsQuartic = quarticequation.QuarticEquation()
    output   = None

    # set variables
    for iCount, varData in enumerate( quarticVars ):
      # print( f"iCount: {iCount}, data: {varData}" )
      # pylint: disable=multiple-statements
      if   iCount == 0: clsQuartic.a = symexpress3.ConvertToSymexpress3String( varData )
      elif iCount == 1: clsQuartic.b = symexpress3.ConvertToSymexpress3String( varData )
      elif iCount == 2: clsQuartic.c = symexpress3.ConvertToSymexpress3String( varData )
      elif iCount == 3: clsQuartic.d = symexpress3.ConvertToSymexpress3String( varData )
      elif iCount == 4: clsQuartic.e = symexpress3.ConvertToSymexpress3String( varData )
      else:
        break

    # must set real calculation before starting
    if 'c' in outputFormat:
      clsQuartic.realCalc = True
    else:
      clsQuartic.realCalc = False

    if 'h' in outputFormat:
      output = symexpress3.SymToHtml( None, "Quartic equation" )
      clsQuartic.htmlOutput = output

    # calculate the solutions
    clsQuartic.calcSolutions()

    # output data
    for cOutput in outputFormat:
      if cOutput == "s":
        print( f"x1: {clsQuartic.x1Optimized}" )
        print( f"x2: {clsQuartic.x2Optimized}" )
        print( f"x3: {clsQuartic.x3Optimized}" )
        print( f"x4: {clsQuartic.x4Optimized}" )

      elif cOutput == "n":
        print( f"x1 not optimized: {clsQuartic.x1}" )
        print( f"x2 not optimized: {clsQuartic.x2}" )
        print( f"x3 not optimized: {clsQuartic.x3}" )
        print( f"x4 not optimized: {clsQuartic.x4}" )

      elif cOutput == "c":
        print( f"x1 value: {clsQuartic.x1Value}" )
        print( f"x2 value: {clsQuartic.x2Value}" )
        print( f"x3 value: {clsQuartic.x3Value}" )
        print( f"x4 value: {clsQuartic.x4Value}" )

      elif cOutput == "h":
        pass # do nothing html (output) is already set

      else:
        print( f"Unknown output format '{cOutput}' ignored" )

    if output != None:
      output.closeFile()
      output = None

  except Exception as exceptAll: # pylint: disable=broad-exception-caught
    print( f"Error: {str( exceptAll )}" )



def DisplayVersion():
  """
  Display version information
  """
  print( "Version    : " + quarticequation.__version__    )

  print( "Author     : " + quarticequation.__author__     )
  print( "Copyright  : " + quarticequation.__copyright__  )
  print( "License    : " + quarticequation.__license__    )
  print( "Maintainer : " + quarticequation.__maintainer__ )
  print( "Email      : " + quarticequation.__email__      )
  print( "Status     : " + quarticequation.__status__     )


def DisplayHelp():
  """
  Display help
  """
  print( "Give the exact solutions of a quartic equation: a x^4 + b x^3 + c x^2 + d x + e = 0" )
  print( " " )
  print( "usage: python -m quarticequation [options] [arg]" )
  print( "options: " )
  print( "  -h           : Help" )
  print( "  -v           : Version information" )
  print( "  -o <format>  : Output format" )
  print( "                 s - string format (default)" )
  print( "                 n - not optimized solutions in string format" )
  print( "                 c - calculated values (default)" )
  print( "                 h - html" )
  print( "arg:" )
  print( "a b c d" )
  print( "The arguments can be a symexpress3 string or a real number" )
  print( " " )
  print( "Example: " )
  print( 'python -m quarticequation -o nsc 1 2 3 4 5' )

def CommandLine( argv ):
  """
  Process the quartic equation command line parameters
  """
  outputFormat  = ""
  quarticvars     = []

  nrarg = len( argv )

  # nothing given, then display help
  if nrarg <= 1:
    DisplayHelp()

  mode = ""
  for iCnt in range( 1, nrarg ) :
    cArg = argv[ iCnt ]

    if mode == "output":
      outputFormat = cArg
      mode = ""
      continue

    if cArg == "-h" :
      DisplayHelp()
      return  # direct stop by help

    if cArg == "-v" :
      DisplayVersion()
      return  # direct stop by version information

    if cArg == "-o":
      mode = "output"

    else:
      if cArg.startswith( "-" ):
        print( f"Unknown option: {cArg}, use -h for help")
      else:
        # collect arguments
        quarticvars.append( cArg )

  CalcSolutions( quarticvars, outputFormat )


# ---------------------------
# The end
# ---------------------------

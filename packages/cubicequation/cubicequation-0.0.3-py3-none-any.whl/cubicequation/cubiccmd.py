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
import cubicequation


def CalcSolutions( cubicVars, outputFormat ):
  """
  Calculate the cubic solutions
  """
  if len( cubicVars ) == 0:
    print( "No parameters are given, nothing to calculate" )
    return

  if len( cubicVars ) > 4:
    print( f"Only the first 4 parameters are used, found {len( cubicVars )} parameters" )

  # default output format, solutions as string and calculated values
  if outputFormat in( "", None ):
    outputFormat = "sc"

  try:

    clsCubic = cubicequation.CubicEquation()
    output   = None

    # set variables
    for iCount, varData in enumerate( cubicVars ):
      # print( f"iCount: {iCount}, data: {varData}" )
      # pylint: disable=multiple-statements
      if   iCount == 0: clsCubic.a = symexpress3.ConvertToSymexpress3String( varData )
      elif iCount == 1: clsCubic.b = symexpress3.ConvertToSymexpress3String( varData )
      elif iCount == 2: clsCubic.c = symexpress3.ConvertToSymexpress3String( varData )
      elif iCount == 3: clsCubic.d = symexpress3.ConvertToSymexpress3String( varData )
      else:
        break

    # must set real calculation before starting
    if 'c' in outputFormat:
      clsCubic.realCalc = True
    else:
      clsCubic.realCalc = False

    if 'h' in outputFormat:
      output = symexpress3.SymToHtml( None, "Cubic equation" )
      clsCubic.htmlOutput = output

    # calculate the solutions
    clsCubic.calcSolutions()

    # output data
    for cOutput in outputFormat:
      if cOutput == "s":
        print( f"x1: {clsCubic.x1Optimized}" )
        print( f"x2: {clsCubic.x2Optimized}" )
        print( f"x3: {clsCubic.x3Optimized}" )

      elif cOutput == "n":
        print( f"x1 not optimized: {clsCubic.x1}" )
        print( f"x2 not optimized: {clsCubic.x2}" )
        print( f"x3 not optimized: {clsCubic.x3}" )

      elif cOutput == "c":
        print( f"x1 value: {clsCubic.x1Value}" )
        print( f"x2 value: {clsCubic.x2Value}" )
        print( f"x3 value: {clsCubic.x3Value}" )

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
  print( "Version    : " + cubicequation.__version__    )

  print( "Author     : " + cubicequation.__author__     )
  print( "Copyright  : " + cubicequation.__copyright__  )
  print( "License    : " + cubicequation.__license__    )
  print( "Maintainer : " + cubicequation.__maintainer__ )
  print( "Email      : " + cubicequation.__email__      )
  print( "Status     : " + cubicequation.__status__     )


def DisplayHelp():
  """
  Display help
  """
  print( "Give the exact solutions of a cubic equation: a x^3 + b x^2 + c x + d = 0" )
  print( " " )
  print( "usage: python -m cubicequation [options] [arg]" )
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
  print( 'python -m cubicequation -o nsc 1 2 3 4' )

def CommandLine( argv ):
  """
  Process the cubic equation command line parameters
  """
  outputFormat  = ""
  cubicvars     = []

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
        cubicvars.append( cArg )

  CalcSolutions( cubicvars, outputFormat )


# ---------------------------
# The end
# ---------------------------

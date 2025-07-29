#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Cubic root calculation

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
      https://en.wikipedia.org/wiki/Cubic_equation

    More information cubic root:
      https://staff.fnwi.uva.nl/j.vandecraats/CG.pdf

"""

import symexpress3

class CubicEquation():
  """
  Cubic equation solver, a x^4 + b x^3 + c x + d = 0
  Give the calculated values and the exact values in symexpress3 format.
  It gives the exact values from the standard cubic equation and the optimized expressions.
  """

  def __init__( self ):
    # defaults
    self._a           = '1'   # symexpress3 string
    self._b           = '0'
    self._c           = '0'
    self._d           = '0'
    self._output      = None  # symexpress3.SymToHtml object
    self._realCalc    = True  # boolean True = calc real values

    # calculated values
    self._x1          = None  # the solutions with the standard cubic equation
    self._x2          = None
    self._x3          = None
    self._x1Optimized = None  # the optimized solutions
    self._x2Optimized = None
    self._x3Optimized = None
    self._x1Value     = None  # the calculated values
    self._x2Value     = None
    self._x3Value     = None

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
  def htmlOutput(self):
    """
    Html output object, see symexpress3.SymToHtml()
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
    Calculate the real values of the solutions, default is True.
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
    The first solution (x1), in symepxress3 format
    """
    return self._x1

  @property
  def x2(self):
    """
    The second solution (x2), in symepxress3 format
    """
    return self._x2

  @property
  def x3(self):
    """
    The third solution (x3), in symepxress3 format
    """
    return self._x3

  @property
  def x1Optimized(self):
    """
    The first solution (x1) in optimized symexpress3 format
    """
    return self._x1Optimized

  @property
  def x2Optimized(self):
    """
    The second solution (x2) in optimized symexpress3 format
    """
    return self._x2Optimized

  @property
  def x3Optimized(self):
    """
    The third solution (x3)  in optimized symexpress3 format
    """
    return self._x3Optimized

  @property
  def x1Value(self):
    """
    The calculated value of the first solution (x1)
    """
    return self._x1Value

  @property
  def x2Value(self):
    """
    The calculated value of the second solution (x2)
    """
    return self._x2Value

  @property
  def x3Value(self):
    """
    The calculated value of the third solution (x3)
    """
    return self._x3Value


  #
  # Calc the 3 solutions of the cubic equation
  #
  def calcSolutions(self):
    """
    Determined the three solutions of the cubic equation.
    Based on https://en.wikipedia.org/wiki/Cubic_equation
    """

    self._x1Value    = None
    self._x2Value    = None
    self._x3Value    = None

    orgForm = "a * x^^3 + b * x^^2 + c * x + d"
    delta0  = "b^^2 - 3 a c"
    delta1  = "2 b^^3 - 9 a b c + 27 a^2 d"

    epsilon = "( -1 + i (3)^^(1/2) ) / 2"

    bigC    = "( ( delta1 + (delta1^^2 - 4 delta0^^3)^^(1/2) ) / 2 )^^(1/3)"

    x1 = "-1/(3a) * (b + bigC              + delta0 / bigC )"
    x2 = "-1/(3a) * (b + epsilon   * bigC  + delta0 / ( epsilon   * bigC ) )"
    x3 = "-1/(3a) * (b + epsilon^2 * bigC  + delta0 / ( epsilon^2 * bigC ) )"

    oOrgForm = symexpress3.SymFormulaParser( orgForm  )
    oDelta0  = symexpress3.SymFormulaParser( delta0   )
    oDelta1  = symexpress3.SymFormulaParser( delta1   )
    oEpsilon = symexpress3.SymFormulaParser( epsilon  )
    oBigC    = symexpress3.SymFormulaParser( bigC     )
    oX1      = symexpress3.SymFormulaParser( x1       )
    oX2      = symexpress3.SymFormulaParser( x2       )
    oX3      = symexpress3.SymFormulaParser( x3       )

    oDelta0.optimizeExtended()
    oDelta1.optimizeExtended()

    oEpsilon.optimizeExtended()

    oBigC.optimizeExtended()

    oX1.optimizeExtended()
    oX2.optimizeExtended()
    oX3.optimizeExtended()

    dVars = {}
    dVars[ 'a' ] = self._a
    dVars[ 'b' ] = self._b
    dVars[ 'c' ] = self._c
    dVars[ 'd' ] = self._d

    # it only works correct with principals
    oOrgForm.replaceVariable( dVars )
    oOrgForm.optimize( "setOnlyOne" )
    oOrgForm.optimize()

    if self._output != None:
      self._output.writeVariables( dVars )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oOrgForm, "Start expression" )
      self._output.writeLine( str( oOrgForm ) )
      self._output.writeLine( '' )

      self._output.writeLine( 'Based on <a href="https://en.wikipedia.org/wiki/Cubic_equation">https://en.wikipedia.org/wiki/Cubic_equation</a>' )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oDelta0, 'Delta 0' )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oDelta1, 'Delta 1' )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oEpsilon, 'Epsilon' )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oBigC, 'bigC' )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oX1, 'x1' )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oX2, 'x2' )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oX3, 'x3' )
      self._output.writeLine( '' )

    dDictBigC = {}
    dDictBigC[ 'delta0' ] = str( oDelta0 )
    dDictBigC[ 'delta1' ] = str( oDelta1 )

    oBigC.replaceVariable( dDictBigC )
    oBigC.optimize( "setOnlyOne" )
    oBigC.optimizeNormal( )

    if self._output != None:
      self._output.writeSymExpress( oBigC, 'bigC filled delta0 and delta1' )
      self._output.writeLine( str( oBigC ) )
      self._output.writeLine( '' )

    dDictX = {}
    dDictX[ 'epsilon' ] = str( oEpsilon )
    dDictX[ 'bigC'    ] = str( oBigC    )
    dDictX[ 'delta0'  ] = str( oDelta0  )
    dDictX[ 'delta1'  ] = str( oDelta1  )

    oX1.replaceVariable( dDictX )
    oX1.optimize( "setOnlyOne" )
    oX1.optimizeNormal( )

    oX2.replaceVariable( dDictX )
    oX2.optimize( "setOnlyOne" )
    oX2.optimizeNormal( )

    oX3.replaceVariable( dDictX )
    oX3.optimize( "setOnlyOne" )
    oX3.optimizeNormal( )

    if self._output != None:
      self._output.writeSymExpress( oX1, 'x1 filled bigC and epsilon' )
      self._output.writeLine( str( oX1 ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oX2, 'x2 filled bigC and epsilon' )
      self._output.writeLine( str( oX2 ) )
      self._output.writeLine( '' )

      self._output.writeSymExpress( oX3, 'x3 filled bigC and epsilon' )
      self._output.writeLine( str( oX3 ) )
      self._output.writeLine( '' )


    # fill in the variables
    dVars = {}
    dVars[ 'a' ] = str( self._a )
    dVars[ 'b' ] = str( self._b )
    dVars[ 'c' ] = str( self._c )
    dVars[ 'd' ] = str( self._d )

    oX1.replaceVariable( dVars )
    oX1.optimize( "setOnlyOne" )

    if self._output != None:
      self._output.writeSymExpress( oX1, 'x1 filled' )
      self._output.writeLine( str( oX1 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX1, None, None, "Result x1" )
        self._output.writeLine('')

    oX1.optimizeNormal( )

    if self._output != None:
      self._output.writeSymExpress( oX1, 'x1 filled and optimized' )
      self._output.writeLine( str( oX1 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX1, None, None, "Result x1" )
        self._output.writeLine('')


    oX2.replaceVariable( dVars )
    oX2.optimize( "setOnlyOne" )

    if self._output != None:
      self._output.writeSymExpress( oX2, 'x2 filled' )
      self._output.writeLine( str( oX2 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX2, None, None, "Result x2" )
        self._output.writeLine('')

    oX2.optimizeNormal( )

    if self._output != None:
      self._output.writeSymExpress( oX2, 'x2 filled and optimized' )
      self._output.writeLine( str( oX2 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX2, None, None, "Result x2" )
        self._output.writeLine('')


    oX3.replaceVariable( dVars )
    oX3.optimize( "setOnlyOne" )

    if self._output != None:
      self._output.writeSymExpress( oX3, 'x3 filled' )
      self._output.writeLine( str( oX3 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX3, None, None, "Result x3" )
        self._output.writeLine('')

    oX3.optimizeNormal( )

    if self._output != None:
      self._output.writeSymExpress( oX3, 'x3 filled and optimized' )
      self._output.writeLine( str( oX3 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX3, None, None, "Result x3" )
        self._output.writeLine('')

    self._x1 = oX1.copy()
    self._x2 = oX2.copy()
    self._x3 = oX3.copy()


    oX1.optimizeExtended()

    if self._output != None:
      self._output.writeSymExpress( oX1, 'x1 optimized extended' )
      self._output.writeLine( str( oX1 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX1, None, None, "Result x1" )
        self._output.writeLine('')


    oX2.optimizeExtended( )

    if self._output != None:
      self._output.writeSymExpress( oX2, 'x2 optimized extended' )
      self._output.writeLine( str( oX2 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX2, None, None, "Result x2" )
        self._output.writeLine('')


    oX3.optimizeExtended( )

    if self._output != None:
      self._output.writeSymExpress( oX3, 'x3 optimized extended' )
      self._output.writeLine( str( oX3 ) )
      if self._realCalc == True:
        self._output.writeGetValues( oX3, None, None, "Result x3" )
        self._output.writeLine('')


    self._x1Optimized = oX1.copy()
    self._x2Optimized = oX2.copy()
    self._x3Optimized = oX3.copy()

    if self._realCalc == True:
      self._x1Value    = self._x1Optimized.getValue()
      self._x2Value    = self._x2Optimized.getValue()
      self._x3Value    = self._x3Optimized.getValue()

      if self._output != None:
        self._output.writeLine( 'x1: ' + str( self._x1Value  ) )
        self._output.writeLine( 'x2: ' + str( self._x2Value  ) )
        self._output.writeLine( 'x3: ' + str( self._x3Value  ) )

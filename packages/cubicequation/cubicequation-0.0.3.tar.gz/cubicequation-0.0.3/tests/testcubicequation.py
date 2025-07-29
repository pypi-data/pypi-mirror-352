#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Test cubic equation

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
import cubicequation

testData = [ # 1   x^^3 + x^^2 + x + 1 = (x-1)(x-i)(x+i)
             { 'a' : '1'
             , 'b' : '1'
             , 'c' : '1'
             , 'd' : '1'
             , 'x1opt' : '-1'
             , 'x2opt' : '-i'
             , 'x3opt' : 'i'
             }
           , # 2   x^^3 + x^^2 * (-6) + x * 11 + (-6)  = (x-1)(x-2)(x-3)
             { 'a' : '1'
             , 'b' : '-6'
             , 'c' : '11'
             , 'd' : '-6'
             , 'x1opt' : '1'
             , 'x2opt' : '3'
             , 'x3opt' : '2'
             }
           , # 3   x^^3 + x^^2 * 9 + x * 27 + 27   = (x+3)(x+3)(x+3)
             { 'a' : '1'
             , 'b' : '9'
             , 'c' : '27'
             , 'd' : '27'
             , 'x1opt' : '-3'
             , 'x2opt' : '-3'
             , 'x3opt' : '-3'
             }
           , # 4   x^^3 + x^^2 * 11 + x * 35 + 25  = (x+5)(x+1)(x+5)
             { 'a' : '1'
             , 'b' : '11'
             , 'c' : '35'
             , 'd' : '25'
             , 'x1opt' : '-5'
             , 'x2opt' : '-1'
             , 'x3opt' : '-5'
             }
           , # 5    4 * x^^3 + 3 * x^^2 + 2 * x + 1
             { 'a' : '4'
             , 'b' : '3'
             , 'c' : '2'
             , 'd' : '1'
             , 'x1opt' : '(-1/4) + (60 * 6^^(1/2) + 135)^^(1/3) * (-1/12) + (1/12) * (60 * 6^^(1/2) + (-135))^^(1/3)'
             , 'x2opt' : '(-1/4) + (1/24) * (60 * 6^^(1/2) + 135)^^(1/3) + (-1/24) * (60 * 6^^(1/2) + 135)^^(1/3) * i * 3^^(1/2) + (-1/24) * i * 3^^(1/2) * (60 * 6^^(1/2) + (-135))^^(1/3) + (-1/24) * (60 * 6^^(1/2) + (-135))^^(1/3)'
             , 'x3opt' : '(-1/4) + (60 * 6^^(1/2) + 135)^^(1/3) * (1/24) + (60 * 6^^(1/2) + 135)^^(1/3) * (1/24) * i * 3^^(1/2) + (1/24) * i * 3^^(1/2) * (60 * 6^^(1/2) + (-135))^^(1/3) + (-1/24) * (60 * 6^^(1/2) + (-135))^^(1/3)'
             }
           , # 6
             { 'a' : '1/4'
             , 'b' : '1/5'
             , 'c' : '1/6'
             , 'd' : '2/7'
             # , 'x1opt' : '(-4/15) + ((23/5600) * 2690^^(1/2) + (1481/7000))^^(1/3) * (-4/3) + (4/3) * ((23/5600) * 2690^^(1/2) + (-1481/7000))^^(1/3)'
             , 'x1opt' : '(-4/15) + (-2/3) * ((23/70) * (269/10)^^(1/2) + (1481/875))^^(1/3) + (2/3) * ((23/70) * (269/10)^^(1/2) + (-1481/875))^^(1/3)'
             # , 'x2opt' : '(-4/15) + (2/3) * ((23/5600) * 2690^^(1/2) + (1481/7000))^^(1/3) + (-2/3) * ((23/5600) * 2690^^(1/2) + (1481/7000))^^(1/3) * i * 3^^(1/2) + (-1/3) * i * 3^^(1/2) * ((23/700) * 2690^^(1/2) + (-1481/875))^^(1/3) + (-1/3) * ((23/700) * 2690^^(1/2) + (-1481/875))^^(1/3)'
             , 'x2opt' : '(-4/15) + (1/3) * ((23/70) * (269/10)^^(1/2) + (1481/875))^^(1/3) + (-1/3) * i * 3^^(1/2) * ((23/70) * (269/10)^^(1/2) + (1481/875))^^(1/3) + (-1/3) * i * 3^^(1/2) * ((23/70) * (269/10)^^(1/2) + (-1481/875))^^(1/3) + (-1/3) * ((23/70) * (269/10)^^(1/2) + (-1481/875))^^(1/3)'
             # , 'x3opt' : '(-4/15) + ((23/5600) * 2690^^(1/2) + (1481/7000))^^(1/3) * (2/3) + ((23/5600) * 2690^^(1/2) + (1481/7000))^^(1/3) * (2/3) * i * 3^^(1/2) + (1/3) * i * 3^^(1/2) * ((23/700) * 2690^^(1/2) + (-1481/875))^^(1/3) + (-1/3) * ((23/700) * 2690^^(1/2) + (-1481/875))^^(1/3)'
             , 'x3opt' : '(-4/15) + (1/3) * ((23/70) * (269/10)^^(1/2) + (1481/875))^^(1/3) + (1/3) * i * 3^^(1/2) * ((23/70) * (269/10)^^(1/2) + (1481/875))^^(1/3) + (1/3) * i * 3^^(1/2) * ((23/70) * (269/10)^^(1/2) + (-1481/875))^^(1/3) + (-1/3) * ((23/70) * (269/10)^^(1/2) + (-1481/875))^^(1/3)'
             }
           , # 7  105 * x^^3 + x^^2 * (-73/3) + x * (589/315) + (-1/21) = (3x-1/5)(5x-3/7)(7x-5/9)
             { 'a' : '105'
             , 'b' : '-73/3'
             , 'c' : '589/315'
             , 'd' : '-1/21'
             , 'x1opt' : '1/15'
             , 'x2opt' : '3/35'
             , 'x3opt' : '5/63'
             }
           ]

startTime = datetime.now()

# test cubic equation
iTests = 0
iGood  = 0
iBad   = 0

clsCubic = cubicequation.CubicEquation()
clsCubic.realCalc = False

for dData in testData :
  iTests += 1
  print( f"Test: {iTests}", end='\r')

  clsCubic.a = dData.get( 'a' )
  clsCubic.b = dData.get( 'b' )
  clsCubic.c = dData.get( 'c' )
  clsCubic.d = dData.get( 'd' )

  clsCubic.calcSolutions()

  clsCheck1 = symexpress3.SymFormulaParser( dData.get( 'x1opt' )  )
  clsCheck2 = symexpress3.SymFormulaParser( dData.get( 'x2opt' )  )
  clsCheck3 = symexpress3.SymFormulaParser( dData.get( 'x3opt' )  )

  clsCheck1.optimizeNormal()
  clsCheck2.optimizeNormal()
  clsCheck3.optimizeNormal()

  if ( (not clsCheck1.isEqual( clsCubic.x1Optimized )) or
       (not clsCheck2.isEqual( clsCubic.x2Optimized )) or
       (not clsCheck3.isEqual( clsCubic.x3Optimized ))   ):
    iBad += 1

    print( f'Entry {iTests} not equal'  )
    print( f' x1 : {clsCubic.x1Optimized}, expected: {clsCheck1}' )
    print( f' x2 : {clsCubic.x2Optimized}, expected: {clsCheck2}' )
    print( f' x3 : {clsCubic.x3Optimized}, expected: {clsCheck3}' )

  else:
    iGood += 1

endTime   = datetime.now()
timeInSec = ( endTime - startTime ).total_seconds()

print( f"Number of tests: {iTests}, passed: {iGood}, failed; {iBad}, total time: {timeInSec} (sec)" )

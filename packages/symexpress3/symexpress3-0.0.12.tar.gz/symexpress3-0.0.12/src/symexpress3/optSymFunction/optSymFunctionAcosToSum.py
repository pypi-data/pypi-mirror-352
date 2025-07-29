#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    acos to sum for Sym Express 3

    Copyright (C) 2025 Gien van den Enden - swvandenenden@gmail.com

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


    https://proofwiki.org/wiki/Power_Series_Expansion_for_Real_Arccosine_Function
    https://en.wikipedia.org/wiki/List_of_trigonometric_identities

"""

from symexpress3 import symexpress3
from symexpress3 import optFunctionBase
from symexpress3 import symtools

class OptSymFunctionAcosToSum( optFunctionBase.OptFunctionBase ):
  """
  Convert asin to sum
  """
  def __init__( self ):
    super().__init__()
    self._name         = "acosToSum"
    self._desc         = "Convert acos to sum"
    self._funcName     = "acos"                    # name of the function
    self._minparams    = 1                        # minimum number of parameters
    self._maxparams    = 1                        # maximum number of parameters


  def optimize( self, elem, action ):
    if self.checkType( elem, action ) != True:
      return None

    elemParam = elem.elements[ 0 ]

    # https://proofwiki.org/wiki/Power_Series_Expansion_for_Real_Arccosine_Function
    varName = symtools.VariableGenerateGet()
    elemSym = symexpress3.SymFormulaParser( f"pi / 2 - sum( {varName}, 0 ,infinity, factorial( 2 * {varName} ) / ( exp( 2 * {varName}, 2) * factorial( {varName})^^2) * exp( ( 2 * {varName} ) + 1, x) / ( 2 * {varName} + 1)" )

    dDict = {}
    dDict[ 'x' ] = str( elemParam )

    elemSym.replaceVariable( dDict )

    elemSym.powerCounter     = elem.powerCounter
    elemSym.powerDenominator = elem.powerDenominator
    elemSym.powerSign        = elem.powerSign
    elemSym.onlyOneRoot      = elem.onlyOneRoot

    return elemSym

#
# Test routine (unit test), see testsymexpress3.py
#
def Test( display = False):
  """
  Unit test
  """
  symtools.VariableGenerateReset()

  symTest = symexpress3.SymFormulaParser( "acos(pi/4)" )
  symTest.optimize()
  symTest = symTest.elements[ 0 ]

  # print( "symTest: " + str( symTest ))

  testClass = OptSymFunctionAcosToSum()
  symNew    = testClass.optimize( symTest, "acosToSum" )

  if display == True :
    print( f"naam      : {testClass.name}" )
    print( f"orginal   : {str( symTest )}" )
    print( f"optimized : {str( symNew  )}" )

  if str( symNew ).strip() != "pi * 2^^-1 + (-1) *  sum( n1,0,infinity, factorial( 2 * n1 ) * ( exp( 2 * n1,2 ) *  factorial( n1 )^^2)^^-1 *  exp( 2 * n1 + 1,pi * 1 * 4^^-1 ) * (2 * n1 + 1)^^-1 )":
    print( f"Error unit test {testClass.name} function" )
    raise NameError( f'SymFunction optimize {testClass.name}, unit test error: {str( symTest )}, value: {str( symNew )}' )

if __name__ == '__main__':
  Test( True )

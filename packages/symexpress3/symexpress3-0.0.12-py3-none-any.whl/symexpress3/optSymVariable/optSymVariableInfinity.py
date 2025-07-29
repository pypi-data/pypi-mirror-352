#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Simplify infinity for Sym Express 3

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


"""

from symexpress3 import symexpress3
from symexpress3 import optTypeBase

class OptSymVariableInfinity( optTypeBase.OptTypeBase ):
  """
  Simplify i
  """
  def __init__( self ):
    super().__init__()
    self._name         = "infinity"
    self._symtype      = symexpress3.SymVariable
    self._desc         = "Simplify infinity"

  def optimize( self, elem, action ):
    if self.checkType( elem, action ) != True:
      return None

    if elem.name != 'infinity' :
      return None

    if elem.powerCounter != 1 or elem.powerDenominator != 1 or elem.onlyOneRoot != 1:
      elemNew = elem.copy()
      elemNew.powerCounter     = 1
      elemNew.powerDenominator = 1
      elemNew.onlyOneRoot      = 1
      return elemNew

    return None

#
# Test routine (unit test), see testsymexpress3.py
#
def Test( display = False):
  """
  Unit test
  """
  symTest = symexpress3.SymVariable( 'infinity', 1, 2, 1, 1 )

  testClass = OptSymVariableInfinity()
  symNew    = testClass.optimize( symTest, "infinity" )

  if display == True :
    print( f"naam      : {testClass.name}" )
    print( f"orginal   : {str( symTest )}" )
    print( f"optimized : {str( symNew  )}" )

  if str( symNew ).strip() != "infinity":
    print( f"Error unit test {testClass.name} function" )
    raise NameError( f'SymVariable optimize {testClass.name}, unit test error: {str( symTest )}, value: {symNew}' )

if __name__ == '__main__':
  Test( True )

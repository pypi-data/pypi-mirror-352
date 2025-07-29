#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    IntegralResult function for Sym Express 3

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


   	https://www.mathsisfun.com/calculus/integration-rules.html
    https://en.wikipedia.org/wiki/Lists_of_integrals
    https://en.wikibooks.org/wiki/Calculus/Integration_techniques

"""

from symexpress3         import symexpress3
from symexpress3.symfunc import symFuncBase

class SymFuncIntegralResult( symFuncBase.SymFuncBase ):
  """
  IntegralResult function, integralresult( <function>,<delta>,<lower>,<upper> )
  The result of integral() but the lower and upper value are not inserted.
  This function insert the upper and lower value
  """
  def __init__( self ):
    super().__init__()
    self._name        = "integralresult"
    self._desc        = "integralresult( <function>,<delta>,<lower>,<upper> )"
    self._minparams   = 4    # minimum number of parameters
    self._maxparams   = 4    # maximum number of parameters
    self._syntax      = "integralresult( <function>,<delta>,<lower>,<upper> )"
    self._synExplain  = "The result of integral() but the lower and upper value are not inserted"


  def mathMl( self, elem ):
    if self._checkCorrectFunction( elem ) != True:
      return [], None

    output = ""

    output += '<msubsup>'

    output += "<mfenced separators='' open='|' close='|'>"
    output += elem.elements[ 0 ].mathMl()
    output += "</mfenced>"

    output += elem.elements[ 2 ].mathMl()
    output += elem.elements[ 3 ].mathMl()

    output += '</msubsup>'

    return [ '()' ], output


  def functionToValue( self, elem ):
    if self._checkCorrectFunction( elem ) != True:
      return None

    cVar = self.getVarname( elem.elements[1] )
    if cVar == None:
      return None

    # first work out the arrays
    if elem.existArray() == True:
      return None

    # if there is a integral or derivative then do nothing. This must be first be done
    dictFunc = elem.getFunctions()
    if "integral" in dictFunc:
      return None
    if "derivative" in dictFunc:
      return None

    elemNew = symexpress3.SymExpress( '+' )
    elemNew.powerSign        = elem.powerSign
    elemNew.powerCounter     = elem.powerCounter
    elemNew.powerDenominator = elem.powerDenominator
    elemNew.onlyOneRoot      = elem.onlyOneRoot

    dDictRep = {}

    dDictRep[ cVar ] = str( elem.elements[2] )
    elemLower = elem.elements[ 0 ].copy()
    elemLower.replaceVariable( dDictRep )

    dDictRep[ cVar ] = str( elem.elements[3] )
    elemUpper = elem.elements[ 0 ].copy()
    elemUpper.replaceVariable( dDictRep )

    elemMin = symexpress3.SymExpress('*')
    elemMin.add( symexpress3.SymNumber( -1, 1, 1 ))
    elemMin.add( elemLower )

    elemNew.add( elemUpper )
    elemNew.add( elemMin   )

    return elemNew


  def getValue( self, elemFunc, dDict = None ):
    if self._checkCorrectFunction( elemFunc ) != True:
      return None

    cVar = self.getVarname( elemFunc.elements[1] )
    if cVar == None:
      return None

    dDictRep = {}

    dDictRep[ cVar ] = str( elemFunc.elements[2] )
    elemLower = elemFunc.elements[ 0 ].copy()
    elemLower.replaceVariable( dDictRep )

    dDictRep[ cVar ] = str( elemFunc.elements[3] )
    elemUpper = elemFunc.elements[ 0 ].copy()
    elemUpper.replaceVariable( dDictRep )

    dValue = elemUpper.getValue(dDict) - elemLower.getValue(dDict)

    dValue = elemFunc.valuePow( dValue )

    return dValue


#
# Test routine (unit test), see testsymexpress3.py
#
def Test( display = False):
  """
  Unit test
  """
  def _Check( testClass, symTest, value, dValue, valueCalc, dValueCalc ):
    dValue     = round( float(dValue)    , 10 )
    if dValueCalc != None:
      dValueCalc = round( float(dValueCalc), 10 )
    if display == True :
      print( f"naam    : {testClass.name}" )
      print( f"function: {str( symTest )}" )
      print( f"Value   : {str( value   )}" )
      print( f"DValue  : {str( dValue  )}" )

    if str( value ).strip() != valueCalc or (dValueCalc != None and dValue != dValueCalc) : # pylint: disable=consider-using-in
    # if (dValueCalc != None and dValue != dValueCalc) : # pylint: disable=consider-using-in
      print( f"Error unit test {testClass.name} function" )
      raise NameError( f'function {testClass.name}, unit test error: {str( symTest )}, value: {value} <> {valueCalc}, dValue:{dValue} <> {dValueCalc}' )


  symTest = symexpress3.SymFormulaParser( 'integralresult( 4x, x, 0, 5' )
  symTest.optimize()
  testClass = SymFuncIntegralResult()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "4 * 5 + (-1) * 4 * 0", 20.0 )


if __name__ == '__main__':
  Test( True )

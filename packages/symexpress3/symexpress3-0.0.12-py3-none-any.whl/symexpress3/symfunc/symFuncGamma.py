#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Gamma function for Sym Express 3

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


    https://en.wikipedia.org/wiki/Gamma_function

"""

import mpmath

from symexpress3         import symexpress3
from symexpress3.symfunc import symFuncBase
from symexpress3         import symtools


class SymFuncGamma( symFuncBase.SymFuncBase ):
  """
  Gamma function
  """
  def __init__( self ):
    super().__init__()
    self._name        = "gamma"
    self._desc        = "Gamma function"
    self._minparams   = 1    # minimum number of parameters
    self._maxparams   = 1    # maximum number of parameters
    self._syntax      = "gamma(<n>)"
    self._synExplain  = "gamma(<n>)"

  def mathMl( self, elem ):
    if self._checkCorrectFunction( elem ) != True:
      return [], None

    output = ""

    output += '<mi>&Gamma;</mi>'

    # output += "<mfenced>"

    output += elem.mathMlParameters()

    # output += "</mfenced>"

    return [], output


  def functionToValue( self, elem ):

    def _toFactorial( elem1 ):
      """
      Convert gamma to factorial
      """
      if not isinstance( elem1, symexpress3.SymNumber ) :
        return None

      if elem1.factDenominator != 1:
        return None

      if elem1.factSign != 1:
        return None

      if elem1.factCounter <= 0:
        return None

      elemNew = symexpress3.SymFunction( "factorial" )
      elemPlus = symexpress3.SymExpress( '+' )
      elemPlus.add( elem1 )
      elemPlus.add( symexpress3.SymNumber( -1, 1, 1 ) )
      elemNew.add( elemPlus )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew

    def _toIntegral( elem1 ):
      """
      Convert gamma to integral if the real part is positive
      """
      try:
        val = elem1.getValue()
      except: # pylint: disable=bare-except
        return None

      if isinstance( val, (float, mpmath.mpf )):
        if val <= 0:
          return None
      elif isinstance( val, (complex, mpmath.mpc)):
        if val.real <= 0:
          return None
      else:
        return None

      varName = symtools.VariableGenerateGet()
      varElem = str( elem1 )
      cElem = f"integral(exp( ({varElem} - 1),  {varName}) * exp({varName} * -1), {varName}, 0,infinity )"

      elemNew = symexpress3.SymFormulaParser( cElem )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew

    def _convNegative( elem1 ):
      """
      Convert negative gamma to positive gamma for non integer values
      """
      try:
        val = elem1.getValue()
      except: # pylint: disable=bare-except
        return None

      if isinstance( val, (float, mpmath.mpf )):
        if val >= 0:
          return None

        # integer values not allowed
        if mpmath.floor( val ) == mpmath.ceil( val ):
          return None

      elif isinstance( val, (complex, mpmath.mpc)):
        if val.real >= 0:
          return None

        # integer values not allowed
        if mpmath.floor( val.real ) == mpmath.ceil( val.real ):
          return None

      else:
        return None

      varElem = str( elem1 )
      cElem = f"(1/gamma( ({varElem}) * (-1) + 1)) * ( pi / sin( pi * (  ({varElem}) * (-1) + 1 ) )"

      elemNew = symexpress3.SymFormulaParser( cElem )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew


    if self._checkCorrectFunction( elem ) != True:
      return None

    if elem.numElements() != 1:
      return None

    elem1 = elem.elements[0]

    elemNew = _toFactorial( elem1 )
    if elemNew != None:
      return elemNew

    elemNew = _toIntegral( elem1 )
    if elemNew != None:
      return elemNew

    elemNew = _convNegative( elem1 )
    if elemNew != None:
      return elemNew


    return elemNew


  def _getValueSingle( self, dValue, dValue2 = None ):
    return mpmath.gamma( dValue  )

#
# Test routine (unit test), see testsymexpress3.py
#
def Test( display = False):
  """
  Unit test
  """
  def _Check(  testClass, symTest, value, dValue, valueCalc, dValueCalc ):
    if dValue != None:
      dValue     = round( float(dValue)    , 10 )

    if dValueCalc != None:
      dValueCalc = round( float(dValueCalc), 10 )

    if display == True :
      print( f"naam    : {testClass.name}" )
      print( f"function: {str( symTest )}" )
      print( f"Value   : {str( value   )}" )
      print( f"DValue  : {str( dValue  )}" )

    if str( value ).strip() != valueCalc or dValue != dValueCalc:
      print( f"Error unit test {testClass.name} function" )
      raise NameError( f'function {testClass.name}, unit test error: {str( symTest )}, value: {value} <> {valueCalc}, dValue:{dValue} <> {dValueCalc}' )

  symtools.VariableGenerateReset()

  symTest = symexpress3.SymFormulaParser( 'gamma( 7 )' )
  symTest.optimize()
  testClass = SymFuncGamma()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check(  testClass, symTest, value, dValue, "factorial( 7 + (-1) )", 720 )


  symTest = symexpress3.SymFormulaParser( 'gamma( 1/2 )' )
  symTest.optimize()
  testClass = SymFuncGamma()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check(  testClass, symTest, value, dValue, "integral(  exp( (1 * 2^^-1 + (-1) * 1),n1 ) *  exp( n1 * (-1) ),n1,0,infinity )", 1.7724538509 )


  symTest = symexpress3.SymFormulaParser( 'gamma( -1/2 )' )
  symTest.optimize()
  testClass = SymFuncGamma()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check(  testClass, symTest, value, dValue, "1 *  gamma( (-1) * 1 * 2^^-1 * (-1) + 1 )^^-1 * pi *  sin( pi * ((-1) * 1 * 2^^-1 * (-1) + 1) )^^-1", -3.5449077018  )

if __name__ == '__main__':
  Test( True )

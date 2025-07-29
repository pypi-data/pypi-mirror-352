#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Hypergeometric function for Sym Express 3

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


    https://en.wikipedia.org/wiki/Generalized_hypergeometric_function

    https://docs.sympy.org/latest/modules/simplify/hyperexpand.html
    https://github.com/sympy/sympy/blob/master/sympy/simplify/hyperexpand.py

    https://mathoverflow.net/questions/424518/does-any-hyper-geometric-function-can-be-analytically-continuated-to-the-whole-c
    https://dlmf.nist.gov/15.2
    https://encyclopediaofmath.org/wiki/Hypergeometric_function
    https://fa.ewi.tudelft.nl/~koekoek/documents/wi4006/hyper.pdf

    analytic continuation of 2F1
    https://www.sciencedirect.com/science/article/pii/S0377042700002673



    _2F_1(a, b; c; z) = (1-z)^{-a} {}_2F_1(c-a, b; c; 1-z).

    Kummer's transformation


    https://functions.wolfram.com/PDF/Hypergeometric2F1.pdf

    ChatGP2: Written the same as Wolfram but with 2F1 in steeds of sums
    2F1(a,b;c;z) = (Γ(b)Γ(c−a)) / (Γ(c)Γ(b−a)) * (−z)^−a * 2F1(a,a−c+1;a−b+1;1/z) + (Γ(a)Γ(c−b)) / (Γ(c)Γ(a−b)) * (−z)^−b * 2F1(b,b−c+1;b−a+1;1/z)
    This is valid when:
    z∉[0,1]z∈/[0,1]
    arg(−z)arg(−z) is defined (usually −π<arg (−z)<π−π<arg(−z)<π)
    c, a−b, and b−a are not integers to avoid poles in the Gamma functions

"""

import mpmath

from symexpress3         import symexpress3
from symexpress3.symfunc import symFuncBase
from symexpress3         import symtools


class SymFuncHypergeometric( symFuncBase.SymFuncBase ):
  """
  Hypergeometric function, hypergeometric( p, q, a1,..,ap, b1,..,bq, z )
  """
  def __init__( self ):
    super().__init__()
    self._name        = "hypergeometric"
    self._desc        = "Hypergeometric function"
    self._minparams   = 3      # minimum number of parameters
    self._maxparams   = 100    # maximum number of parameters
    self._syntax      = "hypergeometric( p, q, a1,..,ap, b1,..,bq, z )"
    self._synExplain  = "hypergeometric( p, q, a1,..,ap, b1,..,bq, z ) Example: hypergeometric( 2, 1, a1, a2, b1, z )"

  def mathMl( self, elem ):
    if self._checkCorrectFunction( elem ) != True:
      return None, None

    elemP   = elem.elements[ 0 ]
    elemQ   = elem.elements[ 1 ]

    elemTot = len( elem.elements )
    elemZ   = elem.elements[ elemTot - 1 ]

    if not isinstance( elemP, symexpress3.SymNumber ):
      dVars = elemP.getVariables()
      if len( dVars ) != 0:
        return None, None
    else:
      if elemP.power != 1:
        return None, None
      if elemP.factDenominator != 1:
        return None, None

    if not isinstance( elemQ, symexpress3.SymNumber):
      dVars = elemQ.getVariables()
      if len( dVars ) != 0:
        return None, None
    else:
      if elemQ.power != 1:
        return None, None
      if elemQ.factDenominator != 1:
        return None, None

    try:
      valP = elemP.getValue()
      valQ = elemQ.getValue()
    except: # pylint: disable=bare-except
      return None, None

    if not isinstance(valP, int):
      return None, None
    if not isinstance(valQ, int):
      return None, None

    if valP + valQ + 3 != elemTot:
      return None, None


    output = ""

    # https://developer.mozilla.org/en-US/docs/Web/MathML/Element/mmultiscripts
    output += '<mmultiscripts>'
    output += '<mi>F</mi>'                           # <!-- base expression -->
    output += '<mi>' + elemQ.mathMl() + '</mi>'      # <!-- post-sub-script -->
    output += '<mrow></mrow>'                        # <!-- post-sup-script -->
    output += '<mprescripts />'                      #
    output += '<mi>' + elemP.mathMl() + '</mi>'      # <!-- pre-sub-script -->
    output += '<mrow></mrow>'                        # <!-- pre-sup-script -->
    output += '</mmultiscripts>'

    output += "<mfenced separators=''>"

    # print( f"valP {valP}" )
    # print( f"valQ {valQ}" )
    # print( f"elemTot {elemTot}" )

    output += elem.mathMlParameters( False, 2, valP + 1 )

    output += '<mspace width="4px"></mspace>'
    output += '<mi>;</mi>'
    output += '<mspace width="8px"></mspace>'

    output += elem.mathMlParameters( False, valP + 2, elemTot - 2 )

    output += '<mspace width="4px"></mspace>'
    output += '<mi>;</mi>'
    output += '<mspace width="8px"></mspace>'

    output += elemZ.mathMl()

    output += "</mfenced>"

    return [ '()' ], output


  def functionToValue( self, elem ):
    # pylint: disable=unused-argument

    def _analytic2F1( valP, valQ, startP, startQ, elemZ ):
      # analytic continution of 2f2 if z > 1
      if valP != 2 or valQ != 1:
        return None

      # below transformation is only valid if abs(z) > 1
      try:
        valZ = elemZ.getValue()
        if abs( valZ ) <= 1 :
          return None
      except: # pylint: disable=bare-except
        return None

      strA = str( elem.elements[ startP     ] )
      strB = str( elem.elements[ startP + 1 ] )
      strC = str( elem.elements[ startQ     ] )
      strZ = str( elemZ )

      strElem1 = f"gamma( {strC} ) * gamma( ({strC}) - ({strA}) - ({strB}) )"
      strElem2 = f"gamma( ({strC}) - ({strA}) ) * gamma( ({strC}) - ({strB}) ) * exp( ({strA}) + ({strB}) - ({strC}), (1 - ({strZ})))"
      strElem3 = f"hypergeometric( 2, 1, ({strC}) - ({strA}),({strC}) - ({strA}), {strC}, 1 / ( 1 - ({strZ}) ))"

      strElem = f" ({strElem1}) / ( {strElem2} * {strElem3} ) "

      elemNew = symexpress3.SymFormulaParser( strElem )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew


    def _transPPlusQPlus( valP, valQ, startP, startQ, elemZ ):
      # p+1 F q+1 => gamma * integral( ... * pFq )
      if valP <= 0 or valQ <= 0:
        return None

      # below transformation is only valid if abs(z) < 1
      try:
        valZ = elemZ.getValue()
        if abs( valZ ) >= 1:
          return None
      except: # pylint: disable=bare-except
        return None

      strC = str( elem.elements[ startP + valP - 1] )
      strD = str( elem.elements[ startQ + valQ - 1] )

      fLower = elem.copy()
      fLower.powerSign        = elem.powerSign
      fLower.powerCounter     = elem.powerCounter
      fLower.powerDenominator = elem.powerDenominator

      del fLower.elements[ startQ + valQ - 1 ]
      del fLower.elements[ startP + valP - 1 ]

      fLower.elements[ 0 ].factCounter -= 1
      fLower.elements[ 1 ].factCounter -= 1

      varName = symtools.VariableGenerateGet()
      elemNewZ = symexpress3.SymExpress( '*' )
      elemNewZ.add( elemZ )
      elemNewZ.add( symexpress3.SymVariable( varName ))

      fLower.elements[ -1 ] = elemNewZ

      strfLower = str( fLower )

      strElem = f"(gamma( {strD}) / ( gamma({strC}) * gamma( ({strD}) - ({strC}) ) ))"
      strElem += f"integral(  exp( ({strC}) - 1, {varName}) * exp( ({strD}) - ({strC}) - 1, 1 - {varName})  * {strfLower}, {varName}, 0,1)"

      elemNew = symexpress3.SymFormulaParser( strElem )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew



    def _trans1F0( valP, valQ, startP, startQ, elemZ ):
      # 1F0 = (1 - z)^^(-p)
      if valP != 1 or valQ != 0:
        return None

      strZ = str( elemZ )
      strP = str( elem.elements[ startP ] )

      strElem = f"exp( -1 * ({strP}), 1 - ({strZ} ))"

      elemNew = symexpress3.SymFormulaParser( strElem )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew


    def _trans0F0( valP, valQ, startP, startQ, elemZ ):
      # 0F0 = e^^z
      if valP != 0 or valQ != 0:
        return None

      elemNew = symexpress3.SymFunction( 'exp' )
      elemNew.add( elemZ )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew


    def _equalPQ( valP, valQ, startP, startQ, elemZ ):
      # if a P is equal to a Q then this give a 1 (p/q = 1)
      if valP <= 0 or valQ <= 0:
        return None

      for iCntP in range( startP, valP + startP):
        elemP = elem.elements[ iCntP ]

        for iCntQ in range( startQ, startQ + valQ):
          elemQ = elem.elements[ iCntQ ]

          if elemP.isEqual( elemQ ):
            # ok found equal items, delete equals
            elemNew = elem.copy()
            del elemNew.elements[ iCntQ ]
            del elemNew.elements[ iCntP ]

            elemNew.elements[ 0 ].factCounter -= 1
            elemNew.elements[ 1 ].factCounter -= 1

            return elemNew

      return None

    def _transAbsZSmall( valP, valQ, startP, startQ, elemZ ):
      # below transformation is only valid if abs(z) < 1
      try:
        valZ = elemZ.getValue()
        if abs( valZ ) >= 1:
          return None
      except: # pylint: disable=bare-except
        return None


      elemPQ  = symexpress3.SymExpress( '*' )
      varName = symtools.VariableGenerateGet()
      symVarN = symexpress3.SymVariable( varName )

      for iCntVal in range( startP, valP + startP):
        elemA    = elem.elements[ iCntVal ]
        elemFunc = symexpress3.SymFunction( "risingfactorial" )
        elemFunc.add( elemA   )
        elemFunc.add( symVarN )

        elemPQ.add( elemFunc )

      for iCntVal in range( startQ, startQ + valQ):
        elemB    = elem.elements[ iCntVal ]
        elemFunc = symexpress3.SymFunction( "risingfactorial", -1, 1, 1 )
        elemFunc.add( elemB   )
        elemFunc.add( symVarN )

        elemPQ.add( elemFunc )

      elemZExp = symexpress3.SymFunction( "exp" )
      elemZExp.add( symVarN )
      elemZExp.add( elemZ   ) # z^^n

      elemNFact = symexpress3.SymFunction( 'factorial', -1, 1, 1 )
      elemNFact.add( symVarN )

      elemParam = symexpress3.SymExpress( '*' )
      elemParam.add( elemPQ    )
      elemParam.add( elemZExp  )
      elemParam.add( elemNFact )

      elemProduct = symexpress3.SymFunction( 'sum' )
      elemProduct.add( symVarN )
      elemProduct.add( symexpress3.SymNumber( 1, 0, 1, 1, 1, 1, 1 ) )
      elemProduct.add( symexpress3.SymVariable( 'infinity' ))
      elemProduct.add( elemParam )

      elemProduct.powerSign        = elem.powerSign
      elemProduct.powerCounter     = elem.powerCounter
      elemProduct.powerDenominator = elem.powerDenominator

      return elemProduct


    if self._checkCorrectFunction( elem ) != True:
      return None

    elemP   = elem.elements[ 0 ]
    elemQ   = elem.elements[ 1 ]

    elemTot = len( elem.elements )
    elemZ   = elem.elements[ elemTot - 1 ]

    if not isinstance( elemP, symexpress3.SymNumber ):
      dVars = elemP.getVariables()
      if len( dVars ) != 0:
        return None
    else:
      if elemP.power != 1:
        return None
      if elemP.factDenominator != 1:
        return None

    if not isinstance( elemQ, symexpress3.SymNumber):
      dVars = elemQ.getVariables()
      if len( dVars ) != 0:
        return None
    else:
      if elemQ.power != 1:
        return None
      if elemQ.factDenominator != 1:
        return None

    try:
      valP = elemP.getValue()
      valQ = elemQ.getValue()
    except: # pylint: disable=bare-except
      return None

    if not isinstance(valP, int):
      return None
    if not isinstance(valQ, int):
      return None

    if valP + valQ + 3 != elemTot:
      return None

    # valP = number of p elements
    # valQ = number of q elements

    startP = 2              # first element of p
    startQ = startP + valP  # first element of q

    # multiple solutions
    # 0F0 = e^^z
    # 0F1 = ?
    # 1F0 = (1 - z)^^(-p)
    #
    # 1F1 => integral * 0F0
    # nFm => integral * n(-1)F(m-1)
    #

    elemNew = _equalPQ( valP, valQ, startP, startQ, elemZ )
    if elemNew != None:
      return elemNew

    # 0F0 = e^^z
    elemNew = _trans0F0( valP, valQ, startP, startQ, elemZ )
    if elemNew != None:
      return elemNew

    # 1F0 = (1 - z)^^(-p)
    elemNew = _trans1F0( valP, valQ, startP, startQ, elemZ )
    if elemNew != None:
      return elemNew

    # TODO p+1 F q+1 => gamma * integral( ... * pFq )
    # elemNew = _transPPlusQPlus( valP, valQ, startP, startQ, elemZ )
    if elemNew != None:
      return elemNew

    # TODO analytic2F1
    # elemNew = _analytic2F1( valP, valQ, startP, startQ, elemZ )
    if elemNew != None:
      return elemNew


    # below transformation is only valid if abs(z) < 1
    elemNew = _transAbsZSmall( valP, valQ, startP, startQ, elemZ )
    if elemNew != None:
      return elemNew

    return None

  def getValue( self, elemFunc, dDict = None ):
    #
    # convert to an optimize function with functionToValue()
    # and use that for calculation the value
    #

    # elemNew = self.functionToValue( elemFunc )
    # if elemNew == None:
    #   return None
    elem = elemFunc
    arrA = []
    arrB = []
    z    = None

    elemTot = len( elem.elements )
    if elemTot < 2:
      return None

    elemP   = elem.elements[ 0 ]
    elemQ   = elem.elements[ 1 ]

    elemTot = len( elem.elements )
    elemZ   = elem.elements[ elemTot - 1 ]

    if not isinstance( elemP, symexpress3.SymNumber ):
      dVars = elemP.getVariables()
      if len( dVars ) != 0:
        return None
    else:
      if elemP.power != 1:
        return None
      if elemP.factDenominator != 1:
        return None

    if not isinstance( elemQ, symexpress3.SymNumber):
      dVars = elemQ.getVariables()
      if len( dVars ) != 0:
        return None
    else:
      if elemQ.power != 1:
        return None
      if elemQ.factDenominator != 1:
        return None

    try:
      valP = elemP.getValue( dDict )
      valQ = elemQ.getValue( dDict )
    except: # pylint: disable=bare-except
      return None

    if not isinstance(valP, int):
      return None
    if not isinstance(valQ, int):
      return None

    if valP + valQ + 3 != elemTot:
      return None

    z = elemZ.getValue( dDict )

    for iCntVal in range( 2, valP + 2):
      elemA    = elem.elements[ iCntVal ]
      arrA.append( elemA.getValue( dDict ) )

    for iCntVal in range( valP + 2, valP + valQ + 2):
      elemB    = elem.elements[ iCntVal ]
      arrB.append( elemB.getValue( dDict ) )

    # print( f"arrA: {arrA}" )
    # print( f"arrB: {arrB}" )
    # print( f"z: {z}" )

    dValue = mpmath.hyper( arrA, arrB, z )

    # print( f"dValue: {dValue}" )

    # dValue = elemNew.getValue( dDict )

    # print( f"HyperGeometric: {elemFunc}, value: {dValue}")
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
    # dValue = round( float(dValue), 10 )
    dValue = symexpress3.SymRound( dValue, 10 )
    if dValueCalc != None:
      # dValueCalc = round( float(dValueCalc), 10 )
      dValueCalc = symexpress3.SymRound( dValueCalc, 10 )
    if display == True :
      print( f"naam    : {testClass.name}" )
      print( f"function: {str( symTest )}" )
      print( f"Value   : {str( value   )}" )
      print( f"DValue  : {str( dValue  )}" )

    if str( value ).strip() != valueCalc.strip() or (dValueCalc != None and dValue != dValueCalc) : # pylint: disable=consider-using-in
      print( f"Error unit test {testClass.name} function" )
      raise NameError( f'function {testClass.name}, unit test error: {str( symTest )}, value: {value} <> {valueCalc}, dValue:{dValue} <> {dValueCalc}' )

  # https://reference.wolfram.com/language/ref/Hypergeometric2F1.html
  # 0.156542+0.150796i
  symTest = symexpress3.SymFormulaParser( 'hypergeometric( 2, 1, 2, 3, 4, 1/2 )' )
  symTest.optimize()
  testClass = SymFuncHypergeometric()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  # _Check( testClass, symTest, value, dValue, "sum( n2,0,infinity, risingfactorial( 2,n2 ) *  risingfactorial( 3,n2 ) *  risingfactorial( 4,n2 )^^-1 *  exp( n2,(1/2) ) *  factorial( n2 )^^-1 )", 2.7289353331 )
  # TODO _Check( testClass, symTest, value, dValue, "gamma( 4 ) * ( gamma( 3 ) *  gamma( 4 + (-1) * 3 ))^^-1 *  integral(  exp( 3 + (-1) * 1,n2 ) *  exp( 4 + (-1) * 3 + (-1) * 1,1 + (-1) * n2 ) *  hypergeometric( 1,0,2,1 * 2^^-1 * n2 ),n2,0,1 )", 2.7289353331 )


  symTest = symexpress3.SymFormulaParser( 'hypergeometric( 3, 2, 1, 2, 3, 4, 3, 1/2 )' )
  symTest.optimize()
  testClass = SymFuncHypergeometric()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "hypergeometric( 2,1,1,2,4,(1/2) )", 1.3644676666 )


  symTest = symexpress3.SymFormulaParser( 'hypergeometric( 0, 0, 1/2 )' )
  symTest.optimize()
  testClass = SymFuncHypergeometric()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "exp( (1/2) )", 1.6487212707  )


  symTest = symexpress3.SymFormulaParser( 'hypergeometric( 1, 0, 1/3, 1/2 )' )
  symTest.optimize()
  testClass = SymFuncHypergeometric()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "exp( (-1) * 1 * 3^^-1,1 + (-1) * 1 * 2^^-1 )", 1.2599210499 )


  symTest = symexpress3.SymFormulaParser( 'hypergeometric( 2, 1, 1/3, 1/2, 1/5, 2 )' )
  symTest.optimize()
  testClass = SymFuncHypergeometric()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  # TODO check hypergoemetric function
  # _Check( testClass, symTest, value, dValue, "gamma( 1 * 5^^-1 ) *  gamma( 1 * 5^^-1 + (-1) * 1 * 3^^-1 + (-1) * 1 * 2^^-1 ) * ( gamma( 1 * 5^^-1 + (-1) * 1 * 3^^-1 ) *  gamma( 1 * 5^^-1 + (-1) * 1 * 2^^-1 ) *  exp( 1 * 3^^-1 + 1 * 2^^-1 + (-1) * 1 * 5^^-1,(1 + (-1) * 2) ) *  hypergeometric( 2,1,1 * 5^^-1 + (-1) * 1 * 3^^-1,1 * 5^^-1 + (-1) * 1 * 3^^-1,1 * (1 + (-1) * 2)^^-1 ))^^-1", -0.9625193447 - 1.1369043195j  )


if __name__ == '__main__':
  Test( True )

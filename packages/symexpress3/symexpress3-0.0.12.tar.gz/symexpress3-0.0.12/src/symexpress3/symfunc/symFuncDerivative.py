#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Derivative function for Sym Express 3

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


 	  https://en.wikipedia.org/wiki/Derivative
    https://en.wikipedia.org/wiki/Differentiation_rules
"""

from symexpress3         import symexpress3
from symexpress3.symfunc import symFuncBase

class SymFuncDerivative( symFuncBase.SymFuncBase ):
  """
  Derivative function, derivative( <function>,<delta> )
  """
  def __init__( self ):
    super().__init__()
    self._name        = "derivative"
    self._desc        = "derivative( <function>,<delta> )"
    self._minparams   = 2    # minimum number of parameters
    self._maxparams   = 2    # maximum number of parameters
    self._syntax      = "derivative( <function>,<delta> )"
    self._synExplain  = "derivative( <function>,<delta> )"


  def mathMl( self, elem ):
    if self._checkCorrectFunction( elem ) != True:
      return [], None

    output = ""

    output += "<mfrac>"

    output += "<mrow>"
    output += "<mi>d</mi>"

    output += "<mfenced separators=''>"
    output += elem.elements[ 0 ].mathMl()
    output += "</mfenced>"

    output += "</mrow>"

    output += "<mrow>"
    output += "<mi>d</mi>"
    output += elem.elements[ 1 ].mathMl()
    output += "</mrow>"
    output += "</mfrac>"

    return [ '()' ], output


  def functionToValue( self, elem ):

    def _subGetConstantAndVariable( elemFunc ):
      """
      Split the function into a constant and the variable
      Give 2 result, first = constant, second = variable
      Result is None,None if nothing valid is found
      """

      # first make the function a principal
      if elemFunc.onlyOneRoot != 1:
        return None, None

      cVarName = elem.elements[ 1 ].name

      # plus expression with 1 element
      if (     isinstance( elemFunc, symexpress3.SymExpress )
           and elemFunc.symType == '+'
           and elemFunc.numElements() == 1
         ):
        elemFunc = elemFunc.elements[ 0 ]
        if (   elemFunc.onlyOneRoot      != 1
            or elemFunc.powerSign        != 1
            or elemFunc.powerCounter     != 1
            or elemFunc.powerDenominator != 1
           ):
          return None, None

      # variable type check it
      if isinstance( elemFunc, symexpress3.SymVariable ):
        if elemFunc.name == cVarName :
          return None, [ elemFunc ]
        return [ elemFunc ], None

      # fill 2 arrays with elements
      arrConst = []
      arrVar   = []

      if isinstance( elemFunc, symexpress3.SymExpress ) and elemFunc.symType == '*' :
        for elemCheck in elemFunc.elements:
          dictVars = elemCheck.getVariables()
          if cVarName in dictVars:
            arrVar.append( elemCheck )
          else:
            arrConst.append( elemCheck )
      else:
        # array check is already done, now only the is there is an variable in it
        dictVars = elemFunc.getVariables()
        if cVarName in dictVars:
          arrVar.append( elemFunc )
        else:
          arrConst.append( elemFunc )

      if len( arrConst ) == 0:
        arrConst = None
      if len( arrVar ) == 0:
        arrVar = None

      return arrConst, arrVar

    def _derivativeLog():
      """
        derivative( log( a x, b ) ) = 1 / ( x log( b ))
      """
      elemFunc = elem.elements[ 0 ]
      if (   elemFunc.onlyOneRoot      != 1
          or elemFunc.powerSign        != 1
          or elemFunc.powerCounter     != 1
          or elemFunc.powerDenominator != 1
         ):
        return None

      if not isinstance( elemFunc, symexpress3.SymFunction ):
        return None

      cFuncName = elemFunc.name
      if cFuncName != "log":
        return None

      elemParam = elemFunc.elements[ 0 ]
      # arrConst, arrVar = _subGetConstantAndVariable ( elemParam )
      _, arrVar = _subGetConstantAndVariable ( elemParam )
      if arrVar == None:
        return None

      dictBase = None
      if elemFunc.numElements() >= 2:
        # contains the base the variable
        dictBase = elemFunc.elements[1].getVariables()
        if (  len( dictBase ) == 0
           or not elem.elements[1].name in dictBase
           ):
          dictBase = None # no variable in base
      if dictBase != None:
        return None # log( a, x ) not supported

      expVar = symexpress3.SymExpress( '*' )
      for elemVar in arrVar:
        expVar.add( elemVar )

      elemNew = symexpress3.SymExpress( '*' )
      elemDiv = symexpress3.SymExpress( '*' )
      elemDiv.powerSign = -1
      elemDiv.add( expVar )

      if elemFunc.numElements() >= 2:
        elemLog = symexpress3.SymFunction( 'log' )
        elemLog.add( elemFunc.elements[1] )
        elemDiv.add( elemLog )

      elemNew.add( elemDiv )

      if (   len( arrVar ) > 1
          or not isinstance( arrVar[0], symexpress3.SymVariable )
          or arrVar[0].name  != elem.elements[ 1 ] .name
          or arrVar[0].power != 1
         ):

        elemDir = symexpress3.SymFunction( 'derivative' )
        elemDir.add( expVar )
        elemDir.add( elem.elements[ 1 ] )
        elemNew.add( elemDir )

      elem.copyPower( elemNew )

      return elemNew


    def _derivativeExp():
      """
        derivative( exp( a x , c ) = a exp( a x, c) * log( c )
        derivative( exp( a x     ) = a exp( a x   )
      """
      elemFunc = elem.elements[ 0 ]
      if (   elemFunc.onlyOneRoot      != 1
          or elemFunc.powerSign        != 1
          or elemFunc.powerCounter     != 1
          or elemFunc.powerDenominator != 1
         ):
        return None

      if not isinstance( elemFunc, symexpress3.SymFunction ):
        return None

      cFuncName = elemFunc.name
      if cFuncName != "exp":
        return None

      elemParam = elemFunc.elements[ 0 ]
      arrConst, arrVar = _subGetConstantAndVariable ( elemParam )
      if arrVar == None and arrConst == None:
        return None

      if arrVar == None and elemFunc.numElements() == 1:
        return None

      dictBase = None
      if elemFunc.numElements() >= 2:
        # contains the base the variable
        dictBase = elemFunc.elements[1].getVariables()
        if (  len( dictBase ) == 0
           or not elem.elements[1].name in dictBase
           ):
          dictBase = None # no variable in base

      # if dictBase != None then the base contains the variable
      if arrVar != None and dictBase != None:
        return None # exp( x, x ) not supported

      if arrVar != None:
        # derivative( exp( a x, b ) = a exp( a x , b ) log( b )
        if arrConst != None:
          expConst = symexpress3.SymExpress( '*' )
          for elemConst in arrConst:
            expConst.add( elemConst )

        expVar = symexpress3.SymExpress( '*' )
        for elemVar in arrVar:
          expVar.add( elemVar )

        elemNew = symexpress3.SymExpress( '*' )
        if arrConst != None:
          elemNew.add( expConst )
        elemNew.add( elemFunc )

        if dictBase == None and elemFunc.numElements() >= 2:
          elemLog = symexpress3.SymFunction( 'log' )
          elemLog.add( elemFunc.elements[1] )
          elemNew.add( elemLog )


        if (   len( arrVar ) > 1
            or not isinstance( arrVar[0], symexpress3.SymVariable )
            or arrVar[0].name  != elem.elements[ 1 ] .name
            or arrVar[0].power != 1
           ):

          expVar = symexpress3.SymExpress( '*' )
          for elemVar in arrVar:
            expVar.add( elemVar )

          elemDir = symexpress3.SymFunction( 'derivative' )
          elemDir.add( expVar )
          elemDir.add( elem.elements[ 1 ] )
          elemNew.add( elemDir )

        elem.copyPower( elemNew )

        return elemNew

      # exp( a, x ) = exp( a - 1, x ) * a
      elemBase = elemFunc.elements[ 1 ]
      if (   not isinstance( elemBase, symexpress3.SymVariable )
          or elemBase.name != elem.elements[1].name
          or elemBase.power != 1
         ):
        return None

      if (   isinstance( elemParam, symexpress3.SymNumber )
         and elemParam.factor == 1
         ):
        # exp( 1, x ) = 1
        elemNew = symexpress3.SymNumber()
      else:
        elemNew = symexpress3.SymExpress('*')
        elemMin = symexpress3.SymExpress('+')
        elemMin.add( elemParam )
        elemMin.add( symexpress3.SymNumber( -1, 1, 1 ))
        elemNew.add( elemParam )

        elemExp = symexpress3.SymFunction( 'exp' )
        elemExp.add( elemMin )
        elemExp.add( elem.elements[1] )

        elemNew.add( elemExp )

      elem.copyPower( elemNew )

      return elemNew


    def _derivativeTrigonometric():
      """
        derivative of trigonometric and inverse trigonometric functions
      """
      elemFunc = elem.elements[ 0 ]
      if (   elemFunc.onlyOneRoot      != 1
          or elemFunc.powerSign        != 1
          or elemFunc.powerCounter     != 1
          or elemFunc.powerDenominator != 1
         ):
        return None

      if not isinstance( elemFunc, symexpress3.SymFunction ):
        return None

      cFuncName = elemFunc.name
      if not cFuncName in [ 'sin', 'cos', 'tan', 'asin', 'acos', 'atan' ]:
        return None

      if elemFunc.numElements() != 1:
        return None

      elemParam = elemFunc.elements[ 0 ]

      elemNew = symexpress3.SymExpress('*')
      if cFuncName == "sin":
        # derivative( sin(x), x)  = cos(x)
        elemFnc = symexpress3.SymFunction( 'cos' )
        elemFnc.add( elemParam )
        elemNew.add( elemFnc )

      elif cFuncName == "cos":
        # derivative( cos(x), x) = - sin(x)
        elemNew.add( symexpress3.SymNumber( -1, 1, 1 ) )
        elemFnc = symexpress3.SymFunction( 'sin' )
        elemFnc.add( elemParam )
        elemNew.add( elemFnc )

      elif cFuncName == "tan":
        # derivative( tan(x), x ) = 1 + tan(x)^^2
        elemFnc = symexpress3.SymFunction( 'tan' )
        elemFnc.add( elemParam )
        elemFnc.powerCounter = 2

        elemPlus = symexpress3.SymExpress('+' )
        elemPlus.add( symexpress3.SymNumber() )
        elemPlus.add( elemFnc )

        elemNew.add( elemPlus )

      elif cFuncName == "asin":
        # derivative( asin(x), x ) = 1 / (1 - x^^2)^^(1/2)

        elemFnc = symexpress3.SymExpress('*' )

        elemFnc.powerSign        = -1
        elemFnc.powerDenominator = 2

        elemMin = symexpress3.SymExpress('+')
        elemMin.add( symexpress3.SymNumber(1,1,1))

        elemPower = symexpress3.SymExpress( '*')
        elemPower.add( symexpress3.SymNumber( -1,1,1))
        elemParam.powerCounter = 2
        elemPower.add( elemParam )
        elemParam.powerCounter = 1

        elemMin.add( elemPower )
        elemFnc.add( elemMin )

        elemNew.add( elemFnc )

      elif cFuncName == "acos":
        # derivative( acos(x), x ) = -1 / (1 - x^^2)^^(1/2)

        elemNew.add( symexpress3.SymNumber( -1,1,1))
        elemFnc = symexpress3.SymExpress('*' )

        elemFnc.powerSign        = -1
        elemFnc.powerDenominator = 2

        elemMin = symexpress3.SymExpress('+')
        elemMin.add( symexpress3.SymNumber(1,1,1))

        elemPower = symexpress3.SymExpress( '*')
        elemPower.add( symexpress3.SymNumber( -1,1,1))
        elemParam.powerCounter = 2
        elemPower.add( elemParam )
        elemParam.powerCounter = 1

        elemMin.add( elemPower )
        elemFnc.add( elemMin )

        elemNew.add( elemFnc )

      elif cFuncName == "atan":
        # derivative( atan(x), x ) = 1 / (1 + x^^2)

        elemNew.add( symexpress3.SymNumber( -1,1,1))
        elemFnc = symexpress3.SymExpress('*' )

        elemFnc.powerSign        = -1

        elemMin = symexpress3.SymExpress('+')
        elemMin.add( symexpress3.SymNumber(1,1,1))

        elemPower = symexpress3.SymExpress( '*')
        elemParam.powerCounter = 2
        elemPower.add( elemParam )
        elemParam.powerCounter = 1

        elemMin.add( elemPower )
        elemFnc.add( elemMin )

        elemNew.add( elemFnc )

      else:
        return None # theoretical not possible


      if (   not isinstance( elemParam, symexpress3.SymVariable )
          or elemParam.name  != elem.elements[ 1 ] .name
          or elemParam.power != 1
         ):

        elemDir = symexpress3.SymFunction( 'derivative' )
        elemDir.add( elemParam )
        elemDir.add( elem.elements[ 1 ] )
        elemNew.add( elemDir )


      elem.copyPower( elemNew )

      return elemNew



    def _derivativePower():
      """
      derivative( x^^2     , x ) = 2 x^^1, x
      derivative( sin(x)^^2, x ) = 2 sin(x)^^1 * derivative( sin(x), x )
      """
      elemFunc = elem.elements[ 0 ]
      if elemFunc.onlyOneRoot != 1:
        return None

      if (    elemFunc.powerCounter     == 1
          and elemFunc.powerDenominator == 1
         ):
        return None

      elemNum                 = symexpress3.SymNumber()
      elemNum.factSign        = elemFunc.powerSign
      elemNum.factCounter     = elemFunc.powerCounter
      elemNum.factDenominator = elemFunc.powerDenominator

      elemBase = elemFunc.copy()
      elemBase.powerSign        = 1
      elemBase.powerCounter     = 1
      elemBase.powerDenominator = 1

      elemNew = symexpress3.SymExpress( '*' )

      elemNew.add( elemNum )
      elemExp = symexpress3.SymFunction( 'exp' )
      elemExpPower = symexpress3.SymExpress('+')
      elemExpPower.add( elemNum )
      elemExpPower.add( symexpress3.SymNumber( -1, 1, 1 ))
      elemExp.add( elemExpPower )
      elemExp.add( elemBase )
      elemNew.add( elemExp )

      if not isinstance( elemBase, symexpress3.SymVariable ):
        elemDir = symexpress3.SymFunction( 'derivative' )
        elemDir.add( elemBase )
        elemDir.add( elem.elements[ 1 ] )
        elemNew.add( elemDir )

      elem.copyPower( elemNew )

      return elemNew


    def _derivativeProduct():
      """
      derivative( x * y, x ) = derivative( x, x ) * y + x * derivative( y, x )
      """
      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymExpress ) :
        return None
      if elemFunc.symType != '*':
        return None

      if elemFunc.numElements() <= 1:
        return None

      if (   elemFunc.powerSign        != 1
          or elemFunc.powerCounter     != 1
          or elemFunc.powerDenominator != 1
          or elemFunc.onlyOneRoot      != 1
         ):
        return None

      elemFirst  = None
      elemSecond = None
      for elemProd in elemFunc.elements:
        if elemFirst == None:
          elemFirst = elemProd
          elemSecond = symexpress3.SymExpress( '*' )
        else:
          elemSecond.add( elemProd )

      elemNew  = symexpress3.SymExpress( '+' )

      expFirst = symexpress3.SymExpress( '*' )
      elemDer  = symexpress3.SymFunction( 'derivative' )
      elemDer.add( elemFirst )
      elemDer.add( elem.elements[ 1 ] )
      expFirst.add( elemDer )
      expFirst.add( elemSecond )
      elemNew.add( expFirst )

      expSecond = symexpress3.SymExpress( '*' )
      expSecond.add( elemFirst )
      elemDer  = symexpress3.SymFunction( 'derivative' )
      elemDer.add( elemSecond )
      elemDer.add( elem.elements[ 1 ] )
      expSecond.add( elemDer )
      elemNew.add( expSecond )

      elem.copyPower( elemNew )

      return elemNew



    def _derivativePlus():
      """
        derivative( x + y, x ) = derivative( x, x ) + deriate( y, x )
      """
      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymExpress ) :
        return None
      if elemFunc.symType != '+':
        return None

      if elemFunc.numElements() <= 1:
        return None

      if (   elemFunc.powerSign        != 1
          or elemFunc.powerCounter     != 1
          or elemFunc.powerDenominator != 1
          or elemFunc.onlyOneRoot      != 1
         ):
        return None

      elemNew = symexpress3.SymExpress( '+' )
      for elemPlus in elemFunc.elements:
        elemDer = symexpress3.SymFunction( 'derivative' )
        elemDer.add( elemPlus )
        elemDer.add( elem.elements[ 1 ] )
        elemNew.add( elemDer )

      elem.copyPower( elemNew )

      return elemNew

    def _derivativeConstant():
      """
        derivative( a  , x ) = 0
        derivative( a x, x ) = a deriate( x, x )
      """
      elemFunc = elem.elements[ 0 ]
      arrConst, arrVar = _subGetConstantAndVariable ( elemFunc )

      if arrVar == None and arrConst == None:
        return None

      if arrVar == None :
        return symexpress3.SymNumber( 1, 0, 1 )

      if arrConst == None:
        if (     len( arrVar )     == 1
             and arrVar[ 0 ].power == 1
             and isinstance( arrVar[0], symexpress3.SymVariable )

            ):
          return symexpress3.SymNumber( 1, 1, 1 )

        return None

      elemNew = symexpress3.SymExpress( '*' )

      expConst = symexpress3.SymExpress( '*' )
      for elemConst in arrConst:
        expConst.add( elemConst )

      expVar = symexpress3.SymExpress( '*' )
      for elemVar in arrVar:
        expVar.add( elemVar )

      elemNew.add( expConst )

      elemDer = symexpress3.SymFunction( 'derivative' )
      elemDer.add( expVar )
      elemDer.add( elem.elements[ 1 ] )
      elemNew.add( elemDer )

      elem.copyPower( elemNew )

      return elemNew


    #
    # start derivative conversion
    # .........................
    if self._checkCorrectFunction( elem ) != True:
      return None

    # first write out roots
    if elem.elements[ 0 ].onlyOneRoot != 1:
      return None

    # first work out the arrays
    if elem.existArray() == True:
      return None

    #
    # for now, only support d<varname>
    #
    elemVar = elem.elements[ 1 ]
    if not isinstance( elemVar, symexpress3.SymVariable ):
      return None
    if elemVar.power != 1:
      return None

    # constant
    elemNew = _derivativeConstant()
    if elemNew != None:
      return elemNew

    # plus
    elemNew = _derivativePlus()
    if elemNew != None:
      return elemNew

    # product
    elemNew = _derivativeProduct()
    if elemNew != None:
      return elemNew

    # power (with chain rule)
    elemNew = _derivativePower()
    if elemNew != None:
      return elemNew

    # trigonometric and inverse (with chain rule)
    elemNew = _derivativeTrigonometric()
    if elemNew != None:
      return elemNew

    # exp (with chain rule)
    elemNew = _derivativeExp()
    if elemNew != None:
      return elemNew

    # log (with chain rule)
    elemNew = _derivativeLog()
    if elemNew != None:
      return elemNew


    return None


  def getValue( self, elemFunc, dDict = None ):
    if self._checkCorrectFunction( elemFunc ) != True:
      return None

    # print( "Calc derivative" )

    if dDict == None:
      dDictSum = {}
    else:
      dDictSum = dDict.copy()

    # derivative = lim( (f(x + h) - f(x)) / h )
    h = 0.00000001

    # delta must always a variable
    cVar = self.getVarname( elemFunc.elements[1] )
    if cVar == None:
      return None

    elemExpress = elemFunc.elements[0]

    dDictSum[ cVar ] = dDictSum[ cVar ] + h

    valFirst = elemExpress.getValue( dDictSum )
    valLast  = elemExpress.getValue( dDict    )

    # if one is a list, both are lists
    if isinstance( valFirst, list ):
      dValue = []
      for iCnt, elem in enumerate( valFirst ) :
        dValue.append( (elem - valLast[ iCnt ]) / h )
    else:
      dValue = (valFirst - valLast) / h

    dValue = elemFunc.valuePow( dValue )

    return dValue

#
# Test routine (unit test), see testsymexpress3.py
#
def Test( display = False):
  """
  Unit test
  """
  def _Check( testClass, symTest, value, valueCalc ):
    if display == True :
      print( f"naam    : {testClass.name}" )
      print( f"function: {str( symTest )}" )
      print( f"Value   : {str( value   )}" )

    if str( value ).strip() != valueCalc : # pylint: disable=consider-using-in
      print( f"Error unit test {testClass.name} function" )
      raise NameError( f'function {testClass.name}, unit test error: {str( symTest )}, value: {value} <> {valueCalc}' )

  # constant
  symTest = symexpress3.SymFormulaParser( 'derivative( 4, x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '0' )

  # constant x
  symTest = symexpress3.SymFormulaParser( 'derivative( x, x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '1' )

  # power
  symTest = symexpress3.SymFormulaParser( 'derivative( x^^(2/3), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '(2/3) *  exp( (2/3) + (-1),x )' )

  # power chain
  symTest = symexpress3.SymFormulaParser( 'derivative( sin(x)^^(2/3), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '(2/3) *  exp( (2/3) + (-1), sin( x ) ) *  derivative(  sin( x ),x )' )

  # plus
  symTest = symexpress3.SymFormulaParser( 'derivative( sin(x) + cos(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, 'derivative(  sin( x ),x ) +  derivative(  cos( x ),x )' )

  # product
  symTest = symexpress3.SymFormulaParser( 'derivative( sin(x) * cos(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, 'derivative(  sin( x ),x ) *  cos( x ) +  sin( x ) *  derivative(  cos( x ),x )' )

  # sin
  symTest = symexpress3.SymFormulaParser( 'derivative( sin(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, 'cos( x )' )

  # cos
  symTest = symexpress3.SymFormulaParser( 'derivative( cos(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '(-1) *  sin( x )' )

  # tan
  symTest = symexpress3.SymFormulaParser( 'derivative( tan(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '(1 +  tan( x )^^2)' )

  # asin
  symTest = symexpress3.SymFormulaParser( 'derivative( asin(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '((1 + (-1) * x^^2))^^(-1/2)' )

  # acos
  symTest = symexpress3.SymFormulaParser( 'derivative( acos(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '(-1) * ((1 + (-1) * x^^2))^^(-1/2)' )

  # atan
  symTest = symexpress3.SymFormulaParser( 'derivative( atan(x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '(-1) * ((1 + x^^2))^^-1' )


  # exp( a, x )
  symTest = symexpress3.SymFormulaParser( 'derivative( exp( a, x), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, 'a *  exp( a + (-1),x )' )


  # exp( a x, b )
  symTest = symexpress3.SymFormulaParser( 'derivative( exp( a x, b), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, 'a *  exp( a * x,b ) *  log( b )' )


  # exp( a x )
  symTest = symexpress3.SymFormulaParser( 'derivative( exp( a x ), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, 'a *  exp( a * x )' )


  # log
  symTest = symexpress3.SymFormulaParser( 'derivative( log( sin(x) , a ), x )')
  symTest.optimize()
  testClass = SymFuncDerivative()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, '( sin( x ) *  log( a ))^^-1 *  derivative(  sin( x ),x )' )


if __name__ == '__main__':
  Test( True )

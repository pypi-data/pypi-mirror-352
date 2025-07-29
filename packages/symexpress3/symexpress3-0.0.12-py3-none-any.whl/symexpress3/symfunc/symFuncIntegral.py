#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Integral function for Sym Express 3

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
    https://en.wikipedia.org/wiki/Integration_by_parts

"""

from symexpress3         import symexpress3
from symexpress3.symfunc import symFuncBase
from symexpress3         import symtools

class SymFuncIntegral( symFuncBase.SymFuncBase ):
  """
  Integral function, integral( <function>,<delta> [,<lower>,<upper>] )
  """
  def __init__( self ):
    super().__init__()
    self._name        = "integral"
    self._desc        = "integral( <function>,<delta> [,<lower>,<upper>] )"
    self._minparams   = 2    # minimum number of parameters
    self._maxparams   = 4    # maximum number of parameters
    self._syntax      = "integral( <function>,<delta> [,<lower>,<upper>] )"
    self._synExplain  = "integral( <function>,<delta> [,<lower>,<upper>] )"

  def _checkCorrectFunction( self, elem ):
    result = super()._checkCorrectFunction( elem )
    if result != True:
      return result

    # both lower and upper must be present or none
    if elem.numElements() == 3:
      return False

    return result

  def mathMl( self, elem ):
    if self._checkCorrectFunction( elem ) != True:
      return [], None

    output = ""

    if elem.numElements() <= 2:
      output += '<mn>&int;</mn>'  # this give a product with above and lower the range
    else:
      output += "<munderover>"
      output += '<mn>&int;</mn>'  # this give a product with above and lower the range

      output += elem.elements[ 2 ].mathMl()
      output += elem.elements[ 3 ].mathMl()

      output += '</munderover>'

    output += "<mfenced separators=''>"
    output += elem.elements[ 0 ].mathMl()
    output += "</mfenced>"

    output += "<mi>d&nbsp;</mi>"
    output += elem.elements[ 1 ].mathMl()

    return [ '()' ], output


  def functionToValue( self, elem ):

    def _subToResultAndPower( elemNew ):
      """
      Give the integral function back or if upper and lower are given,
      give the integralresult function back.
      Also it set the power correct
      """
      if elem.numElements() >= 3:
        elemResult = symexpress3.SymFunction( 'integralresult' )
        elemResult.add( elemNew )
        elemResult.add( elem.elements[ 1 ] )
        elemResult.add( elem.elements[ 2 ] )
        elemResult.add( elem.elements[ 3 ] )

        elemNew = elemResult

      elem.copyPower( elemNew )
      return elemNew

    def _subGetConstantAndVariable( elemFunc, checkPower = True ):
      """
      Split the function into a constant and the variable
      Give 2 result, first = constant, second = variable
      Result is None,None if nothing valid is found
      """

      # first make the function a principal
      if elemFunc.onlyOneRoot != 1:
        return None, None


      # first write out the power
      if checkPower == True:
        if (   elemFunc.powerSign        != 1
            or elemFunc.powerCounter     != 1
            or elemFunc.powerDenominator != 1
           ):
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
        # array check is already done, now only the is there is a variable in it
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

    def _integralSum():
      """
      Integral of a sum: integral( sum( x, -1, 1, x ))
      """
      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymFunction ):
        return None

      cFuncName = elemFunc.name
      if cFuncName != "sum":
        return None

      # no power supported
      if elemFunc.power != 1:
        return None
      if elemFunc.onlyOneRoot != 1:
        return None

      if elemFunc.numElements() != 4:
        return None

      # the lower and upper limit may not contain the integral variable
      elemVar = elem.elements[ 1 ]

      elemLower = elemFunc.elements[ 1 ]
      elemUpper = elemFunc.elements[ 2 ]

      dictVarLower = elemLower.getVariables()
      dictVarUpper = elemUpper.getVariables()

      if elemVar in dictVarLower:
        return None

      if elemVar in dictVarUpper:
        return None

      elemNew = symexpress3.SymFunction( "sum" )
      elemNew.add( elemFunc.elements[ 0 ] )
      elemNew.add( elemFunc.elements[ 1 ] )
      elemNew.add( elemFunc.elements[ 2 ] )

      elemInt = symexpress3.SymFunction( "integral" )
      elemInt.add( elemFunc.elements[ 3 ] )
      elemInt.add( elemVar )

      if elem.numElements() >= 3:
        elemInt.add( elem.elements[2] )

      if elem.numElements() >= 4:
        elemInt.add( elem.elements[3] )

      elemNew.add( elemInt )

      return elemNew

    def _integralByParts():
      """
      Integral by parts: integral( f(x) * g(x), x ) = f(x) * integral( g(x), x ) - integral( derivative( f(x), x) * integral( g(x),x), x )
      https://en.wikipedia.org/wiki/Integration_by_parts
      """

      # TODO it can generate an never ending loop. Need to remember the original and look if it appears in the sub integrals...
      # but how....

      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymExpress ):
        # convert function with power into a SymExpress()
        if  isinstance( elemFunc, symexpress3.SymFunction ):
          if elemFunc.powerCounter > 1 and elemFunc.powerDenominator == 1:
            elemFunc = symexpress3.SymExpress( '*' )
            elemFunc.add( elem.elements[ 0 ] )
          else:
            return None
        else:
          return None

      if elemFunc.symType != '*':
        return None

      # do not support radicals
      if elemFunc.powerDenominator != 1:
        return None

      if elemFunc.numElements() <= 1:
        if isinstance( elemFunc.elements[0], symexpress3.SymFunction ):
          if elemFunc.elements[0].powerCounter <= 1:
            return None
        else:
          return None

      # if there is a integral or derivative then do nothing. This must be first be done
      dictFunc = elemFunc.getFunctions()
      if "integral" in dictFunc:
        return None
      if "derivative" in dictFunc:
        return None

      # the LIATE rule
      # 0 = log
      # 1 = inverse trigonometric function
      # 2 = variables
      # 3 = trigonometric function
      # 4 = exp
      # 5 = rest of functions and expressions
      arrLite = [ [], [], [], [], [], [] ]
      for _, elemSub in enumerate( elemFunc.elements ):
        if isinstance( elemSub, symexpress3.SymFunction ):
          # do not supported powers on functions
          if elemSub.powerDenominator != 1:
            return None
          if elemSub.name == "log":
            arrLite[ 0 ].append( elemSub )
          elif elemSub.name in [ 'asin', 'acos', 'atan' ]:
            arrLite[ 1 ].append( elemSub )
          elif elemSub.name in [ 'sin', 'cos', 'tan' ]:
            arrLite[ 3 ].append( elemSub )
          elif elemSub.name == 'exp' :
            arrLite[ 4 ].append( elemSub )
          else:
            # unknown / not supported function
            return None
            # arrLite[ 5 ].append( elemSub )

        elif isinstance( elemSub, symexpress3.SymVariable ):
          # only support whole number powers (no fractions)
          if elemSub.powerDenominator > 1:
            return None
          arrLite[ 2 ].append( elemSub )
        else:
          if isinstance( elemSub, symexpress3.SymExpress ):
            # only support multi expression of plus with 1 element
            if elemSub.numElements() == 1 or elemSub.symType == '*':
              arrLite[ 5 ].append( elemSub )
            else:
              return None
          else:
            # not supported element
            return None

      # split elemFunc.elements in 2
      # 1 = f(x), 2 = g(x)
      # first found in array = f(x)
      elemFx = None
      elemGx = symexpress3.SymExpress( '*' )
      for arrElem in arrLite:
        if len( arrElem ) <= 0:
          continue
        elemFx = arrElem[ 0 ]
        break

      if elemFx == None:  # should not be possible
        return None

      for elemSub in elemFunc.elements:
        if elemSub == elemFx:
          if not isinstance( elemFx, symexpress3.SymVariable ) and elemFx.powerCounter > 1:
            # split power into 1 for f(x) and the rest in g(x), but not for a variable
            elemCopy = elemFx.copy()
            elemCopy.powerCounter = elemCopy.powerCounter - 1
            elemGx.add( elemCopy )
            elemFx = elemCopy
            elemFx.powerCounter = 1
          continue
        elemGx.add( elemSub )

      # how we have elemFx en elemGx
      # integral( f(x) * g(x), x ) = f(x) * integral( g(x), x ) - integral( derivative( f(x), x) * integral( g(x),x), x )
      elemNew = symexpress3.SymExpress( '+' )

      elemPart1 = symexpress3.SymExpress( '*' )
      elemPart1.add( elemFx )
      elemInt1 = symexpress3.SymFunction( 'integral' )
      elemInt1.add( elemGx )
      elemInt1.add( elem.elements[ 1 ] )
      if elem.numElements() >= 4:
        elemInt1.add( elem.elements[ 2 ] )
        elemInt1.add( elem.elements[ 3 ] )

      # give integral a new variable
      varName = symtools.VariableGenerateGet()
      varDict = {}
      varDict[ elem.elements[ 1 ].name ] = varName
      elemInt1.replaceVariable( varDict )

      elemPart1.add( elemInt1 )

      if elem.numElements() >= 4:
        elemRest1 = symexpress3.SymFunction( 'integralresult' )
        elemRest1.add( elemPart1 )
        elemRest1.add( elem.elements[ 1 ] )
        elemRest1.add( elem.elements[ 2 ] )
        elemRest1.add( elem.elements[ 3 ] )

        elemNew.add( elemRest1 )
      else:
        elemNew.add( elemPart1 )

      elemPart2 = symexpress3.SymExpress( '*' )
      elemPart2.add( symexpress3.SymNumber( -1, 1, 1, 1 ))

      elemInt2 = symexpress3.SymFunction( 'integral' )

      elemExp2 = symexpress3.SymExpress( '*' )

      elemDer2 = symexpress3.SymFunction( 'derivative' )
      elemDer2.add( elemFx )
      elemDer2.add( elem.elements[1])
      elemExp2.add( elemDer2 )

      elemInt21 = symexpress3.SymFunction( 'integral' )
      elemInt21.add( elemGx )
      elemInt21.add( elem.elements[ 1 ] )
      if elem.numElements() >= 4:
        elemInt21.add( elem.elements[ 2 ] )
        elemInt21.add( elem.elements[ 3 ] )

      # give integral a new variable
      varName = symtools.VariableGenerateGet()
      varDict = {}
      varDict[ elem.elements[ 1 ].name ] = varName
      elemInt21.replaceVariable( varDict )

      elemExp2.add( elemInt21 )

      elemInt2.add( elemExp2 )
      elemInt2.add( elem.elements[1] )

      if elem.numElements() >= 4:
        elemInt2.add( elem.elements[2] )
        elemInt2.add( elem.elements[3] )

      elemPart2.add( elemInt2 )

      elemNew.add( elemPart2 )

      elemNew.powerSign        = elem.powerSign
      elemNew.powerCounter     = elem.powerCounter
      elemNew.powerDenominator = elem.powerDenominator

      return elemNew

    def _integralLog():
      """
      Integral( log( a x, b ), x ) =  x log( a x ) - x / log( a, e )
      """
      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymFunction ):
        return None

      cFuncName = elemFunc.name
      if cFuncName != "log":
        return None

      # no power supported
      if elemFunc.power != 1:
        return None

      if elemFunc.numElements() > 2:
        return None

      elemParam = elemFunc.elements[ 0 ]
      arrConst, arrVar = _subGetConstantAndVariable ( elemParam )
      if arrVar == None :
        return None

      # log( 3 x ) = log(3) + log(x)
      if arrConst != None:
        return None

      if len( arrVar ) > 1:
        return None

      if (    arrVar[ 0 ].powerSign        != 1
           or arrVar[ 0 ].powerCounter     != 1
           or arrVar[ 0 ].powerDenominator != 1
           or arrVar[ 0 ].onlyOneRoot      != 1
         ):
        return None

      if not isinstance( arrVar[ 0 ], symexpress3.SymVariable ):
        return None

      # print( "check 1" )

      if elemFunc.numElements() >= 2:
        # integral( log( x, x))  not supported
        elemBase = elemFunc.elements[1]
        dDictVar = elemBase.getVariables()
        if elem.elements[1].name in dDictVar:
          return None


      elemNew = symexpress3.SymExpress( '+' )
      elemPart1 = symexpress3.SymExpress( '*' )
      elemPart1.add( symexpress3.SymVariable( elem.elements[1].name ))
      elemPart1.add( elemFunc )
      elemNew.add( elemPart1 )

      elemPart2 = symexpress3.SymExpress( '*' )
      elemPart2.add( symexpress3.SymNumber( -1, 1,1,1))
      elemPart2.add( symexpress3.SymVariable( elem.elements[1].name ))

      if elemFunc.numElements() >= 2:
        elemLn = symexpress3.SymFunction( 'log' )
        elemLn.powerSign = -1
        elemLn.add( elemFunc.elements[ 1 ])
        elemPart2.add( elemLn )

      elemNew.add( elemPart2 )

      elemNew = _subToResultAndPower( elemNew )

      return elemNew

    def _integralExp():
      """
      Integral( exp( a x    ), x) = exp( a x    ) / a
      Integral( exp( a x, b ), x) = exp( a x, b ) / (a ln( b )) , b > 0 and b <> 1
      """
      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymFunction ):
        return None

      cFuncName = elemFunc.name
      if cFuncName != "exp":
        return None

      # no power supported
      if elemFunc.power != 1:
        return None

      if elemFunc.numElements() > 2:
        return None

      elemParam = elemFunc.elements[ 0 ]
      arrConst, arrVar = _subGetConstantAndVariable ( elemParam, False )
      if arrVar == None and arrConst == None:
        return None

      if arrVar == None :
        # exp( a, x ) = x^a
        if elemFunc.numElements() >= 2:
          elemBase = elemFunc.elements[1]

          if (    isinstance( elemBase, symexpress3.SymVariable)
              and elemBase.name  == elem.elements[1].name
              and elemBase.power == 1
             ):
            # result = exp( constants + 1, x ) / ( n + 1)  , n <> -1
            if (    len( arrConst )    == 1
                and isinstance( arrConst[0], symexpress3.SymNumber )
                and arrConst[0].factor == -1
               ):
              # 1/x = ln(abs(x))
              # x^^(-1) => ln( abs( x ))
              elemNew = symexpress3.SymFunction( "log" )
              elemAbs = symexpress3.SymFunction( "abs" )
              elemAbs.add( symexpress3.SymVariable( elemBase.name ) )
              elemNew.add( elemAbs )

              elemNew = _subToResultAndPower( elemNew )
            else:
              expConst = symexpress3.SymExpress( '*' )
              # exp( n + 1, x ) / ( n + 1)
              for elemConst in arrConst:
                expConst.add( elemConst )

              elemNew = symexpress3.SymExpress( '*' )

              elemPlus = symexpress3.SymExpress( '+' )
              elemPlus.add( symexpress3.SymNumber() )
              elemPlus.add( expConst )

              elemExp = symexpress3.SymFunction( 'exp' )
              elemExp.add( elemPlus )
              elemExp.add( elemBase )

              elemNew.add( elemExp )

              elemPlus.powerSign = -1
              elemNew.add( elemPlus )

            elemNew = _subToResultAndPower( elemNew )
            return elemNew


        return None

      if len( arrVar ) > 1:
        return None

      if (    arrVar[ 0 ].powerSign        != 1
           or arrVar[ 0 ].powerCounter     != 1
           or arrVar[ 0 ].powerDenominator != 1
           or arrVar[ 0 ].onlyOneRoot      != 1
         ):
        return None

      if not isinstance( arrVar[ 0 ], symexpress3.SymVariable ):
        return None

      if elemFunc.numElements() >= 2:
        elemBase = elemFunc.elements[1]
        dDictVar = elemBase.getVariables()
        if elem.elements[1].name in dDictVar:
          return None


      # create constant expression
      expConst = symexpress3.SymExpress( '*' )
      if arrConst == None:
        expConst.add( symexpress3.SymNumber() )
      else:
        for elemConst in arrConst:
          expConst.add( elemConst )

      elemNew = symexpress3.SymExpress( '*' )
      elemNew.add( elemFunc )

      elemDiv = symexpress3.SymExpress( '*' )
      elemDiv.powerSign = -1
      elemDiv.add( expConst )

      if elemFunc.numElements() == 2:
        # TO DO ignore for the moment Integral( a exp( x, b ), x) = exp( a x, b ) / (a ln( b )) , b > 0 and b <> 1
        # Integral( a exp( x, b ), x) = exp( a x, b ) / (a ln( b )) , b > 0 and b <> 1
        elemLog = symexpress3.SymFunction( 'log' )
        elemLog.add( elemFunc.elements[ 1 ] )
        elemDiv.add( elemLog )

      elemNew.add( elemDiv )

      elemNew = _subToResultAndPower( elemNew )

      return elemNew

    def _integralTrigonometricFunctions():
      """
      Integral of (inverse) trigonometric functions
      integral( sin/cos/tan/asin/acos/atan, x )
      """
      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymFunction ):
        return None

      # no power supported
      if elemFunc.power != 1:
        return None

      cFuncName = elemFunc.name
      # print( f"integral funcname: {cFuncName}" )
      if not cFuncName in [ 'sin', 'cos', 'tan', 'asin', 'acos', 'atan' ]:
        return None

      if elemFunc.numElements() != 1:
        return None

      elemParam = elemFunc.elements[ 0 ]
      arrConst, arrVar = _subGetConstantAndVariable ( elemParam )
      if arrVar == None :
        # no variable found in function with power of 1
        # convert the function into a sum to get integrated
        # example: integral( sin( x^3 ),x)

        # convert to sum
        if cFuncName == "sin":
          elemCopy = elem.copy()
          elemCopy.optimize( 'sinToSum' )
          return elemCopy

        if cFuncName == "cos":
          elemCopy = elem.copy()
          elemCopy.optimize( 'cosToSum' )
          return elemCopy

        # tan has no power series with is always valid, see https://proofwiki.org/wiki/Power_Series_Expansion_for_Exponential_of_Tangent_of_x
        # atan was 3 power series for 3 different domains, see https://proofwiki.org/wiki/Power_Series_Expansion_for_Real_Arctangent_Function

        if cFuncName == "asin":
          elemCopy = elem.copy()
          elemCopy.optimize( 'asinToSum' )
          return elemCopy

        if cFuncName == "acos":
          elemCopy = elem.copy()
          elemCopy.optimize( 'acosToSum' )
          return elemCopy

        return None

      if len( arrVar ) > 1:
        return None

      if (    arrVar[ 0 ].powerSign        != 1
           or arrVar[ 0 ].powerCounter     != 1
           or arrVar[ 0 ].powerDenominator != 1
           or arrVar[ 0 ].onlyOneRoot      != 1
         ):
        return None

      if not isinstance( arrVar[ 0 ], symexpress3.SymVariable ):
        return None

      # create constant expression
      expConst = symexpress3.SymExpress( '*' )
      if arrConst == None:
        expConst.add( symexpress3.SymNumber() )
      else:
        for elemConst in arrConst:
          expConst.add( elemConst )

      elemNew = symexpress3.SymExpress( '*' )

      if cFuncName == 'sin':
        # integral( sin( a x )) = (-1 / a ) * cos( a x )
        elemNew.add( symexpress3.SymNumber( -1, 1, 1,1 ) )
        expConst.powerSign = -1
        elemNew.add( expConst )

        elemFnc = symexpress3.SymFunction( 'cos' )
        elemFnc.add( elemParam )
        elemNew.add( elemFnc )

      elif cFuncName == "cos":
        # integral( cos( a x )) = ( 1 / a ) * sin( a x )
        expConst.powerSign = -1
        elemNew.add( expConst )

        elemFnc = symexpress3.SymFunction( 'sin' )
        elemFnc.add( elemParam )
        elemNew.add( elemFnc )

      elif cFuncName == "tan":
        # integral( tan( a x )) = ( -1 / a ) * ln( abs( cos( a x )))
        elemNew.add( symexpress3.SymNumber( -1, 1, 1,1 ) )
        expConst.powerSign = -1
        elemNew.add( expConst )

        elemLog = symexpress3.SymFunction( 'log' )
        elemAbs = symexpress3.SymFunction( 'abs' )
        elemCos = symexpress3.SymFunction( 'cos' )
        elemCos.add( elemParam )
        elemAbs.add( elemCos )
        elemLog.add( elemAbs )
        elemNew.add( elemLog )

      elif cFuncName == "asin":
        # integral( asin( a x )) =  x asin( a x ) + (( 1 - a^^2 x^^2 )^^(1/2)) / a
        elemNew = symexpress3.SymExpress( '+' )

        elemPlus1 = symexpress3.SymExpress( '*' )
        elemAsin = symexpress3.SymFunction( 'asin' )
        elemAsin.add( elemParam )
        elemPlus1.add( symexpress3.SymVariable( elem.elements[ 1 ].name ))
        elemPlus1.add( elemAsin )

        elemNew.add( elemPlus1 )

        elemPlus2 = symexpress3.SymExpress( '*' )
        expConst.powerSign    = -1
        elemPlus2.add( expConst )
        expConst.powerSign    = 1
        expConst.powerCounter = 2

        elemSqrt = symexpress3.SymExpress( '+' )
        elemSqrt.powerDenominator = 2
        elemSqrt.add( symexpress3.SymNumber() )

        elemPower = symexpress3.SymExpress( '*' )
        elemPower.add( symexpress3.SymNumber( -1, 1,1,1 ))
        elemPower.add( expConst )
        elemPower.add( symexpress3.SymVariable( elem.elements[ 1 ].name,1 ,2 ,1 ))

        elemSqrt.add( elemPower )
        elemPlus2.add( elemSqrt )

        elemNew.add( elemPlus2 )

      elif cFuncName == "acos":
        # integral( acos( a x )) =  x acos( a x ) - (( 1 - a^^2 x^^2 )^^(1/2)) / a
        elemNew = symexpress3.SymExpress( '+' )

        elemPlus1 = symexpress3.SymExpress( '*' )
        elemAsin = symexpress3.SymFunction( 'acos' )
        elemAsin.add( elemParam )
        elemPlus1.add( symexpress3.SymVariable( elem.elements[ 1 ].name ))
        elemPlus1.add( elemAsin )

        elemNew.add( elemPlus1 )

        elemPlus2 = symexpress3.SymExpress( '*' )
        elemPlus2.add( symexpress3.SymNumber( -1, 1, 1, 1 ) )
        expConst.powerSign    = -1
        elemPlus2.add( expConst )
        expConst.powerSign    = 1
        expConst.powerCounter = 2

        elemSqrt = symexpress3.SymExpress( '+' )
        elemSqrt.powerDenominator = 2
        elemSqrt.add( symexpress3.SymNumber() )

        elemPower = symexpress3.SymExpress( '*' )
        elemPower.add( symexpress3.SymNumber( -1, 1,1,1 ))
        elemPower.add( expConst )
        elemPower.add( symexpress3.SymVariable( elem.elements[ 1 ].name,1 ,2 ,1 ))

        elemSqrt.add( elemPower )
        elemPlus2.add( elemSqrt )

        elemNew.add( elemPlus2 )

      elif cFuncName == "atan":
        # integral( atan( a x )) =  x atan( a x ) - ln( a^^2 x^^2 + 1) / ( 2 a )
        elemNew = symexpress3.SymExpress( '+' )

        elemPlus1 = symexpress3.SymExpress( '*' )
        elemAsin = symexpress3.SymFunction( 'atan' )
        elemAsin.add( elemParam )
        elemPlus1.add( symexpress3.SymVariable( elem.elements[ 1 ].name ))
        elemPlus1.add( elemAsin )

        elemNew.add( elemPlus1 )

        elemPlus2 = symexpress3.SymExpress( '*' )
        elemPlus2.add( symexpress3.SymNumber( -1, 1, 1, 1 ) )

        elemLog = symexpress3.SymFunction( "log" )
        elemLogParam = symexpress3.SymExpress( '+' )

        expConst.powerCounter = 2
        elemLogParam1 = symexpress3.SymExpress( '*' )
        elemLogParam1.add( expConst )
        elemLogParam1.add( symexpress3.SymVariable( elem.elements[ 1 ].name, 1, 2, 1 ))
        expConst.powerCounter = 1

        elemLogParam.add( elemLogParam1 )
        elemLogParam.add( symexpress3.SymNumber() )
        elemLog.add( elemLogParam )
        elemPlus2.add( elemLog )

        elemPlus2Div = symexpress3.SymExpress( '*' )
        elemPlus2Div.powerSign = -1
        elemPlus2Div.add( symexpress3.SymNumber( 1, 2, 1 ) )
        elemPlus2Div.add( expConst )

        elemPlus2.add( elemPlus2Div )

        elemNew.add( elemPlus2 )

      else:
        return None # is theoretical not possible

      elemNew = _subToResultAndPower( elemNew )

      return elemNew

    def _integralVariable():
      """
      Integral of x^<power> dx
      """
      # get power of x integral( x^^2, x ) = (x^^3)/3, with special case integral(x^^(-1)) = ln( abs(x))
      elemFunc = elem.elements[ 0 ]
      if not isinstance( elemFunc, symexpress3.SymVariable ):
        return None

      if elemFunc.name != elem.elements[1].name:
        return None

      if elemFunc.onlyOneRoot != 1:
        return None

      if (    elemFunc.powerSign        == -1
          and elemFunc.powerCounter     == 1
          and elemFunc.powerDenominator == 1
         ):
        # x^^(-1) => ln( abs( x ))
        elemNew = symexpress3.SymFunction( "log" )
        elemAbs = symexpress3.SymFunction( "abs" )
        elemAbs.add( symexpress3.SymVariable( elemFunc.name ) )
        elemNew.add( elemAbs )

        elemNew = _subToResultAndPower( elemNew )

        return elemNew

      # x^^y => x^^(y+1) / (y + 1)
      # = (y+1)^^(-1) * exp( y + 1, x )
      elemFact = symexpress3.SymNumber( )
      elemFact.factSign        = elemFunc.powerSign
      elemFact.factCounter     = elemFunc.powerCounter
      elemFact.factDenominator = elemFunc.powerDenominator

      elemPlus = symexpress3.SymExpress( '+' )
      elemPlus.add( elemFact )
      elemPlus.add( symexpress3.SymNumber( 1,1,1,1 ))

      elemExp = symexpress3.SymFunction( 'exp' )
      elemExp.add( elemPlus )
      elemExp.add( symexpress3.SymVariable( elemFunc.name ))

      elemPlus.powerSign = -1

      elemNew = symexpress3.SymExpress( '*' )
      elemNew.add( elemPlus )
      elemNew.add( elemExp  )

      elemNew = _subToResultAndPower( elemNew )

      return elemNew


    def _intergralConstantAndVariable():
      """
      Get the constant(s) out of the integral
      integral( a x, x ) = a integral( x, x )
      """
      elemFunc = elem.elements[ 0 ]

      arrConst, arrVar = _subGetConstantAndVariable ( elemFunc )
      if arrVar == None :
        return None

      if arrConst == None:
        return None

      elemNew = symexpress3.SymExpress( '*' )
      elem.copyPower( elemNew )

      for elemConst in arrConst:
        elemNew.add( elemConst )

      elemFnc = symexpress3.SymFunction( 'integral' )

      expVar = symexpress3.SymExpress( '*' )
      for elemVar in arrVar:
        expVar.add( elemVar )
      elemFnc.add( expVar )

      elemFnc.add( elem.elements[ 1 ] )
      if elem.numElements() > 2:
        elemFnc.add( elem.elements[ 2 ] )
        elemFnc.add( elem.elements[ 3 ] )
      elemNew.add( elemFnc )

      return elemNew


    def _integralPlus():
      """
      integral( a + b ) = integral( a ) + integral( b )
      """
      elemFunc = elem.elements[ 0 ]
      if (   isinstance( elemFunc, symexpress3.SymExpress )
          and elemFunc.symType          == '+'
          and elemFunc.numElements()    >  1
          and elemFunc.powerSign        == 1
          and elemFunc.powerCounter     == 1
          and elemFunc.powerDenominator == 1
         ):
        # valid plus integral found
        pass
      else:
        return None

      elemNew = symexpress3.SymExpress( '+' )
      elem.copyPower( elemNew )
      for elemPlus in elemFunc.elements:
        elemAdd = symexpress3.SymFunction( 'integral' )
        elemAdd.add( elemPlus )
        elemAdd.add( elem.elements[ 1 ] )

        if elem.numElements() >= 3:
          elemAdd.add( elem.elements[ 2 ] )
          elemAdd.add( elem.elements[ 3 ] )

        elemNew.add( elemAdd )


      return elemNew

    def _integralConstant():
      """
      integral( a, x ) = a x
      """
      # check if the function is a constant with regarding the variable
      dictVars = elem.elements[ 0 ].getVariables()

      # print( f"elem: {str(elem)}" )
      # print( f"Integral: { str(elem.elements[ 0 ]) }" )
      # print( f"dictVars: { str(dictVars)}" )
      # print( f"Name: {elem.elements[ 1 ].name}" )

      if elem.elements[ 1 ].name in dictVars:
        return None

      elemNew = symexpress3.SymExpress( '*' )

      elemNew.add( elem.elements[ 0 ] )
      elemNew.add( elem.elements[ 1 ] )

      elemNew = _subToResultAndPower( elemNew )

      return elemNew

    #
    # start integral conversion
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

    # constant integral
    elemNew = _integralConstant()
    if elemNew != None:
      return elemNew

    # plus integral
    elemNew = _integralPlus()
    if elemNew != None:
      return elemNew

    # get constant out integral( a x, x ) = a integral( x, x )
    elemNew = _intergralConstantAndVariable()
    if elemNew != None:
      return elemNew

    # get power of x integral( x^^2, x ) = (x^^3)/3, with special case integral(x^^(-1)) = ln( abs(x))
    elemNew = _integralVariable()
    if elemNew != None:
      return elemNew

    # integral( sin/cos/tan/asin/acos/atan )
    elemNew = _integralTrigonometricFunctions()
    if elemNew != None:
      return elemNew

    # integral( exp( a x ), x ) = exp( a x ) / a
    elemNew = _integralExp()
    if elemNew != None:
      return elemNew

    # integral( log( x, a ))
    elemNew = _integralLog()
    if elemNew != None:
      return elemNew

    # integral( sum( x, -1, 1, x ) )
    elemNew = _integralSum()
    if elemNew != None:
      return elemNew

    # TODO integral by parts
    # elemNew = _integralByParts()
    if elemNew != None:
      return elemNew


    return None


  def getValue( self, elemFunc, dDict = None ):
    if self._checkCorrectFunction( elemFunc ) != True:
      return None

    # print( "Calc integral" )

    # need lower and upper to calculate integral
    # if elemFunc.numElements() != 4:
    #  # print( f"integral getValue number of parameters: {elemFunc.numElements()}" )
    #  return None

    if dDict == None:
      dDictSum = {}
    else:
      dDictSum = dDict.copy()

    listStart  = []
    listEnd    = []

    # print( "Calc integral - before var" )

    # delta must always a variable
    cVar = self.getVarname( elemFunc.elements[1] )
    if cVar == None:
      # print( f"integral no varname: { str(elemFunc.elements[1]) }  elemFunc: {str(elemFunc)}" )
      return None

    if elemFunc.numElements() >= 3:
      startVal = elemFunc.elements[2].getValue( dDict )
      if isinstance( startVal, list ):
        listStart = startVal
      else:
        listStart.append( startVal )
    else:
      # not given use infinity
      listStart.append( symexpress3.SymFormulaParser( '-1 * infinity').getValue(dDict) )

    if elemFunc.numElements() >= 4:
      endVal = elemFunc.elements[3].getValue( dDict )
      if isinstance( endVal, list ):
        listEnd = endVal
      else:
        listEnd.append( endVal )
    else:
      # not given use infinity
      listEnd.append( symexpress3.SymFormulaParser( 'infinity').getValue(dDict) )

    # print( f"listStart: {listStart}" )
    # print( f"listEnd  : {listEnd}"   )

    elemExpress = elemFunc.elements[0]

    numOfSteps = 100.0

    result = []
    for startVal in listStart:
      for endVal in listEnd:
        dStart = float( startVal )
        dEnd   = float( endVal   )

        if dStart >= dEnd:
          return None

        dValue = 0
        dStep  = (dEnd - dStart) / numOfSteps

        # print( f"dStart: {dStart}, dEnd: {dEnd}, dStep: {dStep}" )

        dStart += (dStep / 2)
        while dStart < dEnd:

          # print( f"Calc dStart: {dStart}" )

          # for iCnt in range( dStart, dEnd + 1 ):
          dDictSum[ cVar ] = dStart
          # if multiple values are given back, only the first will be used
          # see above by functionToValue()
          value = elemExpress.getValue( dDictSum )

          # print( f"Value: {value}" )

          if isinstance( value, list ):
            dValue += (value[ 0 ] * dStep)
          else:
            dValue += (value * dStep)

          dStart += dStep

        result.append( dValue )

    if len( result ) == 1:
      dValue = result[ 0 ]
    else:
      dValue = result

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
    if dValue != None:
      dValue = round( float(dValue), 10 )
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

  # constant
  symTest = symexpress3.SymFormulaParser( 'integral( 4, x, 0, 5' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, 'integralresult( 4 * x,x,0,5 )', 20.0 )

  # plus
  symTest = symexpress3.SymFormulaParser( 'integral( 4 + x, x, 4 ,8 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integral( 4,x,4,8 ) +  integral( x,x,4,8 )", 40 )

  # constant and variable
  symTest = symexpress3.SymFormulaParser( 'integral( 4 x, x, 1 ,5 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "4 *  integral( x,x,1,5 )", 48 )

  # variable
  symTest = symexpress3.SymFormulaParser( 'integral( x^^2, x, 1 ,5 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( (2 + 1)^^-1 *  exp( 2 + 1,x ),x,1,5 )", 41.3328  )

  # variable (special case)
  symTest = symexpress3.SymFormulaParser( 'integral( x^^-1, x, 1 ,5 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult(  log(  abs( x ) ),x,1,5 )", 1.6093739311 )


  # variable
  symTest = symexpress3.SymFormulaParser( 'integral( x^^(2/3), x, 1 ,5 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( ((2/3) + 1)^^-1 *  exp( (2/3) + 1,x ),x,1,5 )", 8.1720716669 )


  # sin
  symTest = symexpress3.SymFormulaParser( 'integral( sin( 3 x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( (-1) * (3)^^-1 *  cos( 3 * x ),x,(1/10),2 * (1/10) )", 0.043333641  )


  # cos
  symTest = symexpress3.SymFormulaParser( 'integral( cos( 3 x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( (3)^^-1 *  sin( 3 * x ),x,(1/10),2 * (1/10) )", 0.0897074559 )


  # tan
  symTest = symexpress3.SymFormulaParser( 'integral( tan( 3 x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( (-1) * (3)^^-1 *  log(  abs(  cos( 3 * x ) ) ),x,(1/10),2 * (1/10) )", 0.0487577913 )


  # asin
  symTest = symexpress3.SymFormulaParser( 'integral( asin( 3 x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( x *  asin( 3 * x ) + (3)^^-1 * (1 + (-1) * (3)^^2 * x^^2)^^(1/2),x,(1/10),2 * (1/10) )", 0.046917864 )


  # acos
  symTest = symexpress3.SymFormulaParser( 'integral( acos( 3 x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( x *  acos( 3 * x ) + (-1) * (3)^^-1 * (1 + (-1) * (3)^^2 * x^^2)^^(1/2),x,(1/10),2 * (1/10) )", 0.1101617687 )


  # atan
  symTest = symexpress3.SymFormulaParser( 'integral( atan( 3 x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( x *  atan( 3 * x ) + (-1) *  log( (3)^^2 * x^^2 + 1 ) * (2 * 3)^^-1,x,(1/10),2 * (1/10) )", 0.0420537428 )

  # exp
  symTest = symexpress3.SymFormulaParser( 'integral( exp( 3 x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult(  exp( 3 * x ) * (3)^^-1,x,(1/10),2 * (1/10) )", 0.1574199386 )

  # exp base 10
  symTest = symexpress3.SymFormulaParser( 'integral( exp( 3 x, 10 ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult(  exp( 3 * x,10 ) * (3 *  log( 10 ))^^-1,x,(1/10),2 * (1/10) )", 0.2874747819 )

  # exp base x
  symTest = symexpress3.SymFormulaParser( 'integral( exp( 3^^(1/2), x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult(  exp( 1 + 3^^(1/2),x ) * (1 + 3^^(1/2))^^-1,x,(1/10),2 * (1/10) )", 0.0038286527  )


  # log
  symTest = symexpress3.SymFormulaParser( 'integral( log( x ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( x *  log( x ) + (-1) * x,x,(1/10),2 * (1/10) )", -0.1916288649 )


  # log base 10
  symTest = symexpress3.SymFormulaParser( 'integral( log( x, 10 ), x, 1/10 , 2/10 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "integralresult( x *  log( x,10 ) + (-1) * x *  log( 10 )^^-1,x,(1/10),2 * (1/10) )", -0.0832233586 )


  # sum
  symTest = symexpress3.SymFormulaParser( 'integral( sum( n,1,5,n * x^2 ),x )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = None

  _Check( testClass, symTest, value, dValue, "sum( n,1,5, integral( n * x^2,x ) )", None )

  # sum 2
  symTest = symexpress3.SymFormulaParser( 'integral( sum( n,0,4,n * x^^2 ),x,(-10),20 )' )
  symTest.optimize()
  testClass = SymFuncIntegral()
  value     = testClass.functionToValue( symTest.elements[ 0 ] )
  dValue    = testClass.getValue(        symTest.elements[ 0 ] )

  _Check( testClass, symTest, value, dValue, "sum( n,0,4, integral( n * x^^2,x,(-10),20 ) )", 29997.75 )

if __name__ == '__main__':
  Test( True )

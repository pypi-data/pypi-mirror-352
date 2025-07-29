#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Infinity for Sym Express 3

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


    Handle infinity with the idea that all infinities are equal, positive and real.
    This mean:
    infinity - infinity = 0
    infinity / infinity = 1
    infinity * infinity = infinity
    infinity + infinity = infinity

    Accumulation of infinity with the same operation has priority.
    infinity * infinity * infinity / infinity = infinity / infinity = 1

    There are 4 type of infinity's in complex numbers
     1:          infinity  (positive real)
     2: -1 *     infinity  (negative real)
     3:      i * infinity  (positive imaginary)
     4: -1 * i * infinity  (negative imaginary)

     This only work with infinity and numbers.
     Functions are not optimized for infinity. Function must handle infinity them self

"""

from symexpress3          import symexpress3
from symexpress3.optimize import optimizeBase

class OptimizeInfinity( optimizeBase.OptimizeBase ):
  """
  Optimize infinity
  """
  def __init__( self ):
    super().__init__()
    self._name         = "infinity"
    self._symtype      = "all"
    self._desc         = "Optimize infinity"


  def optimize( self, symExpr, action ):
    """
    there are 4 infinity's in complex numbers
     1:          infinity  (positive real)
     2: -1 *     infinity  (negative real)
     3:      i * infinity  (positive imaginary)
     4: -1 * i * infinity  (negative imaginary)
    """

    def _firstInfinity():
      """
      Return the first infinity variable found
      """
      if symExpr.symType == '*':
        # by * only 1 type exist
        for iCnt, elem in enumerate( symExpr.elements ):
          if isinstance( elem, symexpress3.SymVariable ):
            if elem.name == "infinity":
              return iCnt
      else:
        # + type, 4 infinity types exist
        for iCnt, elem in enumerate( symExpr.elements ):
          if isinstance( elem, symexpress3.SymVariable ):
            if elem.name == "infinity":
              return iCnt
          elif (    isinstance( elem, symexpress3.SymExpress )
                and elem.symType       ==  '*'
                and elem.power         == 1  # can only has the power of 1, only infinity variable can has power sign -1
                and elem.numElements() <= 3  # can has max 3 elements
               ) :
            iFound        = 0
            oneFound      = 0
            infinityFound = 0
            for elemSub in elem.elements:
              if isinstance( elemSub, symexpress3.SymNumber ):
                if elemSub.power != 1:
                  return -1
                if elemSub.factor != -1:
                  return -1
                oneFound += 1
              elif isinstance( elemSub, symexpress3.SymVariable ):
                if elemSub.name == 'i':
                  if elemSub.power != 1:
                    return -1
                  iFound += 1
                elif elemSub.name == 'infinity':
                  infinityFound += 1
                else:
                  return -1
              else:
                return -1
            if infinityFound == 0:
              return -1

            if iFound > 1 or oneFound > 1 or infinityFound > 1:
              return -1

            return iCnt # ok, found the first infinity

      return -1 # nothing found

    result = False

    # ----
    # Main
    # ----
    if self.checkExpression( symExpr, action ) != True:
      return result

    # search for first infinity
    firstInfinity = _firstInfinity()
    if firstInfinity < 0:
      return result

    # print( f"found one: {firstInfinity}" )

    if symExpr.symType == '*':
      startInfinity = symExpr.elements[ firstInfinity ]
      sameInfinity = []
      diffInfinity = []

      for iCnt, elem in enumerate( symExpr.elements ) :
        # skip first found
        if iCnt == firstInfinity:
          continue
        if isinstance( elem, symexpress3.SymVariable ):
          if elem.name == "infinity":
            if elem.powerSign == startInfinity.powerSign:
              sameInfinity.append( iCnt )
            else:
              diffInfinity.append( iCnt )
        else:
          # check if there is an infinity in the sub element
          # if so, do nothing, first the the infinity out of the sub element
          dVars = elem.getVariables()
          if 'infinity' in dVars :
            return result # <<<

      # print( f"sameInfinity: {sameInfinity}" )
      # print( f"diffInfinity: {diffInfinity}" )

      # set all the same infinity's to number 1
      if len(sameInfinity) > 0:
        result = True
        for iCnt in sameInfinity:
          symExpr.elements[ iCnt ] = symexpress3.SymNumber()

      otherInfinity = -1
      if len(diffInfinity) > 0:
        result        = True
        otherInfinity = diffInfinity[ 0 ]
        diffInfinity.pop(0)
        for iCnt in diffInfinity:
          symExpr.elements[ iCnt ] = symexpress3.SymNumber()

      # At this point max 2 infinity's exist and if there are 2, they have different power signs
      # This make there value 1 (infinity / infinity = 1)
      if otherInfinity >= 0:
        result = True
        symExpr.elements[ otherInfinity ] = symexpress3.SymNumber()
        symExpr.elements[ firstInfinity ] = symexpress3.SymNumber()
        return result # <<<

      # 1 infinity found, delete all the numbers ( = making them 1)
      iCnt = len( symExpr.elements )
      while iCnt > 0:
        iCnt -= 1
        elem = symExpr.elements[ iCnt ]
        if isinstance( elem, symexpress3.SymNumber ):
          if elem.factSign == -1 and elem.powerDenominator > 1:
            # this is an imaginary number do not change it
            pass
          else:
            if not elem.factor in [ -1, 1 ] :
              symExpr.elements[ iCnt ] = symexpress3.SymNumber( elem.factSign ) # make it 1, multiply will delete it
              result = True
        elif isinstance( elem, symexpress3.SymVariable ):
          if elem.name in [ 'e', 'pi' ]:
            symExpr.elements[ iCnt ] = symexpress3.SymNumber( ) # make it 1, multiply will delete it
            result = True


      # get infinity out of the power
      if ( symExpr.powerCounter > 1 or symExpr.powerDenominator > 1):
        elemCopy = symExpr.copy()

        symExpr.powerCounter     = 1
        symExpr.powerDenominator = 1

        elemCopy.powerSign       = 1

        elemInfinity = elemCopy.elements[ firstInfinity ].copy()
        elemCopy.elements[ firstInfinity ] = symexpress3.SymNumber()

        symExpr.elements = []
        symExpr.elements.append( elemInfinity )
        symExpr.elements.append( elemCopy     )
        result = True

      return result

    if symExpr.symType == '+':
      # print( "Infinity check plus: " + str(symExpr) )
      #
      # loop list
      # if 2 types the same but other sign then make it zero
      #
      normalPos = []
      normalNeg = []
      imagPos   = []
      imagNeg   = []
      for iCnt, elem in enumerate( symExpr.elements ) :
        if isinstance( elem, symexpress3.SymVariable ):
          if elem.name == "infinity":
            if not elem.power in [ 1, -1 ]:
              return result

            normalPos.append( iCnt )
        elif isinstance( elem, symexpress3.SymExpress ):
          if elem.symType == '*':
            if not elem.power in [ 1, -1 ]:
              return result

            # print( f"Check elem: {elem}" )

            dVars = elem.getVariables()
            if 'infinity' in dVars:
              # max elements = -1 * i * infinity
              if elem.numElements() > 3:
                return result

              # ok search for number, and count imaginary and infinity
              elemFound = None
              elemImag  = 0
              elemInfi  = 0
              for elemNum in elem.elements:
                if isinstance( elemNum, symexpress3.SymNumber ):
                  if elemFound != None:
                    return result
                  elemFound = elemNum

                  # only want 1 of -1
                  if elemNum.power != 1:
                    return result
                  if elemNum.factCounter != 1:
                    return result
                  if elemNum.factDenominator != 1:
                    return result

                elif not isinstance( elemNum, symexpress3.SymVariable ):
                  return result
                else:
                  # no powers allowed
                  if elemNum.name == 'infinity' :
                    if not elemNum.power in [ 1, -1]:
                      return result
                  elif elemNum.power != 1:
                    return result

                  if elemNum.name == 'i':
                    elemImag += 1
                  elif elemNum.name == 'infinity':
                    elemInfi += 1
                  else:
                    return result

              # print( f"Check 3 elem: {elem}" )

              # there must always be 1 infinity
              if elemInfi != 1:
                return result

              # there may not be more the 1 imaginary
              if elemImag > 1:
                return result

              # count all the types (infinity,  -1 * infinity,  i * infinity,  -1 * i * infinity )
              if 'i' in dVars:
                if elemFound == None or elemFound.factSign == 1:
                  imagPos.append( iCnt )
                else:
                  imagNeg.append( iCnt )
              else:
                if elemFound == None or elemFound.factSign == 1:
                  normalPos.append( iCnt )
                else:
                  normalNeg.append( iCnt )

          elif 'infinity' in elem.getVariables():
            return result
        else:
          # if infinity in sub element, resolve that first
          if 'infinity' in elem.getVariables():
            return result

      # print( f"normalPos: {normalPos}, normalNeg: {normalNeg}" )
      # print( f"imagPos  : {imagPos}  , imagNeg  : {imagNeg}"   )

      # first at the same, so there can be only 1 of each
      if len( normalPos ) > 1 or len( normalNeg ) > 1:
        return result

      if len( imagPos ) > 1 or len( imagNeg ) > 1:
        return result

      if len( normalPos ) == 1 and len( normalNeg ) == 1:
        symExpr.elements[ normalPos[0] ] = symexpress3.SymNumber( 1, 0, 1, 1 )
        symExpr.elements[ normalNeg[0] ] = symexpress3.SymNumber( 1, 0, 1, 1 )
        # 1 positive and 1 negative found, so make them zero

        result = True

      if len( imagPos ) == 1 and len( imagNeg ) == 1:
        symExpr.elements[ imagPos[0] ] = symexpress3.SymNumber( 1, 0, 1, 1 )
        symExpr.elements[ imagNeg[0] ] = symexpress3.SymNumber( 1, 0, 1, 1 )
        # 1 positive and 1 negative found, so make them zero
        result = True

      if result == True:
        return result


      # type of infinity needed
      # - imaginary
      # - small    (= 1/infinity)
      #
      # can only add imaginary numbers with imaginary numbers
      # small + something = small + something
      # big   + something = big
      #
      isImag = False
      isBig  = False
      elemInfinity = symExpr.elements[ firstInfinity ]
      if isinstance( elemInfinity, symexpress3.SymExpress ):
        for elem in elemInfinity.elements:
          if isinstance( elem, symexpress3.SymVariable ):
            if elem.name == 'i':
              isImag = True
            elif elem.name == 'infinity':
              if elem.powerSign == 1:
                isBig = True
      else:
        if elemInfinity.powerSign == 1:
          isBig = True

      # if infinity small then nothing to do
      if isBig == False:
        return result

      for iCnt, elem in enumerate( symExpr.elements ):
        if iCnt == firstInfinity:
          continue

        if isImag == True:
          # search for imaginary expressions
          if isinstance( elem, symexpress3.SymVariable ) and elem.name == 'i':
            symExpr.elements[ iCnt ] = symexpress3.SymNumber( 1, 0, 1, 1 ) # change i into zero
            result = True
          elif isinstance( elem, symexpress3.SymExpress ) and elem.symType == '*' and elem.power == 1:
            iFound     = 0
            numFound   = 0
            otherFound = 0
            for elemSub in elem.elements:
              if isinstance( elemSub, symexpress3.SymVariable ):
                if elemSub.name == 'i':
                  iFound += 1
                elif elemSub.name in [ 'e', 'pi' ]:
                  numFound += 1
                else:
                  otherFound += 1
                  break
              elif isinstance( elemSub, symexpress3.SymNumber ):
                if elem.factSign == 1 or elem.powerDenominator == 1: # only real numbers
                  numFound += 1
                else:
                  otherFound += 1
                  break
              else:
                otherFound += 1
                break
            if otherFound == 0 and iFound == 1:
              # imaginary number found, so set it to zero
              symExpr.elements[ iCnt ] = symexpress3.SymNumber( 1, 0, 1, 1 ) # change i into zero
              result = True
        else:
          if isinstance( elem, symexpress3.SymNumber ):
            if elem.factCounter != 0 and (elem.factSign == 1 or elem.powerDenominator == 1):
              # this is a real number and can never be a imaginary number, so make it zero (0)
              elem.factSign         = 1
              elem.factCounter      = 0
              elem.factDenominator  = 1
              elem.powerSign        = 1
              elem.powerCounter     = 1
              elem.powerDenominator = 1
              result = True
          elif isinstance( elem, symexpress3.SymVariable ):
            if elem.name in [ 'e', 'pi' ]:
              symExpr.elements[ iCnt ] = symexpress3.SymNumber( 1, 0, 1, 1 ) # change var into zero
              result = True

    # print( f"Result infinity: {result}" )
    return result

#
# Test routine (unit test), see testsymexpress3.py
#
def Test( display = False):
  """
  Unit test
  """
  def _Check( testClass, symOrg, symTest, wanted ):
    if display == True :
      print( f"naam      : {testClass.name}" )
      print( f"orginal   : {str( symOrg  )}" )
      print( f"optimized : {str( symTest )}" )

    if str( symTest ).strip() != wanted:
      print( f"Error unit test {testClass.name} function" )
      raise NameError( f'optimize {testClass.name}, unit test error: {str( symTest )}, value: {str( symOrg )}' )

  result  = False
  symTest = symexpress3.SymFormulaParser( '100 / infinity' )
  symTest.optimize()
  symTest = symTest.elements[ 0 ]
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "1 * infinity^^-1" )


  result  = False
  symTest = symexpress3.SymFormulaParser( 'infinity / infinity' )
  symTest.optimize()
  symTest = symTest.elements[ 0 ]
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "1 * 1" )


  result  = False
  symTest = symexpress3.SymFormulaParser( '5 * infinity / infinity * 6 * infinity * infinity / infinity' )
  symTest.optimize()
  symTest = symTest.elements[ 0 ]
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "5 * 1 * 1 * 6 * 1 * 1 * 1" )


  result  = False
  symTest = symexpress3.SymFormulaParser( '5 * infinity' )
  symTest.optimize()
  symTest = symTest.elements[ 0 ]
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "1 * infinity" )


  result  = False
  symTest = symexpress3.SymFormulaParser( '5 * infinity * ( 1 + infinity)' )
  symTest.optimize()
  symTest = symTest.elements[ 0 ]
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "5 * infinity * (1 + infinity)" )


  result  = False
  symTest = symexpress3.SymFormulaParser( '(log( pi ) * 5 * infinity)^^(2/3)' )
  symTest.optimize()
  symTest = symTest.elements[ 0 ]
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "infinity * ( log( pi ) * 1 * 1)^^(2/3)" )


  result  = False
  symTest = symexpress3.SymFormulaParser( 'infinity + 5' )
  symTest.optimize()
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "infinity + 0" )


  result  = False
  symTest = symexpress3.SymFormulaParser( 'infinity + 5 * i' )
  symTest.optimize()
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "infinity + 5 * i" )


  result  = False
  symTest = symexpress3.SymFormulaParser( 'infinity^^-1 + 5' )
  symTest.optimize()
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "infinity^^-1 + 5" )


  result  = False
  symTest = symexpress3.SymFormulaParser( 'infinity * i + i' )
  symTest.optimize()
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "infinity * i + 0" )


  result  = False
  symTest = symexpress3.SymFormulaParser( 'infinity * i + 5 * i' )
  symTest.optimize()
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "infinity * i + 0" )


  result  = False
  symTest = symexpress3.SymFormulaParser( 'infinity * i + a * i' )
  symTest.optimize()
  symOrg  = symTest.copy()

  testClass = OptimizeInfinity()
  result |= testClass.optimize( symTest, "infinity" )

  _Check( testClass, symOrg, symTest, "infinity * i + a * i" )


if __name__ == '__main__':
  Test( True )

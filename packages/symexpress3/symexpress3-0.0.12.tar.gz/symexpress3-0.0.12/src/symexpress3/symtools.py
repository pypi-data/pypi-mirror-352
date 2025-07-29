#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
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

import mpmath

from symexpress3 import symtables
from symexpress3 import symexpress3

# pylint: disable=global-variable-not-assigned
globalVariableLetter  = "n"  # the letter for the generated unique variable
globalVariableCounter = 1    # the current unique number, rises every time a variable is get

def VariableGenerateGet():
  """
  Get a unique generated variable.
  Format is fixed letter with a unique number
  """
  # pylint: disable=global-statement
  global globalVariableLetter, globalVariableCounter

  varName = globalVariableLetter + str( globalVariableCounter )
  globalVariableCounter += 1
  return varName

def VariableGenerateReset():
  """
  Reset the variable counter.
  Is for test scripts
  """
  # pylint: disable=global-statement
  global globalVariableCounter
  globalVariableCounter = 1

def VariableGenerateSet( newCurrentNumber ):
  """
  Set the variable counter to the given number.
  Is for test scripts
  """
  # pylint: disable=global-statement
  global globalVariableCounter
  globalVariableCounter = newCurrentNumber



def GetAllOptimizeActions():
  """
  Get all the optimize actions in a dictionary [key]=description
  """
  result = {}
  for key, value  in symtables.optSymAnyTable.items():
    result[ key ] = value.description

  for key, value  in symtables.optSymNumberTable.items():
    result[ key ] = value.description

  for key, value  in symtables.optSymVariableTable.items():
    result[ key ] = value.description

  for key, value  in symtables.optSymFunctionTable.items():
    result[ key ] = value.description

  for key, value  in symtables.optimizeTable.items():
    result[ key ] = value.description

  for key, value  in symtables.functionTable.items():
    result[ "functionToValue_" + key ] = value.description

  # fixed values
  result[ "functionToValues" ] = 'Convert functions to values'
  result[ "setOnlyOne"       ] = "All radicals are principal"

  return result


def GetAllFunctions():
  """
  Get all the functions in a dictionary [key]=description
  """
  result = {}
  for objFunc in symtables.functionTable.values():
    key = objFunc.syntax
    if key == None:
      key = objFunc.name
    result[ key ] = objFunc.description

  return result


def GetFixedVariables():
  """
  Get dictionary of fixed defined variables ( [variable name] = description
  """
  if len( symtables.fixedVariables ) > 0:
    return symtables.fixedVariables

  symtables.fixedVariables[ "pi"       ] = "π"
  symtables.fixedVariables[ "i"        ] = "Imaginary number"
  symtables.fixedVariables[ "e"        ] = "Euler's number"
  symtables.fixedVariables[ "infinity" ] = "∞"

  return symtables.fixedVariables


def ConvertToSymexpress3String( varData ):
  """
  Convert given data into a symexpress3 string
  """
  def _floatToString( varData ):
    # print( f"Start: {varData}" )

    varData = str( varData )
    varData = varData.replace( '(', '' )
    varData = varData.replace( ')', '' )
    varData = varData.replace( ' ', '' )

    iplusmin = varData.rfind('+')
    if iplusmin < 0:
      iplusmin = varData.rfind('-')

    if iplusmin > 0:
      realPart = varData[ :(iplusmin) ]
      imagPart = varData[ (iplusmin): ]
    else:
      if 'j' in varData:
        realPart = ""
        imagPart = varData
      else:
        realPart = varData
        imagPart = ""

    realPart = realPart.replace( '+', ''  )
    imagPart = imagPart.replace( '+', ''  )
    imagPart = imagPart.replace( 'j', ''  )

    # print( f"1 realPart: {realPart}, imagPart: {imagPart}" )

    if realPart != "":
      iPoint = realPart.find('.')
      if iPoint >= 0:
        iLen = len( realPart )
        realPart += '/1'
        realPart += "0" * ( iLen - iPoint - 1)
        realPart = realPart.replace( '.', '' )

    # print( f"2 realPart: {realPart}, imagPart: {imagPart}" )

    if imagPart != "":
      iPoint = imagPart.find('.')
      if iPoint >= 0:
        iLen = len( imagPart )
        imagPart += '/1'
        imagPart += "0" * ( iLen - iPoint - 1 )
        imagPart = imagPart.replace( '.', '' )

      imagPart = 'i * ' + imagPart

    # print( f"3 realPart: {realPart}, imagPart:{imagPart}" )

    varData = ""
    if realPart != "":
      varData += realPart

    if imagPart != "":
      if varData != '':
        varData += ' + '
      varData += imagPart

    # print( f"varData: {varData}" )

    return varData

  if isinstance( varData, str ):
    # only numbers (complex to)
    # print( f"Check: {varData}" )
    # if not any( checkChar in varData for checkChar in '.1234567890-+j ' ) :
    # if any( checkChar in varData for checkChar in '.j' ) :
    if (not '(' in varData ) and ('j' in varData or '.' in varData):
      try:
        varData = mpmath.mpmathify( varData )
        # print( f"Is number: {varData}" )
      except: # pylint: disable=bare-except)
        pass # so not a float

  if isinstance( varData, (float, mpmath.mpf, complex, mpmath.mpc) ):
    varData = _floatToString( varData )

    # print( f"Complex string: {varData}" )

  if isinstance( varData, int ):
    varData = str( varData )

  # check on correct symexpress3 string
  try:
    symexpress3.SymFormulaParser( varData )
  except Exception as exceptAll:
    # pylint: disable=raise-missing-from
    raise NameError( f"'{varData}' is not a valid symexpress3 string, error: {str(exceptAll)}" )


  # print( f"End varData: {varData}" )

  return varData

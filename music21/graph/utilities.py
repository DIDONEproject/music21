# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         graph/utilities.py
# Purpose:      Methods for finding external modules, manipulating colors, etc.
#
# Authors:      Christopher Ariza
#               Michael Scott Cuthbert
#
# Copyright:    Copyright © 2009-2012, 2017 Michael Scott Cuthbert and the music21 Project
# License:      LGPL or BSD, see license.txt
#-------------------------------------------------------------------------------
'''
Methods for finding external modules, converting colors to Matplotlib colors, etc.
'''
from __future__ import division, print_function, absolute_import

import unittest
from collections import namedtuple

# TODO: Move _missingImport to environment or common so this is unnecessary.
from music21.base import _missingImport 

from music21 import common
from music21 import exceptions21
from music21 import pitch

from music21.ext import six
from music21.ext import webcolors


from music21 import environment
_MOD = 'graph/utilities.py'
environLocal = environment.Environment(_MOD)    



ExtendedModules = namedtuple('ExtendedModules', 
                             'matplotlib Axes3D collections patches plt networkx')

def getExtendedModules():
    '''
    this is done inside a function, so that the slow import of matplotlib is not done
    in ``from music21 import *`` unless it's actually needed.

    Returns a namedtuple: (matplotlib, Axes3D, collections, patches, plt, networkx)
    '''
    if 'matplotlib' in _missingImport:
        raise GraphException(
            'could not find matplotlib, graphing is not allowed') # pragma: no cover
    import matplotlib # @UnresolvedImport
    # backend can be configured from config file, matplotlibrc,
    # but an early test broke all processing
    #matplotlib.use('WXAgg')
    try:
        from mpl_toolkits.mplot3d import Axes3D # @UnresolvedImport
    except ImportError: # pragma: no cover
        Axes3D = None
        environLocal.warn(
            "mpl_toolkits.mplot3d.Axes3D could not be imported -- likely cause is an " + 
            "old version of six.py (< 1.9.0) on your system somewhere")
    
    from matplotlib import collections # @UnresolvedImport
    from matplotlib import patches # @UnresolvedImport

    #from matplotlib.colors import colorConverter
    import matplotlib.pyplot as plt # @UnresolvedImport
    
    try:
        import networkx
    except ImportError: # pragma: no cover
        networkx = None # use for testing
    
    return ExtendedModules(matplotlib, Axes3D, collections, patches, plt, networkx)

#-------------------------------------------------------------------------------
class GraphException(exceptions21.Music21Exception):
    pass

class PlotStreamException(exceptions21.Music21Exception):
    pass

def accidentalLabelToUnicode(label):
    u'''
    Changes a label possibly containing a modifier such as "-" or "#" into
    a unicode string.
    
    >>> print(graph.utilities.accidentalLabelToUnicode('B-4'))
    B♭4
     
    Since matplotlib's default fonts do not support double sharps or double flats,
    etc. these are converted as best we can...
    
    >>> print(graph.utilities.accidentalLabelToUnicode('B--4'))
    B♭♭4
     
    In Python 2, all strings are converted to unicode strings even if there is
    no need to.
    '''
    if not isinstance(label, six.string_types):
        return label
    if six.PY2 and isinstance(label, str):
        label = six.u(label)
    
    for modifier, unicodeAcc in pitch.unicodeFromModifier.items():
        if modifier != '' and modifier in label and modifier in ('-', '#'):
            # ideally eventually matplotlib will do the other accidentals...
            label = label.replace(modifier, unicodeAcc)
            break 

    return label

# define acceptable format and value strings
FORMATS = ['horizontalbar', 'histogram', 'scatter', 'scatterweighted', 
            '3dbars', 'colorgrid', 'horizontalbarweighted']

# first for each row needs to match a format.
FORMAT_SYNONYMS = [('horizontalbar', 'bar', 'horizontal', 'pianoroll', 'piano'),
                   ('histogram', 'histo', 'count'),
                   ('scatter', 'point'),
                   ('scatterweighted', 'weightedscatter', 'weighted'),
                   ('3dbars', '3d'),
                   ('colorgrid', 'grid', 'window', 'windowed'),
                   ('horizontalbarweighted', 'barweighted', 'weightedbar')]


def userFormatsToFormat(value):
    '''
    Replace possible user format strings with defined format names as used herein. 
    Returns string unaltered if no match.
    
    >>> graph.utilities.userFormatsToFormat('horizontal')
    'horizontalbar'
    >>> graph.utilities.userFormatsToFormat('Weighted Scatter')
    'scatterweighted'
    >>> graph.utilities.userFormatsToFormat('3D')
    '3dbars'
    
    Unknown formats pass through unaltered.
    
    >>> graph.utilities.userFormatsToFormat('4D super chart')
    '4dsuperchart'
    '''
    #environLocal.printDebug(['calling user userFormatsToFormat:', value])
    value = value.lower()
    value = value.replace(' ', '')

    for opt in FORMAT_SYNONYMS:
        if value in opt:
            return opt[0] # first one for each is the preferred
    
    # return unaltered if no match
    #environLocal.printDebug(['userFormatsToFormat(): could not match value', value])
    return value

VALUES = ['pitch', 'pitchspace', 'ps', 'pitchclass', 'pc', 'duration', 
          'quarterlength', 'offset', 'time', 'dynamic', 'dynamics', 'instrument']

def userValuesToValues(valueList):
    '''
    Given a value list, replace string with synonyms. Let unmatched values pass.
    
    >>> graph.utilities.userValuesToValues(['pitchSpace', 'Duration'])
    ['pitch', 'quarterlength']
    '''  
    post = []
    for value in valueList:
        value = value.lower()
        value = value.replace(' ', '')
        if value in ['pitch', 'pitchspace', 'ps']:
            post.append('pitch')
        elif value in ['pitchclass', 'pc']:
            post.append('pitchclass')
        elif value in ['duration', 'quarterlength']:
            post.append('quarterlength')
        elif value in ['offset', 'time']:
            post.append('offset')
        elif value in ['dynamic', 'dynamics']:
            post.append('dynamics')
        elif value in ['instrument', 'instruments', 'instrumentation']:
            post.append('instrument')
        else:
            post.append(value)
    return post


def getColor(color):
    '''
    Convert any specification of a color to a hexadecimal color used by matplotlib. 
    
    >>> graph.utilities.getColor('red')
    '#ff0000'
    >>> graph.utilities.getColor('r')
    '#ff0000'
    >>> graph.utilities.getColor('Steel Blue')
    '#4682b4'
    >>> graph.utilities.getColor('#f50')
    '#ff5500'
    >>> graph.utilities.getColor([0.5, 0.5, 0.5])
    '#808080'
    >>> graph.utilities.getColor(0.8)
    '#cccccc'
    >>> graph.utilities.getColor([0.8])
    '#cccccc'
    >>> graph.utilities.getColor([255, 255, 255])
    '#ffffff'
    
    Invalid colors raise GraphExceptions:
    
    >>> graph.utilities.getColor('l')
    Traceback (most recent call last):
    music21.graph.utilities.GraphException: invalid color abbreviation: l

    >>> graph.utilities.getColor('chalkywhitebutsortofgreenish')
    Traceback (most recent call last):
    music21.graph.utilities.GraphException: invalid color name: chalkywhitebutsortofgreenish

    >>> graph.utilities.getColor(True)
    Traceback (most recent call last):
    music21.graph.utilities.GraphException: invalid color specification: True
    '''
    # expand a single value to three
    if common.isNum(color):
        color = [color, color, color]
    if isinstance(color, six.string_types):
        if color[0] == '#': # assume is hex
            # this will expand three-value codes, and check for badly
            # formed codes
            return webcolors.normalize_hex(color)
        color = color.lower().replace(' ', '')
        # check for one character matplotlib colors
        if len(color) == 1:
            colorMap = {'b': 'blue',
                        'g': 'green',
                        'r': 'red',
                        'c': 'cyan',
                        'm': 'magenta',
                        'y': 'yellow',
                        'k': 'black',
                        'w': 'white'}
            try:
                color = colorMap[color]
            except KeyError:
                raise GraphException('invalid color abbreviation: %s' % color)
        try:
            return webcolors.css3_names_to_hex[color]
        except KeyError: # no color match
            raise GraphException('invalid color name: %s' % color)
        
    elif common.isListLike(color):
        percent = False
        for sub in color:
            if sub < 1:
                percent = True  
                break
        if percent:
            if len(color) == 1:
                color = [color[0], color[0], color[0]]
            # convert to 0 100% values as strings with % symbol
            colorStrList = [str(x * 100) + "%" for x in color]
            return webcolors.rgb_percent_to_hex(colorStrList)
        else: # assume integers
            return webcolors.rgb_to_hex(tuple(color))
    raise GraphException('invalid color specification: %s' % color)

class Test(unittest.TestCase):
    def testColors(self):
        self.assertEqual(getColor([0.5, 0.5, 0.5]), '#808080')
        self.assertEqual(getColor(0.5), '#808080')
        self.assertEqual(getColor(255), '#ffffff')
        self.assertEqual(getColor('Steel Blue'), '#4682b4')

if __name__ == "__main__":
    # sys.arg test options will be used in mainTest()
    import music21
    music21.mainTest(Test) #TestExternal, 'noDocTest') #, runTest='testGetPlotsToMakeA')

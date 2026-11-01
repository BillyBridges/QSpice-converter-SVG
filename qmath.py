# -#- coding: utf-8 -#-#/
# Copyright (C) 2026 by Billy Bridges

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#/

# 2026 Billy Bridges(billyjoebridgesmartin@gmail.com)
# Unless otherwise noted.

# Matching QSpice's March 20, 2026 build

import importlib
import uuid
import math
from math import pi, sin, cos, sqrt, atan2, hypot, floor, radians, degrees
from pathlib import Path
import pickle
import random
import sys
import os
import types
import time
import traceback
import logging
import pkgutil

# param_str is for when using on Adroid, where command line parameters
# are not available. Put only the PARAMETERS to the call in it.
# Ex.:"dimmer.qsch /svg /s=10":
param_str = ''

echo = True

class fallen_SafeDict(dict):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except TypeError:
            return None

    def get(self, key, default=None):
        try:
            return super().get(key, default)
        except TypeError:
            return None

    def __contains__(self, key):
        try:
            return super().__contains__(key)
        except TypeError:
            return False

SafeDict = dict

def real_debug_line_logic(s):
    if echo: print(s)

dbinfo = real_debug_line_logic
# Hide function "#dbline"'s declaration so we can comment out
# debug lines without removing the function's declaration:
# Obfuscate the string "#dbline" using hex character escape codes
# \x64 = d, \x62 = b, \x6c = l, \x69 = i, \x6e = n, \x65 = e
hidden_debug_line_function_name = "\x64\x62\x6c\x69\x6e\x65"

globals()[hidden_debug_line_function_name] = real_debug_line_logic

STR = 'str'
HEX = 'hex'
FLOAT = 'float'
INT = 'int'
LOCAL = 'local'

DYN_PRECISION = 5
epsilon =  0.0000001
epsilon3 = 0.0000003
epsilon3rd = epsilon / 3.0
grow = False
SCALE_FACTOR = 1
M0 = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
LM0 = lambda list = list: [list(M0[0]), list(M0[1]), list(M0[2])]
M1 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
LM1 = lambda list = list: [list(M1[0]), list(M1[1]), list(M1[2])]
virgin_bounds = lambda float = float: {MIN_X: float('inf'), MIN_Y: float('inf'), MAX_X: float('-inf'), MAX_Y: float('-inf')}

INTERNAL_OPTIONS = ('/SCFG', '/LCFG', '/LPL', '/SPL')

FLAGS = {
    '/?':    [LOCAL, 'SHOW_HELP', False, 'Displays help'],
    '/OW':   [LOCAL, 'OVERWRITE', False, 'Overwrites existing files'],
    '/D':    [LOCAL, 'debug_', False, 'Runs debug function'],
    '/M':    [LOCAL, 'MONO', False, 'Generate the schematic in monochrome'],
    '/GS':   [LOCAL, 'GRAY_SCALE', False, 'Generate the schematic in gray scale'],
    '-TR':   [LOCAL, 'qtr', True, 'Do not translate the schematic to canvas center'],
    '-BG':   [LOCAL, 'bg', True, 'Do not fill background color'],
    '+B':    [LOCAL, 'MARK_BOUNDS', False, 'Draw element bound squares'],
    '/P':    [LOCAL, 'wait_', False, 'Waits for the user to press "enter" to close the window'],
    '/EF':   [LOCAL, 'embed_font', False, 'Embed font inside SVG file. Requires the font file to be in', 'working folder'],
    '/E':    [LOCAL, 'echo', False, 'Echoes the debug lines'],
    '-HS':   [LOCAL, 'HIDE_SPICE', True, 'Do not hide spice code'],
    '-OP':   [LOCAL, 'OPTIMIZE_PATHS', True, 'Do not optimize paths'],
    '-CL':   [LOCAL, 'CORRECT_LEGIBILITY', True, 'Do not correct text legibility angle'],
    '/SVG':  [LOCAL, 'SAVE_SVG', False, 'Saves the schematic as SVG file, with symbol abstraction(TASK)'],
    '/FSVG': [LOCAL, 'SAVE_FSVG', False, 'Saves the schematic as a flat SVG file(TASK)'],
    '/CRV':  [LOCAL, 'CENTER_RESISTOR_VALUE', False, "Places the resistor value in the symbol's center"],
    '/APRIN':[LOCAL, 'AUTOPLACE_RESISTOR_INSTANCE_NAME', False, "Auto-places resistor instance name in accordance with the same", "parameters used to auto-place the resistor's value"]
}

PARAMETERS = {
    # Parameters to draw the schematic:
    # When the lists are longer than 4, the last
    # parameters are all interpreted as strings
    '/F':      [LOCAL, 'FONT', 'Tahoma', str, 'font'], # Default = 'Tahoma'
    '/S':      [LOCAL, 'SCALE_FACTOR', 1.0, float, 'scale factor'], # Default = 1
    '/R':      [LOCAL, 'VARIANCE', 0.0, float, 'variance', 'Randomizes parameters using unit variance x'], # Default = 0
    '/JD':     [LOCAL, 'JUNCTION_DIAMETER', 80.0, float, 'junction diameter'], # Default = 80
    '/JS':     [LOCAL, 'JUMPER_JUNCTION_SCALE', 0.6, float, 'jumper junction scale'], # Default = 0.6
    '/JW':     [LOCAL, 'JUMPER_LINE_SCALE', 1.66, float, 'jumper line scale'], # Default = 1.66
    '/SW':     [LOCAL, 'STROKE_WIDTH', 15.0, float, 'stroke width'], # Default = 15
    '/NSW':    [LOCAL, 'NOT_STROKE_WIDTH', 15.0, float, '"not" stroke width'], # Default = 15
    '/NAC':    [LOCAL, 'NOT_ASCENT_COEFFICIENT', 0.74, float, '"not" ascent coefficient'], # Default = 0.74
    '/SS':     [LOCAL, 'STROKE_STEP', 4.0, float, 'stroke increase step'], # Default = 4
    '/NDS':    [LOCAL, 'NON_DEFAULT_STROKE_WIDTH', 15.0, float, 'non-default stroke width'], # Default = 15
    '/PNSW':   [LOCAL, 'PIN_SW', 8.0, float, 'pin stroke width'], # Default = 8
    '/TO':     [LOCAL, 'TOLERANCE', 0.2, float, 'distance tolerance' ], # Default = 0.2
    '/PS':     [LOCAL, 'PIN_SIZE', 1.4, float, 'pin size'], # Default = 1.4
    '/FG':     [LOCAL, 'FOREGROUND_COLOR', 0xFF0000, HEX, 'foreground color'], # Default = 0xFF0000
    '/WC':     [LOCAL, 'WIRE_COLOR', 0xFF0000, HEX, 'wire color'], # Default = 0xFF0000
    '/JC':     [LOCAL, 'JUNCTION_COLOR', 0xFF0000, HEX, 'junction color'], # Default = 0xFF0000
    '/CAC':    [LOCAL, 'COMPONENT_ATT_COLOR', 0x000000, HEX, 'component attribute color'], # Default = 0x000000    
    '/ASC':    [LOCAL, 'ANNOTATION_STROKE_COLOR', 0xFF0000, HEX, 'symbol annotation stroke color'], # Default = 0xFF0000 
    '/SASC':   [LOCAL, 'SYMBOL_ANNOTATION_STROKE_COLOR', 0xFF0000, HEX, 'symbol annotation stroke color'], # Default = 0xFF0000     
    '/AFC':    [LOCAL, 'SOLID_ANNOTATION_FILL_COLOR', 0x00FFFF, HEX, 'solid annotation_fill color'], # Default = 0x00FFFF  
    '/SAFC':   [LOCAL, 'SYMBOL_ANNOTATION_FILL_COLOR', 0x00FFFF, HEX, 'symbol annotation_fill color'], # Default = 0x00FFFF 
    '/CCC':    [LOCAL, 'COMPONENT_COMMENT_COLOR', 0xFF0000, HEX, 'component comment color'], # Default = 0xFF0000      
    '/HBSC':   [LOCAL, 'HIERARCHICAL_BLOCK_STROKE_COLOR', 0xFF0000, HEX, 'hierarchical block color'], # Default = 0xFF0000
    '/PNSC':   [LOCAL, 'PIN_STROKE_COLOR', 0x000000, HEX, 'pin stroke color'], # Default = 0x000000
    '/PNFC':   [LOCAL, 'PIN_FILL_COLOR', 0xFFFFFF, HEX, 'pin fill color'], # Default = 0xFFFFFF    
    '/BC':     [LOCAL, 'BACKGROUND_COLOR', 0xE9FFFF, HEX, 'background color'], # Default = 0xE9FFFF
    '/DNC':    [LOCAL, 'DONOTSTUFF_COLOR', 0xAEBFBF, HEX, '"do not stuff" color'], # Default = 0xAEBFBF
    '/QC':     [LOCAL, 'BRAND_COLOR', 0x000000, HEX, 'brand color'], # Default = 0x000000
    '/TC':     [LOCAL, 'TAP_COLOR', 0x0000FF, HEX, 'tap color'], # Default = 0x0000FF
    '/NC':     [LOCAL, 'NET_COLOR', 0x0000FF, HEX, 'net color'], # Default = 0x0000FF
    '/NDC':    [LOCAL, 'NET_DESCRIPTION_COLOR', 0x007700, HEX, 'net description color'], # Default = 0x007700
    '/CC':     [LOCAL, 'COMMENT_COLOR', 0xFF0000, HEX, 'comment color'], # Default = 0xFF0000
    '/SSC':    [LOCAL, 'SPICE_STATEMENT_COLOR', 0x000000, HEX, 'spice statement color'], # Default = 0x000000
    '/HBC':    [LOCAL, 'HIERARCHICAL_BLOCK_COLOR', 0xC8C8C8, HEX, 'hierarchical block color'], # Default = 0xC8C8C8
    '/TSW':    [LOCAL, 'TAP_SW', 0.5, float, 'tap stroke width'], # Default = 0.5
    '/TS':     [LOCAL, 'TAP_SCALE', 13.0, float, 'tap scale'], # Default = 13
    '/JSW':    [LOCAL, 'JUNCTION_SW', 1.0, float, 'junction stroke width'], # Default = 1
    '/FS':     [LOCAL, 'FONT_SCALE', 160.0, float, 'font scale'], # Default = 160
    '/NTXOA':  [LOCAL, 'NET_TEXT_X_OFFSET_ABSOLUTE', 45.0, float, 'net text X absolute offset'], # Default = 45
    '/NTYOA':  [LOCAL, 'NET_TEXT_Y_OFFSET_ABSOLUTE', 0.0, float, 'net text Y absolute offset'], # Default = 0
    '/NTXOR':  [LOCAL, 'NET_TEXT_X_OFFSET_RELATIVE', 0.0, float, 'net text X relative offset'], # Default = 0
    '/NTYOR':  [LOCAL, 'NET_TEXT_Y_OFFSET_RELATIVE', 0.0, float, 'net text Y relative offset'], # Default = 0
    '/PNTXOA': [LOCAL, 'PERPENDICULAR_NET_TEXT_X_OFFSET_ABSOLUTE', 0.0, float, 'perpendicular net text X absolute offset'], # Default = 0
    '/PNTYOA': [LOCAL, 'PERPENDICULAR_NET_TEXT_Y_OFFSET_ABSOLUTE', 0.0, float, 'perpendicular net text Y absolute offset'], # Default = 0
    '/PNTXOR': [LOCAL, 'PERPENDICULAR_NET_TEXT_X_OFFSET_RELATIVE', 0.0, float, 'perpendicular net text X relative offset'], # Default = 0
    '/PNTYOR': [LOCAL, 'PERPENDICULAR_NET_TEXT_Y_OFFSET_RELATIVE', -0.3, float, 'perpendicular net text Y relative offset'], # Default = -0.3
    '/PPNTYOR':[LOCAL, 'PORT_PERPENDICULAR_NET_TEXT_Y_OFFSET_RELATIVE', -0.3, float, 'port perpendicular net text Y relative offset'], # Default = -0.3
    '/PPNTYOA':[LOCAL, 'PORT_PERPENDICULAR_NET_TEXT_Y_OFFSET_ABSOLUTE', 0.0, float, 'port perpendicular net text Y absolute offset'], # Default = 0
    '/PC':     [LOCAL, 'PORT_COLOR', 0xFFFFFF, HEX, 'port color'], # Default = 0xFFFFFF
    '/PSC':    [LOCAL, 'PORT_STROKE_COLOR', 0x0000FF, HEX, 'port stroke color'], # Default = 0x0000FF
    '/PSW':    [LOCAL, 'PORT_SW', 8.0, float, 'port stroke width'], # Default = 8
    '/PPXA':   [LOCAL, 'PORT_PADDING_X_ABSOLUTE', 0.0, float, 'port X absolute padding'], # Default = 0
    '/PPXR':   [LOCAL, 'PORT_PADDING_X_RELATIVE', 0.2, float, 'port X relative padding'], # Default = 0.2
    '/PPYA':   [LOCAL, 'PORT_PADDING_Y_ABSOLUTE', 0.0, float, 'port Y absolute padding'], # Default = 0
    '/PPYR':   [LOCAL, 'PORT_PADDING_Y_RELATIVE', 0.2, float, 'port Y relative padding'], # Default = 0.2
    '/POXA':   [LOCAL, 'PORT_OFFSET_X_ABSOLUTE', 0.0, float, 'port X absolute offset'], # Default = 0
    '/POXR':   [LOCAL, 'PORT_OFFSET_X_RELATIVE', 0.0, float, 'port X relative offset'], # Default = 0.0
    '/POYA':   [LOCAL, 'PORT_OFFSET_Y_ABSOLUTE', 0.0, float, 'port Y absolute offset'], # Default = 0
    '/POYR':   [LOCAL, 'PORT_OFFSET_Y_RELATIVE', 0.0, float, 'port Y relative offset'], # Default = 0.0
    '/CP':     [LOCAL, 'CANVAS_PADDING', 0.035, float, 'canvas padding'], # Default = 0.035
    '/G':      [LOCAL, 'GROW', 2, int, '.QSCH and .QSYM coordinate grow factor', 'Saves a copy of the .QSCH and', '.QSYM files(TASK) with the coordinates multiplied. This is equivalent', 'to altering the grid size. Set "native symbol scale" parameter equal', 'to the used grow factor to draw grown schematics.'], # Default = 2
    '/W':      [LOCAL, 'WIDTHCM', None, float, 'width in centimeters', 'If dimensions are not informed, defaults to A3'],
    '/H':      [LOCAL, 'HEIGHTCM', None, float, 'height in centimeters', 'If dimensions are not informed, defaults to A3'],
    '/UPC':    [LOCAL, 'UNITSPERCM', None, float, 'units per centimeter', 'If dimensions are not informed, defaults to A3'],
    '/NSS':    [LOCAL, 'NATIVE_SYMBOL_SCALE', 1, int, 'native symbol scale' ], # Default = 1
    '/PAOR':   [LOCAL, 'PINLABEL_ANCHOR_OFFSET_RELATIVE', 0.3, float, 'pin label anchor relative offset'], # Default = 0.3
    '/PBOR':   [LOCAL, 'PINLABEL_BASELINE_OFFSET_RELATIVE', 0.0, float, 'pin label baseline relative offset'], # Default = 0
    '/PEOR':   [LOCAL, 'PINLABEL_END_OFFSET_RELATIVE', 0.0, float, 'pin label end relative offset'], # Default = 0
    '/PSOR':   [LOCAL, 'PINLABEL_START_OFFSET_RELATIVE', 0.0, float, 'pin label start relative offset'], # Default = 0
    '/PABOR':  [LOCAL, 'PINLABEL_ALPHABETIC_OFFSET_RELATIVE', -0.3, float, 'pin label alphabetic relative offset'], # Default = -0.3
    '/PHOR':   [LOCAL, 'PINLABEL_HANGING_OFFSET_RELATIVE', 0.0, float, 'pin label hanging relative offset'], # Default = 0
    '/PXOR':   [LOCAL, 'PINLABEL_X_OFFSET_RELATIVE', 0.0, float, 'pin label X relative offset'], # Default = 0
    '/PYOR':   [LOCAL, 'PINLABEL_Y_OFFSET_RELATIVE', 0.0, float, 'pin label Y relative offset'], # Default = 0
    '/PMXOR':  [LOCAL, 'PINLABEL_MIDDLE_X_OFFSET_RELATIVE', 0.0, float, 'pin label middle X relative offset'], # Default = 0
    '/PMYOR':  [LOCAL, 'PINLABEL_MIDDLE_Y_OFFSET_RELATIVE', 0.0, float, 'pin label middle Y relative offset'], # Default = 0
    '/TAOR':   [LOCAL, 'TEXT_ANCHOR_OFFSET_RELATIVE', 0.0, float, 'text anchor relative offset'], # Default = 0
    '/TBOR':   [LOCAL, 'TEXT_BASELINE_OFFSET_RELATIVE', 0.0, float, 'text baseline relative offset'], # Default = 0
    '/TEOR':   [LOCAL, 'TEXT_END_OFFSET_RELATIVE', 0.0, float, 'text end relative offset'], # Default = 0
    '/TSOR':   [LOCAL, 'TEXT_START_OFFSET_RELATIVE', 0.0, float, 'text start relative offset'], # Default = 0
    '/TABOR':  [LOCAL, 'TEXT_ALPHABETIC_OFFSET_RELATIVE', 0.0, float, 'text alphabetic relative offset'], # Default = 0
    '/THOR':   [LOCAL, 'TEXT_HANGING_OFFSET_RELATIVE', 0.0, float, 'text hanging relative offset'], # Default = 0
    '/TXOR':   [LOCAL, 'TEXT_X_OFFSET_RELATIVE', 0.0, float, 'text X relative offset'], # Default = 0
    '/TYOR':   [LOCAL, 'TEXT_Y_OFFSET_RELATIVE', 0.0, float, 'text Y relative offset'], # Default = 0
    '/TMXOR':  [LOCAL, 'TEXT_MIDDLE_X_OFFSET_RELATIVE', 0.0, float, 'text middle X relative offset'], # Default = 0
    '/TMYOR':  [LOCAL, 'TEXT_MIDDLE_Y_OFFSET_RELATIVE', 0.0, float, 'text middle Y relative offset'], # Default = 0
    '/PAOA':   [LOCAL, 'PINLABEL_ANCHOR_OFFSET_ABSOLUTE', 0.0, float, 'pin label anchor absolute offset'], # Default = 0
    '/PBOA':   [LOCAL, 'PINLABEL_BASELINE_OFFSET_ABSOLUTE', 0.0, float, 'pin label baseline absolute offset'], # Default = 0
    '/PEOA':   [LOCAL, 'PINLABEL_END_OFFSET_ABSOLUTE', 0.0, float, 'pin label end absolute offset'], # Default = 0
    '/PSOA':   [LOCAL, 'PINLABEL_START_OFFSET_ABSOLUTE', 0.0, float, 'pin label start absolute offset'], # Default = 0
    '/PABOA':  [LOCAL, 'PINLABEL_ALPHABETIC_OFFSET_ABSOLUTE', 0.0, float, 'pin label alphabetic absolute offset'], # Default = 0
    '/PHOA':   [LOCAL, 'PINLABEL_HANGING_OFFSET_ABSOLUTE', 0.0, float, 'pin label hanging absolute offset'], # Default = 0
    '/PXOA':   [LOCAL, 'PINLABEL_X_OFFSET_ABSOLUTE', 0.0, float, 'pin label X absolute offset'], # Default = 0
    '/PYOA':   [LOCAL, 'PINLABEL_Y_OFFSET_ABSOLUTE', 0.0, float, 'pin label Y absolute offset'], # Default = 0
    '/PMXOA':  [LOCAL, 'PINLABEL_MIDDLE_X_OFFSET_ABSOLUTE', 0.0, float, 'pin label middle X absolute offset'], # Default = 0
    '/PMYOA':  [LOCAL, 'PINLABEL_MIDDLE_Y_OFFSET_ABSOLUTE', 0.0, float, 'pin label middle Y absolute offset'], # Default = 0
    '/TAOA':   [LOCAL, 'TEXT_ANCHOR_OFFSET_ABSOLUTE', 0.0, float, 'text anchor absolute offset'], # Default = 0
    '/TBOA':   [LOCAL, 'TEXT_BASELINE_OFFSET_ABSOLUTE', 0.0, float, 'text baseline absolute offset'], # Default = 0
    '/TEOA':   [LOCAL, 'TEXT_END_OFFSET_ABSOLUTE', 0.0, float, 'text end absolute offset'], # Default = 0
    '/TSOA':   [LOCAL, 'TEXT_START_OFFSET_ABSOLUTE', 0.0, float, 'text start absolute offset'], # Default = 0
    '/TABOA':  [LOCAL, 'TEXT_ALPHABETIC_OFFSET_ABSOLUTE', -2.0, float, 'text alphabetic absolute offset'], # Default = -2
    '/THOA':   [LOCAL, 'TEXT_HANGING_OFFSET_ABSOLUTE', -6.0, float, 'text hanging absolute offset'], # Default = -6
    '/TXOA':   [LOCAL, 'TEXT_X_OFFSET_ABSOLUTE', 0.0, float, 'text X absolute offset'], # Default = 0
    '/TYOA':   [LOCAL, 'TEXT_Y_OFFSET_ABSOLUTE', 0.0, float, 'text Y absolute offset'], # Default = 0
    '/TMXOA':  [LOCAL, 'TEXT_MIDDLE_X_OFFSET_ABSOLUTE', 0.0, float, 'text middle X absolute offset'], # Default = 0
    '/TMYOA':  [LOCAL, 'TEXT_MIDDLE_Y_OFFSET_ABSOLUTE', -10.0, float, 'text middle Y absolute offset'], # Default = -10
    '/TAO':    [LOCAL, 'TEXT_ANGLE_OFFSET', 0.0, float, 'text angle offset'], # Default = 0
    '/TCYOR':  [LOCAL, 'TEXT_CENTER_Y_OFFSET_RELATIVE', 0.0, float, 'text center Y relative offset '], # Default = 0
    '/TCYOA':  [LOCAL, 'TEXT_CENTER_Y_OFFSET_ABSOLUTE', 0.0, float, 'text center Y absolute offset '], # Default = 0
    '/TCXOR':  [LOCAL, 'TEXT_CENTER_X_OFFSET_RELATIVE', 0.0, float, 'text center X relative offset '], # Default = 0
    '/TCXOA':  [LOCAL, 'TEXT_CENTER_X_OFFSET_ABSOLUTE', 0.0, float, 'text center X absolute offset '], # Default = 0
    '/RCVXOA': [LOCAL, 'RESISTOR_CENTER_VALUE_X_OFFSET_ABSOLUTE', 0.0, float, 'resistor center value X absolute offset '], # Default = 0
    '/RCVYOA': [LOCAL, 'RESISTOR_CENTER_VALUE_Y_OFFSET_ABSOLUTE', 0.0, float, 'resistor center value Y absolute offset '], # Default = 0
    '/RCVXOR': [LOCAL, 'RESISTOR_CENTER_VALUE_X_OFFSET_RELATIVE', 0.0, float, 'resistor center value X relative offset '], # Default = 0
    '/RCVYOR': [LOCAL, 'RESISTOR_CENTER_VALUE_Y_OFFSET_RELATIVE', 0.0, float, 'resistor center value Y relative offset '], # Default = 0
    '/RCVAO':  [LOCAL, 'RESISTOR_CENTER_VALUE_ANGLE_OFFSET', -90.0, float, 'resistor center value angle offset'], # Default = -90
    '/RCVCYOR':[LOCAL, 'RESISTOR_CENTER_VALUE_CENTER_Y_OFFSET_RELATIVE', -0.078, float, 'resistor center value Y center relative offset '], # Default = -0.078
    '/RCVCYOA':[LOCAL, 'RESISTOR_CENTER_VALUE_CENTER_Y_OFFSET_ABSOLUTE', 0.0, float, 'resistor center value Y center absolute offset '], # Default = 0
    '/RCVCXOR':[LOCAL, 'RESISTOR_CENTER_VALUE_CENTER_X_OFFSET_RELATIVE', 0.0, float, 'resistor center value X center relative offset'], # Default = 0
    '/RCVCXOA':[LOCAL, 'RESISTOR_CENTER_VALUE_CENTER_X_OFFSET_ABSOLUTE', 0.0, float, 'resistor center value X center absolute offset'], # Default = 0
    '/RCVFRS': [LOCAL, 'RESISTOR_CENTER_VALUE_FONT_RESCALE', 1.0, float, 'resistor center value font rescale'], # Default = 1
    '/RINYOR': [LOCAL, 'RESISTOR_INSTANCE_NAME_Y_OFFSET_RELATIVE', -0.12, float, 'resistor instance name Y relative offset'], # Default = -0.12
    '/RINYOA': [LOCAL, 'RESISTOR_INSTANCE_NAME_Y_OFFSET_ABSOLUTE', -60.0, float, 'resistor instance name Y absolute offset'], # Default = -60
    '/RINFRS': [LOCAL, 'RESISTOR_INSTANCE_NAME_FONT_RESCALE', 1.0, float, 'resistor instance name font rescale'] # Default = 1
}

MARK_BOUNDS = False

HELP_HEADER = [
'',
'QSpice file interpreter.',
'',
'Usage:',
'    python qsconvert.py [filename ...] [options]',
'',
'If called with no filenames in parameters, processes all suitable files ',
'in working directory.',
'',
'Parameter attribution can multiply, add, subtract or divide the value',
'already present with the operators *=, +=, -= and /= respectively.',
''
]
# After printing this help text, the script continues to describe all
# the parameters for the drawing

# Font metrics names:
WIN_ASCENT = 'win_ascent'
WIN_DESCENT = 'win_descent'
TYPO_ASCENT = 'typo_ascent'
TYPO_DESCENT = 'typo_descent'
TYPO_LINE_GAP = 'typo_line_gap'
HHEAD_ASCENT = 'hhead_ascent'
HHEAD_DESCENT = 'hhead_descent'
HHEAD_LINE_GAP = 'hhead_line_gap'
CAPITAL_HEIGHT = 'capital_height'
X_HEIGHT = 'x_height'
ASCENT = 'ascent'
EM_SIZE = 'em_size'
DESCENT = 'descent'
UNDERLINE_POSITION = 'underline_position'
HEIGHT = 'height'

Qorvo = [('M', (8.423401432389602, -77.4430620471866)), ('C', (-25.09396435286681, -77.4430620471866, -52.270509255341885, -50.261234702279204, -52.270509255341885, -16.732166014013533)), ('L', (-52.270509255341885, 42.44606334106125)), ('C', (-52.270509255341885, 49.986182281339026, -46.15903965580485, 56.10418435292023, -38.61892025646368, 56.10418435292023)), ('C', (-31.07306577818732, 56.10418435292023, -24.95557097165242, 49.986182281339026, -24.95557097165242, 42.44606334106125)), ('L', (-24.95557097165242, -16.732166014013533)), ('C', (-24.95557097165242, -35.17503496547365, -10.00799368869302, -50.12420428027066, 8.423401432389602, -50.12420428027066)), ('C', (25.035757869355415, -50.12420428027066, 38.80174041540242, -37.998302818767804, 41.37249540115741, -22.120675960808406)), ('L', (41.38164178014601, -22.120675960808406)), ('C', (42.43174928548789, -15.624928987873933, 48.07235618839031, -10.666825399252136, 54.86075607264957, -10.666825399252136)), ('C', (56.9468502934473, -10.666825399252136, 69.70003525213676, -11.984747732122507, 68.26800995922365, -26.946032188853277)), ('C', (63.41909781143163, -55.6090293988604, 38.47483862077991, -77.4430620471866, 8.423401432389602, -77.4430620471866)), ('Z', ()), ('M', (-135.30766268928062, -77.43260917378917)), ('C', (-168.83076676691596, -77.43260917378917, -196.01269510576924, -50.24948267948718, -196.00810447186612, -16.720406187143876)), ('L', (-196.01725360523506, -4.584498658641381)), ('C', (-196.01128578116098, 28.93860509764957, -168.82945843625356, 56.11463722631766, -135.30635435861822, 56.11463722631766)), ('C', (-101.78325028098291, 56.11463722631766, -74.59415137197294, 28.937864169337608, -74.59415137197294, -4.579272176036325)), ('L', (-74.59676344266381, -16.713873256036326)), ('C', (-74.59676344266381, -23.368846365900996, -75.80234194640313, -29.769355588817664, -77.63858173575498, -35.64029662968305)), ('C', (-79.41745237321938, -41.11462755917023, -84.55319191791311, -45.07410943792735, -90.61856696242877, -45.07410943792735)), ('C', (-98.16442144070514, -45.07410943792735, -104.27538147987892, -38.9508781752671, -104.27538147987892, -31.410760612179487)), ('C', (-104.27538147987892, -27.715373770299145, -101.91692954024217, -23.727012672720797, -101.91692954024217, -16.720406187143876)), ('L', (-101.91692954024217, -4.584498658641381)), ('C', (-101.91692954024217, 13.858372725854702, -116.86479098344017, 28.801006814227208, -135.30766268928062, 28.801006814227208)), ('C', (-153.73331951798434, 28.795498053543447, -168.68794296492166, 13.858372725854702, -168.68794296492166, -4.584498658641381)), ('L', (-168.68794296492166, -16.715179750445156)), ('C', (-168.68794296492166, -35.169523909472936, -153.73331951798434, -50.11244307621082, -135.30766268928062, -50.11244307621082)), ('C', (-122.61152553810541, -50.09940567592593, -119.60115767788461, -44.24832417638889, -112.5554481727208, -44.24832417638889)), ('C', (-105.00959369444445, -44.24832417638889, -98.90322428917379, -50.35905652012109, -98.89863365527066, -57.905140530092595)), ('C', (-98.89863365527066, -63.08108025587607, -101.77389915972222, -67.59155250979344, -106.01449722774217, -69.90385480680199)), ('C', (-114.70219843928064, -74.70106723557691, -124.68608349590455, -77.43260917378917, -135.30766268928062, -77.43260917378917)), ('Z', ()), ('M', (265.69602045049857, -77.41954422970086)), ('C', (232.16717808048435, -77.41954422970086, 204.99034993589746, -50.24276199145299, 204.99034993589746, -16.725632623842593)), ('L', (204.99165826655982, -4.589725141246438)), ('C', (204.99165826655982, 1.7738115752777777, 206.1281982270299, 8.30395772886396, 207.94723691114672, 14.059694516613249)), ('C', (208.13637102795585, 15.194246732603277, 211.5785430943732, 23.763978293162396, 221.00692472364673, 23.763978293162396)), ('C', (228.55277920192307, 23.763978293162396, 234.66504757175926, 17.641769364672367, 234.66504757175926, 10.10716193945869)), ('C', (234.66504757175926, 6.4280993917378915, 232.3065956321225, 2.451242881784188, 232.3065956321225, -4.583192026513532)), ('L', (232.3065956321225, -16.719099692735043)), ('C', (232.3065956321225, -35.161965889814816, 247.25445707532052, -50.10460686413818, 265.697328781161, -50.10460686413818)), ('C', (284.1287239022436, -50.10460686413818, 299.0763007261396, -35.161965889814816, 299.0763007261396, -16.719099692735043)), ('L', (299.0763007261396, -4.588418555024929)), ('C', (299.0763007261396, 13.865929827386038, 284.1287239022436, 28.80157238032407, 265.697328781161, 28.807540204398148)), ('C', (253.03158621705842, 28.807540204398148, 249.98439229166667, 22.938193031623932, 242.94511426460113, 22.938193031623932)), ('C', (235.39352149394588, 22.938193031623932, 229.29403344889602, 29.05489274036681, 229.28829515651708, 36.59500892626424)), ('C', (229.28829515651708, 41.7769164761218, 232.16225692094017, 46.280677682336176, 236.40285498896012, 48.5989478034188)), ('C', (245.090629650641, 53.39065147150997, 255.070011295406, 56.12770676103989, 265.697328781161, 56.12770676103989)), ('C', (299.2146945664174, 56.12770676103989, 326.39646223308404, 28.939912051121794, 326.39646223308404, -4.583192026513532)), ('L', (326.40038263443734, -16.719099692735043)), ('C', (326.39689375267096, -50.24219734348291, 299.213386235755, -77.42551205377494, 265.69602045049857, -77.41954422970086)), ('Z', ()), ('M', (-276.17069017770655, -77.41431549768518)), ('C', (-309.6993076066596, -77.41431549768518, -336.8763606923077, -50.23276818144587, -336.8763606923077, -16.69819394594017)), ('L', (-336.8763606923077, -4.560979463965456)), ('C', (-336.8763606923077, 28.812928690473647, -309.93458677546295, 55.891183530448714, -276.61232752172367, 56.13815963443732)), ('L', (-269.6232067606838, 56.13815963443732)), ('C', (-258.10071566381765, 55.968306180021365, -247.0319260968661, 61.824807381944446, -240.788663988604, 71.88426345388177)), ('L', (-240.77951944586894, 71.88426345388177)), ('C', (-237.3308057261396, 77.51926656997863, -230.19758037624644, 79.97567345584045, -223.908411928953, 77.35901213105413)), ('C', (-215.44240620049857, 73.86112354095441, -213.37890248913817, 63.906636903846156, -217.7398486155627, 57.20567023290598)), ('L', (-217.73723195423787, 57.217426846331904)), ('C', (-229.04740623308405, 39.1877121917735, -248.90092464975072, 28.658062278561253, -269.62189843002136, 28.812766641096864)), ('L', (-276.58880970423786, 28.812766641096864)), ('C', (-294.8308457674501, 28.58323494594017, -309.56141873611114, 13.732696318678775, -309.56141873611114, -4.560979463965456)), ('L', (-309.56141873611114, -16.69819394594017)), ('C', (-309.56141873611114, -35.146567526513536, -294.6065106698718, -50.08892525872507, -276.1693818470442, -50.08892525872507)), ('C', (-257.73224843358264, -50.08892525872507, -242.79040990206553, -35.146567526513536, -242.79040990206553, -16.69819394594017)), ('L', (-242.79040990206553, 19.02877890153134)), ('L', (-242.78518117004987, 19.02877890153134)), ('C', (-242.78518117004987, 26.574862911502848, -236.67422113087608, 32.68559479617165, -229.1283666525997, 32.68559479617165)), ('C', (-221.58251217432337, 32.68559479617165, -215.47155213514955, 26.551909282923788, -215.47155213514955, 19.011793097026352)), ('L', (-215.47155213514955, -16.69819394594017)), ('C', (-215.47155213514955, -50.23276818144587, -242.64758610007124, -77.41431549768518, -276.17069017770655, -77.41431549768518)), ('Z', ()), ('M', (88.98189121011396, -77.40778302564102)), ('C', (87.21933568554131, -77.3727243545228, 85.4616783673433, -76.99966189975072, 83.8168129241453, -76.27233104540599)), ('C', (76.87347914565528, -73.20257415438034, 73.78604831410256, -64.97443212161681, 76.91915595299146, -57.893379326032765)), ('L', (123.57733064245014, 47.628125136217946)), ('C', (126.70469998896012, 54.70321010772792, 134.94448845993588, 58.03167217236467, 141.89356053080485, 54.96742404202279)), ('C', (148.83115601691597, 51.89766715099715, 151.85507542841881, 43.5940266349359, 148.7219677895299, 36.50746507866809)), ('C', (148.70360525391737, 36.46155873963675, 102.05907851905272, -69.00330556339031, 102.05334022667378, -69.00881432407408)), ('C', (99.60026614102566, -74.57332825658831, 94.26956696509971, -77.51294985772792, 88.98189121011396, -77.40778302564102)), ('Z', ()), ('M', (183.88186697596154, -77.40386262428775)), ('C', (178.5953847857906, -77.5010601159188, 173.2653374798789, -74.54394360897436, 170.80388548735755, -68.98007236520655)), ('C', (170.80388548735755, -68.98007236520655, 142.66287732282763, -5.370801576513533, 142.6514007380698, -5.342339646314103)), ('C', (139.52403139155982, 1.7387132869889603, 142.5999856383547, 9.973667682745726, 149.54905770922363, 13.037915813087606)), ('C', (156.48665319533475, 16.09619611935541, 164.6639539576211, 12.858744289975071, 167.78558501175215, 5.773096269853988)), ('L', (195.94852263443732, -57.893379326032765)), ('C', (199.0758919809473, -64.97443212161681, 195.9852522962963, -73.20257415438034, 189.0456369312678, -76.27233104540599)), ('C', (187.40085871011397, -77.000217366453, 185.64402770601853, -77.37146193019943, 183.88186697596154, -77.40386262428775)), ('Z', ()), ('M', (330.91737817913105, 40.220885766773506)), ('C', (326.4472484159544, 40.220885766773506, 323.0110074485399, 43.653435405466524, 323.0110074485399, 48.12333517788461)), ('C', (323.0110074485399, 52.633632987713675, 326.4472484159544, 56.070213662037034, 330.91737817913105, 56.070213662037034)), ('C', (335.4276759889601, 56.070213662037034, 338.81982850836897, 52.633632987713675, 338.81982850836897, 48.12333517788461)), ('C', (338.81982850836897, 43.653435405466524, 335.4276759889601, 40.220885766773506, 330.91737817913105, 40.220885766773506)), ('Z', ()), ('M', (330.91737817913105, 41.58761250585826)), ('C', (334.64152993304845, 41.58761250585826, 337.4139055598291, 44.35901721356838, 337.4139055598291, 48.12333517788461)), ('C', (337.4139055598291, 51.8936228025285, 334.64152993304845, 54.7047938764245, 330.91737817913105, 54.7047938764245)), ('C', (327.1932264252137, 54.7047938764245, 324.41693039707974, 51.8936228025285, 324.41693039707974, 48.12333517788461)), ('C', (324.41693039707974, 44.35901721356838, 327.1932264252137, 41.58761250585826, 330.91737817913105, 41.58761250585826)), ('Z', ()), ('M', (328.6399371559829, 43.69911404905626)), ('C', (328.18638252635327, 43.69911404905626, 327.85335039921654, 43.98538184768518, 327.85335039921654, 44.48439431141382)), ('L', (327.85335039921654, 51.727001154380346)), ('C', (327.85335039921654, 52.92192020619658, 329.4252155820869, 52.868145520655276, 329.4252155820869, 51.727001154380346)), ('L', (329.4252155820869, 48.946509286858976)), ('C', (330.14846995352565, 48.94730346652422, 330.71782791399573, 48.95565382959401, 331.2453376558048, 48.95565382959401)), ('L', (332.8629393242522, 52.05365689102564)), ('C', (333.4112905439815, 53.15487192361111, 334.8011784082977, 52.244856793091174, 334.22835910986464, 51.39381294569088)), ('L', (332.8629393242522, 48.702172797364675)), ('C', (335.19626672453705, 47.990445507656695, 335.30328358208686, 43.69911404905626, 331.5367143709046, 43.69911404905626)), ('Z', ()), ('M', (329.41215063799854, 45.097199867396725)), ('C', (330.60475141969374, 45.101593104042024, 330.8565890049857, 45.10765274079416, 331.45047931303424, 45.10765274079416)), ('L', (331.45178764369655, 45.10765274079416)), ('C', (333.49792498700145, 45.10765274079416, 333.4339774567308, 47.543519753383194, 331.45178764369655, 47.543198409009975)), ('C', (330.7110429570869, 47.54307905252849, 330.387068150641, 47.544878581018516, 329.4069219059829, 47.53535760630342)), ('Z', ())]

# latin-1 font metrics normalized by em-size.
Fonts = {
    'Arial' : {
        WIN_ASCENT: 0.9052734375,
        WIN_DESCENT: 0.2119140625,
        TYPO_ASCENT: 0.72802734375,
        TYPO_DESCENT: -0.21044921875,
        TYPO_LINE_GAP: 0.14990234375,
        HHEAD_ASCENT: 0.9052734375,
        HHEAD_DESCENT: -0.2119140625,
        HHEAD_LINE_GAP: 0.03271484375,
        CAPITAL_HEIGHT: 0.71630859375,
        X_HEIGHT: 0.5185546875,
        ASCENT: 0.7998046875,
        DESCENT: 0.2001953125,
        UNDERLINE_POSITION: -0.142578125,
        HEIGHT: 0.0732421875,
        32: 0.27783203125, 33: 0.27783203125, 34: 0.35498046875, 35: 0.55615234375,
        36: 0.55615234375, 37: 0.88916015625, 38: 0.6669921875, 39: 0.19091796875,
        40: 0.3330078125, 41: 0.3330078125, 42: 0.38916015625, 43: 0.583984375,
        44: 0.27783203125, 45: 0.3330078125, 46: 0.27783203125, 47: 0.27783203125,
        48: 0.55615234375, 49: 0.55615234375, 50: 0.55615234375, 51: 0.55615234375,
        52: 0.55615234375, 53: 0.55615234375, 54: 0.55615234375, 55: 0.55615234375,
        56: 0.55615234375, 57: 0.55615234375, 58: 0.27783203125, 59: 0.27783203125,
        60: 0.583984375, 61: 0.583984375, 62: 0.583984375, 63: 0.55615234375,
        64: 1.01513671875, 65: 0.6669921875, 66: 0.6669921875, 67: 0.72216796875,
        68: 0.72216796875, 69: 0.6669921875, 70: 0.61083984375, 71: 0.77783203125,
        72: 0.72216796875, 73: 0.27783203125, 74: 0.5, 75: 0.6669921875,
        76: 0.55615234375, 77: 0.8330078125, 78: 0.72216796875, 79: 0.77783203125,
        80: 0.6669921875, 81: 0.77783203125, 82: 0.72216796875, 83: 0.6669921875,
        84: 0.61083984375, 85: 0.72216796875, 86: 0.6669921875, 87: 0.94384765625,
        88: 0.6669921875, 89: 0.6669921875, 90: 0.61083984375, 91: 0.27783203125,
        92: 0.27783203125, 93: 0.27783203125, 94: 0.46923828125, 95: 0.55615234375,
        96: 0.3330078125, 97: 0.55615234375, 98: 0.55615234375, 99: 0.5,
        100: 0.55615234375, 101: 0.55615234375, 102: 0.27783203125, 103: 0.55615234375,
        104: 0.55615234375, 105: 0.22216796875, 106: 0.22216796875, 107: 0.5,
        108: 0.22216796875, 109: 0.8330078125, 110: 0.55615234375, 111: 0.55615234375,
        112: 0.55615234375, 113: 0.55615234375, 114: 0.3330078125, 115: 0.5,
        116: 0.27783203125, 117: 0.55615234375, 118: 0.5, 119: 0.72216796875,
        120: 0.5, 121: 0.5, 122: 0.5, 123: 0.333984375,
        124: 0.259765625, 125: 0.333984375, 126: 0.583984375, 160: 0.27783203125,
        161: 0.3330078125, 162: 0.55615234375, 163: 0.55615234375, 164: 0.55615234375,
        165: 0.55615234375, 166: 0.259765625, 167: 0.55615234375, 168: 0.3330078125,
        169: 0.73681640625, 170: 0.3701171875, 171: 0.55615234375, 172: 0.583984375,
        173: 0.3330078125, 174: 0.73681640625, 175: 0.55224609375, 176: 0.39990234375,
        177: 0.548828125, 178: 0.3330078125, 179: 0.3330078125, 180: 0.3330078125,
        181: 0.576171875, 182: 0.537109375, 183: 0.3330078125, 184: 0.3330078125,
        185: 0.3330078125, 186: 0.365234375, 187: 0.55615234375, 188: 0.833984375,
        189: 0.833984375, 190: 0.833984375, 191: 0.61083984375, 192: 0.6669921875,
        193: 0.6669921875, 194: 0.6669921875, 195: 0.6669921875, 196: 0.6669921875,
        197: 0.6669921875, 198: 1.0, 199: 0.72216796875, 200: 0.6669921875,
        201: 0.6669921875, 202: 0.6669921875, 203: 0.6669921875, 204: 0.27783203125,
        205: 0.27783203125, 206: 0.27783203125, 207: 0.27783203125, 208: 0.72216796875,
        209: 0.72216796875, 210: 0.77783203125, 211: 0.77783203125, 212: 0.77783203125,
        213: 0.77783203125, 214: 0.77783203125, 215: 0.583984375, 216: 0.77783203125,
        217: 0.72216796875, 218: 0.72216796875, 219: 0.72216796875, 220: 0.72216796875,
        221: 0.6669921875, 222: 0.6669921875, 223: 0.61083984375, 224: 0.55615234375,
        225: 0.55615234375, 226: 0.55615234375, 227: 0.55615234375, 228: 0.55615234375,
        229: 0.55615234375, 230: 0.88916015625, 231: 0.5, 232: 0.55615234375,
        233: 0.55615234375, 234: 0.55615234375, 235: 0.55615234375, 236: 0.27783203125,
        237: 0.27783203125, 238: 0.27783203125, 239: 0.27783203125, 240: 0.55615234375,
        241: 0.55615234375, 242: 0.55615234375, 243: 0.55615234375, 244: 0.55615234375,
        245: 0.55615234375, 246: 0.55615234375, 247: 0.548828125, 248: 0.61083984375,
        249: 0.55615234375, 250: 0.55615234375, 251: 0.55615234375, 252: 0.55615234375,
        253: 0.5, 254: 0.55615234375, 255: 0.5
    },
    'Calibri' : {
        WIN_ASCENT: 0.9521484375,
        WIN_DESCENT: 0.2685546875,
        TYPO_ASCENT: 0.75,
        TYPO_DESCENT: -0.25,
        TYPO_LINE_GAP: 0.220703125,
        HHEAD_ASCENT: 0.75,
        HHEAD_DESCENT: -0.25,
        HHEAD_LINE_GAP:0.220703125,
        CAPITAL_HEIGHT: 0.6318359375,
        X_HEIGHT: 0.46435546875,
        ASCENT: 0.75,
        DESCENT: 0.25,
        UNDERLINE_POSITION: -0.14599609375,
        HEIGHT: 0.0654296875,
        32: 0.22607421875, 33: 0.32568359375, 34: 0.40087890625, 35: 0.498046875,
        36: 0.5068359375, 37: 0.71484375, 38: 0.68212890625, 39: 0.220703125,
        40: 0.30322265625, 41: 0.30322265625, 42: 0.498046875, 43: 0.498046875,
        44: 0.24951171875, 45: 0.30615234375, 46: 0.25244140625, 47: 0.38623046875,
        48: 0.5068359375, 49: 0.5068359375, 50: 0.5068359375, 51: 0.5068359375,
        52: 0.5068359375, 53: 0.5068359375, 54: 0.5068359375, 55: 0.5068359375,
        56: 0.5068359375, 57: 0.5068359375, 58: 0.267578125, 59: 0.267578125,
        60: 0.498046875, 61: 0.498046875, 62: 0.498046875, 63: 0.46337890625,
        64: 0.89404296875, 65: 0.57861328125, 66: 0.5439453125, 67: 0.533203125,
        68: 0.615234375, 69: 0.48828125, 70: 0.45947265625, 71: 0.630859375,
        72: 0.623046875, 73: 0.251953125, 74: 0.31884765625, 75: 0.51953125,
        76: 0.42041015625, 77: 0.85498046875, 78: 0.6455078125, 79: 0.662109375,
        80: 0.5166015625, 81: 0.6728515625, 82: 0.54296875, 83: 0.45947265625,
        84: 0.4873046875, 85: 0.6416015625, 86: 0.5673828125, 87: 0.8896484375,
        88: 0.51904296875, 89: 0.4873046875, 90: 0.46826171875, 91: 0.306640625,
        92: 0.38623046875, 93: 0.306640625, 94: 0.498046875, 95: 0.498046875,
        96: 0.291015625, 97: 0.47900390625, 98: 0.525390625, 99: 0.4228515625,
        100: 0.525390625, 101: 0.49755859375, 102: 0.30517578125, 103: 0.470703125,
        104: 0.525390625, 105: 0.2294921875, 106: 0.2392578125, 107: 0.45458984375,
        108: 0.2294921875, 109: 0.798828125, 110: 0.525390625, 111: 0.52734375,
        112: 0.525390625, 113: 0.525390625, 114: 0.3486328125, 115: 0.39111328125,
        116: 0.3349609375, 117: 0.525390625, 118: 0.45166015625, 119: 0.71484375,
        120: 0.43310546875, 121: 0.45263671875, 122: 0.39501953125, 123: 0.314453125,
        124: 0.46044921875, 125: 0.314453125, 126: 0.498046875, 160: 0.22607421875,
        161: 0.32568359375, 162: 0.498046875, 163: 0.5068359375, 164: 0.498046875,
        165: 0.5068359375, 166: 0.498046875, 167: 0.498046875, 168: 0.392578125,
        169: 0.83447265625, 170: 0.40234375, 171: 0.51220703125, 172: 0.498046875,
        173: 0.30615234375, 174: 0.5068359375, 175: 0.39404296875, 176: 0.3388671875,
        177: 0.498046875, 178: 0.3359375, 179: 0.33447265625, 180: 0.2919921875,
        181: 0.5498046875, 182: 0.5859375, 183: 0.25244140625, 184: 0.30712890625,
        185: 0.24609375, 186: 0.42236328125, 187: 0.51220703125, 188: 0.63623046875,
        189: 0.67138671875, 190: 0.67529296875, 191: 0.46337890625, 192: 0.57861328125,
        193: 0.57861328125, 194: 0.57861328125, 195: 0.57861328125, 196: 0.57861328125,
        197: 0.57861328125, 198: 0.76318359375, 199: 0.533203125, 200: 0.48828125,
        201: 0.48828125, 202: 0.48828125, 203: 0.48828125, 204: 0.251953125,
        205: 0.251953125, 206: 0.251953125, 207: 0.251953125, 208: 0.62451171875,
        209: 0.6455078125, 210: 0.662109375, 211: 0.662109375, 212: 0.662109375,
        213: 0.662109375, 214: 0.662109375, 215: 0.498046875, 216: 0.66357421875,
        217: 0.6416015625, 218: 0.6416015625, 219: 0.6416015625, 220: 0.6416015625,
        221: 0.4873046875, 222: 0.5166015625, 223: 0.52734375, 224: 0.47900390625,
        225: 0.47900390625, 226: 0.47900390625, 227: 0.47900390625, 228: 0.47900390625,
        229: 0.47900390625, 230: 0.77294921875, 231: 0.4228515625, 232: 0.49755859375,
        233: 0.49755859375, 234: 0.49755859375, 235: 0.49755859375, 236: 0.2294921875,
        237: 0.2294921875, 238: 0.2294921875, 239: 0.2294921875, 240: 0.525390625,
        241: 0.525390625, 242: 0.52734375, 243: 0.52734375, 244: 0.52734375,
        245: 0.52734375, 246: 0.52734375, 247: 0.498046875, 248: 0.529296875,
        249: 0.525390625, 250: 0.525390625, 251: 0.525390625, 252: 0.525390625,
        253: 0.45263671875, 254: 0.525390625, 255: 0.45263671875
    },
    'Tahoma' : {
        WIN_ASCENT: 1.00048828125,
        WIN_DESCENT: 0.20654296875,
        TYPO_ASCENT: 0.7646484375,
        TYPO_DESCENT: -0.20654296875,
        TYPO_LINE_GAP: 0.02880859375,
        HHEAD_ASCENT: 1.00048828125,
        HHEAD_DESCENT: -0.20654296875,
        HHEAD_LINE_GAP: 0,
        CAPITAL_HEIGHT: 0.72705078125,
        X_HEIGHT: 0.54541015625,
        ASCENT: 0.7998046875,
        DESCENT: 0.2001953125,
        UNDERLINE_POSITION: -0.11474609375,
        HEIGHT: 0.0634765625,
        32: 0.3125, 33: 0.33203125, 34: 0.4013671875, 35: 0.7275390625,
        36: 0.5458984375, 37: 0.9765625, 38: 0.673828125, 39: 0.2109375,
        40: 0.3828125, 41: 0.3828125, 42: 0.5458984375, 43: 0.7275390625,
        44: 0.302734375, 45: 0.36328125, 46: 0.302734375, 47: 0.38232421875,
        48: 0.5458984375, 49: 0.5458984375, 50: 0.5458984375, 51: 0.5458984375,
        52: 0.5458984375, 53: 0.5458984375, 54: 0.5458984375, 55: 0.5458984375,
        56: 0.5458984375, 57: 0.5458984375, 58: 0.353515625, 59: 0.353515625,
        60: 0.7275390625, 61: 0.7275390625, 62: 0.7275390625, 63: 0.4736328125,
        64: 0.9091796875, 65: 0.599609375, 66: 0.58935546875, 67: 0.6005859375,
        68: 0.67822265625, 69: 0.56103515625, 70: 0.521484375, 71: 0.66748046875,
        72: 0.67529296875, 73: 0.373046875, 74: 0.41650390625, 75: 0.587890625,
        76: 0.49755859375, 77: 0.7705078125, 78: 0.66748046875, 79: 0.70751953125,
        80: 0.55126953125, 81: 0.70751953125, 82: 0.62060546875, 83: 0.55712890625,
        84: 0.583984375, 85: 0.65576171875, 86: 0.5966796875, 87: 0.90185546875,
        88: 0.58056640625, 89: 0.576171875, 90: 0.55908203125, 91: 0.3828125,
        92: 0.38232421875, 93: 0.3828125, 94: 0.7275390625, 95: 0.5458984375,
        96: 0.5458984375, 97: 0.52490234375, 98: 0.552734375, 99: 0.46142578125,
        100: 0.552734375, 101: 0.5263671875, 102: 0.318359375, 103: 0.552734375,
        104: 0.5576171875, 105: 0.228515625, 106: 0.28173828125, 107: 0.498046875,
        108: 0.228515625, 109: 0.83984375, 110: 0.5576171875, 111: 0.54296875,
        112: 0.552734375, 113: 0.552734375, 114: 0.3603515625, 115: 0.4462890625,
        116: 0.33447265625, 117: 0.5576171875, 118: 0.498046875, 119: 0.7421875,
        120: 0.4951171875, 121: 0.498046875, 122: 0.4443359375, 123: 0.48046875,
        124: 0.38232421875, 125: 0.48046875, 126: 0.7275390625, 160: 0.3125,
        161: 0.33203125, 162: 0.5458984375, 163: 0.5458984375, 164: 0.5458984375,
        165: 0.5458984375, 166: 0.38232421875, 167: 0.5458984375, 168: 0.5458984375,
        169: 0.9287109375, 170: 0.4931640625, 171: 0.5732421875, 172: 0.7275390625,
        173: 0.36328125, 174: 0.9287109375, 175: 0.5458984375, 176: 0.470703125,
        177: 0.7275390625, 178: 0.4931640625, 179: 0.4931640625, 180: 0.5458984375,
        181: 0.56787109375, 182: 0.5458984375, 183: 0.353515625, 184: 0.5458984375,
        185: 0.4931640625, 186: 0.4931640625, 187: 0.5732421875, 188: 1.0,
        189: 1.0, 190: 1.0, 191: 0.4736328125, 192: 0.599609375,
        193: 0.599609375, 194: 0.599609375, 195: 0.599609375, 196: 0.599609375,
        197: 0.599609375, 198: 0.9130859375, 199: 0.6005859375, 200: 0.56103515625,
        201: 0.56103515625, 202: 0.56103515625, 203: 0.56103515625, 204: 0.373046875,
        205: 0.373046875, 206: 0.373046875, 207: 0.373046875, 208: 0.6982421875,
        209: 0.66748046875, 210: 0.70751953125, 211: 0.70751953125, 212: 0.70751953125,
        213: 0.70751953125, 214: 0.70751953125, 215: 0.7275390625, 216: 0.70751953125,
        217: 0.65576171875, 218: 0.65576171875, 219: 0.65576171875, 220: 0.65576171875,
        221: 0.576171875, 222: 0.5654296875, 223: 0.54833984375, 224: 0.52490234375,
        225: 0.52490234375, 226: 0.52490234375, 227: 0.52490234375, 228: 0.52490234375,
        229: 0.52490234375, 230: 0.8798828125, 231: 0.46142578125, 232: 0.5263671875,
        233: 0.5263671875, 234: 0.5263671875, 235: 0.5263671875, 236: 0.228515625,
        237: 0.228515625, 238: 0.228515625, 239: 0.228515625, 240: 0.5458984375,
        241: 0.5576171875, 242: 0.54296875, 243: 0.54296875, 244: 0.54296875,
        245: 0.54296875, 246: 0.54296875, 247: 0.7275390625, 248: 0.54296875,
        249: 0.5576171875, 250: 0.5576171875, 251: 0.5576171875, 252: 0.5576171875,
        253: 0.498046875, 254: 0.552734375, 255: 0.498046875
    }
}

# A font's width information in the format above can be
# obtained inside FontForge with the following Python script:
"""
count = 0
st = ''
font = fontforge.activeFont()
em = font.em
for _slot in font.selection:
    glyph = font[_slot]
    if st != '':
        st = f'{st}, {glyph.unicode}: {glyph.width/em},'
    else:
        st = f'{glyph.unicode}: {glyph.width/em}'
    count += 1
    if count % 4 == 0:
        fontforge.logWarning(st)
        st = ''
fontforge.logWarning(st)
"""
# Then use Notepad++ to remove double commas and format the dictionary

TEXTHEIGHT = Fonts['Tahoma'][WIN_ASCENT] + Fonts['Tahoma'][WIN_DESCENT]

MONO = False

# Random identifiers:
LINEBRAKEID = 'ICiLu3Ruzy5tE3'
BACKSLASHID = 'C46eSIcHWHotYu'
DRAWABLEID = '8aRyjspum1NeIz'
SPACEID = 'wxGIfXGMLP2sBY'
SPECIALID = '4LOLEhCmHAeReU'

# Indexing and identifying strings:
WIDTH = 'width'
HIDDEN = 'hidden'
ALPHABETIC = 'alphabetic'
MIDDLE = 'middle'
HANGING = 'hanging'
CONTINUE = 'continue'
END = 'end'
START = 'start'
GND = 'GND'
EARTH = 'EARTH'
CHASSIS = 'CHASSIS'
NET = 'net'
NETPATH = 'netpath'
P1 = 'P1'
ORIENTATION = 'Orientation'
ISPORT = 'IsPort'
DESCRIPTION = 'Description'
JUNCTION = 'junction'
WIRE = 'wire'
P2 = 'P2'
NETNAME = 'NetName'
TAP = 'tap'
ARC3P = 'arc3p'
P3 = 'P3'
P4 = 'P4'
LP1 = 'LP1'
LINEWIDTH = 'LineWidth'
LINETYPE = 'LineType'
LINECOLOR = 'LineColor'
U1 = 'U1'
PINASSOC = 'PinAssoc'
RECT = 'rect'
FILLCOLOR = 'FillColor'
U2 = 'U2'
HBLOCK = 'HBlock'
U3 = 'U3'
COIL = 'coil'
ELLIPSE = 'ellipse'
LINE = 'line'
TRIANGLE = 'triangle'
ZIGZAG = 'zigzag'
PORTBG = 'portbg'
COLOR = 'Color'
PIN = 'pin'
FONTSIZE = 'FontSize'
FONTCOLOR = 'FontColor'
STRG = 'Strg'
TEXT = 'text'
ISCOMMENTORVISIBLE = 'IsCommentOrVisible'
SCHEMATIC = 'schematic'
SYMBOL = 'symbol'
SVG_SYMBOLS = 'SVG_symbols'
CENTRAL = 'central'
NONE = 'none'
COMPONENT = 'component'
ROTATION = 'Rotation'
DONOTSTUFF = 'DoNotStuff'
DEPTH = 'Depth'
TYPE = 'Type'
PARENT_P1 = 'parent_P1'
PARENT_ROTATION = 'parent_Rotation'
PARENT_DONOTSTUFF = 'parent_DoNotStuff'
ALTNAME = 'AltName'
ROUND = 'round'
ANGLE = 'Angle'
ONWIREEND = 'OnWireEnd'
EXTRA_ = 'Extra_'
EXTRA_10 = f'{EXTRA_}10'
IMAGE = 'image'
NETDESCRIPTION = 'netdescription'
PINLABEL = 'pinlabel'
NETTEXT = 'nettext'
TRANSLATE = 0
ROTATE = 1
TRANSFORM = 'transform'
SCALE = 2
MIN_X = 'min_x'
MIN_Y = 'min_y'
MAX_X = 'max_x'
MAX_Y = 'max_y'
BOUNDS = 'bounds'
PATH = 'path'
CIRCLE = 'circle'
SYMBOLNAME = 'SymbolName'
FILE_BOM = 'ÿØÿÛ'
DRAWABLE = 'Drawable'
INSTANCENAME = 'InstanceName'
COMPONENTVALUE = 'ComponentValue'
SYMBOLTYPE = 'SymbolType'
PARENT = 'parent'
INDEX = 'index'
FALLBACK = 'fallback'
PINNAME = 'PinName'
KEY = 'key'
DIAGONAL = 'diagonal'
ID = 'id'
SVG = 'svg'
HASH = 'hash'
SVG_HASH = 'SVG_hash'
NETARROW = 'NETARROW'
USE = 'use'
ORIGINAL_TEXT = 'original_text'
PATHDATA = 'pathdata'
ISTEXT = 'istext'
ARC = 'arc'
JUMPER_LIST = 'jumper_list'
JUMPER = 'jumper'
OBJ_ID = 'obj_id'
STROKEWIDTH = 'strokewidth'
CASTABLE = 'castable'

# Numerical constants:

# Direction where the text goes:
RIGHT_CENTER = 7 # : (START, MIDDLE), # right center
CENTER_CENTER =  15 # : (MIDDLE, MIDDLE), # center
LEFT_CENTER = 11 # : (END, MIDDLE), # left center
RIGHT_TOP = 6 # : (START, ALPHABETIC), # right top
CENTER_TOP = 14 # : (MIDDLE, ALPHABETIC), # center top
LEFT_TOP = 10 # : (END, ALPHABETIC), # left top
RIGHT_BOTTOM = 5 # : (START, HANGING), # right bottom
CENTER_BOTTOM = 13 # : (MIDDLE, HANGING), # center bottom
LEFT_BOTTOM = 9 # : (END, HANGING) # left bottom

# SVG text justification:
START_MIDDLE = 7 # : (START, MIDDLE), # right center
MIDDLE_MIDDLE = 15 # : (MIDDLE, MIDDLE), # center
END_MIDDLE = 11 # : (END, MIDDLE), # left center
START_ALPHABETIC = 6 # : (START, ALPHABETIC), # right top
MIDDLE_ALPHABETIC = 14 # : (MIDDLE, ALPHABETIC), # center top
END_ALPHABETIC = 10 # : (END, ALPHABETIC), # left top
START_HANGING = 5 # : (START, HANGING), # right bottom
MIDDLE_HANGING = 13 # : (MIDDLE, HANGING), # center bottom
END_HANGING = 9 # : (END, HANGING) # left bottom

# Angle codes
DEG0 = 0 # 0
DEG45CCW = 1 # -45, 45CCW
DEG90CCW = 2 # -90, 90CCW
DEG135CCW = 3 # -135, 135CCW
DEG180 = 4 # 180, 180
DEG135CW = 5 # 135, 135CW
DEG90CW = 6 # 90, 90CW
DEG45CW = 7 # 45, 45CW

# Rotation mapping
ROTATION_MAP = SafeDict({
    DEG0: 0,
    DEG45CCW: -45,
    DEG90CCW: -90,
    DEG135CCW: -135,
    DEG180: 180,
    DEG135CW: 135,
    DEG90CW: 90,
    DEG45CW: 45,
})

ANGLE_TO_CODE = SafeDict({
    0: DEG0, # : 0,
    -45: DEG45CCW, # : -45,
    -90: DEG90CCW, # : -90,
    -135: DEG135CCW, # : -135,
    180: DEG180, # : 180,
    135: DEG135CW, # : 135,
    90: DEG90CW, # : 90,
    45: DEG45CW # : 45,
})

# 4 least significant bits of "Orientation":
JUSTIFICATION_MAP = SafeDict({
    START_MIDDLE:  (START, MIDDLE), # right center
    MIDDLE_MIDDLE: (MIDDLE, MIDDLE), # center
    END_MIDDLE: (END, MIDDLE), # left center
    START_ALPHABETIC:  (START, ALPHABETIC), # right top
    MIDDLE_ALPHABETIC: (MIDDLE, ALPHABETIC), # center top
    END_ALPHABETIC: (END, ALPHABETIC), # left top
    START_HANGING:  (START, HANGING), # right bottom
    MIDDLE_HANGING: (MIDDLE, HANGING), # center bottom
    END_HANGING:  (END, HANGING) # left bottom
})

LINETYPE_MAP = SafeDict({
    0 : None,
    2: (1,3),
    1: (4,4),
    3: (4,3,1,3),
    4: (4,3,1,3,1,3)
})

# Debug names:
# Direction where the text goes:
TEXT_POS_NAMES = SafeDict({
    START_MIDDLE : 'right center', # right center
    MIDDLE_MIDDLE : 'center center', # center
    END_MIDDLE : 'left center', # left center
    START_ALPHABETIC : 'right top', # right top
    MIDDLE_ALPHABETIC : 'center top', # center top
    END_ALPHABETIC : 'left top', # left top
    START_HANGING : 'right bottom', # right bottom
    MIDDLE_HANGING : 'center bottom', # center bottom
    END_HANGING : 'left bottom' # left bottom
})

# SVG text justification:
JUS_NAMES = SafeDict({
    START_MIDDLE : '(START, MIDDLE)', # right center
    MIDDLE_MIDDLE : '(MIDDLE, MIDDLE)', # center
    END_MIDDLE : '(END, MIDDLE)', # left center
    START_ALPHABETIC : '(START, ALPHABETIC)', # right top
    MIDDLE_ALPHABETIC : '(MIDDLE, ALPHABETIC)', # center top
    END_ALPHABETIC : '(END, ALPHABETIC)', # left top
    START_HANGING : '(START, HANGING)', # right bottom
    MIDDLE_HANGING : '(MIDDLE, HANGING)', # center bottom
    END_HANGING : '(END, HANGING)' # left bottom
})

# Angle names
ANGLE_NAMES = SafeDict({
    DEG0 : '0',
    DEG45CCW : '-45, 45CCW',
    DEG90CCW : '-90, 90CCW',
    DEG135CCW : '-135, 135CCW',
    DEG180 : '180',
    DEG135CW : '135, 135CW',
    DEG90CW : '90, 90CW',
    DEG45CW : '45, 45CW'
})

# Valid bits
VALID_JUSTIFICATIONS = (
    START_MIDDLE, # (START, MIDDLE), # right center
    MIDDLE_MIDDLE, # (MIDDLE, MIDDLE), # center
    END_MIDDLE, # (END, MIDDLE), # left center
    START_ALPHABETIC, # (START, ALPHABETIC), # right top
    MIDDLE_ALPHABETIC, # (MIDDLE, ALPHABETIC), # center top
    END_ALPHABETIC, # (END, ALPHABETIC), # left top
    START_HANGING, # (START, HANGING), # right bottom
    MIDDLE_HANGING, # (MIDDLE, HANGING), # center bottom
    END_HANGING # (END, HANGING) # left bottom
)

VALID_ROTATIONS = (
    DEG0, # 0,
    DEG45CCW, # -45,
    DEG90CCW, # -90,
    DEG135CCW, # -135,
    DEG180, # 180,
    DEG135CW, # 135,
    DEG90CW, # 90,
    DEG45CW # 45,
 ) # DEG0 through DEG45CW

VALID_ROTATIONS_ORTHOGONAL = (
    DEG0, # 0,
    # DEG45CCW,   -45, excluded
    DEG90CCW, # -90,
    # DEG135CCW,   -135, excluded
    DEG180, # 180,
    # DEG135CW,   135, excluded
    DEG90CW, # 90,
    # DEG45CW   45,  excluded
)

IMAGE_BLENDS = SafeDict({
    # <!-- 0x6: SRCPAINT (OR / Additive) -->
    0x6: ' style="mix-blend-mode: screen;"',

    # <!-- 0x7: SRCAND (AND / Multiplicative) -->
    0x7: ' style="mix-blend-mode: multiply;"',

    # <!-- 0x8: SRCINVERT (XOR / Subtractive) -->
    0x8: ' style="mix-blend-mode: difference;"',

    # <!-- 0xB: MERGEPAINT (NOT Source OR Dest) -->
    0xb: ' style="mix-blend-mode: screen;"'
})

# Definitions for drawable elements. "Ux" represents unknowns.
# 'path' is a custom element that has 'pathdata' be a path in the format
# worked with in this script and converted from and to string using
# Python's print() and eval()
QSPICE_DEFS = SafeDict({
    FILE_BOM: (),
    SCHEMATIC: (),
    COMPONENT: (P1, ROTATION, DONOTSTUFF),
    SYMBOL : (SYMBOLNAME,), # trailling comma indicates single element tuple
    NET: (P1, FONTSIZE, ORIENTATION, ISPORT, NETNAME, DESCRIPTION),
    JUNCTION: (P1,), # trailling comma indicates single element tuple
    WIRE: (P1, P2, NETNAME),
    TAP: (P1, P2),
    ARC: (P1, P2, P3, P4, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ARC3P: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    RECT: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, U3),
    PATH: (P1, PATHDATA, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, PINASSOC, U3, ISTEXT, TRANSFORM),
    COIL: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ELLIPSE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    CIRCLE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    LINE: (P1, P2, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    TRIANGLE: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U1, PINASSOC),
    ZIGZAG: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    PIN: (P1, LP1, FONTSIZE, ORIENTATION, U1, FONTCOLOR, U2, PINNAME, NETNAME),
    TEXT: (P1, FONTSIZE, ORIENTATION, ISCOMMENTORVISIBLE, FONTCOLOR, U1, U2, STRG),
    JUMPER: (P1, P2)
})

COMPOSE_DEFS = SafeDict({
    FILE_BOM: (),
    SCHEMATIC: (),
    COMPONENT: (P1, ROTATION, DONOTSTUFF),
    SYMBOL : (SYMBOLNAME,), # trailling comma indicates single element tuple
    NET: (P1, FONTSIZE, ORIENTATION, ISPORT, ORIGINAL_TEXT),
    JUNCTION: (P1,), # trailling comma indicates single element tuple
    WIRE: (P1, P2, NETNAME),
    TAP: (P1, P2),
    ARC: (P1, P2, P3, P4, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ARC3P: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    RECT: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, U3),
    PATH: (P1, PATHDATA, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, PINASSOC, U3, ISTEXT, TRANSFORM),
    COIL: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ELLIPSE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    CIRCLE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    LINE: (P1, P2, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    TRIANGLE: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U1, PINASSOC),
    ZIGZAG: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    PIN: (P1, LP1, FONTSIZE, ORIENTATION, U1, FONTCOLOR, U2, ORIGINAL_TEXT),
    TEXT: (P1, FONTSIZE, ORIENTATION, ISCOMMENTORVISIBLE, FONTCOLOR, U1, U2, STRG),
    JUMPER: (P1, P2)
})

DRAWABLE_DEFS = SafeDict({
    NET: (P1, FONTSIZE, ORIENTATION, ISPORT, NETNAME, DESCRIPTION),
    JUNCTION: (P1,), # trailling comma indicates single element tuple
    WIRE: (P1, P2, NETNAME),
    TAP: (P1, P2),
    ARC: (P1, P2, P3, P4, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ARC3P: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    RECT: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, U3),
    PATH: (P1, PATHDATA, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, PINASSOC, U3, ISTEXT, TRANSFORM),
    COIL: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ELLIPSE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    CIRCLE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    LINE: (P1, P2, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    TRIANGLE: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U1, PINASSOC),
    ZIGZAG: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    PIN: (P1, LP1, FONTSIZE, ORIENTATION, U1, FONTCOLOR, U2, PINNAME, NETNAME),
    TEXT: (P1, FONTSIZE, ORIENTATION, ISCOMMENTORVISIBLE, FONTCOLOR, U1, U2, STRG),
    JUMPER: (P1, P2)
})

SCHEMATIC_DEFS = SafeDict({
    COMPONENT: (P1, ROTATION, DONOTSTUFF),
    SYMBOL : (SYMBOLNAME,), # trailling comma indicates single element tuple
    NET: (P1, FONTSIZE, ORIENTATION, ISPORT, NETNAME, DESCRIPTION),
    JUNCTION: (P1,), # trailling comma indicates single element tuple
    WIRE: (P1, P2, NETNAME),
    TAP: (P1, P2),
    ARC: (P1, P2, P3, P4, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ARC3P: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    RECT: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, U3),
    PATH: (P1, PATHDATA, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, PINASSOC, U3, ISTEXT, TRANSFORM),
    COIL: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ELLIPSE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    LINE: (P1, P2, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    TRIANGLE: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U1, PINASSOC),
    ZIGZAG: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    PIN: (P1, LP1, FONTSIZE, ORIENTATION, U1, FONTCOLOR, U2, PINNAME, NETNAME),
    TEXT: (P1, FONTSIZE, ORIENTATION, ISCOMMENTORVISIBLE, FONTCOLOR, U1, U2, STRG),
    JUMPER: (P1, P2)
})

IGNORE_COMPOSE_DEFS = {JUMPER}

ANNOTATION_DEFS = SafeDict({
    ARC: (P1, P2, P3, P4, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ARC3P: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    RECT: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, U3),
    PATH: (P1, PATHDATA, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, HBLOCK, PINASSOC, U3, ISTEXT, TRANSFORM),
    COIL: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC),
    ELLIPSE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    CIRCLE: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U2, PINASSOC),
    LINE: (P1, P2, LINEWIDTH, LINETYPE, LINECOLOR, U1, PINASSOC),
    TRIANGLE: (P1, P2, P3, LINEWIDTH, LINETYPE, LINECOLOR, FILLCOLOR, U1, PINASSOC),
    ZIGZAG: (P1, P2, U1, LINEWIDTH, LINETYPE, LINECOLOR, U2, PINASSOC)
})

SYMBOL_PIN_HASH_DEFS = (P1, LP1, FONTSIZE, ORIENTATION, FONTCOLOR, PINNAME)

SYMBOL_PIN_REGISTER_DEFS = (P1, LP1, FONTSIZE, ORIENTATION, FONTCOLOR, PINNAME, NETNAME)

NATIVE_SYMBOLS = (NET, NETPATH, JUNCTION)

DRAWING_ORDER = [RECT, ELLIPSE, TRIANGLE, TAP, LINE, ARC, ARC3P, COIL, ZIGZAG, PIN, PINLABEL, WIRE, JUNCTION, PATH, TEXT, JUMPER, NET]
R_DRAWING_ORDER = DRAWING_ORDER[::-1]
SYMBOL_DRAWING_ORDER =[RECT, ELLIPSE, LINE, TAP, TRIANGLE, ARC3P, COIL, ZIGZAG, ARC, PIN, PINLABEL, WIRE, JUNCTION, PATH, TEXT, JUMPER, NET]
R_SYMBOL_DRAWING_ORDER = SYMBOL_DRAWING_ORDER[::-1]

SQRT2 = sqrt(2.0)
TRQS2 = 1.0 / SQRT2
PI2 = pi * 2.0
IP2 = 1.0 / PI2
CGAIN = 0.3517 # Gain optimized for circles and ellipses
NGAIN = 1.0 / 3.0 # Gain for parabolas and general functions
IP = 1.0 / pi

# g_stack must never be reassigned
g_stack = []

def push(v, s = g_stack):
    s[-1].append(v)
    
def pop(s = g_stack):
    return s[-1].pop()
    
def Push(v, s = g_stack):
    s.append(v)
    
def Pop(s = g_stack):
    return s.pop()

def stack(i = -1, s = g_stack):
    return s[i]

def q_eval(val):
    if not isinstance(val, str):
        return val
    s = val.strip().replace(" ", "")
    # 1. Try Point (Coordinate pair)
    if s.startswith('(') and s.endswith(')') and ',' in s:
        try:
            parts = s[1:-1].split(',')
            if len(parts) == 2:
                return (int(parts[0]), int(parts[1]))
        except ValueError:
            pass
    # 2. Try Integer
    try:
        return int(s, 0)
    except ValueError:
        try:
            return int(s)
        except ValueError:
            pass
    # 3. Try Float
    try:
        return float(s)
    except ValueError:
        pass
    try:
        return eval(val)
    except:
        return val

def dequote(s):
    if not s: return s
    end = len(s)
    if end in (0, 1): return s
    r = s
    if (s[0] == '"') and (s[end-1] == '"'):
        try:
            r = s[1:end-1]
        except:
            pass
    return r

def int_to_hex(i):
    if i in (NONE, -1, None): return NONE
    if isinstance(i, str): return i
    return hex(i)

class SafeList(list):
# A list subclass supporting safe indexing via .get() and auto-expanding writes via .put().

    def get(self, index: int, default=None):
    # Safely retrieve an item by index. Returns 'default' if out of range.
        try:
            return self[index]
        except IndexError:
            return default

    def put(self, index: int, value, default=None) -> None:
    # Sets 'value' at 'index'. If 'index' is beyond current bounds, auto-expands
    # the list by padding intermediate missing slots with 'default'.

        if index < 0:
            raise IndexError("SafeList.put() does not support negative indices for expansion.")

        current_len = len(self)

        if index < current_len:
            # Overwrite existing slot
            self[index] = value
        else:
            # Fill intermediate gaps with 'default' and append target 'value'
            gap_count = index - current_len
            if gap_count > 0:
                self.extend([default] * gap_count)
            self.append(value)

def get_dynamic_precision(scale, base_precision=5, anchor_scale=1.0):
# Calculates decimal places needed based on scale.
# base_precision: digits desired at the anchor_scale.
    # Avoid math errors if scale is 0
    scale = max(abs(scale), 1e-9)

    # Calculate how many powers of 10 we are away from the anchor
    # If scale is 0.1, log10 is -1.
    # 4 - (-1) = 5 digits.
    diff = math.log10(scale / anchor_scale)
    precision = base_precision - round(diff)

    # Return at least 0 (no decimals) and a reasonable max (like 12)
    return max(0, min(round(precision), 12))

def set_module_global(module_name: str, var_name: str, value):
    # 1. Dynamically import or retrieve the module by string name
    mod = importlib.import_module(module_name)

    # 2. Set the attribute (global variable) on the module object
    setattr(mod, var_name, value)

def get_unique_filename(filename: str | Path) -> Path:
# Returns a Path object guaranteed to point to a non-existent file.

# If 'filename' exists, appends '_1', '_2', etc., before the file extension
# until a free filename is found.

    path = Path(filename)

    # If the file doesn't exist, return it directly
    if not path.exists():
        return path

    counter = 1
    # Deconstruct the filename into stem (name without ext) and suffix (extension)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    # Increment counter until we hit a filename that doesn't exist on disk
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

def get_unique_filename_from_list(filename: str | Path, saved_files) -> Path:
# Returns a Path object guaranteed to point to a non-existent file.

# If 'filename' exists, appends '_1', '_2', etc., before the file extension
# until a free filename is found.

    path = filename

    # If the file doesn't exist, return it directly
    if not path in saved_files:
        return path

    counter = 1
    path = Path(path)
    # Deconstruct the filename into stem (name without ext) and suffix (extension)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    # Increment counter until we hit a filename that doesn't exist on list
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if str(new_path) not in saved_files:
            return new_path
        counter += 1

def handle_exception(s):
    full_trace = "".join(traceback.format_stack())
    logging.error(s)
    logging.error(full_trace)
    logging.exception('Last call:')
    logging.info('*****************************************\n\n\n\n')
    dbinfo(s)
    dbinfo(full_trace)
    if echo:
        traceback.print_exc()
    dbinfo('*****************************************\n\n\n\n')
    if not echo:
        print(s)

def discover_and_load_units(prefix="qs", target_module_name=__name__):
# Scans the same directory as the main script for modules starting with `prefix`,
# loads them, and runs `init_unit()` if present.

    loaded_units = {}

    # Get the directory where the current main script resides
    main_dir = os.path.dirname(os.path.abspath(sys.modules[target_module_name].__file__))

    # Iterate through all Python modules in the main directory
    for _, module_name, _ in pkgutil.iter_modules([main_dir]):

        # Only process modules starting with your designated prefix (e.g., "qs")
        if module_name.startswith(prefix) and (not module_name.startswith('qsconvert')):

            # Dynamically import the module directly
            try:
                mod = importlib.import_module(module_name)
            except Exception as e:
                s = f'Fatal Error while importing module "{module_name}" ({type(e).__name__}): {e}'
                handle_exception(s)
                raise SystemExit
            # Store loaded module indexed by its module name (e.g., "qs_math")
            loaded_units[module_name] = mod

    return loaded_units

def init_unit_dict(unit_dict):
    for key in unit_dict:
        mod = unit_dict[key]
        try:
            if hasattr(mod, "init_unit"):
                mod.init_unit(sys.argv[1:] + internal_parameters)
        except Exception as e:
            s = f'Fatal Error while initializing module "{mod.__name__}" ({type(e).__name__}): {e}'
            handle_exception(s)
            raise SystemExit

def patch(unit_dict):
    for key in unit_dict:
        mod = unit_dict[key]
        try:
            if hasattr(mod, "patch"):
                mod.patch(sys.argv[1:] + internal_parameters)
        except Exception as e:
            s = f'Fatal Error while patching module "{mod.__name__}" ({type(e).__name__}): {e}'
            handle_exception(s)
            raise SystemExit

def inject_namespace(source_mod: types.ModuleType, target_mod: types.ModuleType):
# Injects all public attributes from source_mod into target_mod's namespace.
    # 1. Determine what to export from source
    if hasattr(source_mod, "__all__"):
        names = source_mod.__all__
    else:
        names = [attr for attr in dir(source_mod)]

    # 2. Update the target module's internal namespace dictionary
    for name in names:
        if not name.startswith("_"):
            setattr(target_mod, name, getattr(source_mod, name))

def ext_post_parameter(unit_dict):
    for key in unit_dict:
        mod = unit_dict[key]
        if hasattr(mod, "post_parameter"):
            mod.post_parameter(sys.argv[1:] + internal_parameters)

def declare_parameters():
# Declare the parameters:
    global DYN_PRECISION, epsilon, epsilon3, epsilon3rd, TEXTHEIGHT

    for key, val in PARAMETERS.items():
        if val[0] == LOCAL:
            globals()[val[1]] = val[2]
        else:
            set_module_global(val[0], val[1], val[2])

    # Safely pull the dynamically assigned global variables
    scale_factor = globals().get('SCALE_FACTOR', 1.0)
    font_setting = globals().get('FONT', 'Tahoma')

    DYN_PRECISION = get_dynamic_precision(scale_factor)
    epsilon =  eval(f'1e-{DYN_PRECISION+4}')  # Safety factor for IEEE-754 floats
    epsilon3 = eval(f'3e-{DYN_PRECISION+4}')
    epsilon3rd = epsilon * NGAIN
    TEXTHEIGHT = Fonts[font_setting][WIN_ASCENT] + Fonts[font_setting][WIN_DESCENT]

def declare_flags():
    for key, val in FLAGS.items():
        if val[0] == LOCAL:
            globals()[val[1]] = val[2]
        else:
            set_module_global(val[0], val[1], val[2])

def load_dict(
    file_path: str | Path, current_dict: dict
) -> bool:
# Loads a dictionary from a pickle file if it exists; otherwise retains current_dict.
# Returns:
    # tuple[dict, bool]: A tuple containing (resulting_dict, loaded_from_disk_flag)

    path = Path(file_path)

    if path.is_file():
        try:
            with open(path, "rb") as f:
                loaded_dict = pickle.load(f)
                if isinstance(loaded_dict, dict):
                    for key in loaded_dict:
                        current_dict[key] = loaded_dict[key]
                    # Ensure the unpickled object is actually a dictionary
                    print(f'Successfully loaded file "{str(path)}".')
                    return True
                else:
                    print(f'Warning: Failed to load file "{str(path)}": File is corrupt.')
                    return False
        except (pickle.UnpicklingError, EOFError, OSError) as e:
            print(f'Warning: Failed to load file "{str(path)}": {e}.')
            return False
    else:
        print(f'Warning: Failed to load file "{str(path)}": File not found.')
        return False
    return False

def save_dict(file_path: str | Path, data: dict) -> None:
# Saves a dictionary to disk using pickle, automatically overwriting
# any existing file at the target location.

    path = Path(file_path)

    # Create missing directories in the path automatically if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Standard "wb" (write binary) mode automatically creates or overwrites the file
        with open(path, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f'Successfully saved file "{str(path)}".')
    except Exception as e:
        print(f'Warning: Could not save file "{str(path)}": {e}.')

def load_two_dicts(file_path: str | Path, default1: dict, default2: dict) -> bool:
    path = Path(file_path)

    if path.is_file():
        try:
            with open(path, "rb") as f:
                d1, d2 = pickle.load(f)
                if isinstance(d1, dict) and isinstance(d2, dict):
                    for key in d1:
                        default1[key] = d1[key]
                    for key in d2:
                        default2[key] = d2[key]
                    print(f'Successfully loaded file "{str(path)}".')
                    return True
                else:
                    print(f'Warning: Failed to load file "{str(path)}": File is corrupt.')
                    return False
        except Exception as e:
            print(f'Warning: Could not load file "{str(path)}": {e}.')
            return False
    else:
        print(f'Warning: Failed to load file "{str(path)}": File not found.')
        return False
    return False

def save_two_dicts(file_path: str | Path, dict1: dict, dict2: dict) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "wb") as f:
            # Save as a single tuple container
            pickle.dump((dict1, dict2), f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f'Successfully saved file "{str(path)}".')
    except Exception as e:
        print(f'Warning: Could not save file "{str(path)}": {e}.')

def get_arg_list(s):
    i = 0
    l = []
    lpair = (-1, -1)
    s = s.replace('\n', ' ').replace('\r', ' ')
    while i < len(s):
        while (i < len(s)) and (s[i] == ' '):
            i += 1
        start = i
        if (i < len(s)) and (s[i] == '"'):
            i += 1
            while (i < len(s)) and (s[i] != '"'):
                i += 1
            if (i < len(s)) and (s[i] == '"'):
                i += 1
        else:
            while (i < len(s)) and (s[i] != ' '):
                i += 1
        if (lpair != (start, i)) and (start != i):
            lpair = (start, i)
            l.append(dequote(s[start:i]))

    return l

def load_parameter_line(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            par = file.read()

        l = get_arg_list(par)
        o = []
        for p in l:
            s = p.strip()
            if s:
                su = s.upper()
                if not(su.startswith('/SPL') or su.startswith('/LPL')):
                    o.append(s)
    except Exception as e:
        print(f'Error: Failed loading command line parameter file "{filename}": {e}')
        return ''
    print(f'Successfully loaded command line parameters from "{filename}": {" ".join(o)}')
    return o

def save_parameter_line(filename, parameters):
    try:
        i = 0
        while i < len(parameters):
            su = parameters[i].upper()
            if ' ' in parameters[i]:
                parameters[i] = f'"{parameters[i]}"'
            if (su.startswith('/SPL') or su.startswith('/LPL')):
                del parameters[i]
            else:
                i += 1

        with open(filename, 'w', encoding='utf-8') as file:
            file.write('\n'.join(parameters))

        print(f'Successfully saved command line parameters to "{filename}": {" ".join(parameters)}')
        return True

    except Exception as e:
        print(f'Error: Failed saving command line parameter file to "{filename}": {e}')
        return False

def display_help():
    type_names = {
        int : 'int',
        HEX : 'hex',
        float : 'float',
        str : 'string'
    }
    indent = '               '
    for line in HELP_HEADER:
        print(line)
    print('Options:')
    key = '/lcfg=x'
    print(f'    {key}{" "*(11-len(key))}Loads configuration from file x.pkl')
    print(f'{indent}If file is not informed, loads from config.pkl{" "*(11)}')
    key = '/scfg=x'
    print(f'    {key}{" "*(11-len(key))}Saves configuration to file x.pkl')
    print(f'{indent}If file is not informed, saves to config.pkl{" "*(11)}')
    key = '/lpl=x'
    print(f'    {key}{" "*(11-len(key))}Loads command-line parameters from text file x.txt')
    print(f'{indent}If file is not informed, loads from params.txt{" "*(11)}')
    key = '/spl=x'
    print(f'    {key}{" "*(11-len(key))}Saves command-line parameters to text file x.txt')
    print(f'{indent}If file is not informed, saves to params.txt{" "*(11)}')
    for key, value in FLAGS.items():
        print(f'    {key.lower()}{" "*(11-len(key))}{value[3]}')
        i = 4
        while i < len(value):
            print(f'{indent}{value[i]}')
            i += 1

    for key, value in PARAMETERS.items():
        print(f'    {key.lower()}=x{" "*(9-len(key))}Sets {value[4]} parameter to x.')
        i = 5
        while i < len(value):
            print(f'{indent}{value[i]}')
            i += 1
        print(f'{indent}Default = {value[2] if value[3] != HEX else int_to_hex(value[2])} ({type_names[value[3]]})')

def succ_base26(s):
# Return the successor of a base-26 string using A-Z as digits.
    s = ''.join(c for c in s.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    chars = list(s)
    i = len(chars) - 1

    while i >= 0:
        if chars[i] == 'Z':
            chars[i] = 'A'
            i -= 1
        else:
            chars[i] = chr(ord(chars[i]) + 1)
            return ''.join(chars)

    # Overflow: Z, ZZ, ZZZ, ... -> AA, AAA, ...
    return 'A' + ''.join(chars)

def succ_base63(s):
# Return the successor of a base-63 string using numerals and letters as digits.
    dgs = '_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    s = ''.join(c for c in s if c in dgs)

    chars = list(s)
    i = len(chars) - 1

    while i >= 0:
        if chars[i] == 'z':
            chars[i] = '_'
            i -= 1
        else:
            chars[i] = dgs[dgs.index(chars[i]) + 1]
            return ''.join(chars)

    # Overflow:
    return '_' + ''.join(chars)

def add_parameter(key, l):
# Extension modules can use this function to add parameters to the conversion
# If key slot is taken, create and return nearest upper free slot
    key = '/' + ''.join(c for c in key.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    while (key in PARAMETERS) or (key in INTERNAL_OPTIONS):
        key = '/' + succ_base26(key)
    PARAMETERS[key] = l
    return key

def inflags(k):
    c = k[0]
    f = k[1:]
    if c in ('/'):
        return k in FLAGS
    elif c in ('+', '-'):
        return ('+'+f in FLAGS) or ('-'+f in FLAGS)
    else:
        return None

def add_flag(key, l):
# Extension modules can use this function to add flags to the conversion
# If key slot is taken, create and return nearest upper free slot

    c = key[0]
    if c not in ('+', '-', '/'):
        return None
    key = c + ''.join(c for c in key.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    while inflags(key) or (key in INTERNAL_OPTIONS):
        key = c + succ_base26(key)
    FLAGS[key] = l
    return key

def get_conflag(f):
    c = f[0]
    d = f[1:]
    if c not in ('+', '-'):
        return None
    return ('+'+d, '-'+d)

def fill_conflags(conflags):
    for f in FLAGS:
        cf = get_conflag(f)
        if cf:
            conflags.append(cf)

def detect_flag(f, l, retrieve = False):
    for i in range(len(l)):
        if l[i][1].upper() == f.upper():
            if retrieve:
                return i, l[i][2]
            else:
                return i
    if retrieve:
        return None, None
    else:
        return None

def apply_op(ov, nv, op, tp):
    if tp != str:
        ov = q_eval(ov)
        nv = q_eval(nv)
    if nv is None:
        return tp(ov)
    if (op == '*'):
        v = ov * nv
    elif (op == '+'):
        v = ov + nv
    elif (op == '-'):
        v = ov - nv
    elif (op == '/'):
        v = ov / nv
    else:
        v = nv
    if tp == int:
        v = round(v)
    else:
        v = tp(v)
    return v

def deop(f):
    if f[-1] in ('+', '*', '/', '-'):
        op = f[-1]
        f = f[:-1]
    else:
        op = None
    return f, op

def expand_flag(f, up = False):
    s = f.split('=')
    if len(s) > 0:
        p, op = deop(s[0])
    else:
        p = op = None
    if len(s) > 1:
        v = s[1]
    else:
        v = None
    if up:
        return (f.upper() if f else f), (p.upper() if p else p), (v.upper() if v else v), op
    else:
        return f, p, v, op

def get_variance_range(name):
    if 'RELATIVE' in name or 'SCALE' in name or 'FACTOR' in name:
        return 4
    elif 'ABSOLUTE' in name or 'WIDTH' in name or 'SW' in name or 'SIZE' in name or 'STEP' in name or 'DIAMETER' in name:
        return 200
    elif 'ANGLE' in name:
        return 180
    elif 'PADDING' in name:
        return 4
    else:
        return 100

def generate_test_value(val, variance, name):
# Returns a modified test value based on input type and variance.

# - bool: Returns True or False (50/50 chance).
# - int: Returns a random integer within the variance range.
# - float: Returns a random float within the variance range.

    # CRITICAL: Check for bool FIRST because in Python, bool is a subclass of int
    # (e.g., isinstance(True, int) evaluates to True)
    if isinstance(val, bool):
        return random.choice([True, False])

    if 'COLOR' in name:
        return random.randint(0, 0xffffff)

    if isinstance(val, (int, float)):
        # Calculate upper and lower bounds
        delta = abs(get_variance_range(name) * variance)
        min_val = val - delta
        max_val = val + delta

        # Return integer if original value was an int
        if isinstance(val, int):
            return random.randint(round(min_val), round(max_val))

        # Return float if original value was a float
        return random.uniform(min_val, max_val)

    raise TypeError(f"Unsupported type: {type(val)}. Expected int, float, or bool.")

def randomize_options(variance):
    for key, v in PARAMETERS.items():
        i = v[2]
        t = v[3]
        if (t == HEX):
            t = int
        if t not in (int, float, bool) or key in ('/R', '/G'):
            continue
        if not i:
            i = 0
        i = t(i)
        i = generate_test_value(i, variance, v[1])
        v[2] = i
    PARAMETERS['/UPC'][2] = None

    for key, v in FLAGS.items():
        if key in ('/SVG', '/FSVG', '/OW', '/D', '/P', '/E', '/?'):
            continue
        b = v[2]
        b = generate_test_value(b, variance, v[1])
        v[2] = b

def setup_parameters(params):
    global debug_, MONO, qtr, bg, MARK_BOUNDS, wait_, embed_font, echo, grow, FONT, dimv, FLAGS, PARAMETERS
    save_config = None
    load_config = None
    load_param_line = None
    save_param_line = None
    pklext = '.pkl'
    txtext = '.txt'
    default_config_file = f'config{pklext}'
    default_param_str_file = f'params{txtext}'
    save_config_flag = '/SCFG'
    load_config_flag = '/LCFG'
    load_parameter_line_flag = '/LPL'
    save_parameter_line_flag = '/SPL'
    args = params
    args_save = args[:]
    grow = False
    j = 0
    flags__ = []
    flags_ = []
    while j < len(args):
        if args[j][0] in ('/', '-', '+'):
            flags__.append(expand_flag(args[j], True))
            flags_.append(expand_flag(args[j]))
            del args[j]
        else:
            j += 1
    flags = (flags__, flags_)
    if detect_flag('/?', flags[0]) is not None:
        display_help()
        raise SystemExit
    i, s = detect_flag(save_config_flag, flags[1], True)
    if (i is not None) and (not save_config):
        if s:
            save_config = f'{s}{pklext}'
        else:
            save_config = default_config_file
        del flags[0][i]
        del flags[1][i]
    i, s = detect_flag(load_config_flag, flags[1], True)
    if (i is not None) and (not load_config):
        if s:
            load_config = f'{s}{pklext}'
        else:
            load_config = default_config_file
        del flags[0][i]
        del flags[1][i]
    while True:
        i, s = detect_flag(load_parameter_line_flag, flags[1], True)
        if (i is not None):
            if s:
                load_param_line = f'{s}{txtext}'
            else:
                load_param_line = default_param_str_file
            p_line = load_parameter_line(load_param_line)
            args.extend(p_line)
            args_save.extend(p_line)
            del flags[0][i]
            del flags[1][i]
        else:
            break
    while j < len(args):
        if args[j][0] in ('/', '-', '+'):
            flags__.append(expand_flag(args[j], True))
            flags_.append(expand_flag(args[j]))
            del args[j]
        else:
            j += 1
    i, s = detect_flag(save_parameter_line_flag, flags[1], True)
    if (i is not None) and (not save_param_line):
        if s:
            save_param_line = f'{s}{txtext}'
        else:
            save_param_line = default_param_str_file
        del flags[0][i]
        del flags[1][i]
    if detect_flag('/G', flags[0]) is not None:
        grow = True
    rdmz = (detect_flag('/R', flags[0]) is not None)
    if load_config:
        load_two_dicts(load_config, FLAGS, PARAMETERS)
    CONFLAGS = []
    fill_conflags(CONFLAGS)
    for p in CONFLAGS:
        i1 = detect_flag(p[0], flags[0])
        i2 = detect_flag(p[1], flags[0])
        if (i1 is not None) and (i2 is not None):
            print(f'Conflicting flags: {flags[1][i1]} and {flags[1][i2]}')
            raise SystemExit
    # process flags
    i = 0
    while i < len(flags[0]):
        s = flags[0][i][1]
        if s in FLAGS:
            FLAGS[s][2] = not s.startswith('-')
            del flags[0][i]
            del flags[1][i]
        else:
            i += 1

    # process parameters
    i = 0
    while i < len(flags[0]):
        p = flags[0][i][1]
        if p in PARAMETERS:
            try:
                _tp = int if PARAMETERS[p][3] == HEX else PARAMETERS[p][3]
                PARAMETERS[p][2] = apply_op(PARAMETERS[p][2], flags[0][i][2], flags[0][i][3], _tp)
                print(f'Setting {PARAMETERS[p][4]} to: {PARAMETERS[p][2] if PARAMETERS[p][3] != HEX else int_to_hex(PARAMETERS[p][2])}')
                del flags[0][i]
                del flags[1][i]
            except Exception as e:
                print(f'Invalid syntax: "{flags[1][i][0]}"')
                print(e)
                raise SystemExit
        else:
            i += 1

    if rdmz and (PARAMETERS['/R'][2] != 0.0): # Variance
        randomize_options(PARAMETERS['/R'][2])
    declare_flags()
    declare_parameters()
    dimv = 0
    if WIDTHCM is not None: dimv += 1
    if HEIGHTCM is not None: dimv += 2
    if UNITSPERCM is not None: dimv += 4
    if (dimv not in (0, 1, 2, 3, 4)):
        print('Dimension error: Distance cannot be declared together with resolution.')
        raise SystemExit
    if 0.0 in (WIDTHCM, HEIGHTCM, UNITSPERCM):
        print('Dimension error: Dimension parameters cannot be zero.')
        raise SystemExit

    if (FONT not in Fonts):
        print(f'Unsupported font: "{FONT}". Falling back to "Tahoma"')
        FONT = 'Tahoma'

    for i in range(len(flags[0])):
        if (not inflags(flags[0][i][1])) and (flags[0][i][1] not in PARAMETERS):
            print(f'Ignoring unknown or repeated option "{flags[1][i][0]}"')
    if save_param_line:
        save_parameter_line(save_param_line, args_save)
    if save_config:
        save_two_dicts(save_config, FLAGS, PARAMETERS)

    return args

# Loads any units in the working folder that starts with "qs"
# And transfers control to them
start_time = time.perf_counter()
if os.path.basename(sys.argv[0]) != "qsconvert.py":
    sys.exit("Execution halted: Script's name must be 'qsconvert.py'.")
internal_parameters = get_arg_list(param_str)
try:
    loaded_units = discover_and_load_units()
    init_unit_dict(loaded_units)
except Exception as e:
    s = f'Fatal Error in module loading ({type(e).__name__}): {e}'
    handle_exception(s)
    raise SystemExit
try:
    args = setup_parameters(sys.argv[1:] + internal_parameters)
except Exception as e:
    s = f"Fatal Error while setting up parameters ({type(e).__name__}): {e}"
    handle_exception(s)
    raise SystemExit

class Svg(list):
    def __init__(self, initial_items=None, defs=None):
        # Initialize the underlying list
        super().__init__(initial_items if initial_items is not None else [''])

        # Internal list for defs
        self.defs = defs if defs is not None else ['', '<defs>']

    def close_defs(self):
        self.defs.append('</defs>')
        if self.defs == ['', '<defs>', '</defs>']:
            self.defs = []

QSpice = SafeDict

# *** BEGIN PARSER. ***

IGNORE_ELEMENTS = {}
TEXT_FIELDS = {STRG, NETNAME, DESCRIPTION, PINNAME}

def artifact(d):
# Artifact to get the composition to work if the jpeg boom is not present
    d[f'{EXTRA_}0'] = d[TYPE]
    d[TYPE] = FILE_BOM

def deartifact(d):
# Take back the artifact
    d[TYPE] = d[f'{EXTRA_}0']
    del d[f'{EXTRA_}0']

def tokenize(content):
# Tokenizes content, respecting double-quotes and structural « » brackets.
# Handles internal double quotes by stopping only at the next » or
# a closing quote followed by space/bracket.

    tokens = []
    i = 0
    n = len(content)
    while i < n:
        char = content[i]
        if char == '(':
            start = i
            i += 1
            j = 1
            while (i < n) and (j > 0): 
                i += 1
                if content[i] == "(": j +=1
                if content[i] == ")": j -=1
            if (i < n): i += 1
            if (i > start): tokens.append(content[start:i])
            continue
        if char == '[':
            start = i
            i += 1
            j = 1
            while (i < n) and (j > 0): 
                i += 1
                if content[i] == "[": j +=1
                if content[i] == "]": j -=1
            if (i < n): i += 1
            if (i > start): tokens.append(content[start:i])
            continue
        if char.isspace():
            i += 1
            continue
        if char in ('«', '»'):
            tokens.append(char)
            if char == '«': last_op_brac = i
            i += 1
        elif char == '"':
            start = i
            i += 1
            # Scan until closing quote OR the structural end bracket »
            # We also check if the quote is followed by a separator to be sure
            while i < n:
                if content[i] == '"':
                    # Peek ahead: is this a real closing quote?
                    # Usually followed by space, », or another «
                    while (i+1 < n):
                        if content[i+1].isspace():
                            i += 1
                        else:
                            break
                    if (i+1 >= n) or (content[i+1] == '»'):
                        break
                if (i < n): i += 1
            if (i < n) and (content[i] == '"'):
                i += 1
            raw_str = content[start:i]
            if raw_str: tokens.append(raw_str)

        else:
            start = i
            while (i < n) and (not content[i].isspace()) and (content[i] not in ('«', '»', '"')):
                if content[i] == ':':
                    while tokens[-1] != '«': tokens.pop()
                    if (i > last_op_brac): tokens.append(content[last_op_brac+1:i+1])
                    i += 1
                    start = i
                    while (i < n) and (content[i] != '»'): i += 1
                    st = content[start:i]
                    st = st.strip()
                    if st: tokens.append(st)
                    start = i
                else:
                    i += 1

            if (i > start): tokens.append(content[start:i])
    tokens.append(' ')
    return tokens

def parse(content, tokens = None, portion = 0, start = None, end = None): # "end" exclusive
    if portion == 0:
        tokens = tokenize(content)
        entry = parse(None, tokens, 1)
        fill_metadata(entry)
        return entry

    if portion == 1:
        entry = QSpice()
        if start is None: start = 0
        if end is None: end = len(tokens)
        i = start
        field_idx = -1
        while i < end:
            token = tokens[i]
            if token == ' ':
                pass
            elif token == '«':
                depth = 1
                start_ = i + 1
                while (depth > 0) and (i < end):
                    i += 1
                    if tokens[i] == '«': depth += 1
                    if tokens[i] == '»': depth -= 1
                    end_ = i
                field = get_field_name(entry, field_idx)
                entry[field] = parse(None, tokens, 1, start_, end_)
                if entry[field].get(TYPE) in (PIN, NET):
                    split_net_strings(entry[field])
            else:
                field = get_field_name(entry, field_idx)
                if (field in TEXT_FIELDS) or (field_idx == -1):
                    entry[field] = token
                else:
                    entry[field] = q_eval(token)
            i += 1
            field_idx += 1
        return entry

def compose_qspice(d, l = None, depth = 0, portion = 0):
# Composes QSpice file from data parsed with "parse".
# "d" is the parsed data and "l" is the destination list of lines

    if portion == 0:
        if l is None:
            l = []
        ftype = d.get(TYPE)
        if isinstance(ftype, QSpice):
            artifact(d)
            artifacted = True
        else:
            artifacted = False
        compose_qspice(d, l, depth, 1)
        if (not artifacted):
            l[1] = l[0] + l[1] # removes the line break after the file bom
        del l[0]
        if (not detect_symbol_file(d)):
            l.append('')
        if artifacted:
            deartifact(d)
        return l

    if portion == 1:
        eltype = d.get(TYPE, None)
        if eltype in IGNORE_COMPOSE_DEFS:
            return l
        i = -1
        st = ((depth - 1)*'  ')+'«' if depth > 0 else ''
        len_d = len(d)
        while i + 1 < len_d:
            if eltype:
                field = get_field_name(None, i, etype = eltype, defs = COMPOSE_DEFS)
                obj = d.get(field)
                if (obj is None):
                    i += 1
                    continue
                if isinstance(obj, QSpice):
                    if st: l.append(st)
                    st = ''
                    compose_qspice(obj, l, depth + 1, 1)
                else:
                    st += f'{" " if (i+1) > 0 else ""}{int_to_hex(obj) if (COLOR in field) else pt_to_str(obj) if (field in (P1, P2, P3, P4, LP1)) else obj}'
            i += 1
        tr_spc = ''
        if st:
            if st.endswith(':'):
                tr_spc = ' '
        l.append((st if st else (depth - 1)*'  ') + (f'{tr_spc}»' if (depth > 0) else ''))

        return l

# *** END PARSER. BEGIN GRAPHICS. ***

def rpub(n, precision = DYN_PRECISION):
# Round for publishing
    v = round(n, precision)
    if v.is_integer():
        v = round(v)
    return v

def rcomp(n, precision = (DYN_PRECISION*2)-1):
# Round for comparison
    return round(n, precision)

def rlis(l, precision = (DYN_PRECISION*2)-1):
# Round list for comparison
    r = []
    for e in l:
        r.append(round(e, precision))
    return r

def rtup(t, precision = (DYN_PRECISION*2)-1):
# Round tuple for comparison
    r = []
    for e in t:
        r.append(round(e, precision))
    return tuple(r)

def round_point(p):
    try:
        return (round(p[0]), round(p[1]))
    except:
        return p

def round_matrix(m, precision = (DYN_PRECISION*2)-1,
    # localize names:
    LM0 = LM0, range = range, round = round, isinstance = isinstance, tuple = tuple):
# Round matrix for comparison
    C = LM0()
    for i in range(3):
        for j in range(3):
            C[i][j] = round(m[i][j], precision)
    if isinstance(m, tuple):
        return (tuple(C[0]), tuple(C[1]), tuple(C[2]))
    else:
        return C

def multiply(A, B,
    # localize names:
    range = range, LM0 = LM0):
# Multiplies two 3x3 matrices.
    C = LM0()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                C[i][j] += A[i][k] * B[k][j]
    return C

def simplify_transforms(tr_,
    # localize names:
    list = list, range = range, len = len, SCALE = SCALE, rcomp = rcomp, 
    LM1 = LM1, M1 = M1, TRANSLATE = TRANSLATE, ROTATE = ROTATE, radians = radians, 
    cos = cos, sin = sin, multiply = multiply, round_matrix = round_matrix, 
    sqrt = sqrt, degrees = degrees, atan2 = atan2, rtup = rtup, tuple = tuple):
# Simplifies transformation sequences to the max 3 needed statements
    if not tr_: return [(TRANSLATE, 0, 0), (ROTATE, 0), (SCALE, 1, 1)], [(0, 0), 0, (1, 1)], M1
    
    _tr = [list(tr_[i]) for i in range(len(tr_))]

    for t in _tr:
        if t[0] == SCALE:
            if len(t) == 2:
                t.append(t[1]) # Scale must contain 2 parameters for code below

    i = 0
    while i < len(_tr):
        j = i+1
        while j < len(_tr) and _tr[i][0] == _tr[j][0]: # Same transformation type?
            k = 1
            while k < len(_tr[i]): # Combine numbers into a single transformation.
                if _tr[i][0] == SCALE:
                    _tr[i][k] *= _tr[j][k] # "scale" multiplies the numbers
                else:
                    _tr[i][k] += _tr[j][k] # "translate" and "rotate" sums numbers.
                k += 1
            del _tr[j] # Deletes element that was absorbed by the previous.
        n = 1 if _tr[i][0] == SCALE else 0 # n is the neutral number to this transformation.
        if all(rcomp(item) == n for item in _tr[i][1:]): # if numbers are neutral, delete.
            del _tr[i]
            i -= 1
            if i >= 0:
                i -= 1 # Come back one more in case next one is same as previous.
        i += 1

    # Identity matrix
    tm = LM1()

    for cmd in _tr:
        op = cmd[0]
        m = LM1() # Identity for this step

        if op == TRANSLATE:
            m[0][2], m[1][2] = cmd[1], cmd[2]
        elif op == ROTATE:
            rad = radians(cmd[1])
            c, s = cos(rad), sin(rad)
            m[0][0], m[0][1] = c, -s
            m[1][0], m[1][1] = s, c
        elif op == SCALE:
            m[0][0], m[1][1] = cmd[1], cmd[2]

        tm = multiply(tm, m)

    mout = round_matrix(tm)
    if mout[2] != [0, 0, 1]:
        print("Warning: Matrix error: 3rd dimension leak.")

    # Decompose
    a, c, e = tm[0]
    b, d, f = tm[1]

    tx, ty = e, f
    sx = sqrt(a**2 + b**2)
    sy = sqrt(c**2 + d**2)

    # Handle reflection
    if (a * d - b * c) < 0:
        sy = -sy

    angle = degrees(atan2(b, a))

    # List version for applying in sequence:
    t = [(TRANSLATE, tx, ty), (ROTATE, angle), (SCALE, sx, sy)]
    # Dict version for component access:
    t_ = [(tx, ty), angle, (sx, sy)]
    i = 0
    while i < len(t):
        if t[i][0] == TRANSLATE:
            if rtup(t[i][1:]) == (0, 0): # If neutral translate, delete
                del t[i]
                continue
        elif t[i][0] == ROTATE: # If neutral rotate, delete
            if rcomp(t[i][1]) == 0:
                del t[i]
                continue
        elif t[i][0] == SCALE:
            if rtup(t[i][1:]) == (1, 1): # If neutral scale, delete
                del t[i]
                continue
            if rcomp(t[i][1]) == rcomp(t[i][2]): # If uniform scale, delete second factor
                t[i] = t[i][:-1] # del t[i][2]
        i += 1
    return t, t_, (tuple(tm[0]), tuple(tm[1]), tuple(tm[2])) # list, raw list, matrix

def plot_function(
# Modified from InkScape's Function Plotter(
    # 2009 Michel Chatelain.
    # 2007 Tavmjong Bah, tavmjong@free.fr
    # 2006 Georg Wiora, xorx@quarkbox.de
    # 2006 Johan Engelen, johan@shouraizou.nl
    # 2005 Aaron Spike, aaron@ekips.org
#)  
# Parameters for unity:
# fx, fy, samples=2, t_start=0, t_end=1, w=1, h=1, l=0, r=1, b=0, t=1, ox=0, oy=0, dx=None, dy=None, tox=0, toy=0, gain=None 
# Here, we use positional parameters for speed
    fx, fy, # /Functions to plot
    samples, # = 2 /Number of output nodes
    t_start, t_end, # = 0, 1 /Time interval passed to the functions
    w, h, # = 1, 1 /Dimensions
    l, r, # = 0, 1 /X domain
    b, t, # = 0, 1 /Y domain
    ox, oy, # = 0, 0 /X and Y offsets
    dx, dy, # = None, None /Derivatives of functions to plot
    tox, toy, # = 0, 0 /Time offsets
    gain, # = None /Approximation constant
    # localize names:
    epsilon = epsilon, epsilon3 = epsilon3
):
    tx_start, ty_start = t_start + tox, t_start + toy

    # coords and scales based on the source rect
    scalex = w / (r - l)
    scaley = h / (t - b)

    # step is increment of t
    step = (t_end - t_start) / (samples - 1)
    ds = step * 0.001 # Step used in calculating derivatives
    hstep = step * 0.5

    a = [] # path array

    # Initialize functions and derivatives for 0;
    # They are carried over from one iteration to the next, to avoid extra function calculations.
    x0, y0 = fx(tx_start), fy(ty_start)

    if dx:
        dxi = dxs = dx
    else: # Set numerical derivative
        dxi = lambda t: ((fx(t + ds) - x0) / ds)
        dxs = lambda t: ((x1 - fx(t - ds)) / ds)
    if dy:
        dyi = dys = dy
    else: # Set numerical derivative
        dyi = lambda t: ((fy(t + ds) - y0) / ds)
        dys = lambda t: ((y1 - fy(t - ds)) / ds)

    # Initial derivatives
    # If analytical derivatives are not informed, calculate numerical derivatives,
    # using 0.001*step as the small differential
    dx0, dy0 = dxi(tx_start), dyi(ty_start)

    # Start curve
    a.append(("M", ((x0 - l) * scalex + ox , (-y0 + b) * scaley + oy))) # initial moveto

    if gain: # User informed gain
        third = step * gain

    for i in range(round(samples - 1)):
        tx0, ty0 = i * step + tx_start, i * step + ty_start
        tx1, ty1 = tx0 + step, ty0 + step

        # Sample endpoint
        x1, y1 = fx(tx1), fy(ty1)

        # Get derivatives at endpoint
        dx1, dy1 = dxs(tx1), dys(ty1)

        if gain is None: # Google Gemini's auto-gain engine:
            # 1. Sample the function at its exact midpoint
            x_mid, y_mid = fx(tx0 + hstep), fy(ty0 + hstep)

            # 2. Calculate the displacement of the true midpoint from a simple straight chord line
            dx_mid, dy_mid = x_mid - 0.5 * (x0 + x1), y_mid - 0.5 * (y0 + y1)

            # 3. Calculate the structural tangent velocity difference vector across the segment
            vx, vy = 0.375 * step * (dx0 - dx1), 0.375 * step * (dy0 - dy1)

            # 4. Apply the Tikhonov Regularization Trick
            den = (vx * vx) + (vy * vy)

            # Smoothly transitions to 1/3 as denominator approaches 0
            auto_gain = (((dx_mid * vx) + (dy_mid * vy)) + epsilon) / (den + epsilon3)

            third = step * auto_gain

        # create curve
        a.append(
            (
                "C",
                (
                    ( (x0 + (dx0 * third)) - l) * scalex + ox,
                    (-(y0 + (dy0 * third)) + b) * scaley + oy,
                    ( (x1 - (dx1 * third)) - l) * scalex + ox,
                    (-(y1 - (dy1 * third)) + b) * scaley + oy,
                    ( (x1)                 - l) * scalex + ox,
                    (-(y1)                 + b) * scaley + oy
                )
            )
        )
        # Assume the functions are smooth everywhere, so carry over the derivatives too
        x0, y0, dx0, dy0 = x1, y1, dx1, dy1
    return a

def u_scale(obj, scale = SCALE_FACTOR,
    # localize names:
    type = type, int = int, float = float,
    isinstance = isinstance, tuple = tuple, 
    dict = dict, us = None):
# Recursively traverses nested structures (tuples, lists, dicts)
# and multiplies every int/float by "scale".
# Preserves original collection types.

    # 1. Base Case: Scale numbers (avoiding Booleans, which are a subclass of int)
    if type(obj) in (int, float):
        return float(obj * scale)

    # 2. Tuples
    elif isinstance(obj, tuple):
        return tuple(us(item, scale) for item in obj)

    # 3. Lists
    elif isinstance(obj, list):
        return [us(item, scale) for item in obj]

    # 4. Dictionaries (scales values, leaves keys intact)
    elif isinstance(obj, (dict, QSpice)):
        return {k: us(v, scale) for k, v in obj.items()}

    # 5. Pass through strings, None, Booleans, etc. unchanged
    return obj

u_scale.__defaults__ = u_scale.__defaults__[:-1] + (u_scale,)

def tr(obj, scale = SCALE_FACTOR, ind = 0,
    # localize names:
    type = type, int = int, float = float,
    isinstance = isinstance, tuple = tuple, 
    dict = dict, range = range, t = None):
# Recursively traverses nested structures (tuples, lists, dicts)
# and multiplies every int/float by "scale" if index is even
# and "-scale" if index is odd.
# Preserves original collection types.

    # 1. Base Case: Scale numbers (avoiding Booleans, which are a subclass of int)
    if type(obj) in (int, float):
        out = float(obj * scale)
        if ind % 2 != 0:
            out *= -1
        return out

    # 2. Tuples
    elif isinstance(obj, tuple):
        return tuple(t(obj[i], scale, i) for i in range(len(obj)))

    # 3. Lists
    elif isinstance(obj, list):
        return [t(obj[i], scale, i) for i in range(len(obj))]

    # 4. Dictionaries (scales values, leaves keys intact)
    elif isinstance(obj, (dict, QSpice)):
        return {k: t(v, scale) for k, v in obj.items()}

    # 5. Pass through strings, None, Booleans, etc. unchanged
    return obj

tr.__defaults__ = tr.__defaults__[:-1] + (tr,)

def sort_line(p1, p2):
# Sorts points such that Y takes precedence (top-to-bottom), then X (left-to-right).
    if p1[1] < p2[1] or (p1[1] == p2[1] and p1[0] < p2[0]):
        return p1, p2
    return p2, p1

def sort_line_(x1, y1, x2, y2):
# Sorts points such that Y takes precedence (top-to-bottom), then X (left-to-right).
    if y1 < y2 or (y1 == y2 and x1 < x2):
        return x1, y1, x2, y2
    return x2, y2, x1, y1

def sort_duke(v1, v2):
    if v1 > v2: return v2, v1
    return v1, v2

def get_width(p1, p2):
    return p2[0] - p1[0]

def get_height(p1, p2):
    return p2[1] - p1[1]

def get_aspect(p1, p2,
    # localize names:
    get_width = get_width, get_height = get_height
):
    return get_width(p1, p2) / get_height(p1, p2)

class ConnMap(dict):
    def append(self, point):
    # Appends an unrounded point to the bucket list determined by round_point(point).
        key = round_point(point)
        # setdefault is efficient: retrieves existing list or initializes a new one in O(1)
        self.setdefault(key, []).append(point)

    def __getitem__(self, point):
    # Allows reading by passing a point, which gets rounded to find the correct list.
        key = round_point(point)
        return super().__getitem__(key)

    def __contains__(self, point):
    # Checks if a rounded point key exists in the map.
        key = round_point(point)
        return super().__contains__(key)
        
    def get(self, point, default=None):
    # Safely retrieves the bucket list for a rounded point, returning default if absent.
        key = round_point(point)
        return super().get(key, default)        

def count(eltype, counter):
    if counter is not None:
        if (eltype not in counter): counter[eltype] = 0
        counter[eltype] += 1

def uncount(eltype, counter):
    if counter is not None:
        if (eltype not in counter): counter[eltype] = 0
        counter[eltype] -= 1

def sample_cubic_bezier(p0, p1, p2, p3, t):
# Evaluates a 1D cubic Bezier equation at time t using De Casteljau's/Polynomial form.
    return (1.0 - t)**3.0 * p0 + 3.0 * (1.0 - t)**2.0 * t * p1 + 3.0 * (1.0 - t) * t**2.0 * p2 + t**3.0 * p3

def solve_bezier_derivative_roots(p0, p1, p2, p3,
    # localize names:
    sqrt = math.sqrt):
# Finds the t-values (0 <= t <= 1) where the curve's derivative is 0.
# Solves the quadratic equation: At^2 + Bt + C = 0 derived from the Bezier formula.

    roots = []

    # Coefficients of the quadratic derivative equation
    a = 3.0 * (-p0 + 3.0 * p1 - 3.0 * p2 + p3)
    b = 6.0 * (p0 - 2.0 * p1 + p2)
    c = 3.0 * (-p0 + p1)

    # If it's a linear equation (a is zero), solve Bt + C = 0
    if abs(a) < 1e-12:
        if abs(b) > 1e-12:
            t = -c / b
            if 0.0 <= t <= 1.0:
                roots.append(t)
        return roots

    # Determinant/Discriminant (b^2 - 4ac)
    discriminant = b*b - 4.0*a*c

    if discriminant >= 0.0:
        sqrt_d = sqrt(discriminant)

        # Root 1
        t1 = (-b + sqrt_d) / (2.0 * a)
        if 0.0 <= t1 <= 1.0:
            roots.append(t1)

        # Root 2
        t2 = (-b - sqrt_d) / (2.0 * a)
        if 0.0 <= t2 <= 1.0:
            roots.append(t2)

    return roots

def get_cubic_bezier_bounds(path_array,
    # localize names:
    sbdr = solve_bezier_derivative_roots, scb = sample_cubic_bezier,
    float = float, min = min, max = max):
# Calculates the exact bounding box (xmin, ymin, xmax, ymax) of a path array.
# Matches FontForge's logic by solving for the first derivative's roots (extrema).

    if not path_array:
        return 0.0, 0.0, 0.0, 0.0

    # Initialize bounding box with infinity
    xmin, ymin = float('inf'), float('inf')
    xmax, ymax = float('-inf'), float('-inf')

    # Track current cursor position across path commands
    current_pos = (0.0, 0.0)

    for command, coords in path_array:
        if command == "M":
            # Move-to sets the starting point
            current_pos = coords
            xmin = min(xmin, current_pos[0])
            ymin = min(ymin, current_pos[1])
            xmax = max(xmax, current_pos[0])
            ymax = max(ymax, current_pos[1])

        elif command == "L":
            # Line-to draws a straight line to a new point
            # Because it's a straight line, it has no hidden mid-curve peaks (extrema).
            # We only need to check the destination endpoint.
            lx, ly = coords
            xmin = min(xmin, lx)
            xmax = max(xmax, lx)
            ymin = min(ymin, ly)
            ymax = max(ymax, ly)

            # CRITICAL: Move the cursor to this new endpoint!
            current_pos = (lx, ly)
        elif command == "C":
            # Cubic Bezier curve segment
            # P0: Start Point, P1/P2: Control Points, P3: End Point
            p0_x, p0_y = current_pos
            p1_x, p1_y, p2_x, p2_y, p3_x, p3_y = coords

            # --- Dimension X Extrema ---
            x_roots = sbdr(p0_x, p1_x, p2_x, p3_x)

            for t in x_roots:
                xt = scb(p0_x, p1_x, p2_x, p3_x, t)
                xmin = min(xmin, xt)
                xmax = max(xmax, xt)

            # --- Dimension Y Extrema ---
            y_roots = sbdr(p0_y, p1_y, p2_y, p3_y)

            for t in y_roots:
                yt = scb(p0_y, p1_y, p2_y, p3_y, t)
                ymin = min(ymin, yt)
                ymax = max(ymax, yt)

            # Always include the endpoint itself
            xmin = min(xmin, p3_x)
            xmax = max(xmax, p3_x)
            ymin = min(ymin, p3_y)
            ymax = max(ymax, p3_y)

            # Update the cursor to the endpoint of this curve
            current_pos = (p3_x, p3_y)
        elif command == "_":
            x1, y1, x2, y2  = coords
            xmin = min(xmin, x1)
            xmax = max(xmax, x1)
            ymin = min(ymin, y1)
            ymax = max(ymax, y1)
            xmin = min(xmin, x2)
            xmax = max(xmax, x2)
            ymin = min(ymin, y2)
            ymax = max(ymax, y2)

    return xmin, ymin, xmax, ymax

def combine_bounds(bounds_dicts):
    if not bounds_dicts:
        return virgin_bounds()

    return {
        MIN_X: min(b[MIN_X] for b in bounds_dicts),
        MIN_Y: min(b[MIN_Y] for b in bounds_dicts),
        MAX_X: max(b[MAX_X] for b in bounds_dicts),
        MAX_Y: max(b[MAX_Y] for b in bounds_dicts),
    }

def get_path_bounds(path, b, svg_paths, mark, counter, sw = 0, _id = None, bound_transform = None,
    # localize names:
    gcbb = get_cubic_bezier_bounds, isinstance = isinstance, list = list,
    SCALE_FACTOR = SCALE_FACTOR, NATIVE_SYMBOL_SCALE = NATIVE_SYMBOL_SCALE,
    STROKE_WIDTH = STROKE_WIDTH, BOUNDS = BOUNDS, rpub = rpub):
# Used to calculate the drawing boundaries.
# Returns (min_x, min_y, max_x, max_y) for an absolute path.
# Assumes path format: [('M', (x, y)), ('L', (x, y, x2, y2...)), ...]
# At the moment, supporting only cubic paths with "L", "M" and "C" commands
    opath = path
    if bound_transform:
        path = apply_transform(path, bound_transform)
        min_x, min_y, max_x, max_y = gcbb(path)
        omin_x, omin_y, omax_x, omax_y = gcbb(opath)
    else:
        min_x, min_y, max_x, max_y = omin_x, omin_y, omax_x, omax_y = gcbb(path)        
    s = sw * 0.5
    min_x -= s; min_y -= s; max_x += s; max_y += s
    omin_x -= s; omin_y -= s; omax_x += s; omax_y += s
    _b = b if isinstance(b, list) else [b]

    for b_ in _b:
        if min_x < b_[MIN_X]: b_[MIN_X] = min_x
        if max_x > b_[MAX_X]: b_[MAX_X] = max_x
        if min_y < b_[MIN_Y]: b_[MIN_Y] = min_y
        if max_y > b_[MAX_Y]: b_[MAX_Y] = max_y

    if mark and (svg_paths is not None):
        # Marks the bounds' rectangle visibly in the drawing for
        # checking if the bounds are being calculated correctly
        _sw = SCALE_FACTOR * NATIVE_SYMBOL_SCALE * STROKE_WIDTH
        if _id:
            id_ = f'{BOUNDS}_{_id}'
        else:
            id_ = BOUNDS
        count(id_, counter)
        rect = f'<rect x="{rpub(omin_x)}" y="{rpub(omin_y)}" width="{rpub(omax_x-omin_x)}" height="{rpub(omax_y-omin_y)}" stroke="#FF00FF" fill="none" stroke-width="{rpub(_sw)}" id="{id_}_{counter[id_]}" />'
        svg_paths.append(rect)

    return (min_x, min_y, max_x, max_y)

def absolute_to_relative(abs_path):  # untested
# Converts absolute SVG path commands to relative ones.
# Handles single commands, repeated commands, and implicit chained coordinate tuples.

    # Number of coordinate pairs (x, y) per single command segment
    CMD_PAIR_COUNTS = {
        'M': 1, 'L': 1,  # 1 pair (2 floats: x, y)
        'C': 3,          # 3 pairs (6 floats: x1, y1, x2, y2, x, y)
        'Q': 2, 'S': 2,  # 2 pairs (4 floats: x1, y1, x, y)
    }
    rel_path = []
    cursor_x, cursor_y = 0.0, 0.0

    for cmd, coords in abs_path:
        cmd_upper = cmd.upper()

        # 1. First move command anchors the path in absolute space
        if len(rel_path) == 0 and cmd_upper == 'M':
            rel_path.append(('M', coords))
            cursor_x, cursor_y = coords[-2], coords[-1]
            continue

        rel_coords = []
        # Determine how many coordinate pairs form one complete command segment
        pairs_per_segment = CMD_PAIR_COUNTS.get(cmd_upper, 1)
        floats_per_segment = pairs_per_segment * 2

        # Step through coordinate blocks (e.g. 2 floats for L, 6 floats for C)
        for block_start in range(0, len(coords), floats_per_segment):
            block = coords[block_start : block_start + floats_per_segment]

            # Convert each (x, y) in the block relative to the pen position BEFORE this block
            for i in range(0, len(block), 2):
                abs_x, abs_y = block[i], block[i+1]
                rel_coords.append(abs_x - cursor_x)
                rel_coords.append(abs_y - cursor_y)

            # *** RESET RELATIVE ANCHOR ***
            # The pen position now shifts to the endpoint of this completed segment
            cursor_x = block[-2]
            cursor_y = block[-1]

        rel_path.append((cmd.lower(), tuple(rel_coords)))

    return rel_path

def relative_to_absolute_chained(rel_path): # untested
    # Number of coordinate pairs required per command type
    CMD_PAIR_COUNTS = {
        'M': 1, 'L': 1, 'H': 0, 'V': 0,  # Single point (x, y)
        'C': 3,                           # 3 pairs (ctrl1, ctrl2, end)
        'S': 2, 'Q': 2,                   # 2 pairs (ctrl, end)
        'A': 3,                           # (rx/ry/rotation flags processed differently)
    }
    abs_path = []
    cursor_x, cursor_y = 0.0, 0.0

    for cmd, coords in rel_path:
        cmd_upper = cmd.upper()

        if len(abs_path) == 0 and cmd_upper == 'M':
            abs_path.append(('M', coords))
            cursor_x, cursor_y = coords[-2], coords[-1]
            continue

        abs_coords = []
        pairs_per_cmd = CMD_PAIR_COUNTS.get(cmd_upper, 1)
        step = pairs_per_cmd * 2  # Number of float values per full command block

        # Process each full sub-command block (e.g., 6 floats at a time for 'c')
        for block_start in range(0, len(coords), step):
            block = coords[block_start : block_start + step]

            # Each pair inside the block is relative to the START of this block
            for i in range(0, len(block), 2):
                dx, dy = block[i], block[i+1]
                abs_coords.append(cursor_x + dx)
                abs_coords.append(cursor_y + dy)

            # *** RESETS RELATIVE ANCHOR ***
            # Update cursor to the endpoint of THIS completed sub-command
            cursor_x = abs_coords[-2]
            cursor_y = abs_coords[-1]

        abs_path.append((cmd_upper, tuple(abs_coords)))

    return abs_path

def rotate_point(point, angle_deg, origin=(0, 0),
    # localize names:
    sin = sin, cos = cos, radians = radians):
# Rotates a point (x, y) around an origin by angle_deg.
    ox, oy = origin
    px, py = point
    angle_rad = radians(angle_deg)

    qx = ox + cos(angle_rad) * (px - ox) - sin(angle_rad) * (py - oy)
    qy = oy + sin(angle_rad) * (px - ox) + cos(angle_rad) * (py - oy)
    return (qx, qy)

def scale_point(point, sx, sy=None):
# Scales a point (x, y) by sx and sy.
    if sy is None: sy = sx # Handle uniform scale
    return point[0] * sx, point[1] * sy

def translate_point(point, tx, ty):
# Translates a point (x, y) by tx and ty.
    return point[0] + tx, point[1] + ty

def mirror_point(p, angle_deg,  # untested
    # localize names:
    radians = radians, cos = cos, sin = sin):
# Reflect point (x, y) across a line passing through the origin
# at angle angle_deg (degrees).
    x, y = p
    theta = radians(angle_deg)

    cos_t = cos(theta)
    sin_t = sin(theta)

    # Rotate into axis frame
    xr = x * cos_t + y * sin_t
    yr = -x * sin_t + y * cos_t

    # Mirror across X axis
    yr = -yr

    # Rotate back
    x_out = xr * cos_t - yr * sin_t
    y_out = xr * sin_t + yr * cos_t

    return (x_out, y_out)

def apply_transform(path, _tr_, backwards = True,
    # localize names:
    list= list, translate_point = translate_point, TRANSLATE = TRANSLATE, 
    ROTATE = ROTATE, SCALE = SCALE, len = len, abs = abs, range = range, 
    rotate_point = rotate_point, int = int, scale_point = scale_point, 
    tuple = tuple
):

# Applies a sequence of transforms to a path in the order provided.
# Bakes the transformations directly into the coordinates.
#
# Supports:
# - Standard coordinate pairs (M, L, C, Q, S, T)
# - SVG Arc segments (A)
# - Empty coordinate lists (Z)

    if not _tr_: return path
    _tr = _tr_[::-1] if backwards else _tr_
    new_path = []

    for cmd_type, coords in path:
        # Work on a copy of the coordinates for this command
        current_coords = list(coords)

        # If there are no coordinates (like in 'Z'), just pass it through
        if not current_coords:
            new_path.append((cmd_type, ()))
            continue

        # Process each transformation in the list sequentially
        for t in _tr:
            op = t[0]
            temp_coords = []

            if cmd_type == 'A':
                # SVG Arc structure: [rx, ry, x_axis_rot, large_arc, sweep, x, y]
                rx, ry, x_rot, large, sweep, x, y = current_coords

                if op == TRANSLATE:
                    # Only the final destination point is translated
                    x, y = translate_point((x, y), t[1], t[2])

                elif op == ROTATE:
                    angle = t[1]
                    # Rotate the final point around (0,0)
                    x, y = rotate_point((x, y), angle)
                    # The orientation of the ellipse itself is rotated
                    x_rot += angle

                elif op == SCALE:
                    sx = t[1]
                    sy = t[2] if len(t) > 2 else sx
                    # Radii are always absolute/positive
                    rx *= abs(sx)
                    ry *= abs(sy)
                    # Scale the final point
                    x, y = scale_point((x, y), sx, sy)
                    # Flip sweep flag if mirroring (only one axis is negative)
                    if sx * sy < 0:
                        sweep = 1 - sweep

                temp_coords = [rx, ry, x_rot, int(large), int(sweep), x, y]

            else:
                # Standard Logic for all other commands (M, L, C, Q, S, T)
                # These consist entirely of x,y coordinate pairs
                for i in range(0, len(current_coords), 2):
                    # Index check to prevent crashes on malformed data
                    if i + 1 < len(current_coords):
                        p = (current_coords[i], current_coords[i+1])

                        if op == TRANSLATE:
                            p = translate_point(p, t[1], t[2])
                        elif op == ROTATE:
                            p = rotate_point(p, t[1])
                        elif op == SCALE:
                            sx = t[1]
                            sy = t[2] if len(t) > 2 else sx
                            p = scale_point(p, sx, sy)

                        temp_coords.extend([p[0], p[1]])

            # Update current_coords so the next transform in the list
            # applies to the result of this one
            current_coords = temp_coords

        new_path.append((cmd_type, tuple(current_coords)))

    return new_path

def nang(a):
# Normalize angle
    return (360 - (abs(a) % 360)) if (a < 0) else (a % 360)

def gnan(a,
    # localize names:
    nang = nang):
# Returns the angle in the mapping format(-179.9_ to 180)
    s = nang(a)
    r = (s - 360) if (s > 180) else s
    return r

def demirror(rot_code):
    return (rot_code - 8) if (rot_code >= 8) else rot_code

def ismirror(rot_code):
    return (rot_code >= 8)

def isdiagonal(rot_code):
    return ((rot_code % 2) != 0)

def combine_angle_codes(codes,
    # localize names:
    ROTATION_MAP = ROTATION_MAP, ANGLE_TO_CODE = ANGLE_TO_CODE,
    gnan = gnan, sum = sum, len = len
):
    if len(codes) == 0: return 0
    if len(codes) == 1: return codes[0]
    total_rotation = sum(ROTATION_MAP.get(a, 0) for a in codes)
    return ANGLE_TO_CODE.get(gnan(total_rotation), 0)

def combine_rotations(rots, 
    # localize names:
    len = len, ROTATION_MAP = ROTATION_MAP, ANGLE_TO_CODE = ANGLE_TO_CODE,
    gnan = gnan
):
    if len(rots) == 0: return 0
    if len(rots) == 1: return rots[0]
    m = 0
    angle = 0
    for r in rots:
        if r >= 8:
            m += 1
            angle += ROTATION_MAP.get((r - 8), 0)
        else:
            angle += ROTATION_MAP.get(r, 0)
    mirror = (m % 2) != 0
    return ANGLE_TO_CODE.get(gnan(angle), 0) + (8 if mirror else 0)

def ispoint(p, 
    # localize names:
    isinstance = isinstance, tuple = tuple, len = len,
    type = type, int = int, float = float
):
    if not isinstance(p, tuple): return False
    if len(p) != 2: return False
    return (type(p[0]) in (int, float)) and (type(p[1]) in (int, float))

def combine_points(pts, 
    # localize names:
    ispoint = ispoint, sum = sum):
    # Catching the edge case: if they passed a single unpacked point like combine_points(10, 20)
    if ispoint(pts):
        return pts

    sum_x = sum(p[0] for p in pts)
    sum_y = sum(p[1] for p in pts)
    return (sum_x, sum_y)

def average_points(pts,
    # localize names:
    ispoint = ispoint, len = len):
    # Catching the edge case: if they passed a single unpacked point like combine_points(10, 20)
    if ispoint(pts):
        return pts

    sum_x = sum(p[0] for p in pts) / len(pts)
    sum_y = sum(p[1] for p in pts) / len(pts)
    return (sum_x, sum_y)

def get_ellipse_points(center, radius):
    p1 = (center[0] - radius, center[1] - radius)
    p2 = (center[0] + radius, center[1] + radius)
    return p1, p2

def combine_dnss(dnss,
    # localize names
    isinstance = isinstance, int = int, max = max
):
    if not dnss: return 0
    if isinstance(dnss, int):
        return dnss
    return max(dnss)

def iscoordtup(x, 
    # localize names:
    isinstance = isinstance, tuple = tuple, int = int, float = float,
    bool = bool, all = all, type = type 
):
# Returns True if x is a tuple containing only int or float types.
# Returns False otherwise (including empty tuples).
    return (
        isinstance(x, tuple)
        and bool(x)  # Ensures the tuple is not empty
        and all(type(item) in (int, float) for item in x)
    )

def iscoordcol(x, 
    # localize names:
    isinstance = isinstance, tuple = tuple, list = list, bool = bool, 
    all = all, type = type, int = int, float = float):
# Returns True if x is a tuple or list containing only int or float types.
# Returns False otherwise (including empty tuples).
    return (
        isinstance(x, (tuple, list))
        and bool(x)  # Ensures the tuple is not empty
        and all(type(item) in (int, float) for item in x)
    )

def to_svg_string_opt(path_list,
    # localize names:
    rtup = rtup, len = len, SafeList = SafeList, rcomp = rcomp, 
    str = str, DYN_PRECISION = DYN_PRECISION, rpub = rpub
):

    # Transforms a path command list to an SVG string
    if len(path_list) == 0: return ''
    m1 = path_list[0][1][0], path_list[0][1][1]
    m1r = rtup(m1, DYN_PRECISION)
    p1 = 0.0, 0.0
    p2 = 0.0, 0.0
    subpath_start = m1  # Track subpath closure origin
    er = m1r[0] - m1[0], m1r[1] - m1[1] # Rounding compensation

    segments = []
    strcmd = []
    cmdi = 0
    prevcmd = None
    while cmdi < len(path_list):
        cmd = path_list[cmdi][0]
        coords = SafeList(path_list[cmdi][1])
        curcmd = cmd.lower()
        strcmd = []

        if coords:
            p2 = coords.get(len(coords) - 2, p2[0]), coords.get(len(coords) - 1, p2[1])
            if curcmd == 'm':
                subpath_start = p2  # Store origin of new subpath

        pp = p1
        if coords:
            coordi = 0
            while coordi < len(coords):

                p = coords.get(coordi, 0), coords.get(coordi + 1, 0)
                if (rcomp(p[0]) == rcomp(pp[0])) and (rcomp(p[1]) == rcomp(pp[1])) and (curcmd == 'l'):
                    coordi += 2
                    continue
                if (rcomp(p[0]) == rcomp(pp[0])) and (curcmd == 'l'):
                    curcmd = 'v'
                if (rcomp(p[1]) == rcomp(pp[1])) and (curcmd == 'l'):
                    curcmd = 'h'
                if curcmd not in('v', 'h'):
                    strcmd.append(str(rpub((p[0] -  p1[0]) + er[0])))
                    strcmd.append(' ')
                    strcmd.append(str(rpub((p[1] -  p1[1]) + er[1])))
                    strcmd.append(' ')
                elif curcmd == 'h':
                    strcmd.append(str(rpub((p[0] -  pp[0]))))
                    strcmd.append(' ')
                elif curcmd == 'v':
                    strcmd.append(str(rpub((p[1] -  pp[1]))))
                    strcmd.append(' ')
                coordi += 2
                pp = p
            if prevcmd != curcmd:
                strcmd.insert(0, ' ')
                strcmd.insert(0, curcmd)
        else:
            # Handle 'Z' or other commands without parameters
            strcmd.append(curcmd)
            strcmd.append(' ')
            p2 = subpath_start

        p1 = p2
        cmdi += 1
        segments.extend(strcmd)
        prevcmd = curcmd
    del segments[-1]
    segments[0] = segments[0].upper()
    return "".join(segments)

def to_svg_string_not_opt(path_list,
    # localize names:
    rpub = rpub
):
# Transforms a path command list to an SVG string
    segments = []
    for cmd, coords in path_list:
        # If coords exists and isn't empty, join them; otherwise, empty string
        if coords:
            coords_str = " ".join(str(rpub(c)) for c in coords)
            segments.append(f"{cmd} {coords_str}")
        else:
            # Handle 'Z' or other commands without parameters
            segments.append(cmd)

    # Use .strip() or just join to ensure no accidental double spaces
    return " ".join(segments).strip()

def qorvo(fs, 
    # localize names:
    at = apply_transform, Q = Qorvo
):
    if rcomp(fs) != 1:
        p = at(Qorvo, [(SCALE, fs, fs)])
        return p
    else:
        return Q

def to_svg_string(path_list, 
    # localize names:
    OPTIMIZE_PATHS = OPTIMIZE_PATHS, 
    tsso = to_svg_string_opt,
    tssno = to_svg_string_not_opt
):
    if OPTIMIZE_PATHS:
        return tsso(path_list)
    else:
        return tssno(path_list)

def line_(x1, y1, x2, y2):
    return [
        ("M", (x1, y1)),
        ("L", (x2, y2))
    ]

def line(p1, p2,
    # localize names:
    line_ = line_
):
    return line_(p1[0], p1[1], p2[0], p2[1])

def triangle_(x1, y1, x2, y2, x3, y3):
    return [
        ("M", (x1, y1)),
        ("L", (x2, y2)),
        ("L", (x3, y3)),
        ("Z", ())
    ]

def triangle(p1, p2, p3, 
    # localize names:
    triangle_ = triangle_
):
    return triangle_(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])

def rect_(x1, y1, x2, y2):
    # Calculate intermediate corners
    corner2 = (x2, y1)
    corner4 = (x1, y2)

    return [
        ("M", (x1, y1)),
        ("L", corner2),
        ("L", (x2, y2)),
        ("L", corner4),
        ("Z", ())
    ]

def rect(p1, p2,
    # localize names:
    rect_ = rect_
):
    return rect_(p1[0], p1[1], p2[0], p2[1])
    
def pin_(x, y, scale):
    r = rect_(-12.5 * scale + x, -12.5 * scale + y, 12.5 * scale + x, 12.5 * scale + y)
    x1 = line_(-8 * scale + x, -8 * scale + y, 8 * scale + x, 8 * scale + y)
    x2 = line_(8 * scale + x, -8 * scale + y, -8 * scale + x, 8 * scale + y)
    r.extend(x1)
    r.extend(x2)
    return r

def pin(p, scale,
    # localize names:
    pin_ = pin_
):
    return pin_(p[0], p[1], scale)

def netarrow_(x, y, scale):
    return [("M", (-23*scale + x,            y)), 
            ("L", ( 23*scale + x,            y)), 
            ("L", (            x, 80*scale + y)), 
            ("Z", ())]
    
def netarrow(p, scale,
    # localize names:
    netarrow_ = netarrow_
):
    return netarrow_(p[0], p[1], scale)
    
def gnd_(x, y, scale):
    return [("M", (-80*scale + x,            y)), 
            ("L", ( 80*scale + x,            y)), 
            ("L", (            x, 80*scale + y)), 
            ("Z", ())]

def gnd(p, scale, 
    # localize names:
    gnd_ = gnd_
):
    return gnd_(p[0], p[1], scale)

def earth_(x, y, scale):
    return [
        ("M", (-20*scale + x, 60*scale + y)), ("L", (20*scale + x, 60*scale + y)),
        ("M", (-40*scale + x, 30*scale + y)), ("L", (40*scale + x, 30*scale + y)),
        ("M", (-80*scale + x,            y)), ("L", (80*scale + x,            y))
    ]
    
def earth(p, scale, 
    # localize names:
    earth_ = earth_
):
    return earth_(p[0], p[1], scale)

def chassis_(x, y, scale):
    return [
        ("M", ( 50*scale + x, y)), ("L",  ( 20*scale  + x, 50*scale + y)),
        ("M", (            x, y)), ("L",  (-30*scale  + x, 50*scale + y)),
        ("M", (-50*scale + x, y)), ("L",  (-80*scale  + x, 50*scale + y)),
        ("M", (-80*scale + x, y)), ("L",  ( 80*scale  + x,            y))
    ]
    
def chassis(p, scale,
    # localize names:
    chassis_ = chassis_
):
    return chassis_(p[0], p[1], scale)
    
_sin = lambda t, f=sin: -f(t) # ellipse function

def ellipse_(x1, y1, x2, y2, samples=5, 
    # localize names:
    fx=cos, fy=sin, dx=_sin, dy=cos, plt = plot_function, PI2 = PI2,
    min = min, max = max, abs = abs, len = len):
# Generates an ellipse as a list of path commands.

    # Use plot_function to map a unit circle onto the bounding box.
    # We use t to drive cos/sin, and the plot_function parameters
    # (width, height, left, bottom) to place it correctly in the SVG space.
    d = plt(
        fx, fy, samples, 0, PI2, abs(x2 - x1), abs(y2 - y1), -1, 1, -1, 1, 
        min(x1, x2), max(y1, y2), dx, dy, 0, 0, None 
    )

    # Snap the last point to the first to fix numerical drift from 'ds'
    if d and len(d) > 1:
        d[-1] = (d[-1][0], d[-1][1][:4] + d[0][1])
        d.append(("Z", ()))

    return d

def ellipse(p1, p2, samples=5,
    # localize names:
    ellipse_ = ellipse_
):
    return ellipse_(p1[0], p1[1], p2[0], p2[1], samples)

# coil functions
f_coil = lambda t, p=0.0, k=0.0, f=cos: p*t + k*f(t) # growth + bob
d_coil = lambda t, p=0.0, k=0.0, f=sin: p - k*f(t) # derivative of f_coil

def coil_(x1, y1, x2, y2, 
    # localize names:
    f = f_coil, d = d_coil, plt = plot_function, sd = sort_duke,
    fl = floor, PI2 = PI2, pi = pi, cos = cos, sin = sin,
    abs = abs, min = min, max = max):
# Draws a spring seen from 30 degrees in parallel projection
# inside the bounding box defined by (x1, y1) and (x2, y2).
# Auto-rotates if height > width.
# Auto-mirrors if coordinates are reversed.

    # 1. Declare constants
    w, h = abs(x2 - x1), abs(y2 - y1) # dimensions
    H, W = sd(w, h) # sorted dimensions
    ox, oy = min(x1, x2), max(y1, y2) # positions
    m = -1 if ((x2 < x1) != (y2 < y1)) else 1 # mirror

    # Calculate number of cycles based on aspect ratio
    # Cycles are always an integer bigger than zero plus a half
    c = max(0.5 + fl((1.5 * (W / H)) - 1), 1.5) # cycles
    T = c * PI2 # time domain

    # Geometry for 30 degrees parallel projection:
    # Radius is half of the height
    # Bob distance is the radius times the sine of 30deg
    k = H * 0.25 # bob distance
    p = (W - (2.0 * k)) / T # period
    # half cycle offset = period*half - bob*cos(2*pi*half)
    o = p*pi + k # half cycle offset

    # 2. Push parameters
    f.__defaults__ = p, k, cos 
    d.__defaults__ = p, k, sin

    # 3. Pass constants and functions to plot_function in accordance with orientation
    if h >= w: # vertical
        return plt(sin, f, c*4, 0, T, w, h, -m, m, 0, W, ox, oy-o, cos, d, 0, -pi, None)
    else: # horizontal
        return plt(f, sin, c*4, 0, T, w, h, 0, W, -m, m, ox+o, oy, d, cos, -pi, 0, None)
    
def coil(p1, p2,
    # localize names:
    coil_ = coil_
):
    return coil_(p1[0], p1[1], p2[0], p2[1])

# zigzag functions
v_zigzag = lambda g, o, cm="L", oxa=0.0, oy=0.0: (f"{cm}", ((oxa + o), (oy + g))) # Oscillation is X, Growth is Y
h_zigzag = lambda g, o, cm="L", oya=0.0, ox=0.0: (f"{cm}", ((ox + g), (oya - o))) # Growth is X, Oscillation is Y

def zigzag_(x1, y1, x2, y2, 
    # localize names:
    v = v_zigzag, n = h_zigzag, fl = floor, abs = abs, min = min,
    range = range, max = max):
# Generates a triangle wave path using LineTo commands.
# Fits perfectly between (x1, y1) and (x2, y2).

    # 1. Declare constants
    w, h = abs(x2 - x1), abs(y2 - y1) # dimensions
    ox, oy = min(x1, x2), min(y1, y2) # position
    l = max(h, w) # length
    a = min(w, h) * 0.5 # amplitude
    c = fl((0.75) * (l / (a * 2.0)) + 1.0) # cycles
    p = l / c # period
    q1, q3 = p * 0.25, p * 0.75 # quarters

    d = [] # path array
 
    # 2. Push parameters
    if (h >= w): # vertical
        n = v
        n.__defaults__ = "L", ox + a, oy
    else:
        n.__defaults__ = "L", oy + a, ox

    # 3. Generate the points
    # Growth domain is 0 to l
    # Oscillation domain is -a to a
    # Calculate the start point
    d.append(n(0.0, 0.0, "M")) # start at middle
    for i in range(c): # Calculate mid-points
        b = i * p # current cycle
        # Calculate first quarter of the cycle
        d.append(n(b + q1,  a)) # up to peak
        # Skip second quarter as there is no change of derivative
        # Calculate third quarter of the cycle
        d.append(n(b + q3, -a)) # down to valley
    # Calculate end point
    d.append(n(l, 0.0)) # back to middle

    return d

def zigzag(p1, p2,
    # localize names:
    zigzag_ = zigzag_
):
    return zigzag_(p1[0], p1[1], p2[0], p2[1])

def arc_(x1, y1, x2, y2, x3, y3, x4, y4, 
    # localize names:
    fx=cos, fy=sin, dx=_sin, dy=cos, plt = plot_function,
    at = atan2, PI2 = PI2, IP = IP, abs = abs, round = round,
):
# Draws an elliptical arc.
# p1 and p2 define the bounding rectangle.
# p3 and p4 define the radial lines determining the arc endpoints.

    # 1. Declare constants
    # Center of the rectangle / ellipse
    cx = (x1 + x2) * 0.5
    cy = (y1 + y2) * 0.5

    # Semi-axes
    rx = abs(x2 - x1) * 0.5
    ry = abs(y2 - y1) * 0.5

    aspect = rx / ry

    # Angles of the lines p3 -> center and p4 -> center.
    # Note that plot_function's coordinate system has Y inverted,
    # so use (cy - y) rather than (y - cy).
    t_start = at((cy - y3)*aspect, (x3 - cx))
    t_end   = at((cy - y4)*aspect, (x4 - cx))

    # Make the arc proceed counter-clockwise.
    if t_end < t_start:
        t_end += PI2
    
    # 2. Call plot_function
    return plt(
        fx, fy, round(abs(t_end - t_start) * 1.5 * IP) + 2, t_start, t_end, 
        rx, ry, 0, 1, 0, 1, cx, cy, dx, dy, 0, 0, None
    )

def arc(p1, p2, p3, p4,
    # localize names:
    arc_ = arc_
):
    return arc_(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1])

# arc3p functions
# Formulas template: Center + (Lerp Radius) * sin(Lerp Angle)
fx_arc3p = lambda t, x3=0.0, r1=0.0, r=0.0, a1=0.0, a=0.0, f=cos:  x3 + (r1 + t * r) * f(a1 + t * a)
fy_arc3p = lambda t, y3=0.0, r1=0.0, r=0.0, a1=0.0, a=0.0, f=sin: -y3 + (r1 + t * r) * f(a1 + t * a)

# Exact analytical derivatives
dx_arc3p = lambda t, r1=0.0, r=0.0, a1=0.0, a=0.0, f1=cos, f2=sin: r * f1(a1 + t * a) - (r1 + t * r) * a * f2(a1 + t * a)
dy_arc3p = lambda t, r1=0.0, r=0.0, a1=0.0, a=0.0, f1=cos, f2=sin: r * f2(a1 + t * a) + (r1 + t * r) * a * f1(a1 + t * a)

def arc3p_(x1, y1, x2, y2, x3, y3, 
    # localize names:
    fx=fx_arc3p, fy=fy_arc3p, dx=dx_arc3p, dy=dy_arc3p, plt = plot_function,
    hp = hypot, at = atan2, PI2 = PI2, IP = IP, round = round, abs = abs,
    cos = cos, sin = sin):
# Draws an irregular radius arc that starts at p1, ends at
# p2 and bends around p3, using linear interpolation

    # 1. Declare constants
    # Relative vectors from center p3:
    d1x, d1y, d2x, d2y = (x1 - x3), (y3 - y1), (x2 - x3), (y3 - y2)

    r1, r2 = hp(d1x, d1y), hp(d2x, d2y) # radii
    a1, a2 = at(d1y, d1x), at(d2y, d2x) # angles

    if a2 < a1: # CCW wrap-around logic
        a2 += PI2

    r, a = (r2 - r1), (a2 - a1) # radius, angle
    
    # 2. Push parameters
    fx.__defaults__ = x3, r1, r, a1, a, cos
    fy.__defaults__ = y3, r1, r, a1, a, sin
    dx.__defaults__ = dy.__defaults__ = r1, r, a1, a, cos, sin
    
    # 3. Call plot_function
    return plt(
        fx, fy, round(abs(a) * 1.5 * IP) + 2, 0, 1, 1, 1, 
        0, 1, 0, 1, 0, 0, dx, dy, 0, 0, None 
    )

def arc3p(p1, p2, p3,
    # localize names:
    arc3p_ = arc3p_
):
    return arc3p_(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])

def tap(p1, p2, scale):
# Draws the QSpice TAP as a single elongated hexagon.
# 1. Sorts p1 and p2.
# 2. Calculates the distance (stretch).
# 3. Offsets the bottom points of the normalized path by that distance.
# 4. Rotates the entire shape by the angle between p1 and p2.
# 5. Translates the shape to the position of p1.

    # 1. Sort points (Top-to-Bottom, then Left-to-Right)
    pa, pb = sort_line(p1, p2)

    # 2. Calculate distance and angle between the sorted parameters
    dx = pb[0] - pa[0]
    dy = pb[1] - pa[1]
    dist = hypot(dx, dy)
    # Since they are sorted, this angle will naturally be between -90 and +90
    angle = atan2(dy, dx)

    # 3. Define the normalized points from the path
    # d="M -1.3,2.5 L 0.0,0.0 L 1.3,2.5 L 1.3,-2.5 L 0.0,0.0 L -1.3,-2.5 Z"
    # We multiply by scale immediately.
    s = scale
    pts = [
        [-1.3 * s,  2.5 * s], # pts1
        [ 0.0    ,  0.0    ], # pts2 (Zero 1)
        [ 1.3 * s,  2.5 * s], # pts3
        [ 1.3 * s, -2.5 * s], # pts4
        [ 0.0    ,  0.0    ], # pts5 (Zero 2)
        [-1.3 * s, -2.5 * s]  # pts6
    ]

    # 4. Stretch the path: Move pts4, pts5, and pts6 "down" by the distance
    # In the normalized local space, the "growth" is along the Y axis
    # because pts5 (Zero 2) needs to move away from pts2 (Zero 1).
    # We add dist from Y because pts5 starts at 0 and needs to reach +dist.
    pts[3][1] += dist
    pts[4][1] += dist
    pts[5][1] += dist

    # 5. Rotate and Translate
    # We rotate the entire stretched shape and move it to the start point (pa)
    path_data = []
    for i, (lx, ly) in enumerate(pts):
        # Rotate point (around 0,0)
        # Since the normalized growth was on Y, we swap/adjust to align with angle
        # Actually, let's treat the 'length' of the tap as the X axis for the rotation
        # To make Y-growth align with the angle, we rotate ly to the angle direction

        # rotation around origin:
        # nx = x*cos - y*sin
        # ny = x*sin + y*cos
        # Note: In SVG's coordinate system, we map the local 'Y' growth to the segment direction
        nx = ly * cos(angle) - lx * sin(angle)
        ny = ly * sin(angle) + lx * cos(angle)

        cmd = "M" if i == 0 else "L"
        path_data.append((cmd, (pa[0] + nx, pa[1] + ny)))

    path_data.append(("Z", ()))
    return path_data

def tap_(x1, y1, x2, y2, scale,
    # localize names:
    tap = tap
):
    return tap((x1, y1), (x2, y2), scale)

def gen_uuid():
# Generates a random UUID format string for KiCad elements.
    return str(uuid.uuid4())

def comp_str(s1, s2):
# returns True if strings match, regardless of case
    return s1.casefold() == s2.casefold()

def strip_bom(text):
# Removes the UTF-8 BOM if present in string form.
    _t = text.replace('"ï»¿', '"')
    if _t.startswith('ï»¿'):
        return _t[3:]
    return _t

def round_path(p, precision = (DYN_PRECISION*2)-1,
    # localize names:
    range = range, len = len, isinstance = isinstance,
    tuple = tuple, round = round 
):
    for i in range(len(p)):
        cmd, coords = p[i]

        if isinstance(coords, tuple):
            # Create a new rounded tuple or list matching the original type
            p[i] = (cmd, tuple(round(c, precision) for c in coords))

    return p

def flip(v, v1, v2):
    return v1 if v == v2 else v2 if v == v1 else v

def get_linetype_string(t, sw,
    # localize names:
    LINETYPE_MAP = LINETYPE_MAP, str = str, rpub = rpub
):
    m = LINETYPE_MAP[t]
    if m:
        st = ''
        for p in m:
            st = st + ' ' + str(rpub(p*sw))
        return f' style="stroke-dasharray:{st}; stroke-dashoffset:0"'
    return ''

def pt_to_str(p, 
    # localize names:
    round = round
):
    return f"({round(p[0])},{round(p[1])})"

def fix_qspice_encoding(s):
# QSpice files are read as cp1252, but text strings are UTF-8 with a BOM.
# This converts the cp1252 'corruption' back to proper UTF-8.

    if not s: return ""

    # If the string contains the 'ï»¿' marker (the UTF-8 BOM interpreted as cp1252)
    if "ï»¿" in s:
        try:
            # 1. Convert the cp1252 string back to raw bytes
            # 2. Strip the 3-byte BOM (0xEF 0xBB 0xBF)
            # 3. Decode the remaining bytes as utf-8
            raw_bytes = s.encode('cp1252').replace(b'\x22\xef\xbb\xbf', b'\x22')
            if raw_bytes.startswith(b'\xef\xbb\xbf'):
                return raw_bytes[3:].decode('utf-8')
            return raw_bytes.decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Fallback to simple strip if binary conversion fails
            return strip_bom(s)

    return s

def gimmick_str(s):
# Handles QSpice specific string escaping and formatting.

    if not s: return ""

    s = fix_qspice_encoding(s)
    ss = s.replace('\\\\', BACKSLASHID)
    s = ss.replace('\\n', LINEBRAKEID)

    # Note: Double quotes inside the string are NOT escaped in QSpice,
    # so we leave them as is for SVG/Inkscape to handle.
    return s

_escape_svg_table = {
    ord('&'): '&amp;',
    ord('<'): '&lt;',
    ord('>'): '&gt;',
    ord('"'): '&quot;',
    ord("'"): '&#39;',
}

def escape_svg(text, table=_escape_svg_table):
# Escape &, <, > as well as single and double quotes for SVG.
    return text.translate(table)

def denot(line):
    denotted = []
    notpos = []
    if "¬" in line:
        i = 0
        while i < len(line):
            if line[i] == "¬":
                notpos.append(len(denotted))
                try:
                    denotted.append(line[i+1])
                except:
                    pass
                i += 2
            else:
                denotted.append(line[i])
                i += 1
        line = "".join(denotted)  
    return line, notpos

def parse_str(raw_text, fs):
    clean_text = gimmick_str(dequote(raw_text))
    clean_text = clean_text.replace(BACKSLASHID, '\\')
    lines = clean_text.split(LINEBRAKEID)
    _out = []
    for i, line in enumerate(lines):
        ly = i*1.2*fs
        notpos = []
        line, notpos = denot(line)       
        # Basic XML escaping for SVG safety
        _out.append([line, escape_svg(line), 0, ly, notpos])
    return _out

def parse_single_line(raw_text):
    clean_text = gimmick_str(dequote(raw_text))
    clean_text = clean_text.replace(BACKSLASHID, '\\')
    clean_text = clean_text.replace(LINEBRAKEID, '\\n')
    clean_text, notpos = denot(clean_text)
    # Basic XML escaping for SVG safety
    _out = [clean_text, escape_svg(clean_text), 0, 0, notpos]
    return _out

def get_text_width(text, font_family, font_size):
    # Sum the normalized widths and multiply by the actual font size
    # .get(ord(c), 0.6) provides a safe fallback for unknown characters
    if (font_family not in Fonts): font_family = 'Tahoma'
    total_width = sum(Fonts[font_family].get(ord(c), 0.6) for c in text)

    return total_width * font_size

def get_text_corners(text, font_family, font_size, anchor, baseline):
    w = get_text_width(text, font_family, font_size)
    sx = -1 if anchor == END else 0 if anchor == START else -0.5
    sy = 1 if baseline == HANGING else -0.8 if baseline == ALPHABETIC else -0.5
    min_x = w * sx
    min_y = font_size * sy
    max_x = min_x + w
    max_y = min_y + font_size
    return min_x, min_y, max_x, max_y

def generate_text_rect(text, font_family, font_size, anchor, baseline, push_x, push_y, _tr = None):
    _x, _y, x, y  = get_text_corners(text, font_family, font_size, anchor, baseline)
    _x += push_x
    _y += push_y
    x += push_x
    y += push_y
    p = rect_(_x, _y, x, y)
    bk = apply_transform(p, _tr) if _tr else p
    return bk

def get_text_bounds(text, font_family, font_size, anchor, baseline, b, push_x, push_y, svg_paths, mark, counter, _tr = None, _id = None):
    p = generate_text_rect(text, font_family, font_size, anchor, baseline, push_x, push_y, _tr)
    return get_path_bounds(p, b, svg_paths, mark, counter, _id = _id)
    
def bound_to_rect(b, 
    # localize names:
    rect_ = rect_
):
    return rect_(b[MIN_X], b[MIN_Y], b[MAX_X], b[MAX_Y])

def get_text_push_y(_i, fs, baseline, font):
# Calculate the vertical location that the SVG renderer takes from the font's metrics.
    tlg = Fonts[font][TYPO_LINE_GAP]
    ch = Fonts[font][CAPITAL_HEIGHT]
    return (fs * (ch + tlg) if (baseline == HANGING)
    else fs*(ch - (1.2 * _i)) if (baseline == ALPHABETIC)
    else fs*((ch + tlg) - (0.6 * _i)))

def get_char_span(text, i, anchor, baseline, font_family, font_size, ox):
    w = get_text_width(text, font_family, font_size)
    offset = 0 if (anchor == START) else (w / 2) if (anchor == MIDDLE) else w
    x1 = (sum(Fonts[font_family].get(ord(text[j]), 0.6) for j in range(i))*font_size) - offset + ox
    x2 = x1 + (Fonts[font_family].get(ord(text[i]), 0.6)*font_size)
    return x1, x2
    
def get_char_overline(text, i, anchor, baseline, font_family, font_size, ox, oy):
    x1, x2 = get_char_span(text, i, anchor, baseline, font_family, font_size, ox)
    y = -Fonts[font_family][ASCENT]*NOT_ASCENT_COEFFICIENT*font_size + oy 
    return line_(x1, y, x2, y)

def hex_to_int(hex_str, 
    # localize names:
    NONE = NONE, isinstance = isinstance, int = int
):
    if hex_str in (None, NONE, -1): return -1
    if isinstance(hex_str, int): return hex_str
    return int(hex_str, 16)

def compose_color(r, g, b):
    return (((r & 0xff) << 16)) + (((g & 0xff) << 8)) + (b & 0xff)

def decompose_color(c):
    return ((c >> 16) & 0xff),  ((c >> 8) & 0xff),  (c & 0xff)

def get_color_lum(c,
    # localize names:
    round = round, decompose_color = decompose_color
):
    r, g, b = decompose_color(c)
    return round(0.299*r + 0.587*g + 0.114*b)

def to_grayscale(c,
    # localize names:
    round = round, compose_color = compose_color, max = max,
    get_color_lum = get_color_lum
):
    l = get_color_lum(c)
    return compose_color(l, l, l)
    s = round(max(l-70, 0))
    return compose_color(s, s, s)

def to_mono(c, 
    # localize names:
    get_color_lum = get_color_lum
):
    if get_color_lum(c) > 127:
        return 0xffffff
    else:
        return 0

def pub_color(q_color,
    # localize names:
    hex_to_int = hex_to_int, to_grayscale = to_grayscale, 
    to_mono = to_mono, NONE = NONE, GRAY_SCALE = GRAY_SCALE, MONO = MONO
):
    # Extract RGB (QSpice stores as BGR in the lower 3 bytes)
    if q_color is None: return NONE
    q_color = hex_to_int(q_color)
    if q_color == -1: return NONE
    try:
        if GRAY_SCALE and (not MONO):
            q_color = to_grayscale(q_color)
        elif MONO:
            q_color = to_mono(q_color)
        blue = (q_color >> 16) & 0xFF
        green = (q_color >> 8) & 0xFF
        red = q_color & 0xFF
        return f"#{red:02x}{green:02x}{blue:02x}"
    except (ValueError, TypeError):
        return NONE

def get_color(q_color_, do_not_stuff=0, isfill = False, hblock = 0, issymbol = False, 
    # localize names:
    hex_to_int = hex_to_int, int_to_hex = int_to_hex, DONOTSTUFF_COLOR = DONOTSTUFF_COLOR,
    HIERARCHICAL_BLOCK_COLOR = HIERARCHICAL_BLOCK_COLOR, 
    HIERARCHICAL_BLOCK_STROKE_COLOR = HIERARCHICAL_BLOCK_STROKE_COLOR,
    SYMBOL_ANNOTATION_STROKE_COLOR = SYMBOL_ANNOTATION_STROKE_COLOR,
    BACKGROUND_COLOR = BACKGROUND_COLOR, 
    SYMBOL_ANNOTATION_FILL_COLOR = SYMBOL_ANNOTATION_FILL_COLOR, 
    ANNOTATION_STROKE_COLOR = ANNOTATION_STROKE_COLOR,
    SOLID_ANNOTATION_FILL_COLOR = SOLID_ANNOTATION_FILL_COLOR
):
# Translates QSpice color integers to SVG colors.
    q_color = hex_to_int(q_color_)
    q_color_ = int_to_hex(q_color_)
    if q_color < 0: return -1
    if do_not_stuff > 0:
        return -1 if isfill else DONOTSTUFF_COLOR
    if hblock > 0:
        return HIERARCHICAL_BLOCK_COLOR if isfill else HIERARCHICAL_BLOCK_STROKE_COLOR
    if (q_color_.startswith("0x1") and (q_color > 0xFFFFFF)):
        return -1 if isfill else SYMBOL_ANNOTATION_STROKE_COLOR if issymbol else ANNOTATION_STROKE_COLOR # no fill
    if (q_color_.startswith("0x2") and (q_color > 0xFFFFFF)):
        return BACKGROUND_COLOR
    if (q_color_.startswith("0x3") and (q_color > 0xFFFFFF)):
        return SYMBOL_ANNOTATION_STROKE_COLOR if issymbol else ANNOTATION_STROKE_COLOR
    if (q_color_.startswith("0x4") and (q_color > 0xFFFFFF)):
        return (SYMBOL_ANNOTATION_FILL_COLOR if issymbol else SOLID_ANNOTATION_FILL_COLOR) if isfill else (SYMBOL_ANNOTATION_STROKE_COLOR if issymbol else ANNOTATION_STROKE_COLOR) 
    q_color = q_color & 0xffffff
    return q_color

def get_absolute_pos(local_pt, parent_p1, rotation_field):
    if (parent_p1 in (None, [()], (0, 0), [(0, 0)])) and (rotation_field in (None, 0, [0])): return local_pt[0], local_pt[1]

    p_p1 = [parent_p1] if ispoint(parent_p1) else parent_p1

    x, y = local_pt[0], local_pt[1]
    rot_code = rotation_field if isinstance(rotation_field, list) else [rotation_field]

    r = len(rot_code) - 1
    p = len(p_p1) - 1

    while (p >= 0) or (r >= 0):
        if (rot_code[r] if r >= 0 else 0) >= 8:
            mirror = True
            rc = rot_code[r] - 8
        else:
            rc = rot_code[r] if r >= 0 else 0
            mirror = False

        # 1. Scale diagonal (Must happen first)
        if rc % 2 != 0:
            x *= SQRT2
            y *= SQRT2

        # 2. Rotate (CW rotation to match SVG rotate property)
        angle = radians(ROTATION_MAP.get(rc, 0))
        # In Y-up space, CW rotation is:
        # nx = x*cos + y*sin
        # ny = -x*sin + y*cos
        nx = x * cos(angle) + y * sin(angle)
        ny = -x * sin(angle) + y * cos(angle)

        # 3. Mirror (Applied to the rotated coordinates)
        if mirror:
            nx = -nx

        x, y = (nx + p_p1[p][0], ny + p_p1[p][1]) if p >= 0 else (nx, ny)
        p -= 1; r -= 1
    # 4. Translate (Final step)
    return (x, y)

def is_connected(pos, conn_map):
    c = 0
    p = conn_map.get(pos)
    if p:
        for cp in p:
            if hypot(pos[0] - cp[0], pos[1] - cp[1]) < TOLERANCE:
                c += 1
                if (c > 1): return True
        return (c > 1)
    else:
        return False

def detect_straight_line(v):
# Where "v" is the vector
    if not v: return False
    return math.isclose(v[0], 0.0, abs_tol = 0.00001) and math.isclose(v[1], 0.0, abs_tol = 0.00001) and (v[2] == 2) # Only 2 wires connected to that point(necessary for 180deg angle)

def split_net_strings(el):
# Splits the net name into 2 and put the second part into field "Description".
# Or splits the pin name into 2 and put the second part into field "NetName".
# Should only be called if el[TYPE] is NET or PIN.

    etype = el.get(TYPE)
    _1 = NETNAME if (etype == NET) else PINNAME
    _2 = DESCRIPTION if (etype == NET) else NETNAME
    if _2 in el:
        if isinstance(el[_2], str):
            return None
    original_field = el.get(_1)
    if isinstance(original_field, str):
        el[ORIGINAL_TEXT] = original_field
    else:
        original_field = ''
    st = dequote(original_field)
    i = 0
    fp = None
    sp = None
    for char in st:
        if char == '"':
            if (fp is None): # Found first marker
                fp = i
                i += 1
                continue
            if (sp is None) and fp: # Found second marker
                sp = i
                break
        i += 1
    if not(sp) or (sp >= len(st)-1):
        el[_2] = None
        return None
    net_name = st[0:fp] if (fp >= 0) else ''
    description = st[sp+1:len(st)] if sp+1 < len(st) else None
    if description is not None:
        el[_2] = f'"{description}"'
    else:
        el[_2] = None
    el[_1] = f'"{net_name}"'

def get_matrix_str(total_matrix, 
    # localize names:
    rpub = rpub
):
# Converts a 3x3 transformation matrix into an SVG matrix string.

# total_matrix format:
# [
#     [a, c, e],
#     [b, d, f],
#     [0, 0, 1]
# ]

    # Extract coefficients:
    a, c, e = total_matrix[0]
    b, d, f = total_matrix[1]

    # SVG expects the order: a, b, c, d, e, f
    return f"matrix({rpub(a)}, {rpub(b)}, {rpub(c)}, {rpub(d)}, {rpub(e)}, {rpub(f)})"

trcmd =('translate', 'rotate', 'scale')

def get_transform_string(tr_, _m_ = None, backwards = False,
    # localize names:
    len = len, rpub = rpub, get_matrix_str = get_matrix_str,
    round_matrix = round_matrix
):
# Formats the transform string from the list given,
# Assumes it's only "translate", "rotate" and "scale" statements.
    _tr_ = tr_[::-1] if backwards else tr_
    res = ''
    if (not _m_) or (len(_tr_) < 3):
        i = 0
        while i < len(_tr_):
            res += f' {trcmd[_tr_[i][0]]}('
            k = 1
            while k < len(_tr_[i]):
                res += f'{"" if k == 1 else " "}{rpub(_tr_[i][k])}'
                k += 1
            res += ')'
            i += 1
        res = f' transform="{res.strip()}"' if res != '' else ''
        return res
    else:
        res = f' transform="{get_matrix_str(_m_)}"' if (round_matrix(_m_) != M1) else ''
        return res

def get_field_name(d, i, defs = QSPICE_DEFS, etype = None):
    eltype = d.get(TYPE) if etype is None else etype
    if i == -1:
        field = TYPE
    else:
        tp = defs.get(eltype, None)
        if tp:
            if i < len(tp):
                field = tp[i]
            else:
                field = f'{EXTRA_}{i}'
        else:
            field = f'{EXTRA_}{i}'
    return field
    
def add_qspice_value(d, v):
    if isinstance(d, QSpice):
        fn = get_field_name(d, len(d)-1)
        d[fn] = v
        return fn, v
    return None

def isbottom(d, 
    # localize names:
    isinstance = isinstance, DRAWABLEID = DRAWABLEID, 
    PARENT = PARENT, QSpice = QSpice
):
    for key in d:
        if isinstance(d[key], QSpice):
            if (DRAWABLEID not in d[key]) and (key != PARENT):
                return False
    return True

def detect_symbol_file(content):
    try:
        etype = content.get(TYPE)
        if etype == SYMBOL:
            return content
        if isinstance(etype, QSpice):
            return detect_symbol_file(etype)
        content = content.get(f'{EXTRA_}0')
        if content.get(TYPE) == SYMBOL:
            return content
    except:
        return None
    return None

def get_instance_name(d):
    el = get_instance_name_object(d)
    if el:
        n = parse_single_line(el.get(STRG, ''))[0]
        if n: return n
    dtype = get_symbol_type(d)
    el = get_symbol_object(d)
    index = el.get(INDEX, 'E') if el else d.get(INDEX, 'E')
    return f'{dtype}_{index}'

def get_component_value(d):
    el = get_component_value_object(d)
    n = ''
    if el:
        n = parse_single_line(el.get(STRG, ''))[0]
        if n: return n
    el = get_symbol_object(d)
    if not el: el = d
    sname = el.get(SYMBOLNAME)
    if isinstance(sname, str): n = parse_single_line(sname)[0]
    if n: return n
    el = get_element_by_index(el, 1, 'type:')
    if el:
        st = el.get(f'{EXTRA_}0', '')
        if isinstance(st, str): n = parse_single_line(st)[0]
        if n: return n
    return ''

def get_symbol_object(d):
    if not isinstance(d, QSpice): return None
    while d and (d.get(TYPE) not in(COMPONENT, SYMBOL)):
        d = d.get(PARENT)
    if not d:
        return None
    s = d
    if d.get(TYPE) == COMPONENT:
        s = get_element_by_index(d, 1, SYMBOL)
    if isinstance(s, QSpice) and (s.get(TYPE) == SYMBOL):
        return s
    else:
        return None

def get_component_object(d):
    if not isinstance(d, QSpice): return None
    while d and (d.get(TYPE) != COMPONENT):
        d = d.get(PARENT)
    if not d:
        return None
        
def get_schematic_object(d, init = True):
    if init:
        try:
            if d.get(TYPE) == SCHEMATIC:
                return d
            d = gp(d)
            if d.get(TYPE) == SCHEMATIC:
                return d
        except:
            return None
    try:
        for k, i in d.items():
            if (k != PARENT) and (isinstance(i, QSpice)):
                if (i.get(TYPE) == SCHEMATIC):
                    return i
        for k, i in d.items():  
            if (k != PARENT) and (isinstance(i, QSpice)):
                r = get_schematic_object(i, False)
                if r: return r
    except:
        return None
    return None

def get_symbol_drawable_by_index(d, index, otype):
    d = get_symbol_object(d)
    return get_element_by_index(d, index, otype)

def get_element_by_index(d, index, otype):
    if not isinstance(d, QSpice): return None
    i = 0
    lend = len(d)
    while i < lend:
        field = get_field_name(d, i)
        if isinstance(d.get(field), QSpice):
            if d[field].get(TYPE) == otype:
                if d[field].get(INDEX) == index:
                    return d[field]
        i += 1
    return None

def get_component_value_object(d):
    return get_symbol_drawable_by_index(d, 2, TEXT)

def get_instance_name_object(d):
    return get_symbol_drawable_by_index(d, 1, TEXT)

def get_symbol_type(d):
    if not isinstance(d, QSpice): return ''
    if (d.get(TYPE) != SYMBOL) and (d.get(SYMBOLNAME)):
        return parse_single_line(d[SYMBOLNAME])[0]
    el = get_symbol_object(d)
    n = ''
    if not el: el = d
    el = get_element_by_index(el, 1, 'type:')
    if el:
        st = el.get(f'{EXTRA_}0', '')
        if isinstance(st, str): n = parse_single_line(st)[0]
        if n: return n
    el = get_symbol_object(d)
    if not el: el = d
    if el:
        sname = el.get(SYMBOLNAME)
        if isinstance(sname, str): n = parse_single_line(sname)[0]
        if n: return n
    return ''

def get_raw_symbol_bounds(d, portion = 0, l = None, 
    # localize names:
    TYPE = TYPE, COMPONENT = COMPONENT, SYMBOL = SYMBOL,
    PARENT = PARENT, 
    P1 = P1, P2 = P2, P3 = P3,
    ispoint = ispoint, ANNOTATION_DEFS = ANNOTATION_DEFS,
    min = min, max = max, isinstance = isinstance, QSpice = QSpice,
    grsb = None
):
    if portion == 0:
        while d and (d.get(TYPE) not in(COMPONENT, SYMBOL)):
            d = d.get(PARENT)
        if not d:
            return 0, 0, 0, 0
        l = [float('inf'), float('inf'), float('-inf'), float('-inf')]
        portion = 1

    if portion == 1:
        for key in d:
            if key in (P1, P2, P3):
                p = d[key]
                if ispoint(p) and (d.get(TYPE) in ANNOTATION_DEFS):
                    l[0] = min(l[0], p[0])
                    l[1] = min(l[1], p[1])
                    l[2] = max(l[2], p[0])
                    l[3] = max(l[3], p[1])
            if isinstance(d[key], QSpice) and (key != PARENT):
                grsb(d[key], 1, l)
        return l

get_raw_symbol_bounds.__defaults__ = get_raw_symbol_bounds.__defaults__[:-1] + (get_raw_symbol_bounds,)     
     
def get_resistor_rect(d):
    r = get_symbol_drawable_by_index(d, 1, RECT)
    if r:
        try:
            x1, y1 = r[P1]
            x2, y2 = r[P2]
            return x1, y1, x2, y2
        except:
            return None
    else:
        return None

def get_rect_center(x1, y1, x2, y2):
    return (x1+x2)*0.5, (y1+y2)*0.5

def get_drawing_order(item, DRAWING_ORDER = DRAWING_ORDER,
    # localize names:
    isinstance = isinstance, len = len, QSpice = QSpice,
    TYPE = TYPE,  tuple = tuple
):
    if isinstance(item, tuple):
        i = 0
        while (i < len(item)) and (not isinstance(item[i], QSpice)):
            i += 1
        if i >= len(item):
            return -1
        item = item[i]
    if not isinstance(item, QSpice): return -1
    etype = item.get(TYPE)
    if etype in DRAWING_ORDER:
        o = DRAWING_ORDER.index(etype)
    else:
        o = -1
    return o
    
def list_in_drawing_order(qspice, order, exclude_drawables = True, 
    # localize names:
    PARENT = PARENT, SVG_SYMBOLS = SVG_SYMBOLS, isinstance = isinstance,
    DRAWABLEID = DRAWABLEID, QSpice = QSpice, gdo = get_drawing_order):
    # Filter valid QSpice child keys
    its = [(k, v) for k, v in qspice.items() if (k != PARENT) and (k != SVG_SYMBOLS) and isinstance(v, QSpice) and (not((DRAWABLE in k) and exclude_drawables))]
    # Sort keys by evaluating the drawing order of the underlying QSpice object
    its.sort(key=lambda i: gdo(i[1], order))
    return its
    
def process_element(d, f_dict, aux, depth = 0, k = None, parent = None):
    count = 0
    eltype = d.get(TYPE)
    if eltype in f_dict:
        count += f_dict[eltype](d, f_dict, aux, depth, k, parent)
    elif k in f_dict:
        count += f_dict[k](d, f_dict, aux, depth, k, parent)
    elif 'dict_fb' in f_dict: # Fallback function
        count += f_dict['dict_fb'](d, f_dict, aux, depth, k, parent)
    return count

def traverse(d, f_dict, aux, depth = 0):
    count = 0
    for i in range(len(d)+1):
        key = get_field_name(d, i-1)
        if key not in d:
            break
        if isinstance(d[key], QSpice):
            count += process_element(d[key], f_dict, aux, depth+1, key, d)
        elif key in f_dict: # Fallback function
            count += f_dict[key](d[key], f_dict, aux, depth+1, key, d)
        elif 'value_fb' in f_dict:
            count += f_dict['value_fb'](d[key], f_dict, aux, depth+1, key, d)

    return count

def traverse_numeric(d, f_dict, aux, depth = 0, hard = False):
    count = 0
    if not isinstance(d, QSpice):
        return 0
    for key in list(d.keys()):
        if (key != PARENT) or (hard):
            if isinstance(d[key], QSpice):
                count += process_element(d[key], f_dict, aux, depth+1, key, d)
            elif key in f_dict: # Fallback function
                count += f_dict[key](d[key], f_dict, aux, depth+1, key, d)
            elif 'value_fb' in f_dict: # Fallback function
                count += f_dict['value_fb'](d[key], f_dict, aux, depth+1, key, d)
    return count
    
def r_traverse(d, f_dict, aux, depth = 0):
    count = 0
    for i in range(len(d), -1, -1):
        key = get_field_name(d, i-1)
        if key not in d:
            continue
        if isinstance(d[key], QSpice):
            count += process_element(d[key], f_dict, aux, depth+1, key, d)
        elif key in f_dict: # Fallback function
            count += f_dict[key](d[key], f_dict, aux, depth+1, key, d)
        elif 'value_fb' in f_dict:
            count += f_dict['value_fb'](d[key], f_dict, aux, depth+1, key, d)

    return count

def r_traverse_numeric(d, f_dict, aux, depth = 0, hard = False):
    count = 0
    if not isinstance(d, QSpice):
        return 0
    for key in reversed(list(d.keys())):
        if (key != PARENT) or (hard):
            if isinstance(d[key], QSpice):
                count += process_element(d[key], f_dict, aux, depth+1, key, d)
            elif key in f_dict: # Fallback function
                count += f_dict[key](d[key], f_dict, aux, depth+1, key, d)
            elif 'value_fb' in f_dict: # Fallback function
                count += f_dict['value_fb'](d[key], f_dict, aux, depth+1, key, d)
    return count    

def gp(d,
    # localize names:
    PARENT = PARENT
):
# Gets first ancestral of the element
    while True:
        p = d.get(PARENT)
        if p is not None:
            d = p
        else:
            return d

def print_qspice(el, forceshow = False):
    if (not forceshow):
        if (not echo):
            return None
    count = 0
    out = []

    def _value(d, f_dict, aux, depth, k, parent):
        nonlocal count, out

        if count > 0:
            out.append(f'{k}: </{d}\\>')
            out.append(', ')
        else:
            out.append(f'\n{"  "*(depth-1)}{k}: </{d}\\>')
            out.append(', ')
        count += 1

        return 0

    def _dict(d, f_dict, aux, depth, k, parent):
        nonlocal count, out

        if count > 0:
            out.append(f'{k}: {"</{"}')
            count = 0
        else:
            out.append(f'\n{"  "*(depth-1)}{k}: {"</{"}')
        if k != PARENT:
            count = 0
            traverse_numeric(d, f_dict, None, depth, hard = True)
            if out:
                if out[-1] == ', ': del out[-1]
            out.append('}\\>')
            out.append(', ')
            count = 0
        else:
            out.append('...}\\>')
            out.append(', ')
            count += 1

        return 0

    f_dict = {'value_fb': _value, 'dict_fb': _dict}
    traverse_numeric(el, f_dict, None, hard = True)
    if out:
        if out[-1] == ', ': del out[-1]
    out_ = "".join(out)
    print(out_)

def print_qspice_with_filter(el, dict_filter = None, value_filter = None, forceshow = False):
# Filters should be lists of strings.
# Matching deep dictionaries will show with their parents, even if
# the parents don't match the filter.
# QSpice instances match by key or "Type" field.
# Values only show if they are inside a matching QSpice instance.

    if (not forceshow):
        if (not echo):
            return None
    count = 0
    fout = []

    def _value(d, f_dict, aux, depth, k, parent):
        nonlocal count
        ran = False
        run = not value_filter
        if not run:
            run = k in value_filter
        if run and (aux.get('rundict', True)):
            if count > 0:
                aux['out'].append(f'{k}: </{d}\\>')
                aux['out'].append(', ')
            else:
                aux['out'].append(f'\n{"  "*(depth-1)}{k}: </{d}\\>')
                aux['out'].append(', ')
            count += 1
            ran = True
        return 1 if ran else 0

    def _dict(d, f_dict, aux, depth, k, parent):
        nonlocal count
        out = []
        rundict = not dict_filter
        if not rundict:
            if isinstance(d, QSpice):
                etype = d.get(TYPE)
            else:
                etype = None
            rundict = (k in dict_filter) or (etype in dict_filter)

        lc = 0
        if count > 0:
            out.append(f'{k}: {"</{"}')
            count = 0
        else:
            out.append(f'\n{"  "*(depth-1)}{k}: {"</{"}')
        if k != PARENT:
            count = 0
            lc = traverse_numeric(d, f_dict, {'rundict': rundict, 'out': out}, depth, hard = True)
            if out:
                if out[-1] == ', ': del out[-1]
            out.append('}\\>')
            out.append(', ')
            count = 0
        else:
            out.append('...}\\>')
            out.append(', ')
            count += 1
            if dict_filter:
                if PARENT in dict_filter:
                    lc += 1
            else:
                lc += 1
        if lc > 0:
            aux['out'].extend(out)

        return lc

    f_dict = {'value_fb': _value, 'dict_fb': _dict}
    traverse_numeric(el, f_dict, {'rundict': True, 'out': fout}, hard = True)
    if fout:
        if fout[-1] == ', ': del fout[-1]
    out_ = "".join(fout)
    print(out_)

def get_viewbox_string(b, padding=10):
    # 1. Expand bounds for stroke width + extra margin
    vx = b[MIN_X] - padding
    vy = b[MIN_Y] - padding
    vw = (b[MAX_X] - b[MIN_X]) + (padding * 2)
    vh = (b[MAX_Y] - b[MIN_Y]) + (padding * 2)

    # 2. Round to clean precision
    return vx, vy, vw, vh, f'viewBox="{rpub(vx)} {rpub(vy)} {rpub(vw)} {rpub(vh)}"'

def has_jumper(dns, n_pins):
    s = dns % 4
    return (s in (2, 3)) and (n_pins == 2)

def get_component_pins(qspice, portion = 0, o = None):
    if portion == 0:
        if not isinstance(qspice, QSpice):
            return []
        etype = qspice.get(TYPE)
        if etype != COMPONENT:
            qspice = get_component_object(qspice)
        etype = qspice.get(TYPE)
        if etype != COMPONENT:
            return []
        else:
            return get_component_pins(qspice, 1)
    if portion == 1:
        if o is None: o = []
        for k, v in qspice.items():
            if isinstance(v, QSpice) and (k != PARENT):
                o.extend(get_component_pins(v, 1))
                etype = v.get(TYPE)
                if etype == PIN:
                    o.append(v)
        return o

def get_jumper(qspice):
    if not isinstance(qspice, QSpice):
        return None
    etype = qspice.get(TYPE)
    if etype != COMPONENT:
        qspice = get_component_object(qspice)
    etype = qspice.get(TYPE)
    if etype != COMPONENT:
        return None
    else:
        dns = qspice.get(DONOTSTUFF)
        if dns > 1:
            cp = get_component_pins(qspice, 1)
            if has_jumper(dns, len(cp)):
                p1, p2 = cp[0].get(P1), cp[1].get(P1)
                return sort_line(p1, p2)

def detect_wire_end_points(el, conn_map, wire_endpoints):
    p_p1 = el.get(PARENT_P1, (0, 0))
    p_rot = el.get(PARENT_ROTATION, 0)
    p1, p2 = el[P1], el.get(P2)
    p1 = get_absolute_pos(p1, p_p1, p_rot)
    if p2:
        p2 = get_absolute_pos(p2, p_p1, p_rot)
        p1, p2 = sort_line(p1, p2)
    else:
        p1, p2 = p1, None

    conn_map.append(p1)
    if p2: conn_map.append(p2)
    
    if not p2:
        return CONTINUE

    # Vector logic to calculate angle of net symbols(away from wires):
    # Calculate the direction vector from p1 to p2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    mag = hypot(dx, dy)
    if mag == 0:  return CONTINUE

    # Normalized "Unit" vector (length = 1)
    ux, uy = dx / mag, dy / mag

    # Direction LEAVING p1 is (ux, uy). Direction LEAVING p2 is (-ux, -uy).
    for pt_key, (vx, vy) in ((p1, (ux, uy)), (p2, (-ux, -uy))):
        if not wire_endpoints.get(pt_key):
            wire_endpoints[pt_key] = (vx, vy, 1)
        else:
            d0, d1, d2 = wire_endpoints[pt_key]
            d0 += vx # Sum X component
            d1 += vy # Sum Y component
            d2 += 1  # Increment count
            wire_endpoints[pt_key] = (d0, d1, d2)
                   
def fill_metadata(qspice, portion = 0, depth = 0, key = None, parent = None, index = 1, s_p1 = None, s_rot = None, s_dns = None, conn_map = None, wire_endpoints = None, counter = None):
    if portion == 0:
        if s_p1 is None: s_p1 = []
        if s_dns is None: s_dns = []
        if s_rot is None: s_rot = []
        if conn_map is None: conn_map = ConnMap()
        if wire_endpoints is None: wire_endpoints = {}
        if counter is None: counter = {}
        etype = qspice.get(TYPE)
        if isinstance(etype, QSpice):
            artifact(qspice)
            artifacted = True
        else:
            artifacted = False
        fill_metadata(qspice, 1, depth, key, parent, 1, s_p1, s_rot, s_dns, conn_map, wire_endpoints, counter)
        if artifacted:
            deartifact(qspice)
        qspice['wire_endpoints'] = wire_endpoints
        qspice['conn_map'] = conn_map
        qspice['counter'] = counter
    if portion == 1:
        lcount = {}
        etype = qspice.get(TYPE)    
        dns = qspice.get(DONOTSTUFF, 0)
        rot = qspice.get(ROTATION, 0)
        p1 = qspice.get(P1, (0, 0))
        qspice[PARENT_P1] = s_p1
        if etype != JUMPER: qspice[PARENT_DONOTSTUFF] = s_dns
        qspice[PARENT_ROTATION] = s_rot
        qspice[DEPTH] = depth
        qspice[KEY] = key
        qspice[PARENT] = parent
        qspice[INDEX] = index
        if etype in (WIRE, PIN):
            detect_wire_end_points(qspice, conn_map, wire_endpoints)
        elif etype == JUNCTION:
            _p = qspice.get(P1)
            if _p: 
                conn_map.append(_p)    
        if etype == COMPONENT:
            j = get_jumper(qspice)
            if j:
                k, v = add_qspice_value(qspice, QSpice({TYPE: JUMPER, P1: j[0], P2: j[1]}))
        if etype == SYMBOL:
            st = get_instance_name(qspice)
            vl = get_component_value(qspice)
            symt = get_symbol_type(qspice)
            qspice[INSTANCENAME] = st
            qspice[COMPONENTVALUE] = vl
            qspice[SYMBOLTYPE] = symt      
        if etype == FILE_BOM:
            it = 'file'
        else:
            it = etype
        if not it: 
            it = 'object'
        count(it, counter)
        _id = parse_single_line(f'{it}_{counter[it]}')[1]
        qspice[OBJ_ID] = _id
        for k in list(qspice.keys()):
            if isinstance(qspice[k], QSpice) and (k != PARENT):
                etype = qspice[k].get(TYPE)
                count(etype, lcount)
                i = lcount[etype]
                fill_metadata(qspice[k], 1, depth+1, k, qspice, i, s_p1+[p1], s_rot+[rot], s_dns+[dns], conn_map, wire_endpoints, counter)

def get_flat_object(qspice, order = DRAWING_ORDER, init = True, l = None,
    # localize names:
    DRAWABLE_DEFS = DRAWABLE_DEFS,
    TYPE = TYPE, PARENT = PARENT,
    QSpice = QSpice,
    isinstance = isinstance,
    gfo = None
):
    if init:
        if l is None: l = []
        gfo(qspice, order, False, l)
        return l
    else:
        etype = qspice.get(TYPE)
        if etype in DRAWABLE_DEFS:
            l.append(qspice)
            
        for key, v in list_in_drawing_order(qspice, SYMBOL_DRAWING_ORDER if etype == SYMBOL else order):
            if isinstance(v, QSpice) and (key != PARENT):
                gfo(v, order, False, l)
      
get_flat_object.__defaults__ = get_flat_object.__defaults__[:-1] + (get_flat_object,)

def copy_qspice(d, type_include = (), key_exclude = (), exclude_drawables = True, exclude_inheritance = True, exclude_transform = True, init = True, o = None, function = None):
    if init:
        o = QSpice()
        etype = d.get(TYPE)
        if isinstance(etype, QSpice):
            artifact(d)
        copy_qspice(d, type_include, key_exclude, exclude_drawables, exclude_inheritance, exclude_transform, False, o, function)
        return o        
    else:
        for k, v in d.items():   
            if k != PARENT:
                if (k not in key_exclude) and (not(exclude_drawables and (DRAWABLE in k))) and (not(exclude_inheritance and (PARENT in k))) and (not(exclude_transform and (TRANSFORM == k))):
                    if isinstance(v, QSpice):
                        etype = v.get(TYPE)
                        if (len(type_include) == 0) or (etype in type_include):
                            o[k] = c = QSpice()
                            copy_qspice(v, type_include, key_exclude, exclude_drawables, exclude_inheritance, exclude_transform, False, c, function)
                            if function:
                                function(v, c)
                    else:
                        if isinstance(v, list):
                            o[k] = v[:]
                        else:
                            o[k] = v

BrandPath = QSpice({TYPE: PATH, P1: (0, 0), PATHDATA: Qorvo, U1: 0, LINEWIDTH: -1, LINETYPE: 0, LINECOLOR: 0, FILLCOLOR: 0, U2: -1, HBLOCK: 0, PINASSOC: -1, U3: -1, ISTEXT: 1})
BrandSymbol = QSpice({TYPE: SYMBOL, SYMBOLNAME: 'Qorvo', f'{EXTRA_}1': BrandPath, CASTABLE: True})
fill_metadata(BrandSymbol)

if __name__ == '__main__':
    print('This module is an extension for "qsconvert.py" and cannot be run standalone.')
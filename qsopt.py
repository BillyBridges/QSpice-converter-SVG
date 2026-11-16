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

# Version 1.01

# Matching QSpice's March 20, 2026 build

import sys
import qmath as q
import oppathfont as o
import math
from qmath import push, pop, Push, Pop, stack

# Reference command line:
# qsconvert.py -hs /e /svg /fsvg AudioAmp.qsch /aprin /crv /fs*=1.17 /optsw/=1.17 /m

main = sys.modules['__main__']
opfont = q.Fonts['qsopenpath'] = {
    q.WIN_ASCENT: 1.056060606060606,
    q.WIN_DESCENT: 0.3109090909090909,
    q.TYPO_ASCENT: 1.054242424242424,
    q.TYPO_DESCENT: -0.2890909090909091,
    q.TYPO_LINE_GAP: 0,
    q.HHEAD_ASCENT: 1.054242424242424,
    q.HHEAD_DESCENT: -0.2890909090909091,
    q.HHEAD_LINE_GAP: 0,
    q.CAPITAL_HEIGHT: 0.6581818181818182,
    q.X_HEIGHT: 0.4081818181818182,
    q.ASCENT: 0.7996969696969697,
    q.DESCENT: 0.2003030303030303,
    q.UNDERLINE_POSITION: -0.1248484848484848,
    q.HEIGHT: 0.0496969696969697}

skew_height = 0.974
capital_half_height = opfont[q.CAPITAL_HEIGHT] * 0.5
hang_dec = opfont[q.HHEAD_ASCENT] - capital_half_height

def render_text(text, font, anchor, baseline, scale=1.0, skew_angle=0.0, skew_height=0.0, x_offset=0.0, y_offset=0.0):
# Renders an entire string into a single SVG path object, applying scale,
# skew, offsets, and handling typographic Y-up to SVG Y-down conversion.

    # Precompute skew matrix factors
    # Skew angle in degrees converted to radians (horizontal shear based on height offset)
    skew_rad = math.radians(skew_angle)
    tan_skew = math.tan(skew_rad)

    combined_path_commands = []
    tw = q.get_text_width(text, 'qsopenpath', scale)
    sx = -tw if anchor == q.END else 0 if anchor == q.START else -0.5*tw
    current_x = x_offset + sx
    sy = -capital_half_height*scale if (baseline == q.ALPHABETIC) else (0 if (baseline in (q.MIDDLE, q.CENTRAL)) else hang_dec*scale)

    for char in text:
        code_point = ord(char)

        glyph = font.get_glyph(code_point)
        if not glyph:
            continue

        spline_set = glyph.get("SplineSet", [])
        raw_width = glyph.get("Width", 0.467878787878)

        # Process and transform each command's coordinates for this glyph
        for cmd, data in spline_set:
            op_coords = []

            # Flatten data tuples/lists
            flat_coords = []
            for item in data:
                if isinstance(item, (tuple, list)):
                    flat_coords.extend(item)
                else:
                    flat_coords.append(item)

            # Transform coordinate pairs (x, y)
            for i in range(0, len(flat_coords), 2):
                gx = flat_coords[i]
                gy = flat_coords[i+1]

                # 1. Apply horizontal cursor offset and character scaling
                scaled_x = gx * scale
                scaled_y = gy * scale

                # 2. Apply skew around the given skew_height
                # Horizontal shear formula: x_new = x + (y - height) * tan(angle)
                if tan_skew != 0.0:
                    scaled_x += (scaled_y - (skew_height * scale)) * tan_skew

                # 3. Translate by current string cursor position and user offsets
                final_x = scaled_x + current_x

                # 4. Convert typographic Y-up to SVG Y-down, then apply scale & Y offset
                # SVG origin is top-left, so Y needs inversion relative to em_size scaled space
                final_y = scale - scaled_y + y_offset + sy

                op_coords.extend([final_x, final_y])

            combined_path_commands.append((cmd, tuple(op_coords)))

        # Advance cursor for the next character (scaled by user scale factor)
        current_x += raw_width * scale

    return combined_path_commands

def generate_text_svg_markup(text, font, scale=1.0, skew_angle=0.0, skew_height=0.0, y_offset=0.0, x_offset=0.0, stroke_width=200, color = 0x0):
# Helper wrapper to generate the complete SVG wrapper element
    path_d = q.to_svg_string(render_text(text, font, q.START, q.HANGING, scale, skew_angle, skew_height, x_offset, y_offset))
    return f"""<path d="{path_d}" fill="none" stroke="{q.pub_color(color)}" stroke-width="{stroke_width}" stroke-linejoin="{q.ROUND}" stroke-linecap="{q.ROUND}"/>"""

def get_text_svg_or(transform, font, fontsize, color, anchor, baseline, id_, safe_lines, depth, counter, b, fs, crv = None, aprin = None, ispin = None, remove_fill = False, castable = False, invisible = False):
# Replaces "get_text_svg" in the main function, now to generate the text in the form of a "path" command instead of "text".

    sls = [safe_lines] if isinstance(safe_lines[0], str) else safe_lines
    gopen = False
    tspans_l = []
    for line in sls:
        if line[4]: # annoying lines over characters
            notpos = line[4]
            for i in notpos:
                tspans_l.extend(q.get_char_overline(line[0], i, anchor, baseline, q.FONT, fs, line[2], line[3]))

    # Remove redundant nodes:
    i = 1
    while i < len(tspans_l):
        if q.rtup(tspans_l[i][1][-2:]) == q.rtup(tspans_l[i-1][1][-2:]):
            del tspans_l[i]
        else:
            i += 1
    i = 1
    while i < len(tspans_l):
        if (tspans_l[i][0] == 'L') and (tspans_l[i-1][0] == 'L'):
            del tspans_l[i-1]
        else:
            i += 1

    if len(sls) > 1:
        for sl in sls:
            tspans_l.extend(render_text(sl[0], opfont, anchor, baseline, fontsize, OPEN_PATH_TEXT_SKEW_ANGLE, skew_height, sl[2], sl[3]))
    else:
        tspans_l.extend(render_text(sls[0][0], opfont, anchor, baseline, fontsize, OPEN_PATH_TEXT_SKEW_ANGLE, skew_height, sls[0][2], sls[0][3]))

    if invisible: color = None
    stroke_str = f' stroke="{q.pub_color(color)}"'
    sw = (OPEN_PATH_TEXT_STROKE_WIDTH / 160) * fontsize
    sw_str = f' stroke-width="{sw}"'
    path_str = f' d="{q.to_svg_string(tspans_l)}"'
    fill_str = f' fill="{q.NONE}"'
    return (f'<{q.PATH}{path_str}{transform}{stroke_str}{fill_str}{sw_str}'
                         f' stroke-linejoin="{q.ROUND}" stroke-linecap="{q.ROUND}" id="{id_}"/>')

def generate_text_svg_markup_sample(text, font, scale=1.0, skew_angle=0.0, skew_height=0.0, y_offset=0.0, x_offset=0.0, stroke_width=200):
    approx_width = q.get_text_width(text, 'qsopenpath', scale)
    d = generate_text_svg_markup(text, font, scale, skew_angle, skew_height, y_offset, x_offset, stroke_width)
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {approx_width} {scale * 1.5}"
width="100%" height="100%">
{d}
</svg>"""

def run_test():
    svg_output = generate_text_svg_markup_sample('Glib Jocks Quiz (Nymph) To Vex Dwarf Pack My Box With Five Dozen Liquor Jugs JACKDAWS LOVE MY BIG SPHINX OF QUARTZ1234567890', o.get_open_path_font(), scale=160.0, skew_angle=19.0, skew_height=skew_height, y_offset=0.0, x_offset=0.0, stroke_width=15)

    output_filename = "text_visual_test.svg"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(svg_output)

    print(f"Successfully generated visual test SVG: {output_filename}")

def init_unit(pstr):
    q.add_parameter('/OPTSW', ['qsopt', 'OPEN_PATH_TEXT_STROKE_WIDTH', 15.0, float, 'open path text stroke width']) # Default = 15
    q.add_parameter('/OPTSA', ['qsopt', 'OPEN_PATH_TEXT_SKEW_ANGLE', 19.0, float, 'open path text skew angle']) # Default = 19
    q.add_parameter('/OPTSH', ['qsopt', 'OPEN_PATH_TEXT_SKEW_HEIGHT', 0.974, float, 'open path text skew height factor']) # Default = 0.974
    q.add_parameter('/OPTWS', ['qsopt', 'OPEN_PATH_TEXT_WIDTH_OFFSET', 0.05, float, 'open path text width offset']) # Default = 0.05
    q.HELP_HEADER.append('Supported fonts:')
    q.HELP_HEADER.append('')
    for f in q.Fonts:
        q.HELP_HEADER.append(f'    {f}')
    q.HELP_HEADER.append('')


def patch(pstr):
    global skew_height, opfont

    if q.FONT == 'qsopenpath':
        main.get_text_svg = get_text_svg_or
        skew_height = OPEN_PATH_TEXT_SKEW_HEIGHT
        o.Glyph.width_offset = o.SplineSet.width_offset = OPEN_PATH_TEXT_WIDTH_OFFSET
        opfont = q.Fonts['qsopenpath'] = o.get_open_path_font()

if __name__ == '__main__':
    run_test()
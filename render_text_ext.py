#!/usr/bin/env python3
import math
import inkex
from inkex import PathElement
import oppathfont as o

DYN_PRECISION = 5

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

def rpub(n, precision = DYN_PRECISION):
# Round for publishing
    v = round(n, precision)
    if v.is_integer():
        v = round(v)
    return v

def rcomp(n, precision = (DYN_PRECISION*2)-1):
# Round for comparison
    return round(n, precision)

def rtup(t, precision = (DYN_PRECISION*2)-1):
# Round tuple for comparison
    r = []
    for e in t:
        r.append(round(e, precision))
    return tuple(r)

def to_svg_string(path_list, dynamic_precision,
    # localize names:
    rtup = rtup, len = len, SafeList = SafeList, rcomp = rcomp,
    str = str, rpub = rpub
):

    # Transforms a path command list to an SVG string
    if len(path_list) == 0: return ''
    m1 = path_list[0][1][0], path_list[0][1][1]
    m1r = rtup(m1, dynamic_precision)
    p1 = 0.0, 0.0
    p2 = 0.0, 0.0
    subpath_start = m1  # Track subpath closure origin
    er = m1r[0] - m1[0], m1r[1] - m1[1] # Rounding compensation

    segments = []
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
                if (rcomp(p[0], dynamic_precision) == rcomp(pp[0], dynamic_precision)) and (rcomp(p[1], dynamic_precision) == rcomp(pp[1], dynamic_precision)) and (curcmd == 'l'):
                    coordi += 2
                    continue
                if (rcomp(p[0], dynamic_precision) == rcomp(pp[0], dynamic_precision)) and (curcmd == 'l'):
                    curcmd = 'v'
                if (rcomp(p[1], dynamic_precision) == rcomp(pp[1], dynamic_precision)) and (curcmd == 'l'):
                    curcmd = 'h'
                if curcmd not in('v', 'h'):
                    strcmd.append(str(rpub((p[0] -  p1[0]) + er[0], dynamic_precision)))
                    strcmd.append(' ')
                    strcmd.append(str(rpub((p[1] -  p1[1]) + er[1], dynamic_precision)))
                    strcmd.append(' ')
                elif curcmd == 'h':
                    strcmd.append(str(rpub((p[0] -  pp[0]) + er[0], dynamic_precision)))
                    strcmd.append(' ')
                elif curcmd == 'v':
                    strcmd.append(str(rpub((p[1] -  pp[1]) + er[1], dynamic_precision)))
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
        if (strcmd[0] in ("Z", "z")) or (len(strcmd) > 2):
            segments.extend(strcmd)
        prevcmd = curcmd
    del segments[-1]
    segments[0] = segments[0].upper()
    return "".join(segments)

# Import or include your rendering function here
def render_text(text, scale=1.0, skew_angle=0.0, skew_height=0.0, x_offset=0.0, y_offset=0.0, width_offset=0.05, dynamic_precision = 5):
# Renders an entire string into a single SVG path object, applying scale,
# skew, offsets, and handling typographic Y-up to SVG Y-down conversion.

    o.Glyph.width_offset = o.SplineSet.width_offset = width_offset

    font = o.get_open_path_font()

    # Precompute skew matrix factors
    # Skew angle in degrees converted to radians (horizontal shear based on height offset)
    skew_rad = math.radians(skew_angle)
    tan_skew = math.tan(skew_rad)

    combined_path_commands = []
    #tw = q.get_text_width(text, 'qsopenpath', scale)
    #sx = -tw if anchor == q.END else 0 if anchor == q.START else -0.5*tw
    current_x = x_offset
    #sy = -capital_half_height*scale if (baseline == q.ALPHABETIC) else (0 if (baseline in (q.MIDDLE, q.CENTRAL)) else hang_dec*scale)

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
                final_y = scale - scaled_y + y_offset

                op_coords.extend([final_x, final_y])

            combined_path_commands.append((cmd, tuple(op_coords)))

        # Advance cursor for the next character (scaled by user scale factor)
        current_x += raw_width * scale

    return to_svg_string(combined_path_commands, dynamic_precision)

class RenderTextExtension(inkex.EffectExtension):
    def add_arguments(self, pars):
        # UI parameters defined by the user in the window (excluding x and y)
        pars.add_argument("--text", type=str, default="Hello", help="Text to render")
        pars.add_argument("--scale", type=float, default=1.0, help="Scale factor")
        pars.add_argument("--skew_angle", type=float, default=19.0, help="Skew angle")
        pars.add_argument("--stroke_width", type=float, default=15.0, help="Stroke width")
        pars.add_argument("--width_offset", type=float, default=5.0, help="Width offset(centesimal)")
        pars.add_argument("--proportional_stroke", type=inkex.Boolean, default=True, help="Proportional stroke width(160)")
        pars.add_argument("--dynamic_precision", type=int, default=5, help="Decimal points precision")
    def effect(self):
        # Automatically grab the current view center (x, y) from Inkscape's viewport
        view_center = self.svg.namedview.center
        x, y = float(view_center[0]), float(view_center[1])

        # Get parameters from the user inputs
        proportional_stroke = self.options.proportional_stroke
        text = self.options.text
        scale = self.options.scale
        skew_angle = self.options.skew_angle
        stroke_width = self.options.stroke_width
        width_offset = self.options.width_offset
        dynamic_precision = self.options.dynamic_precision
        if proportional_stroke:
            stroke_width = (stroke_width / 160) * scale

        # Call your custom rendering function
        # (Assuming it returns an SVG path data string 'd' or path components)
        path_data = render_text(
            text=text, 
            scale=scale, 
            skew_angle=skew_angle,
            width_offset=width_offset/100,
            dynamic_precision=dynamic_precision
        )

        # Create the SVG path element and set its attributes
        path_elem = PathElement()
        path_elem.set('d', path_data)
        
        # Style the path (e.g., black stroke, no fill, specified stroke width)
        path_elem.style = {
            'stroke': '#000000',
            'stroke-width': str(stroke_width),
            'fill': 'none',
            'stroke-linejoin': "round",
            'stroke-linecap': "round",
        }
        
        # Apply a translate transform to place it precisely at the user's current view center (x, y)
        path_elem.transform = f"translate({x}, {y})"

        # Append the new path element to the currently active layer in Inkscape
        self.svg.get_current_layer().append(path_elem)

if __name__ == '__main__':
    RenderTextExtension().run()
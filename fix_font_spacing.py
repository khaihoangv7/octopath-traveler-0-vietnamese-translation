"""
Scale font glyphs for Octopath Traveler Vietnamese.
All fonts use Segoe UI with uniform scaling.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
import os
import glob

FONT_SCALES = {
    '9PCS_Franco_Default.ufont':        0.88,
    '9PCS_Franco_B.ufont':              0.88,
    '9PCS_Rocio_Default.ufont':         0.95,
    '9PCS_Rocio_I.ufont':               0.95,
    '9PCS_CinemaLetter_Std_L.ufont':    0.95,
    '9PCS_ClearTone_Default.ufont':     0.95,
}

Y_SHIFT = 100

ORIGINAL_METRICS = {
    'sTypoAscender': 1374, 'sTypoDescender': -469, 'sTypoLineGap': 0,
    'usWinAscent': 2151, 'usWinDescent': 469,
    'hhea_ascent': 2151, 'hhea_descent': -469, 'hhea_lineGap': 0,
}

MOD_FONT_DIR = r'Mod_Vietnamese\Octopath_Traveler0\Content\UI\Font'
SOURCE_FONT = 'segoeui_modified.ttf'


def create_scaled_font(source_path, output_path, scale):
    font = TTFont(source_path)
    glyf = font['glyf']
    hmtx = font['hmtx']
    scaled = 0
    for name in font.getGlyphOrder():
        try:
            old_glyph = glyf[name]
            if old_glyph.numberOfContours == 0 and not old_glyph.isComposite():
                continue
            pen = TTGlyphPen(None)
            transform = TransformPen(pen, (scale, 0, 0, scale, 0, Y_SHIFT))
            old_glyph.draw(transform, glyf)
            glyf[name] = pen.glyph()
            width, lsb = hmtx[name]
            hmtx[name] = (int(width * scale), int(lsb * scale))
            scaled += 1
        except Exception:
            pass

    os2 = font['OS/2']
    hhea = font['hhea']
    os2.sTypoAscender = ORIGINAL_METRICS['sTypoAscender']
    os2.sTypoDescender = ORIGINAL_METRICS['sTypoDescender']
    os2.sTypoLineGap = ORIGINAL_METRICS['sTypoLineGap']
    os2.usWinAscent = ORIGINAL_METRICS['usWinAscent']
    os2.usWinDescent = ORIGINAL_METRICS['usWinDescent']
    hhea.ascent = ORIGINAL_METRICS['hhea_ascent']
    hhea.descent = ORIGINAL_METRICS['hhea_descent']
    hhea.lineGap = ORIGINAL_METRICS['hhea_lineGap']

    font.save(output_path)
    font.close()
    return scaled


def main():
    print("=" * 60)
    print("  Font Setup: All Segoe UI")
    print("=" * 60)

    cache = {}
    for ufont_name, scale in FONT_SCALES.items():
        ufont_path = os.path.join(MOD_FONT_DIR, ufont_name)
        if not os.path.exists(ufont_path):
            continue
        if scale not in cache:
            temp = f'temp_scaled_{scale}.ttf'
            print(f"\n  Generating scale={scale}...")
            count = create_scaled_font(SOURCE_FONT, temp, scale)
            print(f"    {count} glyphs")
            cache[scale] = temp

        with open(cache[scale], 'rb') as f:
            data = f.read()
        with open(ufont_path, 'wb') as f:
            f.write(data)
        print(f"  {ufont_name}: scale={scale} OK")

    for f in glob.glob('temp_scaled_*.ttf'):
        os.remove(f)
    print(f"\n  Done!")


if __name__ == '__main__':
    main()

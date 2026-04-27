"""
Scale down font glyphs correctly using fontTools.
"""
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
import os

def scale_font(input_path, output_path, scale=0.85):
    font = TTFont(input_path)
    glyf = font['glyf']
    hmtx = font['hmtx']
    glyph_order = font.getGlyphOrder()
    
    # We need to process all glyphs
    new_glyf = {}
    for name in glyph_order:
        old_glyph = glyf[name]
        
        # Create new pen
        pen = TTGlyphPen(glyf)
        # Transform original glyph into the new pen
        transformer = TransformPen(pen, (scale, 0, 0, scale, 0, 100)) # Shift up 100
        old_glyph.draw(transformer, glyf)
        
        # Get the new glyph
        new_glyf[name] = pen.glyph()
        
        # Scale the advance width
        width, lsb = hmtx[name]
        hmtx[name] = (int(width * scale), int(lsb * scale))
        
    # Replace glyf table contents
    for name in glyph_order:
        glyf[name] = new_glyf[name]
        
    # Update metrics
    os2 = font['OS/2']
    hhea = font['hhea']
    os2.sTypoLineGap = 600
    hhea.lineGap = 600
    
    font.save(output_path)
    font.close()
    print(f"Success: {output_path}")

if __name__ == "__main__":
    scale_font('arial.ttf', 'arial_compact.ttf', 0.85)

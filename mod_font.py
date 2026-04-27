"""
Modify font line spacing to prevent text overlap in game.
Increases the line gap so Vietnamese diacritics don't overlap.
"""
from fontTools.ttLib import TTFont
import shutil
import os

INPUT_FONT = r'C:\Windows\Fonts\segoeui.ttf'
OUTPUT_FONT = 'segoeui_modified.ttf'

font = TTFont(INPUT_FONT)

# Print current metrics
os2 = font['OS/2']
hhea = font['hhea']
print("=== BEFORE ===")
print(f"OS/2 sTypoAscender:  {os2.sTypoAscender}")
print(f"OS/2 sTypoDescender: {os2.sTypoDescender}")
print(f"OS/2 sTypoLineGap:   {os2.sTypoLineGap}")
print(f"OS/2 usWinAscent:    {os2.usWinAscent}")
print(f"OS/2 usWinDescent:   {os2.usWinDescent}")
print(f"hhea ascent:         {hhea.ascent}")
print(f"hhea descent:        {hhea.descent}")
print(f"hhea lineGap:        {hhea.lineGap}")

# Increase line spacing by adding to lineGap
# Original line height = ascent + abs(descent) + lineGap
# We increase the line gap significantly to create more space
LINE_GAP_INCREASE = 250  # ~12% of the em-square (2048 units)

os2.sTypoLineGap += LINE_GAP_INCREASE
hhea.lineGap += LINE_GAP_INCREASE

# Also bump usWinAscent slightly so that diacritics are not clipped
os2.usWinAscent = max(os2.usWinAscent, os2.sTypoAscender + 200)

print("\n=== AFTER ===")
print(f"OS/2 sTypoLineGap:   {os2.sTypoLineGap}")
print(f"OS/2 usWinAscent:    {os2.usWinAscent}")
print(f"hhea lineGap:        {hhea.lineGap}")

font.save(OUTPUT_FONT)
print(f"\nSaved modified font to {OUTPUT_FONT}")
font.close()

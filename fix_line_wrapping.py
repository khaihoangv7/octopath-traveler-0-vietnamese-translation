"""
Fix line wrapping for Vietnamese translated text in Octopath Traveler.

Problem: Vietnamese text lines are much longer than English originals
(VI 90th percentile = 59 chars vs EN = 35 chars), causing the game's
auto-wrap to create overlapping lines.

Solution: Re-wrap all Vietnamese text at word boundaries to stay within
~35 chars per line, preventing the game engine from auto-wrapping.
"""
import json
import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TRANSLATED_DIR = 'translated_text'
MAX_LINE_LENGTH = 35  # Based on EN 90th percentile analysis

# Special tags that should not be split across lines
TAG_PATTERN = re.compile(r'(<[^>]+>|\{[^}]+\})')


def wrap_line(text, max_len=MAX_LINE_LENGTH):
    """
    Wrap a single line of text at word boundaries to stay within max_len.
    Handles Vietnamese text and preserves special game tags.
    
    Returns a list of wrapped lines.
    """
    # Check visible length (without tags like <chara_name>, {0})
    visible_len = len(TAG_PATTERN.sub('', text))
    if visible_len <= max_len:
        return [text]
    
    # Split text into segments: regular text and tags
    # Tags like <chara_name>, {0}, </> should not be split
    segments = TAG_PATTERN.split(text)
    
    lines = []
    current_line = ""
    
    for segment in segments:
        if not segment:
            continue
            
        # If this is a tag, add it to current line without breaking
        if TAG_PATTERN.match(segment):
            current_line += segment
            continue
        
        # Split regular text by spaces for word-boundary wrapping
        words = segment.split(' ')
        
        for i, word in enumerate(words):
            if not word:
                continue
                
            # Calculate what the line would look like with this word
            if current_line:
                test_line = current_line + ' ' + word
            else:
                test_line = word
            
            # Calculate visible length (excluding tags)
            visible_len = len(TAG_PATTERN.sub('', test_line))
            
            if visible_len <= max_len or not current_line:
                # Fits, or it's the first word on a new line (must add it)
                if current_line and not current_line.endswith((' ', '\t')):
                    current_line += ' ' + word
                else:
                    current_line += word
            else:
                # Doesn't fit - start a new line
                lines.append(current_line.rstrip())
                current_line = word
    
    # Don't forget the last line
    if current_line:
        lines.append(current_line.rstrip())
    
    return lines


def rewrap_text(vi_text, en_text=""):
    """
    Re-wrap Vietnamese text to fit within MAX_LINE_LENGTH per line.
    
    Strategy (free re-wrap):
    - Split VI text at existing \n boundaries
    - For each segment that's too long, re-wrap at word boundaries
    - Join everything back with \n
    - Clean up: remove leading/trailing whitespace per line
    """
    if not vi_text or not vi_text.strip():
        return vi_text
    
    # Split by existing line breaks
    existing_lines = vi_text.split('\n')
    
    # Re-wrap each line that's too long
    new_lines = []
    for line in existing_lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append('')
            continue
        
        # Check visible length (without tags)
        visible_len = len(TAG_PATTERN.sub('', stripped))
        
        if visible_len <= MAX_LINE_LENGTH:
            new_lines.append(stripped)
        else:
            # This line is too long - rewrap it
            wrapped = wrap_line(stripped, MAX_LINE_LENGTH)
            new_lines.extend(wrapped)
    
    return '\n'.join(new_lines)


def process_file(filepath):
    """Process a single JSON translation file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        return 0, 0
    
    modified_count = 0
    total_translated = 0
    
    for item in data:
        vi = item.get('vi', '')
        en = item.get('en', '')
        
        if not vi or vi == en:
            continue
        
        total_translated += 1
        
        # Re-wrap the Vietnamese text
        new_vi = rewrap_text(vi, en)
        
        if new_vi != vi:
            item['vi'] = new_vi
            modified_count += 1
    
    # Save back
    if modified_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return total_translated, modified_count


def main():
    print("=" * 60)
    print("  Fix Line Wrapping for Vietnamese Text")
    print(f"  Max line length: {MAX_LINE_LENGTH} chars")
    print("=" * 60)
    
    total_files = 0
    total_translated = 0
    total_modified = 0
    
    for filename in sorted(os.listdir(TRANSLATED_DIR)):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(TRANSLATED_DIR, filename)
        translated, modified = process_file(filepath)
        
        total_files += 1
        total_translated += translated
        total_modified += modified
        
        if modified > 0:
            print(f"  {filename}: {modified}/{translated} entries re-wrapped")
        else:
            print(f"  {filename}: OK (no changes needed)")
    
    print(f"\n{'=' * 60}")
    print(f"  RESULTS")
    print(f"  Files processed: {total_files}")
    print(f"  Total translated entries: {total_translated}")
    print(f"  Entries re-wrapped: {total_modified}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()

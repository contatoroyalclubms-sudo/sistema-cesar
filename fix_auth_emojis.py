#!/usr/bin/env python3
"""
Remove all emoji characters from auth.py
"""

import re

def remove_emojis(text):
    """Remove all emoji characters from text"""
    # Pattern to match most emoji characters
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002600-\U000027BF"  # Miscellaneous symbols
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U00002300-\U000023FF"  # Miscellaneous Technical
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U0001F000-\U0001F02F"  # Mahjong/Domino Tiles
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def fix_auth_file():
    """Fix auth.py by removing all emojis"""
    print("[FIX] Removing emojis from auth.py...")
    
    # Read file
    with open('backend/app/routers/auth.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove emojis
    fixed_content = remove_emojis(content)
    
    # Write back
    with open('backend/app/routers/auth.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("[OK] All emojis removed from auth.py")
    
    # Verify no emojis remain
    with open('backend/app/routers/auth.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        emoji_lines = []
        for i, line in enumerate(lines, 1):
            if re.search(r'[\U0001F000-\U0001F9FF]|[\U00002600-\U000027BF]|[\U0001F300-\U0001F5FF]|[\U0001F600-\U0001F64F]|[\U0001F680-\U0001F6FF]', line):
                emoji_lines.append(i)
        
        if emoji_lines:
            print(f"[WARNING] Still found emojis on lines: {emoji_lines}")
        else:
            print("[SUCCESS] No emojis found in auth.py")

if __name__ == "__main__":
    fix_auth_file()
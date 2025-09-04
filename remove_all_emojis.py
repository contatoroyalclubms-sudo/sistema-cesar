#!/usr/bin/env python3
"""
Remove all emoji characters from all Python files in backend
"""

import os
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

def fix_file(filepath):
    """Fix a single file by removing all emojis"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove emojis
        fixed_content = remove_emojis(content)
        
        # Only write if changes were made
        if content != fixed_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Could not fix {filepath}: {e}")
        return False

def main():
    """Fix all Python files in backend"""
    print("[START] Removing emojis from all backend Python files...")
    
    files_fixed = []
    files_checked = 0
    
    # Walk through all Python files in backend
    for root, dirs, files in os.walk('backend/app'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                files_checked += 1
                if fix_file(filepath):
                    files_fixed.append(filepath)
                    print(f"[FIXED] {filepath}")
    
    print(f"\n[COMPLETE] Checked {files_checked} files, fixed {len(files_fixed)} files")
    
    if files_fixed:
        print("\nFiles that were fixed:")
        for filepath in files_fixed:
            print(f"  - {filepath}")
    
    # Verify no emojis remain
    print("\n[VERIFY] Checking for remaining emojis...")
    remaining = []
    for root, dirs, files in os.walk('backend/app'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if re.search(r'[\U0001F000-\U0001F9FF]|[\U00002600-\U000027BF]|[\U0001F300-\U0001F5FF]|[\U0001F600-\U0001F64F]|[\U0001F680-\U0001F6FF]', line):
                                remaining.append(f"{filepath}:{i}")
                except:
                    pass
    
    if remaining:
        print(f"[WARNING] Still found emojis in {len(remaining)} locations")
    else:
        print("[SUCCESS] No emojis found in any backend Python files!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Fix CSP that got duplicated - replace with clean version.
"""

import re
from pathlib import Path

# New clean CSP
NEW_CSP = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests;"

def fix_html_file(filepath):
    """Fix CSP in a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Match the entire meta tag and replace the content attribute
    pattern = r'<meta\s+http-equiv=["\']Content-Security-Policy["\']\s+content=["\'][^"\']*["\']>'
    replacement = f'<meta http-equiv="Content-Security-Policy" content="{NEW_CSP}">'

    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    root = Path(__file__).parent.parent
    html_files = list(root.glob('**/*.html'))

    exclude_dirs = {'_site', 'node_modules', '.git', '_includes', '_layouts'}
    html_files = [f for f in html_files if not any(ex in f.parts for ex in exclude_dirs)]

    print(f"Fixing CSP in {len(html_files)} HTML files")

    fixed = 0
    for filepath in sorted(html_files):
        if fix_html_file(filepath):
            print(f"✓ Fixed: {filepath.relative_to(root)}")
            fixed += 1

    print(f"\nFixed {fixed} files")

if __name__ == '__main__':
    main()

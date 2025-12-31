#!/usr/bin/env python3
"""
Remove inline scripts and update CSP to use only 'self' for scripts.
"""

import re
from pathlib import Path

# New CSP without the hash
NEW_CSP = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests;"

def update_html_file(filepath):
    """Update a single HTML file to remove inline scripts and update CSP."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    # 1. Update CSP to remove the hash
    old_csp_pattern = r'(<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*content=["\'])[^"\']*(["\'][^>]*>)'
    if re.search(old_csp_pattern, content, re.IGNORECASE):
        content = re.sub(
            old_csp_pattern,
            r'\g<1>' + NEW_CSP + r'\g<2>',
            content,
            flags=re.IGNORECASE
        )
        changes.append("Updated CSP to script-src 'self'")

    # 2. Remove inline scripts (no src attribute)
    inline_script_pattern = r'\s*<script(?![^>]*\ssrc=)[^>]*>[\s\S]*?</script>'
    if re.search(inline_script_pattern, content, re.IGNORECASE):
        content = re.sub(inline_script_pattern, '', content, flags=re.IGNORECASE)
        changes.append("Removed inline scripts")

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    return []

def main():
    root = Path(__file__).parent.parent
    html_files = list(root.glob('**/*.html'))

    # Exclude certain directories
    exclude_dirs = {'_site', 'node_modules', '.git', '_includes', '_layouts'}
    html_files = [f for f in html_files if not any(ex in f.parts for ex in exclude_dirs)]

    print(f"Found {len(html_files)} HTML files to process")
    print()

    total_changes = 0
    for filepath in sorted(html_files):
        relative_path = filepath.relative_to(root)
        changes = update_html_file(filepath)
        if changes:
            print(f"✓ {relative_path}")
            for change in changes:
                print(f"    - {change}")
            total_changes += len(changes)
        else:
            print(f"  {relative_path} (no changes needed)")

    print()
    print(f"Total changes made: {total_changes}")

if __name__ == '__main__':
    main()

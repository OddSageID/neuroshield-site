#!/usr/bin/env python3
"""
Remove inline scripts and update CSP to use only 'self' for scripts.
Adds external theme-init.js reference instead.
"""

import os
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

    # 2. Remove inline theme detection script
    inline_script_patterns = [
        r'\s*<script>\s*\(function\(\)\s*\{[^<]*oet-theme-preference[^<]*</script>',
        r'\s*<!-- Inline critical theme detection[^>]*-->\s*',
        r'\s*<!-- Critical: Inline Theme Detection[^>]*-->\s*',
    ]

    for pattern in inline_script_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
            changes.append("Removed inline script")

    # 3. Add external theme-init.js if not present
    # Determine the correct path based on file location
    rel_path = filepath.relative_to(Path(__file__).parent.parent)
    depth = len(rel_path.parts) - 1  # Subtract 1 for the filename itself

    if depth == 0:
        prefix = ""
    else:
        prefix = "../" * depth

    theme_init_script = f'<script src="{prefix}js/theme-init.js"></script>'

    # Check if theme-init.js is already referenced
    if 'theme-init.js' not in content:
        # Add before </head> or after stylesheet
        if '</head>' in content:
            # Add before </head>
            content = content.replace(
                '</head>',
                f'\n  <!-- Theme Detection Script (loaded synchronously to prevent FOUC) -->\n  {theme_init_script}\n</head>'
            )
            changes.append(f"Added external theme-init.js ({prefix}js/theme-init.js)")

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

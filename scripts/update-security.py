#!/usr/bin/env python3
"""
Update security headers in all HTML files.
Replaces existing CSP with hardened version and standardizes security meta tags.
"""

import re
from pathlib import Path

# The new strict CSP without inline script hashes
NEW_CSP = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests;"

# New security meta tags block
NEW_SECURITY_BLOCK = f'''<!-- Security Headers -->
  <meta http-equiv="Content-Security-Policy" content="{NEW_CSP}">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta http-equiv="X-Frame-Options" content="DENY">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="Permissions-Policy" content="accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()">'''

def update_html_file(filepath):
    """Update security headers in a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    # 1. Update or add CSP meta tag
    old_csp_pattern = r'<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*>'
    if re.search(old_csp_pattern, content, re.IGNORECASE):
        content = re.sub(
            old_csp_pattern,
            f'<meta http-equiv="Content-Security-Policy" content="{NEW_CSP}">',
            content,
            flags=re.IGNORECASE
        )
        changes.append("Updated CSP")

    # 2. Ensure X-Content-Type-Options is present
    if 'X-Content-Type-Options' not in content:
        # Add after CSP
        content = content.replace(
            f'<meta http-equiv="Content-Security-Policy" content="{NEW_CSP}">',
            f'<meta http-equiv="Content-Security-Policy" content="{NEW_CSP}">\n  <meta http-equiv="X-Content-Type-Options" content="nosniff">'
        )
        changes.append("Added X-Content-Type-Options")

    # 3. Ensure Permissions-Policy is present
    if 'Permissions-Policy' not in content:
        # Find referrer meta and add after it
        referrer_pattern = r'(<meta\s+name=["\']referrer["\'][^>]*>)'
        if re.search(referrer_pattern, content, re.IGNORECASE):
            content = re.sub(
                referrer_pattern,
                r'\1\n  <meta http-equiv="Permissions-Policy" content="accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()">',
                content,
                flags=re.IGNORECASE
            )
            changes.append("Added Permissions-Policy")

    # 4. Remove Google Fonts references (we're self-hosting)
    google_fonts_patterns = [
        r'\s*<link\s+rel=["\']preconnect["\'][^>]*fonts\.googleapis\.com[^>]*>',
        r'\s*<link\s+rel=["\']preconnect["\'][^>]*fonts\.gstatic\.com[^>]*>',
        r'\s*<link\s+href=["\']https://fonts\.googleapis\.com[^"\']*["\'][^>]*>',
    ]

    for pattern in google_fonts_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            changes.append("Removed Google Fonts reference")

    # 5. Add fonts.css reference if not present (for self-hosted fonts)
    if 'fonts.css' not in content and 'Crimson Pro' in content or 'Source Sans Pro' in content:
        # Find the style.css link and add fonts.css before it
        style_pattern = r'(<link\s+rel=["\']stylesheet["\']\s+href=["\'][^"\']*style\.css["\'][^>]*>)'
        if re.search(style_pattern, content, re.IGNORECASE):
            # Determine the path prefix
            if '/css/style.css' in content:
                fonts_link = '<link rel="stylesheet" href="css/fonts.css">\n  '
            elif '../css/style.css' in content:
                fonts_link = '<link rel="stylesheet" href="../css/fonts.css">\n  '
            else:
                fonts_link = '<link rel="stylesheet" href="/css/fonts.css">\n  '

            content = re.sub(
                style_pattern,
                fonts_link + r'\1',
                content,
                flags=re.IGNORECASE
            )
            changes.append("Added fonts.css reference")

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

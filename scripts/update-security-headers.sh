#!/bin/bash
# Update security headers in all HTML files
# This script adds hardened CSP and standardizes security meta tags

set -e

echo "Updating security headers in all HTML files..."

# The new CSP - strict default-src 'none' with no inline script hashes
NEW_CSP="default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests;"

# Process each HTML file
find . -name "*.html" -not -path "./_site/*" -not -path "./node_modules/*" -not -path "./.git/*" | while read -r file; do
    echo "Processing: $file"

    # Create backup
    cp "$file" "$file.bak"

    # Use Python for more reliable text processing
    python3 << PYTHON_SCRIPT
import re
import sys

with open('$file', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace old CSP with new one
# Match various CSP patterns
old_csp_pattern = r'<meta\s+http-equiv=["\']Content-Security-Policy["\']\s+content=["\'][^"\']*["\']>'
new_csp = '<meta http-equiv="Content-Security-Policy" content="$NEW_CSP">'

if re.search(old_csp_pattern, content, re.IGNORECASE):
    content = re.sub(old_csp_pattern, new_csp, content, flags=re.IGNORECASE)
    print(f"  Updated CSP")
else:
    print(f"  No existing CSP found")

# Add X-Content-Type-Options if missing
if 'X-Content-Type-Options' not in content:
    # Add after CSP
    content = content.replace(new_csp, new_csp + '\n  <meta http-equiv="X-Content-Type-Options" content="nosniff">')
    print(f"  Added X-Content-Type-Options")

# Add Permissions-Policy if missing
if 'Permissions-Policy' not in content:
    # Find the referrer policy and add after it
    referrer_pattern = r'(<meta\s+name=["\']referrer["\'][^>]*>)'
    if re.search(referrer_pattern, content, re.IGNORECASE):
        content = re.sub(
            referrer_pattern,
            r'\1\n  <meta http-equiv="Permissions-Policy" content="accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()">',
            content,
            flags=re.IGNORECASE
        )
        print(f"  Added Permissions-Policy")

with open('$file', 'w', encoding='utf-8') as f:
    f.write(content)

PYTHON_SCRIPT

    # Remove backup if successful
    rm "$file.bak"
done

echo ""
echo "Done! All HTML files updated with hardened security headers."

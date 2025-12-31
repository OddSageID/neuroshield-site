#!/bin/bash
# Download self-hosted fonts for Order of Ethical Technologists
# This script fetches fonts from Google Fonts and saves them locally

set -e

FONTS_DIR="$(dirname "$0")/../fonts"
mkdir -p "$FONTS_DIR"

echo "Downloading fonts to $FONTS_DIR..."

# Google Fonts CSS URLs (we'll parse these to get the actual font files)
# Using User-Agent that requests woff2 format

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Function to download a font file
download_font() {
    local url=$1
    local filename=$2
    echo "  Downloading $filename..."
    curl -s -L -A "$UA" -o "$FONTS_DIR/$filename" "$url"
}

echo ""
echo "=== Crimson Pro ==="

# Crimson Pro fonts (from Google Fonts API)
# These URLs are from the Google Fonts CSS response

# Get the CSS and extract font URLs
CRIMSON_CSS=$(curl -s -A "$UA" "https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400;1,600&display=swap")

# Parse and download Crimson Pro fonts
echo "$CRIMSON_CSS" | grep -oP 'url\(\K[^)]+' | while read -r url; do
    # Determine the weight and style from the CSS context
    if echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-weight: 400" && echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-style: normal"; then
        download_font "$url" "crimson-pro-v24-latin-regular.woff2"
    elif echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-weight: 400" && echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-style: italic"; then
        download_font "$url" "crimson-pro-v24-latin-italic.woff2"
    elif echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-weight: 600" && echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-style: normal"; then
        download_font "$url" "crimson-pro-v24-latin-600.woff2"
    elif echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-weight: 600" && echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-style: italic"; then
        download_font "$url" "crimson-pro-v24-latin-600italic.woff2"
    elif echo "$CRIMSON_CSS" | grep -B5 "$url" | grep -q "font-weight: 700"; then
        download_font "$url" "crimson-pro-v24-latin-700.woff2"
    fi
done

echo ""
echo "=== Source Sans 3 ==="

# Source Sans 3 fonts
SOURCE_CSS=$(curl -s -A "$UA" "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap")

echo "$SOURCE_CSS" | grep -oP 'url\(\K[^)]+' | while read -r url; do
    if echo "$SOURCE_CSS" | grep -B5 "$url" | grep -q "font-weight: 400"; then
        download_font "$url" "source-sans-3-v15-latin-regular.woff2"
    elif echo "$SOURCE_CSS" | grep -B5 "$url" | grep -q "font-weight: 600"; then
        download_font "$url" "source-sans-3-v15-latin-600.woff2"
    elif echo "$SOURCE_CSS" | grep -B5 "$url" | grep -q "font-weight: 700"; then
        download_font "$url" "source-sans-3-v15-latin-700.woff2"
    fi
done

echo ""
echo "=== Verification ==="
echo "Downloaded fonts:"
ls -la "$FONTS_DIR"/*.woff2 2>/dev/null || echo "No .woff2 files found - download may have failed"

echo ""
echo "If download failed, please manually download fonts from:"
echo "  https://gwfh.mranftl.com/fonts"
echo ""
echo "Done!"

# Self-Hosted Fonts

This directory contains self-hosted web fonts to eliminate external CDN dependencies.

## Required Font Files

Download the following WOFF2 files and place them in this directory:

### Crimson Pro (Serif)
- `crimson-pro-v24-latin-regular.woff2`
- `crimson-pro-v24-latin-600.woff2`
- `crimson-pro-v24-latin-700.woff2`
- `crimson-pro-v24-latin-italic.woff2`
- `crimson-pro-v24-latin-600italic.woff2`

### Source Sans 3 (Sans-Serif)
- `source-sans-3-v15-latin-regular.woff2`
- `source-sans-3-v15-latin-600.woff2`
- `source-sans-3-v15-latin-700.woff2`

## Download Instructions

### Option 1: Google Webfonts Helper (Recommended)
1. Visit https://gwfh.mranftl.com/fonts
2. Search for "Crimson Pro" and select weights: 400, 400italic, 600, 600italic, 700
3. Search for "Source Sans 3" and select weights: 400, 600, 700
4. Download the WOFF2 files
5. Rename to match the filenames above

### Option 2: Direct from Google Fonts
1. Visit https://fonts.google.com/
2. Add Crimson Pro (Regular, Italic, SemiBold, SemiBold Italic, Bold)
3. Add Source Sans 3 (Regular, SemiBold, Bold)
4. Use browser dev tools to find the actual font URLs
5. Download and save locally

### Option 3: Using the Download Script
Run the download script from the repository root:
```bash
./scripts/download-fonts.sh
```

## License

Both fonts are licensed under the [SIL Open Font License (OFL)](https://scripts.sil.org/OFL):
- Crimson Pro: Copyright 2018 The Crimson Pro Project Authors
- Source Sans 3: Copyright 2010-2020 Adobe

## Verification

After downloading, verify files are present:
```bash
ls -la fonts/*.woff2
```

Expected output should show 8 font files.

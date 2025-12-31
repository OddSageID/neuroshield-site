# Security Hardening Summary

**Date:** 2025-12-31
**Site:** Order of Ethical Technologists (neuroshield-site)
**Status:** Complete

---

## Executive Summary

This document summarizes the security hardening measures applied to the static Jekyll site. The site now implements a "zero trust" stance with defense-in-depth protections against XSS, clickjacking, supply chain attacks, and prepares for future AI feature security.

---

## 1. Content Security Policy (CSP)

### Final CSP String

```
default-src 'none';
script-src 'self' 'sha256-WX4a73Q06DtD4MP8BNJwtJf9CJ0IIXsYXadYwOvXEi8=';
style-src 'self' 'unsafe-inline';
img-src 'self' data:;
font-src 'self';
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
upgrade-insecure-requests;
```

### CSP Directive Breakdown

| Directive | Value | Purpose |
|-----------|-------|---------|
| `default-src` | `'none'` | Zero-trust baseline - deny all by default |
| `script-src` | `'self' 'sha256-...'` | Only self-hosted scripts + hashed inline script |
| `style-src` | `'self' 'unsafe-inline'` | Self styles + inline (for theme CSS variables) |
| `img-src` | `'self' data:` | Self images + inline SVG data URIs |
| `font-src` | `'self'` | Self-hosted fonts only (no Google CDN) |
| `connect-src` | `'self'` | Same-origin fetch/XHR only |
| `frame-ancestors` | `'none'` | Cannot be embedded (clickjacking protection) |
| `base-uri` | `'self'` | Prevent base tag injection |
| `form-action` | `'self'` | Forms submit only to same origin |
| `upgrade-insecure-requests` | - | Force HTTPS for any HTTP resources |

### Inline Script Hash

The theme detection script is allowed via CSP hash:
- **Hash:** `sha256-WX4a73Q06DtD4MP8BNJwtJf9CJ0IIXsYXadYwOvXEi8=`
- **Script:** `(function(){var s=localStorage.getItem("oet-theme-preference");var p=window.matchMedia("(prefers-color-scheme: dark)").matches;if(s==="dark"||(!s&&p)){document.documentElement.classList.add("dark-mode");}})()`

---

## 2. Security Meta Tags Applied

All 21 HTML pages now include:

```html
<!-- Content Security Policy -->
<meta http-equiv="Content-Security-Policy" content="...">

<!-- Prevent MIME type sniffing -->
<meta http-equiv="X-Content-Type-Options" content="nosniff">

<!-- Prevent clickjacking -->
<meta http-equiv="X-Frame-Options" content="DENY">

<!-- Limit referrer information leakage -->
<meta name="referrer" content="strict-origin-when-cross-origin">

<!-- Disable unused browser features -->
<meta http-equiv="Permissions-Policy" content="accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()">
```

---

## 3. GitHub Pages Limitations

### Headers That Cannot Be Set via Meta Tags

| Header | Purpose | Workaround |
|--------|---------|------------|
| `Strict-Transport-Security` | HSTS | GitHub Pages provides automatically |
| `X-Content-Type-Options` | MIME sniffing | Meta tag (limited browser support) |
| `Cross-Origin-Opener-Policy` | Cross-origin isolation | Cannot be set on GH Pages |
| `Cross-Origin-Embedder-Policy` | Resource isolation | Cannot be set on GH Pages |
| `Cross-Origin-Resource-Policy` | Resource sharing | Cannot be set on GH Pages |

### For Full Header Control

To get complete security header enforcement, consider:

1. **Cloudflare (free tier):**
   - Add as proxy in front of GitHub Pages
   - Configure headers via Transform Rules

2. **Netlify:**
   - Use `_headers` file in repository root
   - Full header control

3. **Vercel:**
   - Use `vercel.json` configuration
   - Full header control

---

## 4. Changes Made

### Files Created

| File | Purpose |
|------|---------|
| `docs/THREAT-MODEL.md` | Comprehensive threat analysis |
| `docs/ai-security.md` | AI security policy and prompt injection resistance |
| `docs/SECURITY-HARDENING.md` | This summary document |
| `_config.yml` | Jekyll configuration |
| `_includes/head.html` | Centralized head with security headers |
| `_includes/security-headers.html` | Security meta tags include |
| `_layouts/default.html` | Base layout template |
| `css/fonts.css` | Self-hosted font definitions |
| `fonts/README.md` | Font download instructions |
| `scripts/download-fonts.sh` | Font download automation |
| `scripts/security-lint.sh` | Security linting script |
| `scripts/update-security.py` | Security header update script |
| `.github/workflows/security-audit.yml` | CI security checks |

### Files Modified

All 21 HTML pages updated with:
- Hardened CSP (`default-src 'none'`)
- Script hash for inline theme script
- Permissions-Policy header
- Removed Google Fonts CDN references
- Added fonts.css reference

### Files Removed/Changed

- Removed Google Fonts CDN dependencies (preconnect + stylesheet links)
- Inline scripts standardized and hashed

---

## 5. DOM XSS Audit Results

### JavaScript Analysis

| File | Status | Dangerous Patterns |
|------|--------|--------------------|
| `js/theme.js` | ✅ Safe | None found |

**Verified Safe:**
- No `innerHTML`, `outerHTML`, `insertAdjacentHTML`
- No `document.write`, `eval`, `new Function`
- No `setTimeout/setInterval` with string arguments
- Uses only safe methods: `classList`, `localStorage`, `addEventListener`

### Inline Scripts

| Location | Status | Hash |
|----------|--------|------|
| Theme detection (all pages) | ✅ Hashed | `sha256-WX4a73Q06DtD4MP8BNJwtJf9CJ0IIXsYXadYwOvXEi8=` |

---

## 6. Supply Chain Hardening

### Before (Risks)

- Google Fonts CDN dependency on 6 pages
- External font loading from `fonts.googleapis.com` and `fonts.gstatic.com`
- No SRI on external resources

### After (Hardened)

- All fonts self-hosted from `/fonts/` directory
- No external CDN dependencies
- CSP `font-src 'self'` blocks all external fonts
- Font files to be downloaded with provided script

### Font Files Required

```
fonts/
├── crimson-pro-v24-latin-regular.woff2
├── crimson-pro-v24-latin-600.woff2
├── crimson-pro-v24-latin-700.woff2
├── crimson-pro-v24-latin-italic.woff2
├── crimson-pro-v24-latin-600italic.woff2
├── source-sans-3-v15-latin-regular.woff2
├── source-sans-3-v15-latin-600.woff2
└── source-sans-3-v15-latin-700.woff2
```

---

## 7. CI Security Checks

### Workflow: `.github/workflows/security-audit.yml`

Runs on every push and PR with the following checks:

| Check | Purpose | Fail Condition |
|-------|---------|----------------|
| CSP Validation | Verify all pages have CSP | Missing CSP meta tag |
| JS Security Audit | Scan for dangerous patterns | `innerHTML`, `eval`, etc. |
| External Script Check | Verify SRI on external scripts | External scripts without SRI |
| Inline Script Audit | Flag unapproved inline scripts | Non-theme inline scripts |
| Link Security | Verify `rel="noopener"` | Missing on `target="_blank"` |
| Dependency Check | External resource audit | Non-font external resources |

---

## 8. Operator Checklist for Future Updates

### When Adding New Pages

- [ ] Use the Jekyll layout (`_layouts/default.html`) or copy security headers
- [ ] Ensure CSP meta tag is present
- [ ] Verify inline script hash matches if modified

### When Adding JavaScript

- [ ] No `innerHTML`, `eval`, or other dangerous sinks
- [ ] Add file to `script-src` in CSP if external
- [ ] Add SRI hash if loading from CDN (avoid if possible)
- [ ] Run `scripts/security-lint.sh` before commit

### When Adding External Resources

- [ ] Prefer self-hosting over CDN
- [ ] If CDN required: add SRI hash
- [ ] Update CSP to allow specific domain
- [ ] Document in threat model

### When Modifying Inline Scripts

- [ ] Recompute SHA256 hash: `echo -n 'script content' | openssl dgst -sha256 -binary | openssl base64`
- [ ] Update CSP `script-src` with new hash
- [ ] Update all HTML files with new hash

### Before Any Release

- [ ] Run `scripts/security-lint.sh`
- [ ] Verify CI checks pass
- [ ] Review any new external dependencies
- [ ] Check for leaked secrets/credentials

### When Adding AI Features

- [ ] Review `docs/ai-security.md` thoroughly
- [ ] Implement instruction hierarchy
- [ ] Add input sanitization
- [ ] Add output filtering
- [ ] Run red team tests
- [ ] Security review before launch

---

## 9. Security Contacts

- **Security Issues:** security@orderoftechnologists.org
- **Security.txt:** `/.well-known/security.txt`
- **Policy:** `/transparency.html`

---

## 10. Appendix: Full File List

### Security Documentation
- `docs/THREAT-MODEL.md` - Threat model and attack surface analysis
- `docs/ai-security.md` - AI security policy and prompt injection resistance
- `docs/SECURITY-HARDENING.md` - This document

### Jekyll Templates
- `_config.yml` - Site configuration
- `_includes/head.html` - Head section with security headers
- `_includes/security-headers.html` - Security meta tags
- `_layouts/default.html` - Base layout

### Scripts
- `scripts/download-fonts.sh` - Download self-hosted fonts
- `scripts/security-lint.sh` - Security linting
- `scripts/update-security.py` - Bulk security updates

### CI/CD
- `.github/workflows/security-audit.yml` - Security checks on PR

### Assets
- `css/fonts.css` - Self-hosted font definitions
- `fonts/README.md` - Font setup instructions

---

*Document maintained by: The Order of Ethical Technologists*
*Last Updated: 2025-12-31*

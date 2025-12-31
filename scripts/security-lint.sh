#!/bin/bash
# Security Linting Script for Order of Ethical Technologists
# Checks for common security issues in static site

set -e

REPORT_FILE="security-report.txt"
ERRORS=0
WARNINGS=0

# Colors for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $1" >> "$REPORT_FILE"
    ((ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo "[WARN] $1" >> "$REPORT_FILE"
    ((WARNINGS++))
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
    echo "[OK] $1" >> "$REPORT_FILE"
}

# Initialize report
echo "Security Lint Report - $(date)" > "$REPORT_FILE"
echo "================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "Starting security lint..."
echo ""

# ============================================
# 1. CSP Meta Tag Check
# ============================================
echo "=== Checking CSP Meta Tags ==="

for file in $(find . -name "*.html" -not -path "./_site/*" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./_includes/*" -not -path "./_layouts/*"); do
    if grep -q 'Content-Security-Policy' "$file"; then
        # Check for strict CSP directives
        if ! grep -q "default-src 'none'" "$file" && ! grep -q "default-src 'self'" "$file"; then
            log_warning "$file: CSP missing strict default-src directive"
        fi

        if grep -q "unsafe-eval" "$file"; then
            log_error "$file: CSP contains unsafe-eval (security risk)"
        fi

        # unsafe-inline for styles is acceptable but not for scripts
        # Extract script-src value and check specifically for unsafe-inline in it
        if grep -oP "script-src[^;]*" "$file" | grep -q "unsafe-inline"; then
            log_error "$file: CSP allows unsafe-inline for scripts (use hashes instead)"
        fi
    else
        log_error "$file: Missing Content-Security-Policy meta tag"
    fi
done

echo ""

# ============================================
# 2. X-Frame-Options Check
# ============================================
echo "=== Checking Clickjacking Protection ==="

for file in $(find . -name "*.html" -not -path "./_site/*" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./_includes/*" -not -path "./_layouts/*"); do
    if ! grep -q 'X-Frame-Options' "$file" && ! grep -q "frame-ancestors 'none'" "$file"; then
        log_warning "$file: Missing clickjacking protection (X-Frame-Options or frame-ancestors)"
    fi
done

echo ""

# ============================================
# 3. JavaScript Security Patterns
# ============================================
echo "=== Checking JavaScript for Dangerous Patterns ==="

DANGEROUS_PATTERNS=(
    "\.innerHTML\s*="
    "\.outerHTML\s*="
    "insertAdjacentHTML"
    "document\.write"
    "eval\s*\("
    "new\s+Function\s*\("
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    MATCHES=$(grep -rln "$pattern" --include="*.js" . 2>/dev/null || true)
    if [ -n "$MATCHES" ]; then
        log_error "Dangerous pattern '$pattern' found in: $MATCHES"
    fi
done

# Check for setTimeout/setInterval with string arguments
TIMEOUT_STRINGS=$(grep -rEn "setTimeout\s*\(\s*['\"]|setInterval\s*\(\s*['\"]" --include="*.js" . 2>/dev/null || true)
if [ -n "$TIMEOUT_STRINGS" ]; then
    log_error "setTimeout/setInterval with string argument (eval-like): $TIMEOUT_STRINGS"
fi

echo ""

# ============================================
# 4. External Resource Check
# ============================================
echo "=== Checking External Resources ==="

# External scripts
EXT_SCRIPTS=$(grep -rEn '<script[^>]+src=["\x27]https?://' --include="*.html" . 2>/dev/null || true)
if [ -n "$EXT_SCRIPTS" ]; then
    # Check for SRI
    NO_SRI=$(echo "$EXT_SCRIPTS" | grep -v 'integrity=' || true)
    if [ -n "$NO_SRI" ]; then
        log_error "External scripts without SRI: $NO_SRI"
    else
        log_warning "External scripts found (with SRI): check if self-hosting is preferred"
    fi
fi

# External iframes
EXT_IFRAMES=$(grep -rEn '<iframe[^>]+src=' --include="*.html" . 2>/dev/null || true)
if [ -n "$EXT_IFRAMES" ]; then
    log_warning "Iframe embeds found (ensure these are necessary): $EXT_IFRAMES"
fi

echo ""

# ============================================
# 5. Inline Script Check
# ============================================
echo "=== Checking Inline Scripts ==="

# Find inline scripts
INLINE_SCRIPTS=$(grep -rEn '<script>[^<]+</script>' --include="*.html" . 2>/dev/null \
    | grep -v '_includes/' \
    | grep -v '_layouts/' \
    || true)

if [ -n "$INLINE_SCRIPTS" ]; then
    # Check if they're the approved theme detection script
    UNAPPROVED=$(echo "$INLINE_SCRIPTS" | grep -v 'oet-theme-preference' || true)
    if [ -n "$UNAPPROVED" ]; then
        log_warning "Inline scripts found (ensure CSP hash is configured): $UNAPPROVED"
    fi
fi

echo ""

# ============================================
# 6. Form Security Check
# ============================================
echo "=== Checking Form Security ==="

FORMS=$(grep -rEn '<form[^>]*>' --include="*.html" . 2>/dev/null || true)
if [ -n "$FORMS" ]; then
    # Check for CSRF protection indicators
    NO_CSRF=$(echo "$FORMS" | grep -v 'csrf' | grep -v 'token' || true)
    if [ -n "$NO_CSRF" ]; then
        log_warning "Forms found without apparent CSRF tokens (review if needed)"
    fi

    # Check action attributes
    EXT_ACTION=$(echo "$FORMS" | grep -E 'action=["\x27]https?://' || true)
    if [ -n "$EXT_ACTION" ]; then
        log_warning "Forms with external action URLs: $EXT_ACTION"
    fi
fi

echo ""

# ============================================
# 7. Referrer Policy Check
# ============================================
echo "=== Checking Referrer Policy ==="

for file in $(find . -name "*.html" -not -path "./_site/*" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./_includes/*" -not -path "./_layouts/*"); do
    if ! grep -q 'referrer' "$file"; then
        log_warning "$file: Missing Referrer-Policy meta tag"
    fi
done

echo ""

# ============================================
# 8. Link Security Check
# ============================================
echo "=== Checking Link Security ==="

# Check target="_blank" without noopener
UNSAFE_BLANKS=$(grep -rEn 'target=["\x27]_blank["\x27]' --include="*.html" . 2>/dev/null \
    | grep -v 'rel=.*noopener' \
    || true)

if [ -n "$UNSAFE_BLANKS" ]; then
    log_warning "Links with target=_blank missing rel='noopener': $UNSAFE_BLANKS"
fi

echo ""

# ============================================
# 9. Sensitive Data Check
# ============================================
echo "=== Checking for Sensitive Data ==="

# Check for potential secrets
POTENTIAL_SECRETS=$(grep -rEin '(api[_-]?key|password|secret|token|credential)\s*[=:]' --include="*.js" --include="*.html" --include="*.json" . 2>/dev/null \
    | grep -v 'node_modules' \
    | grep -v 'package-lock' \
    || true)

if [ -n "$POTENTIAL_SECRETS" ]; then
    log_error "Potential hardcoded secrets found: $POTENTIAL_SECRETS"
fi

# Check for .env files
if [ -f ".env" ] || [ -f ".env.local" ]; then
    log_error ".env file found in repository (should be in .gitignore)"
fi

echo ""

# ============================================
# Summary
# ============================================
echo "=== Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""
echo "Summary" >> "$REPORT_FILE"
echo "=======" >> "$REPORT_FILE"
echo "Errors: $ERRORS" >> "$REPORT_FILE"
echo "Warnings: $WARNINGS" >> "$REPORT_FILE"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Security lint failed with $ERRORS error(s)${NC}"
    exit 1
else
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}Security lint passed with $WARNINGS warning(s)${NC}"
    else
        echo -e "${GREEN}Security lint passed with no issues${NC}"
    fi
    exit 0
fi

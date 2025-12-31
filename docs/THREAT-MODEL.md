# Threat Model: Order of Ethical Technologists Website

**Document Version:** 1.0
**Last Updated:** 2025-12-31
**Classification:** Public

---

## 1. System Overview

**Type:** Static HTML/CSS/JS website
**Hosting:** GitHub Pages
**Purpose:** Informational site for faith leaders and technologists interested in ethical AI
**Attack Surface:** Minimal - no user input forms, no backend, no authentication

### Asset Inventory

| Asset | Type | Location | External Dependencies |
|-------|------|----------|----------------------|
| 21 HTML pages | Static content | Root and subdirectories | None |
| style.css | Stylesheet | /css/ | None |
| fonts.css | Font styles | /css/ | None |
| Fonts | Typography | /fonts/ (self-hosted) | None |

---

## 2. Attack Surfaces

### 2.1 Static Content
- **Surface:** HTML files served from GitHub Pages CDN
- **Risk Level:** Low
- **Vectors:** GitHub account compromise, DNS hijacking, CDN cache poisoning

### 2.2 JavaScript
- **Surface:** None - pure static HTML/CSS site
- **Risk Level:** None
- **Current Status:** ✓ No JavaScript loaded

### 2.3 External Resources
- **Surface:** None - all fonts self-hosted
- **Risk Level:** None
- **Current Status:** ✓ No external dependencies

### 2.4 User Interactions
- **Surface:** Links, mobile navigation
- **Risk Level:** Very Low
- **Vectors:** Limited - no forms, no user input processing

### 2.5 Embeddability
- **Surface:** Site can potentially be embedded in iframes
- **Risk Level:** Medium (without protections)
- **Vectors:** Clickjacking, UI redress attacks

---

## 3. Threat Analysis

### 3.1 Cross-Site Scripting (XSS)

| Sub-Type | Risk | Likelihood | Impact | Mitigation |
|----------|------|------------|--------|------------|
| Stored XSS | N/A | N/A | N/A | No user-generated content |
| Reflected XSS | Low | Very Low | Medium | CSP blocks inline scripts |
| DOM XSS | Low | Low | High | No innerHTML/eval usage; CSP script-src |

**Mitigations Implemented:**
- CSP `script-src 'self'` blocks external and inline scripts
- No JavaScript loaded - pure static HTML/CSS
- No dynamic HTML injection
- No URL parameter processing

### 3.2 Supply Chain Attacks

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| External CDN compromise | N/A | N/A | N/A | All resources self-hosted |
| GitHub account compromise | Medium | Very Low | Critical | 2FA, branch protection, signed commits |
| Malicious dependency injection | N/A | N/A | N/A | No npm/package dependencies |

**Mitigations Implemented:**
- Self-host fonts to eliminate Google CDN dependency
- No external JavaScript dependencies
- SRI (Subresource Integrity) on all external resources
- CSP restricts allowed sources

### 3.3 Clickjacking / UI Redress

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| Iframe embedding | Medium | Low | Medium | frame-ancestors 'none' |
| Invisible overlay attacks | Low | Very Low | Low | X-Frame-Options DENY |

**Mitigations Implemented:**
- CSP `frame-ancestors 'none'`
- `X-Frame-Options: DENY` meta tag
- No sensitive actions to protect

### 3.4 Mixed Content / Downgrade Attacks

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| HTTP resource loading | Low | Very Low | Medium | GitHub Pages forces HTTPS |
| Protocol downgrade | Low | Very Low | Medium | HSTS preload (via GitHub) |

**Mitigations Implemented:**
- All resources use HTTPS
- GitHub Pages provides HSTS
- CSP `upgrade-insecure-requests` directive

### 3.5 Referrer Leakage

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| Full URL in Referer header | Low | Medium | Low | Referrer-Policy: strict-origin-when-cross-origin |
| Query parameter exposure | N/A | N/A | N/A | No query parameters used |

**Mitigations Implemented:**
- `Referrer-Policy: strict-origin-when-cross-origin`
- No sensitive data in URLs

### 3.6 Cache Poisoning / Stale Assets

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| CDN cache poisoning | Low | Very Low | Medium | GitHub Pages controls caching |
| Browser cache manipulation | Very Low | Very Low | Low | Proper cache headers |

**Mitigations Implemented:**
- GitHub Pages manages cache invalidation
- Static assets with version control

### 3.7 Content Injection via Markdown/HTML

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| Malicious content in source | Medium | Very Low | High | Code review, PR approval |
| Script injection via contributor | Medium | Very Low | High | CSP blocks execution |

**Mitigations Implemented:**
- CSP prevents script execution from injected content
- No dynamic content rendering
- All content is version-controlled

---

## 4. AI-Specific Threats (Future Readiness)

### 4.1 Prompt Injection

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| Untrusted content as instructions | High | High | Critical | Input/output isolation |
| Indirect injection via page content | High | Medium | High | Content sanitization |
| Model instruction override | High | Medium | Critical | System prompt hierarchy |

**Mitigations Documented:**
- See `docs/ai-security.md` for comprehensive AI security policy
- No AI features currently implemented
- Scaffolding in place for secure future implementation

### 4.2 Data Exfiltration via AI

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| Model leaking system prompts | Medium | Medium | Medium | Output filtering |
| Credential exposure | High | Low | Critical | No credentials in AI context |

### 4.3 Tool Misuse

| Vector | Risk | Likelihood | Impact | Mitigation |
|--------|------|------------|--------|------------|
| AI executing unintended actions | High | Medium | High | Tool allowlists, confirmation |
| Privilege escalation via tools | High | Low | Critical | Least privilege design |

---

## 5. GitHub Pages Constraints

### Headers That Cannot Be Set

| Header | Purpose | Workaround |
|--------|---------|------------|
| `Strict-Transport-Security` | HSTS | GitHub provides HSTS by default |
| `X-Content-Type-Options` | MIME sniffing | Meta tag (limited effectiveness) |
| `Permissions-Policy` | Feature restrictions | Meta tag (partial support) |
| `Cross-Origin-Opener-Policy` | Cross-origin isolation | Cannot be set |
| `Cross-Origin-Embedder-Policy` | Resource isolation | Cannot be set |
| `Cross-Origin-Resource-Policy` | Resource sharing | Cannot be set |

### Headers That CAN Be Set via Meta Tags

| Header | Implementation | Effectiveness |
|--------|----------------|---------------|
| `Content-Security-Policy` | `<meta http-equiv>` | Most directives work except `frame-ancestors`, `report-uri`, `sandbox` |
| `X-Frame-Options` | `<meta http-equiv>` | Widely supported |
| `Referrer-Policy` | `<meta name>` | Full support |

### Recommendation for Full Header Control

For complete security header enforcement, consider:
1. **Cloudflare** (free tier) - Proxy with custom headers
2. **Netlify** - `_headers` file support
3. **Vercel** - `vercel.json` configuration
4. **Custom reverse proxy** - Full control

---

## 6. Mitigation Summary

| Threat | Severity | Mitigation | Status |
|--------|----------|------------|--------|
| XSS via inline script | High | CSP script-src 'self' (no inline) | ✓ Implemented |
| DOM XSS | N/A | No JavaScript loaded | ✓ N/A |
| Clickjacking | Medium | frame-ancestors 'none' | ✓ Implemented |
| Supply chain (fonts) | Medium | Self-hosted fonts | ✓ Implemented |
| Supply chain (JS) | N/A | No JavaScript | ✓ N/A |
| Referrer leakage | Low | Referrer-Policy | ✓ Implemented |
| Mixed content | Low | HTTPS-only | ✓ GitHub enforces |
| Cache poisoning | Low | GitHub CDN controls | ✓ GitHub manages |
| Prompt injection (future) | High | Policy documented | ✓ Documented |

---

## 7. Residual Risks

1. **GitHub Account Compromise:** If attacker gains access to GitHub account, they can modify site content. Mitigate with 2FA, branch protection rules.

2. **DNS Hijacking:** If DNS is compromised, attacker could redirect traffic. Mitigate with DNSSEC (if available).

3. **Zero-Day Browser Vulnerabilities:** CSP cannot protect against browser vulnerabilities. Keep browsers updated.

4. **Social Engineering:** Users could be tricked into actions outside the site. Document awareness.

---

## 8. Monitoring & Response

### Detection Mechanisms
- GitHub security alerts for repository
- Branch protection and required reviews
- CI/CD security linting on every PR

### Incident Response
1. **Contact:** security@orderoftechnologists.org
2. **Security.txt:** /.well-known/security.txt
3. **Response Time:** As documented in security.txt

---

## 9. Review Schedule

- **Quarterly:** Review threat model for new attack vectors
- **On Change:** Re-assess when adding features (especially AI)
- **Annually:** Full security audit

---

*Document maintained by: The Order of Ethical Technologists Security Team*

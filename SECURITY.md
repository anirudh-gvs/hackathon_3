# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting Security Vulnerabilities

We take the security of Offline DocScan seriously. If you discover a security vulnerability, please follow these guidelines:

### How to Report

**Please do NOT report security vulnerabilities through public GitHub/GitLab issues, discussions, or pull requests.**

Instead, please report security vulnerabilities by emailing the maintainers at:

**Email**: security@example.com (replace with actual security contact)

### What to Include

When reporting a vulnerability, please include:

1. **Description**: Clear description of the vulnerability
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Impact**: Potential impact and severity assessment
4. **Affected Versions**: Which versions are affected
5. **Suggested Fix**: If you have suggestions for fixing the issue
6. **Your Contact Information**: For follow-up questions

### Example Report

```markdown
Subject: Security Vulnerability in [Component]

Description:
[Clear description of the vulnerability]

Steps to Reproduce:
1. [First step]
2. [Second step]
3. [See the vulnerability]

Impact:
[What an attacker could do]

Affected Versions:
- 0.1.0
- 0.1.1

Suggested Fix:
[If available]
```

## Responsible Disclosure Process

### Our Commitment

We are committed to:

1. **Acknowledging** receipt of your vulnerability report within 3 business days
2. **Providing** an initial assessment of the report within 7 business days
3. **Keeping** you informed of progress throughout the remediation process
4. **Crediting** you for the discovery (unless you prefer to remain anonymous)
5. **Not taking** legal action against researchers who follow this policy

### Disclosure Timeline

| Phase | Timeline | Action |
|-------|----------|--------|
| Acknowledgment | 3 business days | Confirm receipt of report |
| Initial Assessment | 7 business days | Evaluate severity and validity |
| Remediation | Varies | Develop and test fix |
| Release | 30-90 days | Coordinate public disclosure |
| Credit | At release | Acknowledge contributor (if desired) |

### Coordinated Disclosure

We follow a coordinated disclosure process:

1. **Report Received**: We acknowledge your report
2. **Validation**: We confirm the vulnerability
3. **Remediation**: We develop a fix
4. **Testing**: We test the fix thoroughly
5. **Release**: We release a patched version
6. **Public Disclosure**: We publish a security advisory
7. **Credit**: We credit the reporter (with permission)

## Confidentiality Policy

### Our Commitment

- We will keep your report confidential and will not share your personal information without your consent
- We will not share details of the vulnerability publicly until a fix is available
- We will work with you to determine the appropriate disclosure timeline

### Your Commitment

- We ask that you do not publicly disclose the vulnerability until we have had a chance to address it
- We ask that you do not exploit the vulnerability beyond what is necessary to demonstrate it
- We ask that you do not access or modify data that does not belong to you

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version of Offline DocScan
2. **Verify Checksums**: Verify the integrity of downloaded models and files
3. **Secure Storage**: Store scanned documents in secure locations
4. **Model Sources**: Only download models from trusted sources
5. **System Security**: Keep your operating system and dependencies updated

### For Contributors

1. **No Secrets**: Never commit API keys, tokens, or credentials
2. **Input Validation**: Always validate and sanitize user input
3. **Dependencies**: Keep dependencies up to date and audit for vulnerabilities
4. **Code Review**: All code changes require review
5. **Testing**: Write tests for security-critical functionality

## Scope of Security Issues

### In Scope

- Security vulnerabilities in the codebase
- Dependency vulnerabilities (when reported with a fix)
- Documentation that could lead to security issues
- CI/CD pipeline security issues
- Model loading and handling issues

### Out of Scope

- Issues in third-party dependencies without a known fix
- Theoretical vulnerabilities without practical exploitation
- Social engineering attacks
- Physical security of user devices
- Network security of user environments

## Security Update Process

### When a Vulnerability is Found

1. **Private Branch**: We create a private branch for the fix
2. **Patch Development**: We develop and test the patch
3. **Version Bump**: We prepare a new release version
4. **Security Advisory**: We draft a security advisory (private)
5. **Release**: We release the patched version
6. **Advisory Publication**: We publish the security advisory
7. **Credit**: We credit the reporter (if desired)

### Communication

- We will notify users through:
  - GitLab security advisories
  - CHANGELOG.md
  - Release notes
  - Project mailing list (if available)

## Secret Scanning

### Automated Secret Detection

We use multiple tools to prevent accidental secret commits:

#### 1. Gitleaks

**Purpose**: Detect secrets, credentials, and sensitive data in code

**What it scans for**:
- API keys (AWS, Azure, Google Cloud, etc.)
- Authentication tokens (GitHub, GitLab, Slack, etc.)
- Database credentials
- Private keys (SSH, RSA, EC)
- Passwords and secrets
- OAuth tokens
- And 100+ other secret types

**Configuration**: `.gitleaks.toml`
- Custom rules for Python code
- Allowlist for false positives
- Redaction enabled in reports
- Scans: docscan/, tests/, scripts/

**CI/CD Integration**:
- Job: `secret-scanning-gitleaks`
- Stage: security
- Runs on: merge_requests, main, develop
- Fails pipeline if secrets detected
- Generates JSON report with redacted secrets

**Local Usage**:
```bash
# Install Gitleaks
pip install gitleaks

# Run secret scan
gitleaks detect --config=.gitleaks.toml --source=. --report-path=gitleaks-report.json --report-format=json --redact

# Review report
cat gitleaks-report.json
```

#### 2. Semgrep Secrets Detection

**Purpose**: Pattern-based secret detection with community rules

**Configuration**: `.semgrep.yml`
- Includes: `https://semgrep.dev/r/secrets`
- Custom rules for hardcoded credentials
- OWASP Top 10 coverage

**Local Usage**:
```bash
semgrep --config=.semgrep.yml --error docscan/
```

#### 3. Custom Secret Scanning

**Purpose**: Project-specific secret validation

**Script**: `docscan/ci_checks.py secrets`
- Custom validation logic
- Project-specific patterns
- Integration with CI/CD

### Secret Management Best Practices

#### For Developers

1. **Never commit secrets**:
   - API keys
   - Passwords
   - Private keys
   - Tokens
   - Database credentials
   - OAuth secrets

2. **Use environment variables**:
   ```python
   # Good
   api_key = os.getenv("API_KEY")
   
   # Bad
   api_key = "sk-1234567890abcdef"
   ```

3. **Use .env files**:
   - Store in `.env` (gitignored)
   - Use `.env.example` for documentation
   - Never commit `.env`

4. **Use secret management tools**:
   - GitLab CI/CD variables
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault

#### If You Accidentally Commit a Secret

1. **Immediate Actions**:
   - Rotate the compromised secret immediately
   - Revoke the exposed credential
   - Generate new keys/tokens

2. **Remove from Git History**:
   ```bash
   # Use git-filter-repo or BFG Repo-Cleaner
   # WARNING: This rewrites git history
   git filter-repo --path <file-with-secret> --invert-paths
   ```

3. **Notify the Team**:
   - Contact security@example.com
   - Document the incident
   - Update SECURITY.md if needed

4. **Prevent Future Occurrences**:
   - Review Gitleaks configuration
   - Add patterns to allowlist if false positive
   - Update pre-commit hooks

### Pre-commit Secret Scanning

Install pre-commit hooks to catch secrets before commit:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# The hooks will automatically:
# - Run Gitleaks
# - Run Semgrep
# - Check for common secret patterns
```

### Secret Scanning Reports

#### CI/CD Reports

- **Gitleaks**: `gitleaks-report.json` (artifact, 1 week retention)
- **Semgrep**: `semgrep-results.sarif` (artifact, 1 week retention)
- **Custom**: Console output from `docscan/ci_checks.py secrets`

#### Reviewing Reports

1. Check pipeline artifacts
2. Review redacted secrets
3. Verify if false positive
4. Update allowlist if needed
5. Fix actual leaks immediately

### Compliance

Our secret scanning ensures compliance with:

- **OWASP Top 10**: A03:2021 – Injection (preventing credential exposure)
- **CWE-798**: Use of Hard-coded Credentials
- **CWE-259**: Use of Hard-coded Password
- **SOC 2**: CC6.1 – Logical Access Security
- **GDPR**: Article 32 – Security of Processing
- **PCI DSS**: Requirement 6.5 – Protect sensitive data

### Security Checklist for Releases

Before each release, verify:

- [ ] Gitleaks scan passes (no secrets found)
- [ ] Semgrep secrets scan passes
- [ ] Custom secret scan passes
- [ ] No secrets in git history
- [ ] All credentials rotated
- [ ] .gitignore includes .env and sensitive files
- [ ] Documentation uses placeholders, not real secrets
- [ ] CI/CD uses protected variables, not hardcoded values

## Known Security Considerations

### Offline-First Design

Offline DocScan is designed to work completely offline, which provides inherent security benefits:

- **No Data Transmission**: Documents never leave your device
- **No Network Dependencies**: No risk of man-in-the-middle attacks
- **Local Processing**: Full control over data processing

### Model Files

- GGUF model files are large binary files (~2-4GB)
- Only download models from trusted sources
- Verify model checksums when available
- Store models in secure locations

### File Processing

- The tool processes user-provided files (PDFs, images, text)
- Malicious files could potentially exploit vulnerabilities in:
  - pdfplumber (PDF parsing)
  - pytesseract (OCR)
  - Pillow (image processing)
- Always scan files with antivirus software before processing

### Dependencies

Key dependencies and their security considerations:

- **llama-cpp-python**: Local LLM inference, no network calls
- **pdfplumber**: PDF text extraction, validate input files
- **pytesseract**: OCR engine, requires Tesseract installation
- **Pillow**: Image processing, handle malformed images gracefully
- **pydantic**: Data validation, helps prevent injection attacks

## Security Checklist for Releases

Before each release, we verify:

- [ ] All dependencies are up to date
- [ ] No known vulnerabilities in dependencies (pip-audit)
- [ ] No secrets in codebase (secret scanning)
- [ ] All tests pass
- [ ] Code review completed
- [ ] Security-sensitive changes documented
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated

## Contact Information

### Security Team

- **Email**: security@example.com (replace with actual contact)
- **Response Time**: 3 business days for acknowledgment
- **PGP Key**: [Link to PGP public key if available]

### General Contact

- **Repository**: https://code.swecha.org/Gvs_Anirudh/cpu_first_hackathon
- **Issues**: https://code.swecha.org/Gvs_Anirudh/cpu_first_hackathon/-/issues
- **Team**: CPU First Hackathon Team

## Attribution

This security policy is inspired by:

- [GitHub Security Policy](https://github.com/github/security)
- [Mozilla Security Bug Handling](https://www.mozilla.org/en-US/security/bug-handling/)
- [OWASP Responsible Disclosure](https://owasp.org/www-project-responsible-disclosure/)

---

**Last Updated**: 2024
**Version**: 0.1.0
**Maintainer**: DocScan Security Team
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug'
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Command used: `python csvcdc.py ...`
2. Input files (if possible, provide sample data)
3. Expected output
4. Actual output

**Sample Data**
If possible, provide minimal sample CSV files that reproduce the issue:

```csv
# base.csv
id,name,value
1,item1,100

# delta.csv  
id,name,value
1,item1,200
```

**Error Output**
```
Paste any error messages or unexpected output here
```

**Environment (please complete the following information):**
 - OS: [e.g. Ubuntu 20.04, Windows 10, macOS 12]
 - Python version: [e.g. 3.9.1]
 - CSV CDC version: [e.g. 1.0.0]
 - File sizes: [e.g. base: 100MB, delta: 105MB]

**Additional context**
Add any other context about the problem here.
```

## .github/ISSUE_TEMPLATE/feature_request.md

```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: 'enhancement'
assignees: ''

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Use case**
Describe the specific use case for this feature. How would you use it?

**Additional context**
Add any other context or screenshots about the feature request here.
```

## .github/PULL_REQUEST_TEMPLATE.md

```markdown
## Description
Brief description of the changes in this PR.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested this with various CSV file sizes and formats

## Test Data
If applicable, describe the test data used:
- File sizes: 
- Record counts:
- Primary key types:
- Special characters/encodings:

## Checklist
- [ ] My code follows the code style of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] Any dependent changes have been merged and published

## Performance Impact
If applicable, describe any performance implications:
- Memory usage change:
- Processing speed change:
- File size limits:

## Screenshots/Output
If applicable, add screenshots or example output to help explain your changes.
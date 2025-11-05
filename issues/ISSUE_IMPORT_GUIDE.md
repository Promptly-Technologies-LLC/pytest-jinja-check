# GitHub Issues Import Guide

This directory contains detailed issue specifications for the jinja2-validator project.

## Issue Organization

```
issues/
├── mvp/                        # v0.1.0 - MVP Release
│   ├── 01-package-structure.md
│   ├── 02-cli-tool.md
│   ├── 03-syntax-validation.md
│   ├── 04-test-suite.md
│   ├── 05-documentation.md
│   └── 06-pypi-publishing.md
│
├── runtime-validation/         # v0.2.0 - Runtime Validation (Killer Feature)
│   ├── 07-runtime-decorator.md
│   ├── 08-fastapi-integration.md
│   └── 09-flask-integration.md
│
└── advanced-analysis/          # v0.3.0 - Advanced Features
    ├── 10-hardcoded-routes.md
    └── 11-type-inference.md
```

## How to Import Issues to GitHub

### Option 1: Manual Creation (Recommended for Review)

1. Go to your repository on GitHub
2. Click "Issues" → "New Issue"
3. Copy the content from each markdown file
4. Extract and fill in:
   - **Title**: From the `title:` field in the frontmatter
   - **Labels**: From the `labels:` field
   - **Milestone**: From the `milestone:` field
   - **Body**: Everything after the frontmatter (after `---`)
5. Repeat for each issue file

### Option 2: GitHub CLI

```bash
# Install GitHub CLI if needed
# https://cli.github.com/

# Authenticate
gh auth login

# Create issues from markdown files
for file in issues/mvp/*.md; do
    gh issue create --title "$(grep '^title:' $file | cut -d' ' -f2-)" \
                    --body-file <(sed '1,/^---$/d;/^---$/,$d' $file) \
                    --label "$(grep '^labels:' $file | cut -d' ' -f2-)" \
                    --milestone "$(grep '^milestone:' $file | cut -d' ' -f2)"
done
```

### Option 3: Python Script

```python
#!/usr/bin/env python3
"""
Import issues to GitHub from markdown files.
"""

import re
import subprocess
from pathlib import Path

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = match.group(1)
    body = match.group(2)

    metadata = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    metadata['body'] = body.strip()
    return metadata

def create_issue(metadata: dict):
    """Create GitHub issue using gh CLI."""
    cmd = [
        'gh', 'issue', 'create',
        '--title', metadata['title'],
        '--body', metadata['body'],
    ]

    if 'labels' in metadata:
        cmd.extend(['--label', metadata['labels']])

    if 'milestone' in metadata:
        cmd.extend(['--milestone', metadata['milestone']])

    subprocess.run(cmd)

def main():
    # Import all issues
    for issue_file in Path('issues').rglob('*.md'):
        if issue_file.name == 'ISSUE_IMPORT_GUIDE.md':
            continue

        print(f"Creating issue from {issue_file}...")
        with open(issue_file) as f:
            content = f.read()

        metadata = parse_frontmatter(content)
        if metadata:
            create_issue(metadata)
            print(f"  ✓ Created: {metadata['title']}")
        else:
            print(f"  ✗ Failed to parse: {issue_file}")

if __name__ == '__main__':
    main()
```

Save as `import_issues.py` and run:
```bash
chmod +x import_issues.py
./import_issues.py
```

## Creating Milestones

Before importing issues, create the milestones:

```bash
# Using GitHub CLI
gh milestone create "v0.1.0" --description "MVP Release - Foundation" --due "2025-02-01"
gh milestone create "v0.2.0" --description "Runtime Validation - Killer Feature" --due "2025-03-01"
gh milestone create "v0.3.0" --description "Advanced Analysis" --due "2025-04-01"
```

Or manually via GitHub UI:
1. Go to Issues → Milestones → New Milestone
2. Create:
   - **v0.1.0**: MVP Release - Foundation
   - **v0.2.0**: Runtime Validation - Killer Feature
   - **v0.3.0**: Advanced Analysis

## Creating Labels

Create these labels before importing:

```bash
# MVP labels
gh label create "mvp" --color "d73a4a" --description "MVP release blocker"
gh label create "infrastructure" --color "0075ca" --description "Build, deploy, tooling"
gh label create "cli" --color "1d76db" --description "Command-line interface"
gh label create "testing" --color "d4c5f9" --description "Testing related"
gh label create "documentation" --color "0075ca" --description "Documentation"

# Feature labels
gh label create "feature" --color "a2eeef" --description "New feature"
gh label create "enhancement" --color "84b6eb" --description "Enhancement to existing feature"

# Framework labels
gh label create "fastapi" --color "009688" --description "FastAPI integration"
gh label create "flask" --color "000000" --description "Flask integration"
gh label create "django" --color "0c4b33" --description "Django integration"

# Technical labels
gh label create "runtime-validation" --color "e99695" --description "Runtime validation feature"
gh label create "static-analysis" --color "f9d0c4" --description "Static analysis"
gh label create "type-checking" --color "c5def5" --description "Type checking and inference"
gh label create "deployment" --color "ededed" --description "Deployment and publishing"

# Priority labels
gh label create "P0" --color "b60205" --description "Critical priority"
gh label create "P1" --color "d93f0b" --description "High priority"
gh label create "P2" --color "fbca04" --description "Medium priority"
gh label create "P3" --color "0e8a16" --description "Low priority"
```

## Issue Priority

**P0 (Critical)**: Must have for the milestone, blocking
**P1 (High)**: Important for the milestone, should have
**P2 (Medium)**: Nice to have, can slip to next milestone
**P3 (Low)**: Future enhancement, not urgent

## Recommended Import Order

1. **Create milestones first** (v0.1.0, v0.2.0, v0.3.0)
2. **Create labels** (see list above)
3. **Import MVP issues** (01-06) - Start with these
4. **Import Runtime Validation issues** (07-09) - After MVP is underway
5. **Import Advanced Analysis issues** (10-11) - For future planning

## After Importing

- [ ] Review each issue for clarity
- [ ] Adjust priorities if needed
- [ ] Assign issues to yourself or team members
- [ ] Link related issues (GitHub auto-links #N)
- [ ] Add any additional context from your original project
- [ ] Create GitHub Project board to track progress
- [ ] Set up issue templates for future contributions

## Project Board Setup

Create a GitHub Project board:

1. Go to "Projects" → "New project"
2. Choose "Board" view
3. Add columns:
   - 📋 Backlog
   - 🎯 Ready
   - 🚧 In Progress
   - 👀 In Review
   - ✅ Done

4. Link issues to the board
5. Set up automation (move to "Done" when closed, etc.)

## Issue Templates

After importing, create issue templates for community contributions:

```markdown
# .github/ISSUE_TEMPLATE/bug_report.md
# .github/ISSUE_TEMPLATE/feature_request.md
# .github/ISSUE_TEMPLATE/question.md
```

See GitHub's documentation: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests

## Tips

- **Review before importing**: Read through each issue to ensure it matches your vision
- **Adjust priorities**: Change P0/P1/P2 based on your actual priorities
- **Add context**: Include any additional context from your original FastAPI project
- **Link issues**: Use "Related to #N" to connect dependent issues
- **Start small**: Focus on MVP issues first, worry about advanced features later

## Need Help?

- GitHub Issues documentation: https://docs.github.com/en/issues
- GitHub CLI documentation: https://cli.github.com/manual/
- Labels best practices: https://robinpowered.com/blog/best-practice-system-for-organizing-and-tagging-github-issues

---

Good luck building jinja2-validator! 🚀

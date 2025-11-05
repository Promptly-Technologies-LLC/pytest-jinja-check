#!/usr/bin/env python3
"""
Import issues to GitHub from markdown files.

Usage:
    python import_issues.py [--dry-run] [--directory DIR]

Requirements:
    - GitHub CLI (gh) installed and authenticated
    - Run from repository root

Example:
    # Dry run to see what would be created
    python import_issues.py --dry-run

    # Actually create issues
    python import_issues.py
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

def parse_frontmatter(content: str) -> Dict[str, str]:
    """
    Extract YAML frontmatter from markdown.

    Args:
        content: Markdown file content

    Returns:
        Dictionary with metadata and body
    """
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

def check_gh_cli():
    """Check if GitHub CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ['gh', 'auth', 'status'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("❌ GitHub CLI not authenticated. Run: gh auth login")
            sys.exit(1)
        print("✓ GitHub CLI authenticated")
    except FileNotFoundError:
        print("❌ GitHub CLI not found. Install from: https://cli.github.com/")
        sys.exit(1)

def create_issue(metadata: Dict[str, str], dry_run: bool = False) -> bool:
    """
    Create GitHub issue using gh CLI.

    Args:
        metadata: Issue metadata (title, body, labels, etc.)
        dry_run: If True, don't actually create issue

    Returns:
        True if successful, False otherwise
    """
    title = metadata.get('title', 'Untitled')
    body = metadata.get('body', '')
    labels = metadata.get('labels', '')
    milestone = metadata.get('milestone', '')

    if dry_run:
        print(f"\nWould create issue:")
        print(f"  Title: {title}")
        print(f"  Labels: {labels}")
        print(f"  Milestone: {milestone}")
        print(f"  Body length: {len(body)} chars")
        return True

    cmd = [
        'gh', 'issue', 'create',
        '--title', title,
        '--body', body,
    ]

    if labels:
        cmd.extend(['--label', labels])

    if milestone:
        cmd.extend(['--milestone', milestone])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✓ Created: {title}")
        if result.stdout:
            print(f"    {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {title}")
        print(f"    Error: {e.stderr}")
        return False

def get_issue_files(directory: Path) -> List[Path]:
    """
    Get all issue markdown files in priority order.

    Args:
        directory: Issues directory

    Returns:
        Sorted list of issue file paths
    """
    files = []

    # Priority order: mvp, runtime-validation, advanced-analysis
    for subdir in ['mvp', 'runtime-validation', 'advanced-analysis']:
        subdir_path = directory / subdir
        if subdir_path.exists():
            files.extend(sorted(subdir_path.glob('*.md')))

    return files

def create_milestones(dry_run: bool = False):
    """Create project milestones."""
    milestones = [
        {
            'title': 'v0.1.0',
            'description': 'MVP Release - Foundation',
            'due': '2025-02-01'
        },
        {
            'title': 'v0.2.0',
            'description': 'Runtime Validation - Killer Feature',
            'due': '2025-03-01'
        },
        {
            'title': 'v0.3.0',
            'description': 'Advanced Analysis',
            'due': '2025-04-01'
        },
    ]

    print("\n📅 Creating milestones...")

    for milestone in milestones:
        if dry_run:
            print(f"  Would create milestone: {milestone['title']}")
            continue

        cmd = [
            'gh', 'milestone', 'create',
            milestone['title'],
            '--description', milestone['description'],
            '--due', milestone['due']
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"  ✓ Created: {milestone['title']}")
        except subprocess.CalledProcessError:
            print(f"  ⚠ Milestone {milestone['title']} may already exist")

def create_labels(dry_run: bool = False):
    """Create project labels."""
    labels = [
        # MVP
        ('mvp', 'd73a4a', 'MVP release blocker'),
        ('infrastructure', '0075ca', 'Build, deploy, tooling'),
        ('cli', '1d76db', 'Command-line interface'),
        ('testing', 'd4c5f9', 'Testing related'),
        ('documentation', '0075ca', 'Documentation'),
        ('deployment', 'ededed', 'Deployment and publishing'),

        # Feature
        ('feature', 'a2eeef', 'New feature'),
        ('enhancement', '84b6eb', 'Enhancement to existing feature'),

        # Framework
        ('fastapi', '009688', 'FastAPI integration'),
        ('flask', '000000', 'Flask integration'),
        ('django', '0c4b33', 'Django integration'),

        # Technical
        ('runtime-validation', 'e99695', 'Runtime validation feature'),
        ('static-analysis', 'f9d0c4', 'Static analysis'),
        ('type-checking', 'c5def5', 'Type checking and inference'),

        # Priority
        ('P0', 'b60205', 'Critical priority'),
        ('P1', 'd93f0b', 'High priority'),
        ('P2', 'fbca04', 'Medium priority'),
        ('P3', '0e8a16', 'Low priority'),
    ]

    print("\n🏷️  Creating labels...")

    for name, color, description in labels:
        if dry_run:
            print(f"  Would create label: {name}")
            continue

        cmd = [
            'gh', 'label', 'create',
            name,
            '--color', color,
            '--description', description
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"  ✓ Created: {name}")
        except subprocess.CalledProcessError:
            print(f"  ⚠ Label {name} may already exist")

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Import GitHub issues from markdown files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating'
    )
    parser.add_argument(
        '--directory',
        type=Path,
        default=Path('issues'),
        help='Issues directory (default: issues/)'
    )
    parser.add_argument(
        '--skip-setup',
        action='store_true',
        help='Skip creating milestones and labels'
    )

    args = parser.parse_args()

    # Check prerequisites
    check_gh_cli()

    if not args.directory.exists():
        print(f"❌ Directory not found: {args.directory}")
        sys.exit(1)

    # Setup (milestones and labels)
    if not args.skip_setup:
        create_milestones(dry_run=args.dry_run)
        create_labels(dry_run=args.dry_run)

    # Get issue files
    issue_files = get_issue_files(args.directory)

    if not issue_files:
        print(f"❌ No issue files found in {args.directory}")
        sys.exit(1)

    print(f"\n📝 Found {len(issue_files)} issue files")

    if args.dry_run:
        print("\n🔍 DRY RUN - No issues will be created\n")
    else:
        print("\n🚀 Creating issues...\n")

    # Create issues
    created = 0
    failed = 0

    for issue_file in issue_files:
        # Skip guide file
        if issue_file.name == 'ISSUE_IMPORT_GUIDE.md':
            continue

        print(f"Processing {issue_file.name}...")

        try:
            with open(issue_file) as f:
                content = f.read()

            metadata = parse_frontmatter(content)

            if not metadata:
                print(f"  ⚠ Failed to parse frontmatter")
                failed += 1
                continue

            if create_issue(metadata, dry_run=args.dry_run):
                created += 1
            else:
                failed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    # Summary
    print(f"\n{'📋 Summary (Dry Run)' if args.dry_run else '✅ Summary'}")
    print(f"  {'Would create' if args.dry_run else 'Created'}: {created} issues")
    if failed > 0:
        print(f"  Failed: {failed} issues")

    if args.dry_run:
        print("\n💡 Run without --dry-run to actually create issues")

if __name__ == '__main__':
    main()

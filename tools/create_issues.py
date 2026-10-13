"""Turn the user stories in requirements.md into GitHub issues (Lesson L1.1, step 8).

Dry run (default) prints what would be created:
    uv run --no-project --python 3.12 tools/create_issues.py docs/product/requirements.md

Create the labels and issues for real, and add them to a GitHub Project:
    uv run --no-project --python 3.12 tools/create_issues.py docs/product/requirements.md --create --project "Pathology Platform"
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HEADING = re.compile(r"^### (US-\d+) (.+)$")
METADATA = re.compile(
    r"^\*\*Role:\*\* (?P<role>.+?) · \*\*Epic:\*\* (?P<epic>.+?)"
    r" · \*\*Priority:\*\* (?P<priority>.+?) · \*\*Module:\*\* (?P<module>\S+)$"
)

# One color per label group, so the board is easy to scan.
LABEL_COLORS = {
    "type": "5319e7",
    "role": "1d76db",
    "epic": "0e8a16",
    "priority": "d93f0b",
    "module": "fbca04",
}


@dataclass
class Story:
    id: str
    title: str
    role: str
    epic: str
    priority: str
    module: str
    body_lines: list[str]

    @property
    def issue_title(self) -> str:
        return f"{self.id} {self.title}"

    @property
    def labels(self) -> list[str]:
        return [
            "type:story",
            f"role:{slug(self.role)}",
            f"epic:{slug(self.epic)}",
            f"priority:{slug(self.priority)}",
            f"module:{self.module.lower()}",
        ]

    def issue_body(self) -> str:
        lines = []
        for line in self.body_lines:
            # Turn acceptance criteria into a checklist GitHub can track.
            if line.startswith("- Given"):
                line = "- [ ] " + line[2:]
            lines.append(line)
        story_text = "\n".join(lines).strip()
        return f"{story_text}\n\nSource: `docs/product/requirements.md`\n"


def slug(text: str) -> str:
    """'Lab technician' -> 'lab-technician'."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_stories(markdown: str) -> list[Story]:
    stories: list[Story] = []
    current: Story | None = None

    for line in markdown.splitlines():
        heading = HEADING.match(line)
        if heading:
            current = Story(heading[1], heading[2].strip(), "", "", "", "", [])
            stories.append(current)
            continue

        # Any other heading or a horizontal rule ends the current story.
        if line.startswith("#") or line.strip() == "---":
            current = None
            continue

        if current is None:
            continue

        metadata = METADATA.match(line)
        if metadata:
            current.role = metadata["role"]
            current.epic = metadata["epic"]
            current.priority = metadata["priority"]
            current.module = metadata["module"]
        else:
            current.body_lines.append(line)

    missing = [s.id for s in stories if not s.role]
    if missing:
        sys.exit(f"Stories without a metadata line: {', '.join(missing)}")
    return stories


def gh(*args: str) -> str:
    """Run a GitHub CLI command and return its output; stop on failure."""
    result = subprocess.run(
        ["gh", *args], check=False, capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args[:2])} failed:\n{result.stderr}")
    return result.stdout


def existing_issue_titles() -> set[str]:
    output = gh("issue", "list", "--state", "all", "--limit", "500", "--json", "title")
    return {issue["title"] for issue in json.loads(output)}


def ensure_labels(stories: list[Story]) -> None:
    labels = sorted({label for story in stories for label in story.labels})
    for label in labels:
        group = label.split(":")[0]
        # --force updates the label if it already exists, so re-running is safe.
        gh("label", "create", label, "--color", LABEL_COLORS[group], "--force")
    print(f"Ensured {len(labels)} labels.")


def create_issues(stories: list[Story], project: str | None) -> None:
    existing = existing_issue_titles()
    for story in stories:
        if story.issue_title in existing:
            print(f"skip    {story.issue_title} (already exists)")
            continue

        args = [
            "issue",
            "create",
            "--title",
            story.issue_title,
            "--body",
            story.issue_body(),
        ]
        for label in story.labels:
            args += ["--label", label]
        if project:
            args += ["--project", project]

        url = gh(*args).strip()
        print(f"created {story.issue_title} -> {url}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create GitHub issues from user stories."
    )
    parser.add_argument("requirements", type=Path, help="Path to requirements.md")
    parser.add_argument(
        "--create", action="store_true", help="Create issues (default is a dry run)"
    )
    parser.add_argument(
        "--project", help="Title of a GitHub Project to add the issues to"
    )
    args = parser.parse_args()

    stories = parse_stories(args.requirements.read_text(encoding="utf-8"))
    print(f"Found {len(stories)} user stories.")

    if not args.create:
        for story in stories:
            print(f"{story.issue_title:<45} {', '.join(story.labels)}")
        print("\nDry run only. Add --create to create the labels and issues.")
        return

    ensure_labels(stories)
    create_issues(stories, args.project)


if __name__ == "__main__":
    main()

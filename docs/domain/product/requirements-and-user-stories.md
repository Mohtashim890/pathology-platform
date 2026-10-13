# Lesson L1.1: Requirements and user stories

**Module 1: Product design and architecture · Week 2 · about 5–7 hours**

| | |
|---|---|
| **Requirements** | 20–30 user stories with acceptance criteria across five roles; non-functional requirements (performance, privacy, availability) |
| **Implementation** | Draft stories yourself; ask the AI to find missing roles, edge cases and untestable criteria |
| **Deliverable** | `docs/product/requirements.md`; a GitHub Projects backlog |

The vision (L0.2) said **why** and **for whom**. Requirements say **exactly what the platform must do** and **how you'll know each part is done**. From now on, every lesson builds stories from this list, and every story's acceptance criteria become tests.

**.NET analogy:** if the vision is the interface, the requirements are its **method signatures and contracts**, and the acceptance criteria are the **unit tests written before the implementation**.

You'll also write your second Python script: it turns the stories into GitHub issues automatically, so your backlog always matches the document.

| Step | What you do | What you have at the end |
|---|---|---|
| 1 | Set up lesson notes | `docs/lessons/L1.1.md` |
| 2 | Learn user stories and acceptance criteria | Notes, 3 practice stories |
| 3 | Map roles against epics and draft your own stories | 10 stories of your own |
| 4 | Compare with the starter set and merge | `docs/product/requirements.md` with 20–30 stories |
| 5 | Write non-functional requirements | NFR table with measurable targets |
| 6 | AI review: missing roles, edge cases, untestable criteria | Improved requirements, AI log entry |
| 7 | Create the GitHub repository and Project | Repository on GitHub, empty board |
| 8 | Generate the backlog with Python | 20–30 issues on the board |
| 9 | Check, reflect and commit | Fourth commit, pushed |

---

## Step 1: Set up lesson notes

Create `docs/lessons/L1.1.md` with the usual template (requirements in your own words, notes, decisions, reflection).

---

## Step 2: User stories and acceptance criteria

### 2.1 A user story

A **user story** is a short description of one thing a user wants, written from their point of view:

```
As a <role>,
I want <capability>,
so that <benefit>.
```

Example:

> As a lab technician, I want unsupported or damaged files rejected with a clear reason, so that I can fix the problem immediately.

Each part has a job:

| Part | Its job | What goes wrong without it |
|---|---|---|
| **As a…** | Names who benefits, so you can ask them | Features nobody asked for |
| **I want…** | The capability, in the user's words, not the implementation | Stories like "add a column to the Slide table" (that's a task, not a story) |
| **so that…** | The reason, which lets you judge alternatives | You can't tell if a simpler solution would do |

### 2.2 INVEST: what makes a story good

| Letter | Means | Check |
|---|---|---|
| **I**ndependent | Can be built without waiting for many others | Few dependencies |
| **N**egotiable | Describes the need, not a fixed design | No UI layouts or class names |
| **V**aluable | Gives value to a user on its own | You could demo it |
| **E**stimable | Clear enough to estimate | No big unknowns |
| **S**mall | Fits in one lesson or less | If not, split it |
| **T**estable | You can prove it's done | Has acceptance criteria |

### 2.3 Acceptance criteria: Given / When / Then

**Acceptance criteria** define when a story is done. The **Given / When / Then** format (from behaviour-driven development) keeps them precise:

```
Given <a starting situation>,
when <an action happens>,
then <an observable result>.
```

You already know this shape: it's **Arrange / Act / Assert** in unit tests. That's not a coincidence. In L2.4 and later, each criterion becomes a test. For example, this criterion from US-13:

> Given a slide with the same checksum already exists, when I upload it again, then I am told which case it belongs to and no new slide is created.

will become something like this (you'll write the real one in Module 3; don't build it now):

```csharp
[Fact]
public async Task Upload_of_existing_slide_is_rejected_as_duplicate()
{
    // Given: a slide with this checksum already exists
    var existing = await IngestSampleSlideAsync("sample.svs");

    // When: the same file is uploaded again
    var response = await UploadAsync("sample.svs");

    // Then: the response names the existing case, and no new slide row exists
    Assert.Equal(HttpStatusCode.Conflict, response.StatusCode);
    Assert.Contains(existing.CaseKey, await response.Content.ReadAsStringAsync());
    Assert.Equal(1, await CountSlidesAsync());
}
```

### 2.4 Testable vs untestable criteria

The most common mistake is criteria that can't be tested. Learn to spot them:

| Untestable | Testable |
|---|---|
| "The viewer is fast." | "Each new view is sharp within 1 second." |
| "The AI is accurate." | "Slide-level AUC ≥ 0.90 on the CAMELYON16 test set." |
| "Errors are handled properly." | "A truncated file is rejected with 'file could not be read' and nothing is stored." |
| "The system is secure." | "A lab technician calling the model registration endpoint gets 403." |
| "User-friendly heatmap." | "A legend shows the scale from 0 to 1 using a colorblind-safe colormap." |

Warning words: *fast, easy, user-friendly, robust, properly, appropriate, etc., and so on, should*. When you see one, ask "how would I measure that?"

### 2.5 Epics and priorities

- An **epic** is a group of related stories (e.g. "Ingestion"). Epics help you see coverage and plan modules.
- **MoSCoW** priorities: **Must** (the release fails without it), **Should** (important, can slip), **Could** (nice to have), **Won't (this time)**, which we call **Later** because it's planned for v2 or v3.

For this project, priorities are relative to **release v1: detection** from your vision.

### 2.6 Practice

In `L1.1.md`, write 3 stories with 2 acceptance criteria each, for any roles. Then check each against INVEST and the warning words. Don't open the starter file yet.

**Done when:** you have 3 practice stories and can say which INVEST letter each might fail.

---

## Step 3: Map roles against epics and draft your own stories

### 3.1 The map

A simple way to find stories is a grid of **roles × epics**. Each cell asks: "what does this role need from this part of the platform?" Copy it into your notes and fill in a few words per cell (some cells stay empty, which is fine):

```markdown
|                | Ingestion | Quality | Viewer | AI results | Models | Reports | Search | Operations | Security |
|----------------|-----------|---------|--------|------------|--------|---------|--------|------------|----------|
| Pathologist    |           |         |        |            |        |         |        |            |          |
| Lab technician |           |         |        |            |        |         |        |            |          |
| Lab manager    |           |         |        |            |        |         |        |            |          |
| Data scientist |           |         |        |            |        |         |        |            |          |
| Administrator  |           |         |        |            |        |         |        |            |          |
```

Use three sources: your **interview notes** from L0.2 (each pain point should become at least one story), your **vision**, and the **Development Plan's** users table and stages.

### 3.2 Draft 10 stories yourself

Write 10 stories, **two per role**, with acceptance criteria, in the format below. Writing them yourself first is the course's rule ("draft stories yourself"), and it's where the learning happens: you'll find you have to decide things, like "what happens if the upload fails halfway?"

Use exactly this format, because the Python script in step 8 reads it:

```markdown
### US-01 Upload a slide
**Role:** Lab technician · **Epic:** Ingestion · **Priority:** Must · **Module:** M3

As a lab technician, I want to upload a slide file and attach it to a case, so that it enters the platform without copying files by hand.

**Acceptance criteria**
- Given a 2 GB SVS file, when I upload it, then it is stored and the server's memory use stays flat during the upload.
- Given an upload finishes, then a SHA-256 checksum is stored and the slide status is "ingested".
```

Notes on the format:

- The heading must be `### US-<number> <short title>`.
- The metadata line uses ` · ` (space, middle dot, space) between fields. On Windows you can type `·` with `Alt+0183`, or copy it from this file.
- Criteria lines start with `- Given`.

**Done when:** 10 stories, two per role, each with at least 2 acceptance criteria.

---

## Step 4: Compare with the starter set and merge

Now open the attached **`L1.1-requirements.md`**. It has 30 stories across the five roles and nine epics, 17 non-functional requirements and three open questions. I built it from your vision, the interview topics and the Development Plan.

1. Copy it to `pathology-platform/docs/product/requirements.md`.
2. **Compare** with your 10 stories. For each of yours:
   - If the starter has a similar story, keep the better wording, or merge criteria from both.
   - If the starter doesn't have it, add it with the next free ID.
3. **Look for what the starter has that you missed.** Write in your notes which kinds of stories you didn't think of. Common blind spots are failure cases (US-10, US-25), data protection (US-28, US-30) and traceability (US-22).
4. **Cut or move to Later** anything that doesn't serve your vision. 20–30 stories is the target; more isn't better.
5. Make sure every **interview pain point** from L0.2 is covered by at least one story. Note the mapping in `L1.1.md`.

Things worth noticing in the starter set:

- **Decision support is built into the stories.** US-03 makes uncertainty visible, US-05 lets the pathologist disagree, and US-07 shows a grade *set* when the model is unsure between two grades.
- **"Real data" is built in too.** US-10 handles slides without mpp; US-18 watches AI agreement per scanner (an early warning of domain shift); US-29 swaps storage by configuration.
- **Failure paths are stories, not afterthoughts.** A platform that loses one slide in a thousand silently is not trustworthy.

**Done when:** `docs/product/requirements.md` has 20–30 stories, including your own, in the script's format.

---

## Step 5: Non-functional requirements

### 5.1 What they are

**Functional** requirements say **what** the system does (upload a slide). **Non-functional requirements** (NFRs, also called quality attributes) say **how well** it does it: speed, security, availability, and so on. They rarely belong to one story; they apply across many.

NFRs are where architecture comes from. "Upload 2 GB with flat memory" forces streaming (L3.2); "no patient identifiers" forces de-identification at the entrance (L10.2); "throughput grows with workers" forces the event-driven design you'll choose in L1.2.

### 5.2 Make them measurable

Every NFR needs a **metric**, a **target** and a **way to verify it**:

| Weak | Measurable |
|---|---|
| "The system should be highly available." | "≥ 99.5% monthly availability during lab hours, measured by Azure Monitor." |
| "Tiles load quickly." | "p95 tile response < 200 ms for cached tiles, measured by the L3.4 benchmark." |
| "Patient data is protected." | "Only pseudonymous case keys are stored or logged; verified by de-identification tests." |

**p95** means "95% of requests are faster than this". It's better than an average, because averages hide the slow requests users actually notice.

### 5.3 Do it

Review the NFR table in your `requirements.md`. For each row, ask: is the target realistic for one person on a PC with Docker? Can I name the lesson where it's verified? Change targets you disagree with and write why in your notes. The curriculum requires at least **performance, privacy and availability**; the starter covers those and more.

**Done when:** every NFR has a target and a "verified in" lesson.

---

## Step 6: AI review

The curriculum says: ask the AI to find missing roles, edge cases and untestable criteria. Paste your `requirements.md` into a fresh AI chat after your `ai-context.md` (from L0.3), then:

```
Review these requirements for a breast cancer pathology AI platform.
Do not rewrite them. Instead, list:
1. Roles or stakeholders I'm missing, and one story each would need.
2. Edge cases and failure paths not covered (bad input, partial failure,
   concurrency, very large or very small slides, missing metadata).
3. Acceptance criteria that are untestable or vague, with a testable rewrite.
4. Stories that violate INVEST (too big, not independent, not valuable alone).
5. Conflicts between stories or between stories and NFRs.
Rank each list by importance.
```

How to use the answer:

- **Don't accept everything.** The AI will suggest more stories than you need. Add only what serves your vision; put the rest under "Open questions" or "Later".
- Expect suggestions like: a **patient or referring clinician** role (out of scope for v1, but note it), **concurrent edits** (two pathologists recording a decision at once), **very small biopsies** with little tissue, **slides with several tissue sections**, **IHC slides** uploaded by mistake, and **model failure on a new scanner**.
- Log the prompt, the three most useful findings and anything wrong in `docs/ai-log.md`.

**Done when:** you've applied at least 5 improvements and logged the review.

---

## Step 7: Create the GitHub repository and Project

Until now your repository lived only on your PC. The curriculum wants the backlog in **GitHub Projects**, which needs the repository on GitHub.

### 7.1 Concepts

- **Issue**: one work item in a GitHub repository, with title, description, labels and comments. Each user story becomes one issue.
- **Label**: a tag on an issue (e.g. `epic:ingestion`). Labels let you filter.
- **GitHub Project**: a board or table that collects issues (from one or more repositories) and adds fields like Status. **.NET analogy:** like Azure DevOps Boards, if you've used them.
- **GitHub CLI (`gh`)**: a command-line tool for GitHub. We use it so a script can create the issues.

### 7.2 Install and sign in

Windows:

```powershell
winget install --id GitHub.cli
```

macOS: `brew install gh`. Then, in a new terminal:

```bash
gh auth login
```

Choose GitHub.com, HTTPS, and log in with your browser. Then give `gh` permission to manage Projects (it isn't included by default):

```bash
gh auth refresh -s project
```

### 7.3 Create the repository

From `pathology-platform/` (it must already have commits from earlier lessons):

```bash
gh repo create pathology-platform --private --source . --remote origin --push
```

This creates a **private** repository on your GitHub account, adds it as the `origin` remote and pushes your commits. Open it in the browser (`gh repo view --web`) and check that `data/`, `.venv/`, `bin/` and `obj/` are **not** there.

### 7.4 Create the Project

```bash
gh project create --owner "@me" --title "Pathology Platform"
```

It prints the project's URL, which ends in a number (e.g. `/projects/1`). Link it to the repository so it shows in the repository's Projects tab, using that number and your GitHub username:

```bash
gh project link 1 --owner "@me" --repo <your-username>/pathology-platform
```

**Done when:** the repository and an empty project exist on GitHub.

---

## Step 8: Generate the backlog with Python

Typing 30 issues by hand is slow, and they'd drift from the document. Instead, a script reads `requirements.md` and creates them. Re-running it is safe: it skips issues that already exist.

### 8.1 The script

Save the attached **`L1.1-create_issues.py`** as `pathology-platform/tools/create_issues.py`. It uses only Python's standard library, so it needs no packages. Read it through before running it (course rule: never run code you can't explain). Here it is in full:

```python
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
```

### 8.2 The new Python ideas in this script

| Python | Meaning | C# equivalent |
|---|---|---|
| `re.compile(r"...")` | A compiled **regular expression**. The `r` prefix makes a "raw string", so `\d` isn't treated as an escape | `new Regex(@"...", RegexOptions.Compiled)` |
| `(?P<role>...)` and `metadata["role"]` | A **named group** and reading it | `(?<role>...)` and `match.Groups["role"].Value` |
| `heading[1]` | The first captured group of a match | `match.Groups[1].Value` |
| `@dataclass class Story:` | Generates the constructor, equality and `repr` from the field list | `record Story(...)` (but a dataclass is mutable by default) |
| `@property def labels(self)` | A computed, read-only property | `public List<string> Labels => ...;` |
| `self` | The current object, always written explicitly as the first parameter of methods | `this` (implicit in C#) |
| `{label for story in stories for label in story.labels}` | A **set comprehension**: build a set from a nested loop, removing duplicates | `stories.SelectMany(s => s.Labels).ToHashSet()` |
| `[s.id for s in stories if not s.role]` | A **list comprehension** with a filter | `stories.Where(s => s.Role == "").Select(s => s.Id).ToList()` |
| `def gh(*args: str)` and `gh(*args)` | `*args` collects any number of arguments into a tuple; at a call site, `*` spreads a list into separate arguments | `params string[] args` |
| `subprocess.run([...], capture_output=True, text=True)` | Run a program and capture its output | `Process.Start` with redirected output (like `ToolCheck` in L0.3) |
| `argparse` | Parses command-line options and generates `--help` | `System.CommandLine` |
| `sys.exit("message")` | Prints the message to stderr and exits with code 1 | `Console.Error.WriteLine(...); return 1;` |
| `json.loads(text)` | Parse JSON into Python lists and dicts | `JsonSerializer.Deserialize<...>(text)` |

The script is built so it's **safe to re-run**: labels use `--force` (create or update) and issues are skipped when the title already exists. This property is called **idempotency**, and it'll come back as a key requirement for the event consumers in L7.1 (US-23).

### 8.3 Run it

From `pathology-platform/`, first a **dry run**, which changes nothing:

```bash
uv run --no-project --python 3.12 tools/create_issues.py docs/product/requirements.md
```

You should see one line per story with its labels, ending with "Dry run only". Fix any "Stories without a metadata line" error by correcting that story's format.

Then create them for real:

```bash
uv run --no-project --python 3.12 tools/create_issues.py docs/product/requirements.md --create --project "Pathology Platform"
```

Run the same command again: every story should say `skip … (already exists)`.

### 8.4 Set up the board

Open the project in the browser (from your repository's **Projects** tab).

1. **Board view**: change the layout to **Board**. It groups by the built-in **Status** field (Todo, In Progress, Done). If items have no status yet, select all and set them to Todo.
2. **Table view by epic**: add a new view, choose **Table**, and set **Group by → Labels**, or filter by `label:epic:ingestion` to see one epic.
3. **v1 view**: add a view filtered by `label:priority:must`. This is your release-v1 scope at a glance.
4. Optional: add a custom **Module** field (single select M3…M13), so you can plan by course module in L1.4.

Open one issue: the acceptance criteria are a **checklist**. You'll tick them as tests pass in later lessons.

**Done when:** every story is an issue on the board, and the three views exist.

---

## Step 9: Check, reflect and commit

### 9.1 Check yourself

1. What's wrong with the story "As a developer, I want a SlideRepository class, so that slides can be saved"?
2. Rewrite this criterion so it's testable: "The QC check should run quickly and give a sensible result."
3. Why is "Server memory stays flat for a 2 GB upload" a non-functional requirement and not a story?
4. Why are failure paths (corrupt files, failed jobs) written as their own stories?
5. What does "idempotent" mean, and why does `create_issues.py` need it?
6. Why is the Project linked to issues instead of tracking stories only in `requirements.md`?

<details>
<summary>Answers</summary>

1. It's a technical task, not a user need: the role isn't a platform user, and the "I want" names an implementation. The real story is a user's need (e.g. US-09 upload); the repository is one way to build it.
2. For example: "Given an ingested slide, then within 5 minutes it shows a QC verdict of pass, warn or fail, with the reason and score for each check."
3. It's a quality of how the system works, not a capability a user asks for, and it constrains the design of several stories (upload, tiling, storage).
4. Because they're real user needs that are easy to forget and expensive to add later. Without them, slides get lost silently, which destroys trust.
5. Running it once or several times gives the same result. Without it, a re-run would create 30 duplicate issues.
6. The document is the specification; the board tracks work status, links to pull requests, and shows progress. The script keeps them consistent.

</details>

### 9.2 Reflect and commit

Fill in the reflection in `L1.1.md`. Then:

```bash
git add docs/ tools/create_issues.py
git commit -m "L1.1: requirements, user stories, NFRs and backlog script"
git push
```

---

## Lesson checklist (rubric)

- [ ] I can explain user stories, INVEST and Given/When/Then, and spot untestable criteria.
- [ ] I drafted 10 stories myself before reading the starter set.
- [ ] `docs/product/requirements.md` has 20–30 stories across all five roles, each with testable acceptance criteria.
- [ ] Every L0.2 interview pain point maps to at least one story.
- [ ] NFRs cover at least performance, privacy and availability, each measurable with a "verified in" lesson.
- [ ] AI review done; at least 5 improvements applied; logged in `ai-log.md`.
- [ ] The repository is on GitHub, the backlog is generated by `create_issues.py`, and the board has three views.
- [ ] Reflection written; committed and pushed.

## How this lesson connects to the rest of the course

| From this lesson | Used in |
|---|---|
| Stories and epics | Architecture (L1.2), data model and API contracts (L1.3) |
| Priorities and modules | Milestones and delivery plan (L1.4) |
| Acceptance criteria | Tests in every lesson from L2.4; definition of done (L1.4) |
| NFRs | Architecture decisions (L1.2), benchmarks (L3.4, L7.5), SLOs (L13.1) |
| GitHub repository | CI (L2.3), pull requests for every lesson from now on |
| Idempotency | Event consumers (L7.1) |

**Next lesson: L1.2 Architecture and decisions.** You'll compare a monolith, a modular monolith and an event-driven design, draw C4 diagrams in Mermaid, and write your first Architecture Decision Records. Tell me in the thread when you're ready.

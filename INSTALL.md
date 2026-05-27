# Install Quality Engineering Suite by QE Suite (powered by QualityForge)

## Quick Install

### Step 1: Clone this repository
```bash
git clone https://github.com/glehman3/qe-suite.git
cd qe-suite
```

### Step 2: Restart Cursor
**Important**: After cloning, restart Cursor to load custom commands:
1. Close Cursor completely (Cmd+Q on Mac, Alt+F4 on Windows)
2. Reopen Cursor
3. Open the `qe-suite` folder in Cursor

### Step 3: Verify `/qforge` is available

In Cursor chat, type `/` and you should see `/qforge` in the list of commands.

If you don't see it:
- Make sure you opened the `cursor-rules` folder (not a parent directory)
- Restart Cursor again
- Check that `.cursor/skills/qforge/SKILL.md` exists in the repository

### Step 4: Use the command!

Type **`/qforge`** for the main menu (Test Cases, Risk Analysis **BETA**, Bug Tickets, Jira Import)

## What's Included

### 🎯 Test Case/Jam Generation (`/qforge` → Option 1)
Automated test jam creation that:
- Analyzes PRs from GitHub
- Generates comprehensive test cases
- Splits test cases across participants
- Creates CSV files ready for distribution

**[Full Documentation](./qualityforge/README.md)** | **[Quick Start](./qualityforge/QUICK-START.md)** | **[Examples](./test-jams/_example_session/)**

### Other Tools
- Automated rules for flag removal
- Test case templates and examples
- Additional testing utilities

## Prerequisites

- **Cursor IDE** - Download from cursor.sh
- **GitHub MCP** - For company repository access (configure in Cursor settings)

## Usage

### Creating a Test Jam

1. Open Cursor in your workspace
2. Type: `/qforge`
3. Follow the prompts:
   - Provide PR URL(s) or repository name
   - Specify number of participants
   - Answer context questions
4. Get your test cases in `test-jams/[session-name]/`

### Example
```
/qforge

→ PR: https://github.com/nova-corp/helix-api/pull/123
→ Participants: 5
→ Focus: SMS functionality and error handling
→ Timeline: Testing tomorrow

✅ Generated 5 CSV files with 35 test cases!
```

## Directory Structure

```
qe-suite/
├── qualityforge/               # QualityForge Suite (docs + scripts)
├── .cursor/
│   └── skills/
│       └── qforge/            # Main /qforge skill
│           ├── SKILL.md       # Entry point
│           └── references/    # Feature docs (loaded on-demand)
├── test-jams/                  # Output directory
│   └── _example_session/       # Example output
└── *.csv, *.md                 # Test case files and docs
```

## Getting Help

- **Docs**: [qualityforge/README.md](./qualityforge/README.md)
- **Quick Start**: [qualityforge/QUICK-START.md](./qualityforge/QUICK-START.md)
- **Example Output**: [test-jams/_example_session/](./test-jams/_example_session/)
- **Testing Guide**: [qualityforge/guides/TESTING-GUIDE.md](./qualityforge/guides/TESTING-GUIDE.md)

## Contributing

Found a bug or have an improvement? 
- File an issue
- Submit a PR
- Contact @repo-maintainer

## License

Internal use only - company

---

**Happy Testing! 🎯**



# Quality Engineering Suite by QE Suite

This repository contains the **Quality Engineering Suite by QE Suite** (powered by **QualityForge**) — a comprehensive Quality Engineering Suite for test case generation, risk analysis, and automation for org/project workflows.

## 🚀 New to Cursor?

If you haven't set up Cursor yet, follow this guide first:  
**[Cursor Setup Guide](https://docs.google.com/document/d/1nQbmLhD4ALjHFN6prMjKxPOVUiQfhXOFfHQUvOo1MG0/edit?tab=t.0)**

Once Cursor is installed, come back here to set up the **Quality Engineering Suite by QE Suite** (powered by **QualityForge**) and start using `/qforge`.

---

## Projects

### 🛠️ QualityForge (`/qforge`)
Comprehensive Quality Engineering Suite with multiple features for building better software.

**Quick Start**: Type `/qforge` in Cursor

**Features**:
1. **📋 Test Case/Jam Generation** - Generate comprehensive test cases from PRs, repos, PRDs, or Jira tickets
2. **⚠️ Risk Analysis** [BETA] - Identify risks before development starts
3. **🐛 Bug Ticket Creation** - Create Jira bug tickets from completed test results
4. **📥 Import Test Cases to Jira** - Import test cases as Jira Task tickets

**Live Features**:
- Interactive guided test jam creation
- GitHub MCP integration for PR analysis
- Intelligent test case generation
- Smart distribution across participants
- CSV + Google Sheets output
- Version checking with automatic update notifications

[Full Documentation](./qualityforge/README.md) | [Quick Start Guide](./qualityforge/QUICK-START.md) | [Example Output](./test-jams/_example_session/)

---

### 🔮 Future Enhancements

**Risk Analysis** is **[BETA]** today; future work is primarily quality/UX improvements (streamlining prompts, improving validation/quality gates, and reducing manual cleanup).

---

## Getting Started

### Prerequisites
- **Cursor IDE** - [Setup Guide](https://docs.google.com/document/d/1nQbmLhD4ALjHFN6prMjKxPOVUiQfhXOFfHQUvOo1MG0/edit?tab=t.0) (if you're new to Cursor)
- Access to GitHub repositories (for MCP integration)
- Appropriate permissions for target repositories

### Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/glehman3/qe-suite.git
   cd qe-suite
   ```
   **Want to add this to your Cloud Workspace?**:
   This is coming soon. In the mean time, please clone this repository in a separate Cursor space. 
   
3. **Restart Cursor** (Important!):
   - Close Cursor completely (Cmd+Q on Mac)
   - Reopen Cursor
   - Open the `qe-suite` folder in Cursor
   - This allows Cursor to discover the `/qforge` skill

4. **Configure MCP servers** (GitHub MCP required for `/qforge`):
   
   **Choose your setup path**:
   - **☁️ Already Have Cloud Workspace?** → No extra MCP setup required!
     - Go to Cursor **Settings → Tools & MCP's**
     - Enable **DAST-Orch** (includes GitHub MCP)
     - Time: 1 minute
   
   - **👋 First Time User?** (Never installed MCPs) → [qualityforge/setup/FIRST-TIME-SETUP.md](./qualityforge/setup/FIRST-TIME-SETUP.md)
     - Complete walkthrough: Cursor, GitHub PAT, GitHub MCP configuration
     - Time: 15-20 minutes
   
   - **⚙️ Need to configure MCPs?** → [qualityforge/setup/MCP-SETUP.md](./qualityforge/setup/MCP-SETUP.md)
     - Quick guide to set up GitHub MCP in Cursor
     - Time: 5 minutes

5. **Start using `/qforge`**:
   - In Cursor chat, type `/qforge` and press Enter
   - Follow the interactive prompts
   - First run will verify your MCP setup automatically

**Note**: If `/qforge` doesn't appear as an option, restart Cursor again to ensure commands are loaded.

### Using Custom Commands

Custom commands are defined in `.mdc` files throughout this repository. To use them:

1. Open Cursor
2. Type `/qforge` to open the Quality Engineering Suite
3. Follow the interactive prompts

---

## Project Structure

```
qe-suite/
├── .cursor/
│   └── skills/
│       └── qforge/                   # /qforge skill (Agent Skills format)
│           ├── SKILL.md              # Main entry point
│           └── references/           # Feature documentation (loaded on-demand)
│               ├── FEATURE-1-TESTJAM.md      # Test Case/Jam Generation
│               ├── FEATURE-2-RISK.md         # Risk Analysis
│               ├── FEATURE-4-BUG-TICKETS.md  # Bug Ticket Creation
│               ├── FEATURE-5-IMPORT-TESTCASES.md  # Import to Jira
│               ├── CSV-GENERATION.md         # CSV formatting rules
│               └── MCP-INTEGRATION.md        # MCP tool usage
├── qualityforge/                     # QualityForge Suite
│   ├── setup/                        # Setup guides
│   │   ├── FIRST-TIME-SETUP.md       # Complete setup guide
│   │   ├── MCP-SETUP.md              # MCP installation guide
│   │   └── TEST-ACCOUNT-SETUP.md     # Test account creation
│   ├── guides/                       # User guides
│   ├── templates/                    # CSV templates and formats
│   ├── reference/                    # Reference documentation
│   ├── README.md                     # Main documentation
│   └── QUICK-START.md                # Quick start guide
├── test-jams/                        # Generated test jams output
│   ├── _example_session/             # Example output
│   │   ├── testjam_participant_1.csv
│   │   ├── testjam_participant_2.csv
│   │   └── test_jam_summary.md
│   └── [timestamped folders]/        # Generated sessions
└── README.md                         # This file
```

---

## Contributing

### Adding New Rules
1. Create a new `.mdc` file in the appropriate directory
2. Follow the MDC format with frontmatter
3. Document the rule in the relevant README
4. Add examples and usage instructions

### Test Case Format
Test cases should follow this CSV structure:
```csv
Test ID,Category,Test Name,Priority,Type,Component,Objective,Pre-conditions,Test Steps,Expected Results,Status,Tester,Date Tested,Actual Results,Notes,Bug ID
```

**Important Formatting Rules:**
- Column 5 must be "Type" not "Test Type"
- **Pre-conditions, Test Steps, and Expected Results** all use numbered format (1., 2., 3.)
  - Format structure is required (numbered lists), not specific wording
  - Content varies based on your test scenario
- Multi-line fields use actual newlines in quoted cells for natural formatting
- Excel/Google Sheets display with line breaks (each item on its own line)
- Cells starting with `=`, `+`, `-`, `@` are prefixed with `'` to prevent formula injection

See existing test case files for examples.

---

## MCP Integration

This project integrates with MCP (Model Context Protocol) servers:

### Required MCP Servers:
- **GitHub MCP** - Repository and PR analysis (required for `/qforge`)

### Optional MCP Servers:
- **Mabl MCP** - Test automation coverage analysis
- **Bugsnag MCP** - Error tracking (where applicable)
- **Atlassian MCP** - Jira issue tracking (where applicable)
- **Figma MCP** - Design integration (where applicable)

Configure MCP servers in your Cursor settings. See [qualityforge/setup/MCP-SETUP.md](./qualityforge/setup/MCP-SETUP.md) for installation instructions.

---

## Common Workflows

### Using QualityForge
```
/qforge → Select Feature → Follow Interactive Prompts
```

**Example - Test Case Generation**:
- Type: `/qforge`
- Select: `1` (Test Case/Jam Generation)
- Provide: `https://github.com/org/project/sms-service/pull/123`
- Participants: `5`
- Get: 5 CSV files with test cases + summary report

**Available Workflows**:
1. **Test Case Generation**: Analyze PRs, repos, PRDs, or Jira tickets
2. **Risk Analysis**: [BETA] Early-stage risk identification
3. **Bug Ticket Creation**: Create Jira tickets from completed test results
4. **Import to Jira**: Import test cases as Jira Task tickets

### Sharing Test Jams
After generating test jams, distribute the CSV files or Google Sheets to participants and use the summary report for briefing.

---

## Support & Troubleshooting

### QualityForge Issues
- See [qualityforge/README.md](./qualityforge/README.md#troubleshooting)
- Check GitHub MCP integration is configured
- Verify repository access permissions
- Ensure proper network/VPN connection to GitHub

### MCP Connection Issues
- Verify MCP servers are configured in Cursor settings
- Check authentication tokens are valid
- Ensure network connectivity to required services
- See [qualityforge/setup/FIRST-TIME-SETUP.md](./qualityforge/setup/FIRST-TIME-SETUP.md) for initial setup

### General Issues
- Ensure Cursor is up to date
- Restart Cursor after installing MCP servers
- Check file permissions for output directories
- Review error messages for specific guidance

---

## Best Practices

1. **Test Cases**: Always include pre-conditions and expected results
2. **Rules**: Document all custom rules with examples
3. **MCP Tools**: Validate repository/PR access before operations
4. **Test Jams**: Review generated test cases before distribution
5. **Version Control**: Commit generated test cases for tracking

---

## Roadmap

### Upcoming Features:
- [ ] Test jam result aggregation tool
- [ ] Visual regression baseline generation
- [ ] Performance benchmark test generation
- [ ] Enhanced PRD parsing and test coverage analysis

---

## Version History

### v1.0.0 - April 2026
- 📦 Consolidated documentation structure
- ✅ Added version checking with GitHub release tags
- ✅ Added usage metrics tracking
- ✅ Added Google Sheets creation for test jams
- 🔄 Streamlined menu to 4 core features
- 🗑️ Deprecated Playwright generation (moved to `_project-dev/`)

### v2.0 - January 2026
- 🎉 Rebranded as **Quality Engineering Suite by QE Suite** (powered by **QualityForge**)
- ✅ New `/qforge` command with menu-driven interface
- ✅ Test Case/Jam Generation (live)
- 🧪 Risk Analysis (**BETA**)
- 🔄 Migrated to Cursor Agent Skills format for better maintainability

### v1.0 - November 2025
- ✅ Initial Test Jam Generator
- ✅ GitHub MCP integration for PR analysis
- ✅ Smart test case distribution across participants
- ✅ CSV output with proper formatting
- ✅ Interactive guided workflow
- ✅ PRD-based test case generation
- ✅ Execution tracking columns for test jams

---

## License

MIT License - see LICENSE file

---

## Contact

For questions, issues, or contributions:
- File an issue in this repository
- Contact the QA team
- Reach out in #mcqa Slack channel

---

**Happy Testing! 🎯**

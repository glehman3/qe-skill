# MCP Setup Guide for QualityForge

**Quick Setup for QualityForge commands (`/qforge`, `/testjam`)**

This guide is for users who **already have CODEGEN CLI installed** and just need to set up MCP servers.

---

## ☁️ Already Have Cloud Workspace?

**If you already have Cloud Workspace set up, you do NOT need CODEGEN CLI!**

Simply:
1. Open Cursor **Settings → Tools & MCP's**
2. Enable **DAST-Orch** (includes GitHub MCP)
3. Start using `/qforge` or `/testjam` immediately!

---

**👋 First Time User?** Never installed Cursor or CODEGEN? → See [FIRST-TIME-SETUP.md](./FIRST-TIME-SETUP.md) for complete installation from scratch.

---

This guide will help you set up the required MCP servers in 3 simple steps (assuming CODEGEN CLI is already installed).

---

## 📋 Quick Command Reference

**First Time Setup:**
```bash
# 1. Configure GitHub MCP (REQUIRED)
# Follow GitHub MCP setup instructions

# 2. Configure Mabl MCP (OPTIONAL - for automation coverage analysis)
# Contact your Mabl admin for API credentials

# 3. Verify setup
# Open Cursor and type: /qforge (or /testjam)
```

---

## Prerequisites (Required for `/qforge` Feature 1 and `/testjam`)

### ✅ **GitHub MCP** (REQUIRED)

The Test Jam Generator needs GitHub MCP to:
- Fetch PR details and metadata
- Analyze files changed in PRs
- Search code for context
- List recent PRs in repositories

**Setup Instructions:**

1. **Check if GitHub MCP is configured in Cursor**:
   - Open Cursor Settings
   - Look for MCP Servers section
   - Verify "github-mcp" is listed

2. **If not configured**, install GitHub MCP using CODEGEN:

   **Prerequisites** (must have CODEGEN CLI and eiamCli installed):
   ```bash
   # Verify CODEGEN is installed
   codegen --version
   
   # Verify eiamCli is installed (required for authentication)
   eiamcli --version
   ```
   
   **If CODEGEN is NOT installed** → See [FIRST-TIME-SETUP.md](./FIRST-TIME-SETUP.md) for complete installation.
   
   **If eiamCli is NOT installed** → Install it first:
   ```bash
   # Add the company EIAM Homebrew tap
   brew tap org/authcli git@github.com:EIAM/eiamCli-golang.git
   
   # Install eiamCli
   brew install eiamCli
   ```

   **Install GitHub MCP**:
   ```bash
   # Run the installation command (eiamCli will open browser for auth)
   codegen mcp install github-mcp:latest
   ```
   
   **During installation, you'll need**:
   - GitHub Personal Access Token (PAT) - Create at https://github.com/settings/tokens
   - Grant ONLY Read permissions: `read:org`, `read:repo_hook`, `read:user`, `read:discussion`, `read:enterprise`, `read:project`
   - Select latest Python version when prompted
   
   **After installation**:
   - Restart Cursor (File → Quit, then reopen)
   - MCP should now appear in Cursor Settings

3. **Verify GitHub MCP is working**:
   ```
   In Cursor, type: check my MCP setup
   ```
   Or try:
   ```
   /testjam
   ```
   If it returns results, GitHub MCP is configured correctly.

**Required Permissions:**
- `repo` - Full control of private repositories
- `read:org` - Read org and team membership

---

### 🎯 **Mabl MCP** (OPTIONAL - Enhances test generation)

Mabl MCP integration provides:
- Existing test coverage analysis
- Automation gap identification
- Mabl test references in generated test cases
- Automation opportunity suggestions

**When to Use Mabl MCP:**
- When testing features that already have Mabl tests
- To avoid duplicating existing automated tests
- To identify which manual tests should be automated
- For comprehensive test coverage analysis

**Setup Instructions:**

1. **Get Mabl API Credentials**:
   - Contact your Mabl administrator
   - Request API key for test automation
   - Note your Mabl workspace ID

2. **Configure Mabl MCP in Cursor**:
   - Add Mabl MCP server to Cursor settings
   - Set environment variables (if required):
     ```bash
     export MABL_API_KEY=your-api-key-here
     export MABL_WORKSPACE_ID=your-workspace-id
     ```

3. **Verify Mabl MCP** (if configured):
   - The `/testjam` command will automatically detect Mabl MCP
   - You'll be prompted: "Should I check Mabl for existing test coverage?"

**Note**: If Mabl MCP is not configured, `/testjam` will work fine without it. Mabl integration is optional and enhances (but doesn't block) test generation.

---


## Quick Prerequisites Check ✓

Before using `/testjam`, verify your setup:

### Check GitHub MCP
```
1. Open Cursor
2. Go to Settings → MCP Servers
3. Verify "github-mcp" (or similar) is listed and active
4. Test: Try searching for a repository
```

**Expected**: You can search and access GitHub repositories

### Check Mabl MCP (Optional)
```
1. Open Cursor
2. Go to Settings → MCP Servers
3. Look for "mabl-mcp" or similar
4. If not present, Mabl features will be skipped (this is fine)
```

**Expected**: Either Mabl MCP is configured, or `/testjam` will proceed without it


## Automatic MCP Verification

When you run `/testjam` for the first time, it will automatically check your MCP setup:

### What Gets Checked?

1. **GitHub MCP (Required)**:
   ```
   ✅ GitHub MCP detected and ready
   ```
   OR
   ```
   ⚠️  GitHub MCP Not Detected
   
   The Test Jam Generator requires GitHub MCP to fetch PR details.
   
   🔧 Setup Required:
   Please configure GitHub MCP in Cursor before using /testjam.
   
   📖 Setup Guide: See qualityforge/setup/MCP-SETUP.md
   ```

2. **Mabl MCP (Optional)**:
   ```
   ✅ Mabl MCP detected - automation coverage analysis available
   ```
   OR
   ```
   ℹ️  Mabl MCP not detected (optional)
   
   Test Jam will proceed without automation coverage analysis.
   ```

3. **Summary**:
   ```
   🔍 MCP Status Check:
   ✅ GitHub MCP: Ready (Required)
   ℹ️  Mabl MCP: Not configured (Optional)
   
   All required dependencies met! Let's create your Test Jam 🎯
   ```

### Manual Verification

You can manually verify your setup at any time by:
- Typing in Cursor: `check my MCP setup`
- Or re-running `/testjam` - it will check again

### What Happens After Verification?

- **All Required MCPs Present**: `/testjam` proceeds directly to test jam creation
- **Missing GitHub MCP**: You'll receive setup instructions and the process stops
- **Missing Mabl MCP**: Test jam proceeds normally, Mabl features are skipped

**See Detailed Examples**: Check out MCP verification examples for visual examples of all verification scenarios.

---

## Using `/testjam` with MCP Integration

### Standard Workflow (GitHub MCP Only)

```
1. Type: /testjam
2. Provide PR URL(s) or repository name
3. Specify participant count
4. Answer context questions
5. Tool fetches PR data from GitHub automatically
6. Get generated test cases with PR context
```

### Enhanced Workflow (with Mabl MCP)

```
1. Type: /testjam
2. Provide PR URL(s) or repository name
3. Specify participant count
4. When asked "Check Mabl?": Answer "yes"
5. Tool fetches:
   - PR data from GitHub
   - Existing test coverage from Mabl
6. Get enhanced test cases with:
   - PR context
   - Automation status
   - Mabl test references
   - Coverage gap analysis
```

---

## Troubleshooting

### "Cannot access GitHub repository"

**Symptom**: Error when trying to fetch PR details

**Fix**:
1. Verify GitHub MCP is configured in Cursor settings
2. Check your GitHub PAT has `repo` permissions
3. Ensure you have access to the target repository
4. Try accessing the repository directly in your browser

### "GitHub MCP not found"

**Symptom**: Tool cannot connect to GitHub MCP

**Fix**:
1. Check Cursor Settings → MCP Servers
2. Verify "github-mcp" is listed and enabled
3. Restart Cursor
4. Contact your Cursor admin if still not working

### "Mabl MCP not available"

**Symptom**: Warning that Mabl features are skipped

**Status**: This is NORMAL if Mabl MCP isn't configured

**Fix** (if you want Mabl integration):
1. Contact Mabl admin for API credentials
2. Configure Mabl MCP in Cursor
3. Restart Cursor and try again

**Workaround**: `/testjam` works perfectly fine without Mabl MCP. You'll just get standard test cases without automation status.

---

## Configuration Files

### Cursor MCP Configuration

Cursor MCP servers are typically configured in:
- **Global**: Cursor Settings → MCP Servers
- **Per-Project**: `.cursor/mcp.json` or similar

**Example MCP Configuration** (reference):
```json
{
  "mcpServers": {
    "github-mcp": {
      "command": "github-mcp-server",
      "env": {
        "GITHUB_TOKEN": "your-pat-token"
      }
    },
    "mabl-mcp": {
      "command": "mabl-mcp-server",
      "env": {
        "MABL_API_KEY": "your-api-key",
        "MABL_WORKSPACE_ID": "your-workspace"
      }
    }
  }
}
```

**Note**: Actual configuration format depends on your Cursor setup. Check with your admin team.

---

## Security Best Practices

### ⚠️ IMPORTANT: Never Commit Secrets

- **DO NOT** commit API keys, tokens, or credentials to git
- Use environment variables or Cursor's secure credential storage
- Add sensitive files to `.gitignore`

### Secure Credential Storage

**Good** ✅:
```bash
# Set in your shell profile
export GITHUB_TOKEN=your-token-here
export MABL_API_KEY=your-api-key
```

**Bad** ❌:
```json
{
  "github_token": "ghp_actualTokenHere123"  // DON'T DO THIS
}
```

---

## Advanced Configuration

### Using Multiple GitHub Accounts

If you need to access multiple GitHub organizations:
1. Use a PAT with access to all required orgs
2. Or configure multiple GitHub MCP instances
3. Consult your Cursor admin for multi-org setup

### Custom MCP Endpoints

For enterprise MCP deployments:
- Configure custom endpoints in Cursor settings
- Use internal MCP proxy servers if required
- Contact your IT team for enterprise-specific setup

---

## Getting Help

### MCP Setup Issues
- **GitHub MCP**: Contact your Cursor admin team or #cursor-support
- **Mabl MCP**: Contact Mabl administrator or #qa-automation
- **General Cursor**: Check Cursor documentation or #cursor-help

### Test Jam Issues
- **Using `/testjam`**: See [README.md](../README.md)
- **Test case quality**: See [TESTING-GUIDE.md](../guides/TESTING-GUIDE.md)
- **Sharing with team**: Share the Google Sheet URL with participants

### Need Immediate Help?
- Reach out in **#mcqa** Slack channel
- File an issue in this repository
- Contact the QA team

---

## Summary - What You Need

### Minimum Required (to use `/testjam`)
1. ✅ **Cursor IDE** installed
2. ✅ **GitHub MCP** configured
3. ✅ Access to GitHub repos

### Optional (enhances test generation)
4. ⭐ **Mabl MCP** configured
5. ⭐ Mabl API credentials

### Nice to Have
6. 📚 Familiarity with test case creation
7. 📋 Understanding of your team's testing processes

---

**Ready to start?** Open Cursor and type `/testjam` to begin! 🎯

If GitHub MCP is configured, everything else will work automatically.


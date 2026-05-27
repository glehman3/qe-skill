# 🚀 First Time Setup Guide - QualityForge

---

## ☁️ Already Have Cloud Workspace?

**If you already have Cloud Workspace set up, you do NOT need to follow this guide!**

Simply:
1. Open Cursor **Settings → Tools & MCP's**
2. Enable **DAST-Orch** (includes GitHub MCP)
3. Start using `/qforge` immediately!

**Time Required**: ~1 minute

---

## 📋 Quick Overview

**What you'll install (if not using Cloud Workspace):**
1. ✅ Cursor IDE
2. ✅ CODEGEN CLI (company's MCP management tool)
3. ✅ GitHub MCP (Required for QualityForge)
4. ⭐ Mabl MCP (Optional - enhances test generation)
5. ⭐ Google Drive MCP (Optional - enables Google Sheets creation)

**Time Required**: ~15-20 minutes

**Who this is for**: First-time users who have never set up Cursor or MCPs before and do NOT have Cloud Workspace

---

## Step 1: Install Cursor IDE

### Download Cursor

1. Go to: https://www.cursor.com/
2. Download Cursor for your operating system
3. Install the application
4. Open Cursor

### Official Installation Guide

For detailed Cursor setup, see: https://docs.example.com/app/dp/capability/CAP-2127/capabilityDocs/main/docs/reference/cursor/onboarding_guide.md

---

## Step 2: Verify GitHub Authentication

Before installing MCPs, ensure you're authenticated with GitHub.

### Check Authentication Status

```bash
gh auth status
```

**Expected Output**:
```
✓ Logged in to github.com as your-username (https)
```

### If Not Authenticated (or using wrong protocol)

Re-authenticate with the correct settings:

```bash
gh auth login -h github.com -p https -w
```

**Follow the prompts**:
1. Select **HTTPS** (not SSH)
2. Authenticate via web browser
3. Complete the login flow

**Verify again**:
```bash
gh auth status
```

You should now see `https` for `github.com`.

---

## Step 3: Install Prerequisites

These tools are required for CODEGEN CLI and MCP installation.

### Install Command Line Tools (if needed)

```bash
xcode-select --install
```

**Note**: The install dialog may appear behind other windows. Look for it!

### Install Required Tools

Run these commands one at a time:

```bash
# Install Git
brew install git

# Install Python 3 (REQUIRED for MCPs)
brew install python3

# Verify Python version (should be 3.9 or higher)
python3 --version

# Install Node.js
brew install node

# Install pipx (Python package installer)
brew install pipx

# Ensure pipx is in your PATH
pipx ensurepath
```

---

## Step 4: Install CODEGEN CLI

BEFORE INSTALLING CODEGEN CLI, THERE IS AN EIM REQUIREMENT. RUN THE FOLLOWING COMMANDS BEFORE CONTINUING WITH CODEGEN CLI SETUP:

```bash
git config --global url."https://github.com/".insteadOf git@github.com:
```

```bash
brew tap org/authcli git@github.com:EIAM/eiamCli-golang.git
```
and

```bash
brew install eiamCli
```

CODEGEN CLI is company's tool for managing MCPs in Cursor.

### Download CODEGEN CLI

```bash
pip3 download platformexps-tools-codegencli-codegencli
```

**Expected**: Downloads a `.whl` file to your current directory

### Install CODEGEN CLI

```bash
pipx install --force platformexps_tools_codegencli_codegencli-*
```

**Expected Output**:
```
  installed package platformexps-tools-codegencli-codegencli X.X.X, installed using Python 3.X.X
  These apps are now globally available
    - codegen
done! ✨ 🌟 ✨
```

### Verify Installation

```bash
codegen version
```

**Expected**: Shows CODEGEN CLI version

---

## Step 5: Create GitHub Personal Access Token (PAT)

You'll need a PAT to authenticate GitHub MCP.

### Create the Token

1. **Go to**: https://github.com/settings/tokens
2. **Click**: "Generate New Token (Classic)"
3. **Name it**: "Cursor GitHub MCP" (or similar)
4. **Set Expiration**: Custom expiration or longer than 30 days (recommended)
5. **Select ONLY Read permissions**:
   - ✅ `read:org` (under admin:org)
   - ✅ `read:repo_hook` (under admin:repo_hook)  
   - ✅ `read:user` (under user)
   - ✅ `read:discussion` (under write:discussion)
   - ✅ `read:enterprise` (under admin:enterprise)
   - ✅ `read:project` (under project)

6. **Click**: "Generate token"
7. **Copy the token** - you won't see it again!

**⚠️ IMPORTANT**: 
- Do NOT grant any Write permissions
- Only select Read permissions
- Save the token securely (you'll need it in the next step)

---

## Step 6: Install GitHub MCP

Now install the GitHub MCP using CODEGEN CLI.

### Run Installation Command

```bash
codegen mcp install github-mcp:latest
```

### During Installation

You'll be prompted several times:

1. **Python Version Selection**: 
   - Select the **latest Python 3.x version** (highest number)
   - Avoid older versions from previous installs

2. **Personal Access Token**:
   - Paste the PAT you created in Step 5
   - Press Enter

3. **Configuration Questions**:
   - Follow any additional prompts
   - Default options are usually fine

### Expected Output

```
✓ Successfully installed github-mcp
✓ MCP server configured in Cursor
✓ Ready to use!
```

### Restart Cursor

**IMPORTANT**: Close and reopen Cursor for the MCP to be recognized.

---

## Step 7: Verify GitHub MCP Installation

After restarting Cursor, verify the installation.

### Option 1: Check Cursor Settings

1. Open Cursor Settings
2. Go to: **MCP Servers** (or similar section)
3. Look for: `github-mcp`
4. Status should show: **Active** or **Connected**

### Option 2: Verify MCP Setup

In Cursor, type:

```
check my MCP setup
```

**Expected Output**:
```
🔍 MCP Status Check:
✅ GitHub MCP: Ready (Required)
   - Can access GitHub repositories
   - PAT authentication working
   - All required permissions available
```

---

## Step 8: (Optional) Install Mabl MCP

Mabl MCP is optional but enhances test generation with automation coverage analysis.

### Installation

Contact your Mabl administrator for:
- Mabl API key
- Workspace ID
- Installation instructions

### Benefits of Mabl MCP

- ✅ Identifies existing automated tests
- ✅ Shows test coverage gaps
- ✅ Suggests automation opportunities
- ✅ Links to Mabl test references

**Note**: QualityForge works perfectly fine without Mabl MCP. It's an enhancement, not a requirement.

---

## Step 9: (Optional) Install Additional MCPs

### Google Drive MCP (Recommended for Google Sheets creation)

Google Drive MCP enables creating formatted Google Sheets directly from test jam generation. This allows you to create professional, ready-to-use spreadsheets for test jams.

**Setup**: Enable via Cursor Settings → Tools & MCP's → DAST-Orch (includes Google Drive MCP)

### Bugsnag MCP

For error tracking and debugging:

```bash
codegen mcp install bugsnag-mcp:latest
```

**Use Case**: Identify bugs and errors in production

**Discussion**: https://company.slack.com/archives/C03TD1T7DP0/p1745344496369909

---

## ✅ Setup Complete!

You're now ready to use QualityForge!

### Quick Test

Try generating your first test jam:

```
/qforge

Provide a PR URL or repository name to get started!
```

### Example Usage

```
/qforge

I need test cases for:
https://github.com/org/messaging-app/pull/12345

Focus on email campaign functionality and billing integration.
```

---

## 🔍 Verification Checklist

Before using QualityForge, verify:

- [ ] Cursor IDE is installed and running
- [ ] GitHub authentication is configured (`gh auth status`)
- [ ] Python 3.9+ is installed (`python3 --version`)
- [ ] eiamCli is installed (`eiamcli --version`)
- [ ] CODEGEN CLI is installed (`codegen --version`)
- [ ] GitHub Personal Access Token is created and saved
- [ ] GitHub MCP is installed (`codegen mcp list` shows github-mcp)
- [ ] Cursor has been restarted after MCP installation
- [ ] MCP verification passes (type: `check my MCP setup`)

---

## 🐛 Troubleshooting

### "codegen: command not found"

**Solution**:
```bash
# Ensure pipx path is configured
pipx ensurepath

# Restart your terminal
source ~/.zshrc  # or source ~/.bashrc

# Verify
codegen --version
```

### "eiamcli: command not found" or Tap Errors

**Solution**:
```bash
# Ensure you have SSH access to github.com
ssh -T git@github.com

# If SSH works, retry the tap:
brew tap org/authcli git@github.com:EIAM/eiamCli-golang.git
brew install eiamCli

# Verify
eiamcli --version
```

**Note**: The tap requires SSH access to github.com. If you see "permission denied: publickey", see the SSH setup section below.

### "Permission denied (publickey)" Error

**Problem**: When running `brew tap` or `git clone` with SSH URLs, you see:
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Cause**: Your machine doesn't have an SSH key registered with github.com.

**Solution - Set up SSH key**:

1. **Check if you already have an SSH key**:
   ```bash
   ls -la ~/.ssh/id_ed25519.pub
   # or
   ls -la ~/.ssh/id_rsa.pub
   ```

2. **If no key exists, generate one**:
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   # Press Enter to accept default location
   # Enter a passphrase (recommended) or press Enter for none
   ```

3. **Start the SSH agent and add your key**:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

4. **Copy the public key to your clipboard**:
   ```bash
   pbcopy < ~/.ssh/id_ed25519.pub
   ```

5. **Add the key to GitHub**:
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Title: "Work Laptop" (or similar)
   - Paste the key
   - Click "Add SSH key"

6. **Verify SSH works**:
   ```bash
   ssh -T git@github.com
   ```
   **Expected**: `Hi username! You've successfully authenticated...`

7. **Now retry the brew tap**:
   ```bash
   brew tap org/authcli git@github.com:EIAM/eiamCli-golang.git
   brew install eiamCli
   ```

### "gh: command not found"

**Solution**:
```bash
brew install gh
gh auth login -h github.com -p https -w
```

### Python Version Issues

**Problem**: CODEGEN installs with wrong Python version

**Solution**:
```bash
# Check available Python versions
ls /usr/local/bin/python*

# Use the latest version explicitly
python3.11 --version  # (use your latest version)

# Reinstall with specific Python version
pipx install --force --python python3.11 platformexps_tools_codegencli_codegencli-*
```

### MCP Not Showing in Cursor

**Solutions**:
1. Restart Cursor (File → Quit, then reopen)
2. Check Cursor Settings → MCP Servers
3. Verify installation: `codegen mcp list`
4. Reinstall if needed: `codegen mcp install github-mcp:latest --force`

### Personal Access Token Errors

**Problem**: Authentication fails or token is rejected

**Solution**:
1. Verify token has correct Read permissions (no Write permissions)
2. Check token hasn't expired: https://github.com/settings/tokens
3. Generate a new token if needed
4. Reinstall GitHub MCP with new token

### "Permission Denied" Errors

**Problem**: Can't install packages or run commands

**Solution**:
```bash
# Fix Homebrew permissions
sudo chown -R $(whoami) /usr/local/bin /usr/local/lib

# Or use sudo for specific installs (not recommended generally)
sudo pip3 install ...
```

### Rate Limit Errors

**Problem**: GitHub API rate limit exceeded

**Solution**:
- Wait 1 hour for rate limits to reset
- Use authenticated requests (PAT provides higher limits)
- Reduce number of PR requests in a short time

---

## 💡 Pro Tips

### Clone Repositories Locally

For better performance and context:

```bash
# Clone the repo you're testing
git clone https://github.com/mctx/messaging-app

# Open in Cursor
cursor /path/to/messaging-app
```

**Benefits**:
- Faster analysis
- Better code context
- Fewer API requests
- More accurate test cases

### Keep Your PAT Secure

**Best Practices**:
- ✅ Store in password manager (1Password, LastPass)
- ✅ Use meaningful token names
- ✅ Set reasonable expiration dates
- ✅ Only grant Read permissions
- ❌ Never commit tokens to git
- ❌ Never share tokens publicly
- ❌ Never grant Write permissions unless required

### Update CODEGEN Regularly

```bash
# Check for updates
codegen --version

# Update CODEGEN
pipx upgrade platformexps-tools-codegencli-codegencli

# Update MCPs
codegen mcp update github-mcp
```

---

## 📚 Additional Resources

### Documentation
- **Cursor Onboarding**: https://docs.example.com/app/dp/capability/CAP-2127/capabilityDocs/main/docs/reference/cursor/onboarding_guide.md
- **Test Jam README**: [README.md](../README.md)
- **MCP Setup Guide**: [MCP-SETUP.md](./MCP-SETUP.md)
- **Quick Start**: [QUICK-START.md](../QUICK-START.md)

### Support Channels
- **Slack**: #mcqa channel
- **CODEGEN Issues**: Reach out to Gregory Lehman (@greg)
- **General Cursor**: #cursor-support or internal documentation

### Related Tools
- **Bugsnag MCP**: For error tracking
- **Atlassian MCP**: For Jira issue management (uses OAuth)
- **Mabl MCP**: For test automation coverage

### Atlassian MCP Setup (for Jira Integration)

To enable Jira ticket fetching and creation in QualityForge:

1. Add to `~/.cursor/mcp.json` under `"mcpServers"`:
   ```json
   "atlassian-mcp-server": {
     "url": "https://mcp.atlassian.com/v1/mcp",
     "type": "http"
   }
   ```

2. Restart Cursor

3. Go to **Settings → Tools & MCP**

4. Find "atlassian-mcp-server" and click **"Authenticate"** (instead of the usual toggle)

5. Complete OAuth login in your browser

Once authenticated, QualityForge can automatically fetch Jira tickets and create new issues.

---

## 🎯 Next Steps

Now that setup is complete:

1. **Try `/qforge`**: Generate your first test jam
2. **Explore examples**: MCP verification will happen automatically
3. **Clone repos**: Set up local repositories for better performance
4. **Install optional MCPs**: Enhance your workflow with Mabl, Bugsnag, or Jira
5. **Share feedback**: Help improve this guide for future users

---

## 📝 Feedback & Updates

**Found an issue?** Help improve this guide!

If you encounter errors not covered here:
1. Document the error and solution
2. Update this guide (PR welcome!)
3. Reach out to Gregory Lehman (@greg) in Slack

**Your contributions help everyone!** 🙌

---

**Ready to create your first Test Jam?** 🎉

Type `/qforge` in Cursor and let's get started!


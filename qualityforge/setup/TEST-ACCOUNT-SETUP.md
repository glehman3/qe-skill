# Test Account Setup Guide

This guide walks you through creating test accounts for Test Jam execution using the Test Tools UI.

---

## Overview

When test cases are generated, you may also receive a **Test Account CSV** that contains pre-populated data for creating test accounts. This makes account creation quick and consistent across all test participants.

### What You'll Need

- Access to Test Tools UI: https://test-tools.example.com/createaccount
- Test Account CSV file (e.g., `testjam_test_accounts.csv`)
- company email address for test accounts
- Z-Scaler Authenticated and Active
- ~2-3 minutes per account

---

## Quick Start

### Step 1: Open Your Test Account CSV

1. Locate your test account CSV file in your test jam folder
   - File: `testjam_test_accounts.csv` or `testjam_participant_N_accounts.csv`
2. Open in spreadsheet application (Excel, Google Sheets, Numbers)
3. Identify which accounts you need to create
   - Look at **Test Case ID** column to match with your assigned test cases
   - Check **Account Purpose** to understand what each account is for

### Step 2: Navigate to Test Tools

1. Open browser (Chrome recommended)
2. Go to: https://test-tools.example.com/createaccount
3. Log in with your SSO credentials if prompted (SSO)
### Step 3: Create Account Using CSV Data

Follow the field mapping below to transfer data from your CSV to the test tools form.

---

## Field-by-Field Mapping

### Account Configuration Section

| Form Field | CSV Column | Instructions |
|------------|------------|--------------|
| **Region** | Region | Select from dropdown (e.g., `us-east`, `us-west`) |
| **Creation Date** | Creation Date | Click date picker, enter date from CSV |
| **Creation Time** | Creation Time | Click time picker, enter time from CSV |
| **Manual activate this account?** | Manual Activation | Select radio button: `Yes` or `No`<br>**Recommended**: `No` |
| **Set Account Signup Source?** | Entry Point | Select from dropdown (usually `Default`) |
| **Mark account as experimental for A/B testing platform** | A/B Test Experimental | Toggle switch: `On` or `Off` |

### Account Login Info Section

| Form Field | CSV Column | Instructions |
|------------|------------|--------------|
| **Email** | Email | Copy/paste email from CSV<br>**Format**: `user+descriptor@example.com` |
| **Username** | Username | Copy/paste username from CSV<br>**Note**: Must be unique across region |
| **Password** | Password | Copy/paste password from CSV<br>**Important**: Save this securely! |

> **💡 Tip**: After form submission, Test Tools will auto-generate username/password if fields are left blank. If your CSV has pre-filled values, use those for consistency.

### Account Contact Info Section

| Form Field | CSV Column | Instructions |
|------------|------------|--------------|
| **First Name** | First Name | Copy/paste from CSV |
| **Last Name** | Last Name | Copy/paste from CSV |
| **Address** | Address | Copy/paste street address |
| **Address 2** | Address 2 | Copy/paste if provided (optional) |
| **City** | City | Copy/paste city name |
| **State** | State | Select from dropdown using CSV value |
| **Zipcode** | Zipcode | Copy/paste ZIP code |
| **Country** | Country | Select from dropdown using CSV value |
| **Sending Domain** | Sending Domain | Copy/paste domain (usually `example.com`) |
| **Company Name** | Company Name | Copy/paste company name |
| **Company Domain** | Company Domain | Copy/paste full URL (include `https://`) |

### Additional Account Options Section

| Form Field | CSV Column | Instructions |
|------------|------------|--------------|
| **Apply Feature Flags** | Feature Flags | Copy/paste feature flag names<br>**Format**: Comma-separated<br>**Example**: `feature_sms_enabled, feature_api_v3` |
| **Set Subscription Plan** | Subscription Plan | Select from dropdown<br>**Options**: Starter, Basic, Pro, Enterprise<br>**⚠️ CRITICAL**: Must match feature requirements! See plan validation below. |

> **🚨 SUBSCRIPTION PLAN VALIDATION**: The Subscription Plan MUST support the features being tested or tests will fail!
> 
> **Common Requirements:**
> - **SMS/MMS Testing** → Requires **Basic+ with messaging add-on** (NOT Starter)
> - **Marketing Automation** → Requires **Pro or Enterprise** (NOT Starter/Basic)
> - **AI Features** → Requires **Pro or Enterprise**
> - **Basic Email** → Starter plan OK
>
> See [feature-to-plan-mapping.md](../templates/feature-to-plan-mapping.md) for complete feature-to-plan matrix.

### Submit

1. **Review all fields** - Double-check data entry
2. **Click "Submit" button** - Create the account
3. **Save confirmation** - Note any confirmation details
4. **Update CSV** - Fill in "Created By" and "Date Created" columns

---

## Step-by-Step Example

### Example: Creating SMS Test Account

**Given this CSV row:**
```csv
Test Case ID: TC-001
Account Purpose: SMS Send Success Testing
Region: us1
Email: qa.test+sms_test@example.com
Username: test_account_sms01
Password: Testing123!
First Name: QA
Last Name: Tester
Address: 405 N Angier Ave NE
City: Atlanta
State: GA
Zipcode: 30308
Country: USA
Sending Domain: example.com
Company Name: QA SMS Testing
Company Domain: https://example.com
Feature Flags: feature_sms_enabled
Subscription Plan: Basic (500 seats) + messaging add-on
Notes: SMS requires paid plan - Basic is minimum tier with messaging add-on
```

**Steps:**

1. **Open Test Tools**: Navigate to create account page
2. **Account Configuration**:
   - Region: Select `us-east`
   - Creation Date: Today's date
   - Creation Time: Current time
   - Manual activate: Select `No`
   - Signup Source: Select `Default`
   - A/B testing platform: Toggle `Off`

3. **Login Info**:
   - Email: `qa.test+sms_test@example.com`
   - Username: `test_account_sms01`
   - Password: `Testing123!` ⚠️ **Save this password!**

4. **Contact Info**:
   - First Name: `QA`
   - Last Name: `Tester`
   - Address: `405 N Angier Ave NE`
   - Address 2: (leave blank)
   - City: `Atlanta`
   - State: `GA`
   - Zipcode: `30308`
   - Country: `USA`
   - Sending Domain: `example.com`
   - Company Name: `QA SMS Testing`
   - Company Domain: `https://example.com`

5. **Additional Options**:
   - Feature Flags: `feature_sms_enabled`
   - Subscription Plan: Select `Basic (500 seats)` ⚠️ **Not Free! SMS requires paid plan**
   - **Note**: messaging add-on must be purchased separately after account creation

6. **Submit**: Click "Submit" button

7. **Verify**: Check for success message

8. **Update CSV**: Add your name to "Created By" column, today's date to "Date Created"

---

## Common Issues and Solutions

### ❌ Email Already Exists

**Problem**: Email address is already registered

**Solution**:
- Use a different email alias: `user+sms_test2@example.com`
- Update CSV with new email for tracking
- Coordinate with team to avoid duplicates

### ❌ Username Already Taken

**Problem**: Username is not unique

**Solution**:
- Add a number suffix: `test_account_sms01` → `test_account_sms02`
- Update CSV with new username
- Ensure username matches what you'll use in tests

### ❌ Invalid ZIP/State Combination

**Problem**: ZIP code doesn't match selected state

**Solution**:
- Verify ZIP code is correct for the state
- Use valid combinations from CSV
- Common valid pairs: `30308/GA`, `94102/CA`, `78701/TX`

### ❌ Feature Flag Not Recognized

**Problem**: Feature flag name is invalid

**Solution**:
- Check with development team for correct flag names
- Flags are case-sensitive and environment-specific
- Leave blank if unsure; can be added later via admin-console

### ❌ Form Submission Fails

**Problem**: Generic submission error

**Solution**:
- Check all required fields are filled
- Verify network/VPN connection
- Try refreshing the page
- Check browser console for specific errors
- Contact Test Tools support team

### ❌ Lost Password

**Problem**: Forgot to save the generated password

**Solution**:
- Passwords cannot be recovered from Test Tools
- Create a new account with different email/username
- Use password manager for future accounts
- Update CSV with actual password used

### ❌ Wrong Subscription Plan Selected

**Problem**: Test fails because feature not available on selected plan (e.g., SMS on Starter plan)

**Solution**:
- **Check CSV Notes column**: Should explain why plan was chosen
- **Consult feature mapping**: See [feature-to-plan-mapping.md](../templates/feature-to-plan-mapping.md)
- **Common mistakes**:
  - SMS testing requires Basic+ (NOT Starter)
  - Marketing automation requires Pro+ (NOT Basic)
  - MMS requires Pro+ (NOT Basic)
- **If plan is wrong**: Create new account with correct plan, or upgrade via admin-console
- **Document**: Note plan issue in test results CSV

### ❌ Missing SMS Add-on

**Problem**: Account is on paid plan but SMS still doesn't work

**Solution**:
- SMS is an add-on that must be purchased separately
- Even with correct plan, SMS credits must be added
- Apply for messaging add-on through account settings
- Wait for SMS application approval (may take time)
- Document messaging add-on status in CSV notes

---

## Best Practices

### ✅ Before Creating Accounts

1. **Review Test Cases First**: Understand which accounts you need
2. **Validate Subscription Plan**: Verify plan supports features being tested (see [feature-to-plan-mapping.md](../templates/feature-to-plan-mapping.md))
3. **Check for Existing Accounts**: Avoid duplicates
4. **Prepare Password Storage**: Have secure location ready
5. **Verify VPN Connection**: Ensure network access

### During Account Creation

1. **Copy/Paste from CSV**: Reduces typos and saves time
2. **Double-Check Feature Flags**: Critical for test success
3. **Verify Email Format**: Must be valid company email address
4. **Save Credentials Immediately**: Don't wait until later

### After Account Creation

1. **Update CSV**: Mark "Created By" and "Date Created"
2. **Test Login**: Verify account works before test jam
3. **Document Issues**: Note any problems in "Notes" column
4. **Share with Team**: Communicate account status

### Security Practices

1. **Use Strong Passwords**: Even for test accounts
2. **Store Securely**: Use password manager or secure wiki
3. **Limit Sharing**: Only share with test jam participants
4. **Clean Up After**: Deactivate/delete accounts post-testing
5. **Follow company Policies**: Adhere to data security guidelines

---

## Account Verification Checklist

After creating an account, verify it's ready for testing:

- [ ] Account created successfully in Test Tools
- [ ] Login credentials saved securely
- [ ] Can log in to account via web UI
- [ ] Feature flags are enabled (if applicable)
- [ ] Subscription plan is correct
- [ ] Account has necessary credits/resources
- [ ] CSV updated with creation details
- [ ] Team notified account is ready

---

## Quick Reference: Test Tools UI

**URL**: https://test-tools.example.com/createaccount

**Required Fields** (cannot be blank):
- Shard
- Creation Date & Time
- Manual Activation selection
- Entry Point
- Email
- Username
- Password
- First Name
- Last Name
- Address
- City
- State
- Zipcode
- Country
- Sending Domain
- Company Name
- Company Domain
- Subscription Plan

**Optional Fields**:
- Address 2
- A/B Test Experimental flag
- Feature Flags

---

## Subscription Plan Validation Guide

> **🚨 CRITICAL**: Always verify the Subscription Plan matches the features being tested!

### Quick Validation Steps

Before creating ANY test account:

1. **Identify the feature(s)** being tested from the Test Case ID or Account Purpose
2. **Look up minimum required plan** in [feature-to-plan-mapping.md](../templates/feature-to-plan-mapping.md)
3. **Verify CSV has correct plan** in Subscription Plan column
4. **Check for add-ons** (especially SMS) that must be purchased separately

### Common Feature Requirements (Quick Reference)

| If Testing... | Minimum Plan Required |
|---------------|---------------------|
| **SMS (text messages)** | Basic + messaging add-on |
| **MMS (picture messages)** | Pro + messaging add-on |
| **Marketing Automation Flows** | Pro |
| **AI Features (AI Assistant)** | Pro |
| **Predictive Segmentation** | Pro |
| **A/B Testing (2 variants)** | Basic |
| **Multivariate Testing (3+ variants)** | Enterprise |
| **Custom HTML Templates** | Enterprise |
| **Basic Email Campaigns** | Free |

### When in Doubt

- **Most features** → Use **Pro** plan (safe middle ground)
- **SMS/MMS testing** → MUST use **paid plan** (Basic minimum for SMS, Pro for MMS)
- **Basic testing only** → Starter plan may be OK (check with test coordinator)

### Red Flags 🚩

**STOP and verify if you see:**
- ❌ SMS testing with Starter plan → **WRONG! Needs Basic+**
- ❌ MMS testing with Basic → **WRONG! Needs Pro+**
- ❌ Automation testing with Basic → **WRONG! Needs Pro+**
- ❌ Any paid feature with Starter plan → **Double-check requirements!**

**See full mapping**: [feature-to-plan-mapping.md](../templates/feature-to-plan-mapping.md)

---

## Additional Resources

- **Feature-to-Plan Mapping**: See [feature-to-plan-mapping.md](../templates/feature-to-plan-mapping.md) for complete feature requirements ⭐ **Use this first!**
- **Field Definitions**: See [test_account_fields.md](../templates/test_account_fields.md) for detailed field descriptions
- **CSV Format**: See [csv-formats.md](../templates/csv-formats.md) for test account CSV structure
- **CSV Template**: See [test_account_template.csv](../templates/test_account_template.csv) for example
- **admin-console Guide**: See [MCADMIN-NAVIGATION.md](../guides/MCADMIN-NAVIGATION.md) for post-creation account modifications

---

## Getting Help

### Test Tools Issues
- **Support**: Contact Test Tools support team
- **Documentation**: Check internal Test Tools wiki
- **Slack**: #test-tools-support channel

### Test Jam Issues
- **Test Coordinator**: Contact your test jam coordinator
- **Team**: Ask in your test jam Slack channel
- **Documentation**: Review test jam summary document

### Account Access Issues
- **VPN**: Ensure corporate VPN is connected
- **Permissions**: Verify you have Test Tools access
- **Authentication**: Check SSO login status

---

## Tips for Efficiency

### 🚀 Speed Tips

1. **Use Browser Autofill**: Configure browser to remember common values
2. **Keyboard Shortcuts**: Tab between fields quickly
3. **Multiple Tabs**: Open CSV and form side-by-side
4. **Copy Common Values**: Save frequently used addresses/domains
5. **Batch Creation**: Create all accounts at once if possible

### 🎯 Accuracy Tips

1. **Copy/Paste**: Don't manually type from CSV
2. **Check Before Submit**: Review all fields once
3. **Test Immediately**: Verify login right after creation
4. **Document Changes**: Note any deviations from CSV
5. **Update CSV Live**: Fill tracking columns immediately

### 👥 Team Tips

1. **Coordinate**: Avoid duplicate account creation
2. **Share Status**: Update team when accounts ready
3. **Help Each Other**: Share solutions to common issues
4. **Standardize**: Use consistent naming conventions
5. **Communicate**: Report problems early

---

## Next Steps

After creating your test accounts:

1. ✅ **Verify Account Access**: Log in to each account
2. ✅ **Review Test Cases**: Match accounts to test case requirements
3. ✅ **Complete Pre-conditions**: Set up any additional account configuration
4. ✅ **Begin Testing**: Execute your assigned test cases
5. ✅ **Track Results**: Update test case CSV with execution results

**Ready to start testing? Good luck with your Test Jam! 🎯**



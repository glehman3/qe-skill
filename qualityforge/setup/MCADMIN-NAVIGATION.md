# admin-console Navigation Guide

> ⚠️ **STATUS**: This guide is currently under development. Specific navigation steps and procedures are being documented and will be added soon.

This guide provides step-by-step instructions for navigating admin-console to modify test account settings after initial account creation.

---

## Overview

After creating test accounts via Test Tools, you may need to modify account settings such as:
- Monthly Recurring Revenue (MRR)
- Account plan/tier changes
- Feature flag modifications
- Credit adjustments
- Account permissions
- Billing settings

admin-console provides the interface for making these post-creation modifications.

---

## Prerequisites

Before using admin-console, ensure you have:
- ✅ Created test account(s) via Test Tools
- ✅ Account username and credentials
- ✅ Access to admin-console (proper permissions)
- ✅ VPN connection to company network
- ✅ Understanding of what settings need to be changed

---

## Quick Reference

### admin-console Access

**URL**: [To be documented]

**Required Permissions**: [To be documented]

**Login Method**: [To be documented]

---

## Common Tasks

### 🔄 Task 1: Changing Monthly Recurring Revenue (MRR)

> **Status**: 🚧 Steps to be documented

**When to use**: When test cases require specific MRR values for billing/plan testing

**Prerequisites**:
- Account created and active
- Know target MRR value
- Access to admin-console billing section

**Steps**:
1. [Step 1 - To be documented]
2. [Step 2 - To be documented]
3. [Step 3 - To be documented]
4. [Verification step - To be documented]

**Expected Result**: [To be documented]

**Troubleshooting**:
- [Common issue 1 - To be documented]
- [Common issue 2 - To be documented]

---

### 📊 Task 2: Modifying Account Plan/Tier

> **Status**: 🚧 Steps to be documented

**When to use**: When upgrading/downgrading test account plans

**Prerequisites**:
- Account created with initial plan
- Know target plan/tier
- Understand plan features and limitations

**Steps**:
1. [Step 1 - To be documented]
2. [Step 2 - To be documented]
3. [Step 3 - To be documented]
4. [Verification step - To be documented]

**Expected Result**: [To be documented]

**Troubleshooting**:
- [Common issue 1 - To be documented]
- [Common issue 2 - To be documented]

---

### 🚩 Task 3: Adding or Modifying Feature Flags

> **Status**: 🚧 Steps to be documented

**When to use**: When enabling/disabling feature flags after account creation

**Prerequisites**:
- Account created
- Know feature flag names
- Understand flag impact on account

**Steps**:
1. [Step 1 - To be documented]
2. [Step 2 - To be documented]
3. [Step 3 - To be documented]
4. [Verification step - To be documented]

**Expected Result**: [To be documented]

**Troubleshooting**:
- [Common issue 1 - To be documented]
- [Common issue 2 - To be documented]

---

### 💳 Task 4: Adjusting Account Credits

> **Status**: 🚧 Steps to be documented

**When to use**: When test cases require specific credit amounts (email credits, SMS credits, etc.)

**Prerequisites**:
- Account created
- Know credit type and amount needed
- Access to credit management in admin-console

**Steps**:
1. [Step 1 - To be documented]
2. [Step 2 - To be documented]
3. [Step 3 - To be documented]
4. [Verification step - To be documented]

**Expected Result**: [To be documented]

**Troubleshooting**:
- [Common issue 1 - To be documented]
- [Common issue 2 - To be documented]

---

### ⚙️ Task 5: Modifying Account Settings

> **Status**: 🚧 Steps to be documented

**When to use**: When changing general account configuration settings

**Prerequisites**:
- Account created
- Know specific settings to modify
- Understand impact of setting changes

**Steps**:
1. [Step 1 - To be documented]
2. [Step 2 - To be documented]
3. [Step 3 - To be documented]
4. [Verification step - To be documented]

**Expected Result**: [To be documented]

**Troubleshooting**:
- [Common issue 1 - To be documented]
- [Common issue 2 - To be documented]

---

### 🔐 Task 6: Managing Account Permissions

> **Status**: 🚧 Steps to be documented

**When to use**: When adding/removing user permissions or roles

**Prerequisites**:
- Account created
- Know permission/role requirements
- Understand permission hierarchy

**Steps**:
1. [Step 1 - To be documented]
2. [Step 2 - To be documented]
3. [Step 3 - To be documented]
4. [Verification step - To be documented]

**Expected Result**: [To be documented]

**Troubleshooting**:
- [Common issue 1 - To be documented]
- [Common issue 2 - To be documented]

---

## Navigation Structure

### admin-console Main Sections

> **Status**: 🚧 To be documented

Expected sections in admin-console:
- Dashboard/Home
- Account Search
- Account Details
- Billing/MRR Management
- Plan Management
- Feature Flags
- Credits Management
- Settings
- User Management
- [Other sections - To be documented]

**Navigation Path Templates**:
```
Home → [Section] → [Subsection] → [Action]
```

---

## Best Practices

### ✅ Before Making Changes

1. **Document Current State**: Record current settings before modifications
2. **Verify Account**: Confirm you're modifying the correct account
3. **Understand Impact**: Know what the change will affect
4. **Check Dependencies**: Ensure no other settings will be broken
5. **Have Rollback Plan**: Know how to undo changes if needed

### ✅ During Changes

1. **One Change at a Time**: Modify one setting, verify, then proceed
2. **Take Screenshots**: Document each step for troubleshooting
3. **Verify Immediately**: Check that change took effect
4. **Update Documentation**: Record what was changed and why
5. **Monitor for Errors**: Watch for error messages or warnings

### ✅ After Changes

1. **Test Functionality**: Verify account works as expected
2. **Update CSV**: Record modifications in test account CSV
3. **Notify Team**: Communicate changes to test participants
4. **Document Learnings**: Note any issues or tips for future use
5. **Verify Test Cases**: Ensure test cases can still execute

---

## Common Issues and Solutions

### ❌ Cannot Access admin-console

**Problem**: Permission denied or cannot load admin-console

**Solution**:
- [To be documented]
- Check VPN connection
- Verify user permissions
- Contact admin-console support team

### ❌ Changes Don't Take Effect

**Problem**: Modified settings but no change visible

**Solution**:
- [To be documented]
- Clear browser cache
- Log out and log back in
- Wait for propagation delay
- Verify change in correct environment

### ❌ Account Not Found

**Problem**: Cannot locate account in admin-console search

**Solution**:
- [To be documented]
- Verify account was created successfully
- Check correct shard/environment
- Try searching by different fields (email, username, ID)
- Confirm account activation status

---

## Field Reference

### MRR (Monthly Recurring Revenue)

**Description**: [To be documented]

**Valid Values**: [To be documented]

**Impact**: [To be documented]

**Related Settings**: [To be documented]

### [Other admin-console Fields]

> **Status**: 🚧 Additional fields to be documented

---

## Examples

### Example 1: Setting MRR for Premium Test Case

> **Status**: 🚧 To be documented with screenshots/detailed steps

**Scenario**: Test case requires account with $299 MRR

**Steps**: [To be documented]

### Example 2: Enabling Beta Feature Flags

> **Status**: 🚧 To be documented with screenshots/detailed steps

**Scenario**: Test case requires beta features enabled

**Steps**: [To be documented]

---

## Verification Checklist

After making changes in admin-console, verify:

- [ ] Changes visible in admin-console UI
- [ ] Changes reflected in account dashboard
- [ ] Related settings updated correctly
- [ ] No error messages or warnings
- [ ] Test account CSV updated with changes
- [ ] Team notified of modifications
- [ ] Test cases can still execute successfully

---

## Integration with Test Jam Workflow

### Workflow Overview

```
1. Create Account (Test Tools)
   ↓
2. Verify Account Created
   ↓
3. Modify Settings (admin-console) ← This guide
   ↓
4. Verify Modifications
   ↓
5. Execute Test Cases
   ↓
6. Document Results
```

### When to Use admin-console

**During Test Jam Setup**:
- Adjusting account settings before testing begins
- Setting up specific account configurations
- Enabling required feature flags

**During Test Execution**:
- Modifying account state for different test scenarios
- Adjusting credits/limits for boundary testing
- Changing plans to test tier-specific features

**After Test Execution**:
- Resetting accounts for reuse
- Documenting final account state
- Cleaning up test modifications

---

## Additional Resources

- **admin-console Documentation**: [Link to be added]
- **admin-console Support**: [Contact info to be added]
- **Slack Channel**: [Channel name to be added]
- **Video Tutorials**: [Links to be added]
- **FAQ**: [Link to be added]

---

## Getting Help

### admin-console Issues
- **Support Team**: [To be documented]
- **Documentation**: [To be documented]
- **Slack**: [To be documented]

### Permission Issues
- **Who to Contact**: [To be documented]
- **Request Process**: [To be documented]

---

## Contributing to This Guide

> **Help Wanted!** This guide is under active development.

If you have experience with admin-console and would like to contribute:

1. **Document Your Process**: Take screenshots and notes while performing tasks
2. **Share Navigation Paths**: Document how you navigate to specific features
3. **Note Common Issues**: Record problems you've encountered and solutions
4. **Submit Updates**: Share your documentation with the test jam team

**Contact**: [To be added]

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-12-19 | Initial placeholder guide created | Test Jam Team |
| TBD | MRR modification steps added | TBD |
| TBD | Feature flag steps added | TBD |
| TBD | Account plan modification steps added | TBD |

---

## Next Steps

1. ✅ Create test account via Test Tools (see [TEST-ACCOUNT-SETUP.md](../setup/TEST-ACCOUNT-SETUP.md))
2. ✅ Access admin-console with proper permissions
3. ⏳ Follow specific task sections above (being documented)
4. ✅ Verify changes took effect
5. ✅ Execute test cases
6. ✅ Document results

---

**Note**: This guide is actively being developed. Check back for updates, or contribute your admin-console knowledge to help complete it!






# Feature-to-Plan Mapping Reference

> **Critical**: Always select the correct Marketing Plan based on the features being tested. Using the wrong plan will cause test failures.

This document maps platform features to their required Marketing Plans to ensure test accounts are created with appropriate access.

**Reference**: [Platform Pricing Page](https://example.com/pricing/)

---

## Marketing Plan Tiers

| Plan | Monthly Cost* | Contacts | Key Use Cases |
|------|--------------|----------|---------------|
| **Free** | $0 | Up to 500 | Basic email marketing only |
| **Essentials** | Starts ~$13/mo | 500+ | Email + basic features |
| **Standard** | Starts ~$20/mo | 500+ | Advanced email + automation |
| **Premium** | Starts ~$350/mo | 10,000+ | Full feature set + priority support |

_*Pricing varies by contact count and features_

---

## Feature Availability Matrix

### 🔴 Premium Plan ONLY

These features **require Premium plan** - will NOT work on Free, Essentials, or Standard:

| Feature | Description | Why Premium Required |
|---------|-------------|---------------------|
| **Multivariate Testing** | A/B/C/D testing with 3+ variants | Advanced analytics feature |
| **Advanced Segmentation** | Unlimited segments with complex logic | Premium analytics |
| **Comparative Reports** | Compare campaigns side-by-side | Premium reporting |
| **Phone Support** | Direct phone support access | Premium service |
| **Personalized Onboarding** | Dedicated onboarding specialist | Premium service |
| **Custom-Coded Templates** | HTML/CSS custom email templates | Premium feature |
| **Enhanced Automations** | Advanced automation workflows | Premium automation |

### 🟡 Standard Plan or Higher

These features **require Standard OR Premium** - will NOT work on Free or Essentials:

| Feature | Description | Minimum Plan |
|---------|-------------|-------------|
| **Marketing Automation Flows** | Customer journey builder, advanced automations | Standard |
| **Behavioral Targeting** | Target based on behavior/activity | Standard |
| **Predictive Segmentation** | AI-powered audience predictions | Standard |
| **Custom Domains** | Custom sending domains | Standard |
| **Retargeting Ads** | Create retargeting campaigns | Standard |
| **Dynamic Content** | Personalized content blocks | Standard |
| **Send Time Optimization** | AI-optimized send times | Standard |
| **AI Assistant (AI)** | AI-powered marketing assistant | Standard |

### 🟢 Essentials Plan or Higher

These features **require Essentials, Standard, OR Premium** - will NOT work on Free:

| Feature | Description | Minimum Plan |
|---------|-------------|-------------|
| **A/B Testing** | Basic A/B testing (2 variants) | Essentials |
| **Custom Branding** | Remove platform branding | Essentials |
| **Email Templates (All)** | Access to all email templates | Essentials |
| **24/7 Email & Chat Support** | Round-the-clock support | Essentials |

### ⚪ Free Plan Included

These features work on **ALL plans** including Free:

| Feature | Available On |
|---------|-------------|
| **Basic Email Campaigns** | All plans |
| **Email Templates (Basic)** | All plans |
| **Audience Management** | All plans |
| **Landing Pages (1)** | All plans (1 published page on Free) |
| **Basic Forms** | All plans |
| **Marketing CRM** | All plans |
| **Website Builder (1)** | All plans (1 site on Free) |
| **Basic Reports** | All plans |

---

## SMS Marketing 🚨 CRITICAL

**SMS is an ADD-ON to PAID PLANS ONLY**

| Feature | Minimum Plan | Notes |
|---------|-------------|-------|
| **SMS Marketing** | **Essentials + SMS add-on** | NOT available on Free plan |
| **MMS (Picture Messages)** | **Standard or Premium** | Only for US/Canada contacts |

### SMS Plan Requirements:

✅ **To test SMS, you MUST:**
1. Use **Essentials, Standard, or Premium** plan (NOT Free)
2. Purchase SMS credits separately (add-on)
3. Have contacts in supported countries
4. Complete SMS application and terms agreement

❌ **SMS will FAIL if:**
- Account is on Free plan
- No SMS credits purchased
- SMS add-on not activated
- Contacts in unsupported countries

**Testing MMS?** → Requires **Standard or Premium** plan

---

## Common Test Scenarios → Required Plans

Use this quick reference when creating test accounts:

### Email Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic email send | **Free** | Core functionality |
| Email with A/B testing | **Essentials** | A/B testing requires Essentials+ |
| Email with automation | **Standard** | Advanced automation on Standard+ |
| Email with predictive segments | **Standard** | AI features on Standard+ |
| Email with custom HTML | **Premium** | Custom templates on Premium |

### SMS/MMS Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| SMS send (text only) | **Essentials + SMS add-on** | SMS requires paid plan |
| MMS send (with images) | **Standard + SMS add-on** | MMS only on Standard/Premium |
| SMS + Email campaign | **Essentials + SMS add-on** | Combined channels |
| SMS automation | **Standard + SMS add-on** | Automation requires Standard+ |

### API Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic API calls | **Free** | API available on all plans |
| Transactional API | **Any paid plan** | Transactional requires paid |
| High-volume API | **Standard or Premium** | Rate limits higher on paid plans |
| Webhook integrations | **Standard or Premium** | Webhooks on Standard+ |

### Automation Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic automation | **Essentials** | Simple automations on Essentials+ |
| Marketing automation flows | **Standard** | Journey builder on Standard+ |
| Advanced segmentation | **Standard** | Complex logic on Standard+ |
| Predictive automations | **Standard** | AI features on Standard+ |
| Custom workflows | **Premium** | Enhanced automations on Premium |

### Website/Landing Page Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Single landing page | **Free** | 1 page included on Free |
| Multiple landing pages | **Essentials** | More pages on paid plans |
| Full website | **Any paid plan** | Multiple sites on paid plans |
| Custom domain | **Standard** | Custom domains on Standard+ |

### Integration Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic integrations | **Free** | Most integrations on all plans |
| E-commerce sync | **Any paid plan** | Transactional features require paid |
| Advanced e-commerce | **Standard** | Product recommendations on Standard+ |
| CRM integration | **Standard or Premium** | Advanced CRM on Standard+ |

---

## Plan Selection Decision Tree

```
START: What feature are you testing?

├─ SMS or MMS?
│  ├─ Text only (SMS) → Essentials + SMS add-on
│  └─ Images (MMS) → Standard + SMS add-on
│
├─ Marketing Automation / Journey Builder?
│  └─ Standard or Premium
│
├─ AI Features (AI Assistant, Predictive Segments)?
│  └─ Standard or Premium
│
├─ A/B Testing?
│  ├─ 2 variants → Essentials or higher
│  └─ 3+ variants → Premium only
│
├─ Custom HTML Templates?
│  └─ Premium only
│
├─ API Only (no UI features)?
│  ├─ Basic API → Free
│  └─ Transactional / High-volume → Standard or Premium
│
├─ Basic Email Campaigns?
│  └─ Free (but Essentials+ recommended for support)
│
└─ When in doubt → Standard
   (covers most features, good middle ground)
```

---

## Validation Checklist

Before creating a test account, verify the plan selection:

### Step 1: Identify Features Being Tested

From PR, PRD, or test case description, list all features:
- [ ] What features are explicitly mentioned?
- [ ] What APIs or endpoints are involved?
- [ ] Are there any integrations?
- [ ] Is this a new feature or existing feature?

### Step 2: Find Maximum Plan Requirement

Check each feature against the matrix above:
- [ ] Does ANY feature require Premium? → Use Premium
- [ ] Does ANY feature require Standard? → Use Standard (minimum)
- [ ] Does ANY feature require Essentials? → Use Essentials (minimum)
- [ ] All features work on Free? → Use Free (or Essentials for better testing)

### Step 3: Check for Add-ons

- [ ] **SMS/MMS?** → Add SMS credits and note in CSV
- [ ] **Transactional Email?** → May need separate setup
- [ ] **High-volume sending?** → Consider contact tier

### Step 4: Document in CSV

In the **Marketing Plan** column, specify:
- Plan tier name (e.g., "Standard (2500 contacts)")
- Any add-ons needed (e.g., "+ SMS credits")
- In **Notes** column, explain why this plan was chosen

---

## Examples with Correct Plans

### ✅ CORRECT Examples

**Example 1: SMS Send Testing**
```csv
Account Purpose: SMS Send Success Flow Testing
Marketing Plan: Essentials (500 contacts) + SMS add-on
Notes: SMS requires paid plan. Essentials is minimum for SMS feature.
```

**Example 2: Marketing Automation Testing**
```csv
Account Purpose: Customer Journey Automation Testing
Marketing Plan: Standard (2500 contacts)
Notes: Marketing automation flows require Standard plan minimum.
```

**Example 3: Basic Email Campaign**
```csv
Account Purpose: Email Send and Open Rate Testing
Marketing Plan: Free plan (500 contacts)
Notes: Basic email testing only. Free plan sufficient for core functionality.
```

**Example 4: MMS Testing**
```csv
Account Purpose: MMS Send with Images Testing
Marketing Plan: Standard (2500 contacts) + SMS add-on
Notes: MMS requires Standard or Premium plan. Standard chosen for cost-effectiveness.
```

**Example 5: AI-Powered Segmentation**
```csv
Account Purpose: Predictive Segmentation Testing
Marketing Plan: Standard (2500 contacts)
Notes: Predictive segments and AI features require Standard plan minimum.
```

### ❌ INCORRECT Examples (DO NOT USE)

**Example 1: ❌ WRONG - SMS on Free Plan**
```csv
Account Purpose: SMS Send Success Flow Testing
Marketing Plan: Free plan (500 contacts)  ← WRONG! SMS not available on Free
Notes: Test account for SMS send functionality
```
**Why Wrong**: SMS is not available on Free plan. Will fail during testing.

**Example 2: ❌ WRONG - Automation on Essentials**
```csv
Account Purpose: Marketing Automation Flows Testing
Marketing Plan: Essentials (500 contacts)  ← WRONG! Flows need Standard
Notes: Test automation workflows
```
**Why Wrong**: Marketing automation flows require Standard plan minimum.

**Example 3: ❌ WRONG - MMS on Essentials**
```csv
Account Purpose: MMS Picture Message Testing
Marketing Plan: Essentials (500 contacts) + SMS add-on  ← WRONG! MMS needs Standard
Notes: Test MMS with images
```
**Why Wrong**: MMS is only available on Standard or Premium plans.

---

## When Testing Multiple Features

If your test jam involves **multiple features with different requirements**:

### Option 1: Use Highest Required Plan (Recommended)

Choose the highest plan tier required by ANY feature being tested.

**Example**: Testing both email campaigns (Free OK) and SMS (Essentials required)
- ✅ **Solution**: Use Essentials or Standard for all test accounts
- **Benefit**: All accounts can test all features

### Option 2: Create Multiple Account Types

Create different account tiers for different test scenarios.

**Example**: Testing email (Free OK), automation (Standard), and custom templates (Premium)
- ✅ **Solution**: 
  - 3 Free plan accounts for basic email tests
  - 5 Standard accounts for automation tests
  - 2 Premium accounts for custom template tests
- **Benefit**: More realistic testing across plan tiers
- **Note**: Document clearly which accounts are for which tests

---

## Special Considerations

### Contact Tier Selection

Higher contact tiers affect cost but not feature availability (except Premium).

**Guidance**:
- **Testing core features**: Use minimum contacts (500 for Free, 500 for paid)
- **Testing scalability**: Use higher contact tiers (10,000+)
- **Testing Premium**: Use 10,000+ contacts (Premium requires this tier)

### Feature Flags vs. Plan Features

Some features are controlled by **feature flags** (internal) vs. **plan tiers** (customer-facing).

**Important**:
- Feature flags can enable beta features on any plan
- Plan tiers control officially released features
- For test accounts, **both** may be needed:
  - Set correct Marketing Plan for released features
  - Add feature flags for beta/internal features

### Environment Differences

Plan features may differ between:
- **Production** (mc.us1.list-manage.com)
- **Pre-Production** (mc.us1.list-manage-preprod.com)
- **Test Environments** (test tools)

**For Test Accounts**: Use the plan tier that matches production requirements to ensure realistic testing.

---

## Quick Reference: Common Mistakes

| ❌ Common Mistake | ✅ Correct Approach |
|------------------|-------------------|
| Using Free plan for SMS testing | Use Essentials + SMS add-on minimum |
| Using Essentials for automation flows | Use Standard plan minimum |
| Using Standard for MMS testing | Standard is OK! (Standard or Premium) |
| Using Free for A/B testing | Use Essentials minimum |
| Forgetting SMS add-on | Must explicitly add SMS credits |
| Using wrong contact tier for Premium | Premium requires 10,000+ contacts |

---

## Updates and Maintenance

**This document should be updated when**:
- platform releases new features
- Plan tiers change
- Feature availability moves between plans
- New add-ons become available

**Last Updated**: December 19, 2025  
**Source**: [Platform Pricing](https://example.com/pricing/)  
**Maintainer**: Test Jam Team

---

## Integration with Test Jam Workflow

### During Test Case Generation

When the `/testjam` command analyzes PRs or PRDs:

1. **Extract feature names** from PR description, file changes, labels
2. **Map to required plan** using this reference document
3. **Generate test account CSV** with correct Marketing Plan pre-filled
4. **Add validation note** in CSV explaining plan selection
5. **Flag ambiguous cases** for manual review

### During Test Account Creation

When participants create accounts:

1. **Review Marketing Plan column** in CSV
2. **Cross-reference** with this document if unclear
3. **Verify** plan selection matches feature being tested
4. **Escalate** if plan seems incorrect

### During Test Execution

If tests fail unexpectedly:

1. **Check account plan** as first troubleshooting step
2. **Verify feature availability** on current plan
3. **Upgrade account if needed** (via admin-console)
4. **Document** plan issues in test results

---

**Next Steps**: See [TEST-ACCOUNT-SETUP.md](../setup/TEST-ACCOUNT-SETUP.md) for account creation process.






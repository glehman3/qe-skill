# Feature-to-Plan Mapping Reference

> **Critical**: Always select the correct Subscription Plan based on the features being tested. Using the wrong plan will cause test failures.

This document maps platform features to their required Subscription Plans to ensure test accounts are created with appropriate access.

**Reference**: [Platform Pricing Page](https://example.com/pricing/)

---

## Subscription Plan Tiers

| Plan | Monthly Cost* | Contacts | Key Use Cases |
|------|--------------|----------|---------------|
| **Starter** | $0 | Up to 500 | Basic email marketing only |
| **Basic** | Starts ~$13/mo | 500+ | Email + basic features |
| **Pro** | Starts ~$20/mo | 500+ | Advanced email + automation |
| **Enterprise** | Starts ~$350/mo | 10,000+ | Full feature set + priority support |

_*Pricing varies by contact count and features_

---

## Feature Availability Matrix

### 🔴 Enterprise Plan ONLY

These features **require Enterprise plan** - will NOT work on Starter, Basic, or Pro:

| Feature | Description | Why Enterprise Required |
|---------|-------------|---------------------|
| **Multivariate Testing** | A/B/C/D testing with 3+ variants | Advanced analytics feature |
| **Advanced Segmentation** | Unlimited segments with complex logic | Enterprise analytics |
| **Comparative Reports** | Compare campaigns side-by-side | Enterprise reporting |
| **Phone Support** | Direct phone support access | Enterprise service |
| **Personalized Onboarding** | Dedicated onboarding specialist | Enterprise service |
| **Custom-Coded Templates** | HTML/CSS custom email templates | Enterprise feature |
| **Enhanced Automations** | Advanced automation workflows | Enterprise automation |

### 🟡 Pro Plan or Higher

These features **require Pro OR Enterprise** - will NOT work on Starter or Basic:

| Feature | Description | Minimum Plan |
|---------|-------------|-------------|
| **Marketing Automation Flows** | Customer journey builder, advanced automations | Pro |
| **Behavioral Targeting** | Target based on behavior/activity | Pro |
| **Predictive Segmentation** | AI-powered audience predictions | Pro |
| **Custom Domains** | Custom sending domains | Pro |
| **Retargeting Ads** | Create retargeting campaigns | Pro |
| **Dynamic Content** | Personalized content blocks | Pro |
| **Send Time Optimization** | AI-optimized send times | Pro |
| **AI Assistant (AI)** | AI-powered marketing assistant | Pro |

### 🟢 Basic Plan or Higher

These features **require Basic, Pro, OR Enterprise** - will NOT work on Starter:

| Feature | Description | Minimum Plan |
|---------|-------------|-------------|
| **A/B Testing** | Basic A/B testing (2 variants) | Basic |
| **Custom Branding** | Remove platform branding | Basic |
| **Email Templates (All)** | Access to all email templates | Basic |
| **24/7 Email & Chat Support** | Round-the-clock support | Basic |

### ⚪ Starter Plan Included

These features work on **ALL plans** including Starter:

| Feature | Available On |
|---------|-------------|
| **Basic Email Campaigns** | All plans |
| **Email Templates (Basic)** | All plans |
| **Audience Management** | All plans |
| **Landing Pages (1)** | All plans (1 published page on Starter) |
| **Basic Forms** | All plans |
| **Marketing CRM** | All plans |
| **Website Builder (1)** | All plans (1 site on Starter) |
| **Basic Reports** | All plans |

---

## SMS Marketing 🚨 CRITICAL

**SMS is an ADD-ON to PAID PLANS ONLY**

| Feature | Minimum Plan | Notes |
|---------|-------------|-------|
| **SMS Marketing** | **Basic + messaging add-on** | NOT available on Starter plan |
| **MMS (Picture Messages)** | **Pro or Enterprise** | Only for US/Canada contacts |

### SMS Plan Requirements:

✅ **To test SMS, you MUST:**
1. Use **Basic, Pro, or Enterprise** plan (NOT Starter)
2. Purchase SMS credits separately (add-on)
3. Have contacts in supported countries
4. Complete SMS application and terms agreement

❌ **SMS will FAIL if:**
- Account is on Starter plan
- No SMS credits purchased
- messaging add-on not activated
- Contacts in unsupported countries

**Testing MMS?** → Requires **Pro or Enterprise** plan

---

## Common Test Scenarios → Required Plans

Use this quick reference when creating test accounts:

### Email Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic email send | **Starter** | Core functionality |
| Email with A/B testing | **Basic** | A/B testing requires Basic+ |
| Email with automation | **Pro** | Advanced automation on Pro+ |
| Email with predictive segments | **Pro** | AI features on Pro+ |
| Email with custom HTML | **Enterprise** | Custom templates on Enterprise |

### SMS/MMS Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| SMS send (text only) | **Basic + messaging add-on** | SMS requires paid plan |
| MMS send (with images) | **Pro + messaging add-on** | MMS only on Pro/Enterprise |
| SMS + Email campaign | **Basic + messaging add-on** | Combined channels |
| SMS automation | **Pro + messaging add-on** | Automation requires Pro+ |

### API Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic API calls | **Starter** | API available on all plans |
| Transactional API | **Any paid plan** | Transactional requires paid |
| High-volume API | **Pro or Enterprise** | Rate limits higher on paid plans |
| Webhook integrations | **Pro or Enterprise** | Webhooks on Pro+ |

### Automation Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic automation | **Basic** | Simple automations on Basic+ |
| Marketing automation flows | **Pro** | Journey builder on Pro+ |
| Advanced segmentation | **Pro** | Complex logic on Pro+ |
| Predictive automations | **Pro** | AI features on Pro+ |
| Custom workflows | **Enterprise** | Enhanced automations on Enterprise |

### Website/Landing Page Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Single landing page | **Starter** | 1 page included on Starter |
| Multiple landing pages | **Basic** | More pages on paid plans |
| Full website | **Any paid plan** | Multiple sites on paid plans |
| Custom domain | **Pro** | Custom domains on Pro+ |

### Integration Testing

| Test Type | Minimum Plan | Rationale |
|-----------|-------------|-----------|
| Basic integrations | **Starter** | Most integrations on all plans |
| E-commerce sync | **Any paid plan** | Transactional features require paid |
| Advanced e-commerce | **Pro** | Product recommendations on Pro+ |
| CRM integration | **Pro or Enterprise** | Advanced CRM on Pro+ |

---

## Plan Selection Decision Tree

```
START: What feature are you testing?

├─ SMS or MMS?
│  ├─ Text only (SMS) → Basic + messaging add-on
│  └─ Images (MMS) → Pro + messaging add-on
│
├─ Marketing Automation / Journey Builder?
│  └─ Pro or Enterprise
│
├─ AI Features (AI Assistant, Predictive Segments)?
│  └─ Pro or Enterprise
│
├─ A/B Testing?
│  ├─ 2 variants → Basic or higher
│  └─ 3+ variants → Enterprise only
│
├─ Custom HTML Templates?
│  └─ Enterprise only
│
├─ API Only (no UI features)?
│  ├─ Basic API → Starter
│  └─ Transactional / High-volume → Pro or Enterprise
│
├─ Basic Email Campaigns?
│  └─ Starter (but Basic+ recommended for support)
│
└─ When in doubt → Pro
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
- [ ] Does ANY feature require Enterprise? → Use Enterprise
- [ ] Does ANY feature require Pro? → Use Pro (minimum)
- [ ] Does ANY feature require Basic? → Use Basic (minimum)
- [ ] All features work on Starter? → Use Starter (or Basic for better testing)

### Step 3: Check for Add-ons

- [ ] **SMS/MMS?** → Add SMS credits and note in CSV
- [ ] **Transactional Email?** → May need separate setup
- [ ] **High-volume sending?** → Consider contact tier

### Step 4: Document in CSV

In the **Subscription Plan** column, specify:
- Plan tier name (e.g., "Pro (2500 seats)")
- Any add-ons needed (e.g., "+ SMS credits")
- In **Notes** column, explain why this plan was chosen

---

## Examples with Correct Plans

### ✅ CORRECT Examples

**Example 1: SMS Send Testing**
```csv
Account Purpose: SMS Send Success Flow Testing
Subscription Plan: Basic (500 seats) + messaging add-on
Notes: SMS requires paid plan. Basic is minimum for SMS feature.
```

**Example 2: Marketing Automation Testing**
```csv
Account Purpose: Customer Journey Automation Testing
Subscription Plan: Pro (2500 seats)
Notes: Marketing automation flows require Pro plan minimum.
```

**Example 3: Basic Email Campaign**
```csv
Account Purpose: Email Send and Open Rate Testing
Subscription Plan: Starter plan (500 seats)
Notes: Basic email testing only. Starter plan sufficient for core functionality.
```

**Example 4: MMS Testing**
```csv
Account Purpose: MMS Send with Images Testing
Subscription Plan: Pro (2500 seats) + messaging add-on
Notes: MMS requires Pro or Enterprise plan. Pro chosen for cost-effectiveness.
```

**Example 5: AI-Powered Segmentation**
```csv
Account Purpose: Predictive Segmentation Testing
Subscription Plan: Pro (2500 seats)
Notes: Predictive segments and AI features require Pro plan minimum.
```

### ❌ INCORRECT Examples (DO NOT USE)

**Example 1: ❌ WRONG - SMS on Starter Plan**
```csv
Account Purpose: SMS Send Success Flow Testing
Subscription Plan: Starter plan (500 seats)  ← WRONG! SMS not available on Starter
Notes: Test account for SMS send functionality
```
**Why Wrong**: SMS is not available on Starter plan. Will fail during testing.

**Example 2: ❌ WRONG - Automation on Basic**
```csv
Account Purpose: Marketing Automation Flows Testing
Subscription Plan: Basic (500 seats)  ← WRONG! Flows need Pro
Notes: Test automation workflows
```
**Why Wrong**: Marketing automation flows require Pro plan minimum.

**Example 3: ❌ WRONG - MMS on Basic**
```csv
Account Purpose: MMS Picture Message Testing
Subscription Plan: Basic (500 seats) + messaging add-on  ← WRONG! MMS needs Pro
Notes: Test MMS with images
```
**Why Wrong**: MMS is only available on Pro or Enterprise plans.

---

## When Testing Multiple Features

If your test jam involves **multiple features with different requirements**:

### Option 1: Use Highest Required Plan (Recommended)

Choose the highest plan tier required by ANY feature being tested.

**Example**: Testing both email campaigns (Starter OK) and SMS (Basic required)
- ✅ **Solution**: Use Basic or Pro for all test accounts
- **Benefit**: All accounts can test all features

### Option 2: Create Multiple Account Types

Create different account tiers for different test scenarios.

**Example**: Testing email (Starter OK), automation (Pro), and custom templates (Enterprise)
- ✅ **Solution**: 
  - 3 Starter plan accounts for basic email tests
  - 5 Pro accounts for automation tests
  - 2 Enterprise accounts for custom template tests
- **Benefit**: More realistic testing across plan tiers
- **Note**: Document clearly which accounts are for which tests

---

## Special Considerations

### Contact Tier Selection

Higher contact tiers affect cost but not feature availability (except Enterprise).

**Guidance**:
- **Testing core features**: Use minimum contacts (500 for Starter, 500 for paid)
- **Testing scalability**: Use higher contact tiers (10,000+)
- **Testing Enterprise**: Use 10,000+ contacts (Enterprise requires this tier)

### Feature Flags vs. Plan Features

Some features are controlled by **feature flags** (internal) vs. **plan tiers** (customer-facing).

**Important**:
- Feature flags can enable beta features on any plan
- Plan tiers control officially released features
- For test accounts, **both** may be needed:
  - Set correct Subscription Plan for released features
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
| Using Starter plan for SMS testing | Use Basic + messaging add-on minimum |
| Using Basic for automation flows | Use Pro plan minimum |
| Using Pro for MMS testing | Pro is OK! (Pro or Enterprise) |
| Using Starter for A/B testing | Use Basic minimum |
| Forgetting messaging add-on | Must explicitly add SMS credits |
| Using wrong contact tier for Enterprise | Enterprise requires 10,000+ contacts |

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
3. **Generate test account CSV** with correct Subscription Plan pre-filled
4. **Add validation note** in CSV explaining plan selection
5. **Flag ambiguous cases** for manual review

### During Test Account Creation

When participants create accounts:

1. **Review Subscription Plan column** in CSV
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






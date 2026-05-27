# Test Account Fields Reference

This document defines all fields required for creating test accounts via the Test Tools UI.

**Test Tools URL**: https://test-tools.example.com/createaccount

---

## Account Configuration

### Shard
- **Field Type**: Dropdown
- **Required**: Yes
- **Description**: The shard/server where the account will be created
- **Example Values**: `us-east`, `us-west`, `eu-west`, etc.
- **Default**: `us1`

### Creation Date
- **Field Type**: Date picker
- **Required**: Yes
- **Format**: `MM/DD/YYYY`
- **Description**: Date when the account should be created
- **Default**: Current date
- **Example**: `12/19/2025`

### Creation Time
- **Field Type**: Time picker
- **Required**: Yes
- **Format**: `HH:MM AM/PM`
- **Description**: Time when the account should be created
- **Default**: Current time
- **Example**: `02:01 PM`

### Manual Activation Account
- **Field Type**: Radio button (Yes/No)
- **Required**: Yes
- **Options**: 
  - `Yes` - Account requires manual activation
  - `No` - Account is automatically activated (recommended)
- **Default**: `No`
- **Description**: Select 'No' to skip setup flow and activate immediately

### Set Account Signup Source
- **Field Type**: Dropdown
- **Required**: Yes
- **Options**: `Default`, and other entry points
- **Default**: `Default`
- **Description**: Defines how the account was created/acquired

### Mark Account as Experimental for A/B testing platform
- **Field Type**: Toggle switch
- **Required**: No
- **Options**: `On` / `Off`
- **Default**: `Off`
- **Description**: Flags account for A/B test experiments

---

## Account Login Info

### Email
- **Field Type**: Text input
- **Required**: Yes
- **Format**: Valid email address
- **Description**: Login email for the test account
- **Example**: `qa.lead@example.com`
- **Notes**: 
  - Use company email addresses for internal testing
  - Can use aliases with `+` notation (e.g., `user+test1@example.com`)

### Username
- **Field Type**: Text input (auto-generated)
- **Required**: Yes
- **Description**: Unique username for the account
- **Auto-generated Format**: `test_account_[random]`
- **Example**: `test_account_3nBigh7`
- **Notes**: System generates a random username; can be customized if needed

### Password
- **Field Type**: Text input (auto-generated)
- **Required**: Yes
- **Description**: Password for the account
- **Auto-generated Format**: Random alphanumeric string
- **Example**: `n2qecC6^`
- **Notes**: 
  - System generates a secure random password
  - Copy Password button available in UI
  - Store securely for test execution

---

## Account Contact Info

### First Name
- **Field Type**: Text input
- **Required**: Yes
- **Description**: Account holder's first name
- **Example**: `Alex`

### Last Name
- **Field Type**: Text input
- **Required**: Yes
- **Description**: Account holder's last name
- **Example**: `Lehman`

### Address
- **Field Type**: Text input
- **Required**: Yes
- **Description**: Street address line 1
- **Example**: `405 N Angier Ave NE`

### Address 2
- **Field Type**: Text input
- **Required**: No (Optional)
- **Description**: Street address line 2 (apt, suite, etc.)
- **Example**: `Apt 4B`

### City
- **Field Type**: Text input
- **Required**: Yes
- **Description**: City name
- **Example**: `Atlanta`

### State
- **Field Type**: Dropdown
- **Required**: Yes
- **Description**: State/province selection
- **Example Values**: `GA`, `CA`, `NY`, etc.
- **Example**: `GA`

### Zipcode
- **Field Type**: Text input
- **Required**: Yes
- **Format**: 5-digit or 9-digit ZIP code
- **Description**: Postal/ZIP code
- **Example**: `30308`

### Country
- **Field Type**: Dropdown
- **Required**: Yes
- **Description**: Country selection
- **Example Values**: `USA`, `Canada`, `UK`, etc.
- **Default**: `USA`
- **Example**: `USA`

### Sending Domain
- **Field Type**: Text input
- **Required**: Yes
- **Format**: Valid domain name
- **Description**: Domain for sending emails/SMS
- **Default**: `example.com`
- **Example**: `example.com`

### Company Name
- **Field Type**: Text input
- **Required**: Yes
- **Description**: Company/organization name
- **Example**: `QA Platform Testing`

### Company Domain
- **Field Type**: Text input (URL)
- **Required**: Yes
- **Format**: Full URL with protocol
- **Description**: Company website URL
- **Example**: `https://example.com`

---

## Additional Account Options

### Apply Feature Flags
- **Field Type**: Text input (free form)
- **Required**: No (Optional)
- **Format**: Comma-separated feature flag names
- **Description**: Feature flags to enable on the account
- **Example**: `feature_sms_enabled, feature_new_dashboard, feature_beta_api`
- **Notes**: 
  - Leave blank if no specific flags needed
  - Multiple flags separated by commas
  - Check with dev team for available flags

### Set Subscription Plan
- **Field Type**: Dropdown
- **Required**: Yes
- **Options**: 
  - `Starter plan (500 seats)` - Basic email only
  - `Basic (500+ seats)` - Email + basic features
  - `Pro (500+ seats)` - Advanced features + automation
  - `Enterprise (10,000+ contacts)` - Full feature set
  - Contact tiers vary by plan
- **Default**: `Starter plan (500 seats)`
- **Description**: Initial subscription plan/tier for the account
- **🚨 CRITICAL**: Must match feature requirements or tests will fail!
  - **SMS/MMS** → Requires Basic+ (NOT Starter)
  - **Marketing Automation** → Requires Pro+ (NOT Starter/Basic)
  - **AI Features** → Requires Pro+
  - See [feature-to-plan-mapping.md](./feature-to-plan-mapping.md) for complete matrix
- **Notes**: 
  - Plan can be changed after account creation via admin-console
  - Some features require add-ons (e.g., SMS) even with correct plan
  - Contact tier affects pricing but not feature availability (except Enterprise)

---

## Submit Action

### Submit Button
- **Action**: Creates the test account with specified configuration
- **Result**: Account created and credentials available
- **Notes**: 
  - Save all account details immediately after creation
  - Account credentials cannot be recovered if lost
  - Username and password are unique per account

---

## Field Dependencies and Validation Rules

### Required Field Combinations:
1. **Minimum Required**: Shard, Creation Date/Time, Email, Username, Password, First Name, Last Name, Address, City, State, Zipcode, Country, Sending Domain, Company Name, Company Domain, Subscription Plan

2. **For Specific Test Scenarios**:
   - **SMS Testing**: 
     - ⚠️ Requires Basic, Pro, or Enterprise (NOT Starter)
     - Must purchase messaging add-on separately after account creation
     - Document "+ messaging add-on" in Subscription Plan or Notes
   - **MMS Testing**: 
     - ⚠️ Requires Pro or Enterprise (NOT Starter or Basic)
     - Must purchase messaging add-on with MMS capabilities
   - **Marketing Automation Testing**: 
     - ⚠️ Requires Pro or Enterprise (NOT Starter or Basic)
   - **AI Features Testing**:
     - ⚠️ Requires Pro or Enterprise
   - **API Testing**: May need specific feature flags enabled
   - **International Testing**: Set appropriate Country, State combinations

### Common Validation Errors:
- **Invalid Email Format**: Must be valid email syntax
- **Duplicate Username**: Username must be unique across region
- **Invalid ZIP/State Combo**: ZIP code must match selected state
- **Invalid URL Format**: Company Domain must include `https://` or `http://`

---

## Best Practices

1. **Naming Conventions**:
   - Use descriptive company names that indicate test purpose
   - Example: `QA SMS Testing`, `Performance Test Account`, `Regression Test 2025-12`

2. **Email Aliases**:
   - Use `+` notation for multiple test accounts
   - Example: `qa.test+sms_test@example.com`, `qa.test+api_test@example.com`

3. **Feature Flags**:
   - Coordinate with dev team to understand available flags
   - Document which flags are enabled for each test account
   - Use flags to test specific features in isolation

4. **Plan Selection** ⚠️ **CRITICAL**:
   - **ALWAYS verify plan matches feature requirements** 
   - See [feature-to-plan-mapping.md](./feature-to-plan-mapping.md) for complete matrix
   - Common mistakes:
     - ❌ Starter plan for SMS (needs Basic+)
     - ❌ Basic for automation (needs Pro+)
     - ❌ Basic for MMS (needs Pro+)
   - When in doubt, use Pro plan (covers most features)
   - Document plan selection rationale in Notes column

5. **Documentation**:
   - Always document created accounts in test case CSV
   - Store credentials securely (password manager, secure wiki)
   - Include account details in test jam materials
   - **Explain plan selection** in Notes column

---

## Troubleshooting

### Account Creation Fails
- **Check**: All required fields filled
- **Check**: Email format is valid
- **Check**: Username is unique
- **Check**: ZIP/State combination is valid
- **Check**: Network connection to test tools

### Cannot Login to Created Account
- **Check**: Username and password copied correctly
- **Check**: Account activation status (manual activate = No recommended)
- **Check**: Correct shard URL being used
- **Check**: Account creation completed successfully

### Feature Flags Not Working
- **Check**: Feature flag names spelled correctly
- **Check**: Flags are valid for current environment
- **Check**: Account has necessary permissions for flag
- **Consult**: Development team for flag availability



# Application-Specific Playwright Patterns

**Source**: Real patterns extracted from `app-monolith/playwright` repository  
**Purpose**: Reference guide for QualityForge generator to create accurate, application-like tests

---

## 1. Page Object Model (POM) Structure

### Class-Based POMs
```javascript
const { expect } = require('@playwright/test');

exports.AudiencePage = class AudiencePage {
  constructor(page) {
    this.page = page;
    
    this.heading = this.page.getByRole('heading', { name: 'Contacts' });
    this.manageYourAudienceBtn = page.getByRole('button', { name: 'Manage Audience' });
    this.importContactsBtn = page.getByRole('link', { name: 'Import contacts' });
  }

  // Helper methods for actions
  async clickManageYourAudience() {
    await this.manageYourAudienceBtn.click();
  }
}
```

**Key Pattern**: All locators are defined in the constructor, not inline in methods.

---

## 2. Locator Strategies (Priority Order)

### 1. `getByRole()` - **Highest Priority**
```javascript
// Buttons
this.disconnectButton = page.getByRole('button', { name: 'Disconnect' });
this.closeModalButton = page.getByRole('button', { name: 'Close Modal' });

// Links
this.viewReporting = page.getByRole('link', { name: 'View reporting' });

// Headings
this.appNameHeaderPartner = page.getByRole('heading', {
  name: 'You've connected Partner App & Helix Platform!',
});

// With exact match
this.appNameHeaderShopify = page.getByRole('heading', {
  name: 'Shopify',
  exact: true,
});
```

### 2. `getByLabel()` - Form Inputs
```javascript
this.disconnectRemoveRadioButton = page.getByLabel(
  'Remove customer, product, and order data on Helix Platform',
);

this.deleteInput = page.getByLabel('Type DELETE to confirm');
```

### 3. `getByText()` - Text Content
```javascript
this.dataBlockCustomers = page.getByText('Customers', { exact: true });
this.dataBlockSubscribers = page.getByText('Subscribers', { exact: true });
```

### 4. `getByTestId()` - Data Attributes
```javascript
this.recommendationsHeader = page.getByTestId('recommendations-header');
this.settingHeader = page.getByTestId('app-settings-header');
```

### 5. `locator()` - CSS/Complex Selectors (Last Resort)
```javascript
// With chaining and filtering
this.wooCommerceTagSetting = page
  .locator('li')
  .filter({
    hasText: 'Tag WooCommerce customersFilter your Helix Platform contacts and personalize your mar',
  })
  .getByRole('button');

// Frame locators for iframes
this.importTextChat = page
  .frameLocator('iframe[name="ada-chat-frame"]')
  .getByText('Here are some tips for formatting your CSV file')
  .last();
```

---

## 3. Test Structure Patterns

### Test Organization
```javascript
test.describe('Audience Import', () => {
  // Use descriptive test names with context
  test('should import contacts from CSV file with updates', async ({ page }) => {
    // Pre-conditions as comments (NOT inline in test name)
    // Feature flag enabled
    // User has CSV file ready
    
    await audiencePage.importContactsSelectFileWithUpdatesNoSMS('path/to/file.csv');
    await expect(audiencePage.importSuccessHeader).toBeVisible();
  });
});
```

### Async/Await Pattern
```javascript
// ✅ Correct: await everything
async clickManageYourAudience() {
  await this.manageYourAudienceBtn.click();
}

// ❌ Wrong: Missing await
async clickManageYourAudience() {
  this.manageYourAudienceBtn.click(); // WRONG
}
```

---

## 4. Complex Interaction Patterns

### Multi-Step Workflows
```javascript
async importContactsCsvFile() {
  await this.fileRadio.click();
  await this.continueBtn.click();
  await this.fileInput.waitFor();
  await this.continueBtn.waitFor();
  await this.fileInput.setInputFiles('config/contacts/sample_contacts.csv');
  await this.continueBtn.click();
  await this.continueBtn.click();
  await this.continueBtn.click();
  await this.continueBtn.click();
  await this.finalizeImportBtn.click();
  await this.completeImportBtn.click();
  await this.exitBtn.click();
}
```

### Frame/Iframe Handling
```javascript
// Wait for frame to be available
async waitForAudiencePageToLoad(audience_name) {
  await this.page
    .frameLocator(`iframe[title="All subscribers of ${audience_name} \\| Helix Platform"]`)
    .getByRole('heading', { name: 'Audience', exact: true })
    .click();
}

// Select within frame
async selectStagedAudienceProfile(number_of_contacts, audience_name, contact_name) {
  await this.page
    .getByRole('link', { name: `${number_of_contacts}` })
    .click();
  await this.page
    .frameLocator(`iframe[title="All subscribers of ${audience_name} \\| Helix Platform"]`)
    .getByRole('link', { name: `${contact_name}` })
    .click();
}
```

### Conditional Logic
```javascript
async selectAudience(audience) {
  const currentAudience = await this.currentAudienceDropDown.textContent();
  if (currentAudience !== audience) {
    await this.currentAudienceDropDown.click();
    await this.page.getByText(audience).click();
  }
}
```

---

## 5. Assertions & Expectations

### Visibility Assertions
```javascript
await expect(this.importSuccessHeader).toBeVisible();
await expect(this.appNameHeaderPartner).toHaveText('You've connected Partner App & Helix Platform!');
```

### URL Assertions
```javascript
async verifyCurrentUrl(expectedUrl) {
  await expect(this.page).toHaveURL(expectedUrl);
}
```

### Text Content Assertions
```javascript
await expect(this.disconnectDescription).toHaveText(
  'Deleting this data from Helix Platform can't be undone',
);
```

### Custom Verification Methods
```javascript
async verifySectionTexts(expectedTexts) {
  if (expectedTexts.quickActions) {
    await expect(this.quickaction).toHaveText(expectedTexts.quickActions, {
      message: 'Quick actions section text mismatch',
    });
  }
}
```

---

## 6. Application-Specific Patterns

### Navigation Patterns
```javascript
// Navigate through dropdowns
async navigateToImportContacts() {
  await this.addContactsBtn.click();
  await this.importContactsBtn.click();
}

// Breadcrumb navigation
this.historyContactsBreadcrumb = page
  .getByLabel('Breadcrumbs')
  .getByRole('link', { name: 'Contacts' });
```

### Button Patterns
```javascript
// Combo buttons (split buttons)
this.comboButton = page.getByRole('button', { name: 'Combo' });

// Action cards
this.addressBookCardButton = page.getByRole('button', { name: 'Import now' });

// Manage buttons
this.manageAppButton = page.getByRole('button', { name: 'Manage App' });
```

### List/Table Patterns
```javascript
// Table interactions
this.topColumnSelect = page.getByRole('button', { name: 'Birthday' });

// List item selection
this.wooCommercePaintedDoorBtn = page
  .locator('li')
  .filter({
    hasText: 'Tag WooCommerce customersFilter your Helix Platform contacts and personalize your mar',
  })
  .getByRole('button');
```

### Modal Patterns
```javascript
// Modal headers
this.mobileDownloadModalHeader = page.getByText('Scan and download the Helix Platform app');

// Modal close buttons
this.closeModalButton = page.getByRole('button', { name: 'Close Modal' });

// Modal dialogs
this.historyErrorModal = page.getByRole('dialog', { name: 'Import errors' });
```

### Status Indicators
```javascript
// Status text
this.historySlatStatusComplete = page.getByText('Complete');
this.historySlatStatusFailed = page.getByText('Failed');
this.historySlatStatusImporting = page.getByText('Importing');

// Connected tiles
this.connectedTile = page.getByText('(Connected)');
```

---

## 7. Form Handling

### Input Fields
```javascript
// Text input
this.importTagEntry = page.getByRole('combobox', { name: 'Search for or create tags' });

// File input
this.fileInput = page.locator('input[type=file]');

// Placeholder-based input
this.deleteButton = page.getByPlaceholder('DELETE');

// Fill and submit
await this.importTagEntry.click();
await this.importTagEntry.fill(tag);
await this.importTagEntry.press('Enter');
```

### Checkboxes & Radio Buttons
```javascript
// Checkbox with label
this.updateExistingCheckbox = page.getByLabel('Update any existing contacts');

// Radio button with label
this.disconnectRemoveRadioButton = page.getByLabel(
  'Remove customer, product, and order data on Helix Platform',
);

// Click to toggle
await this.updateExistingCheckbox.click();
```

### Select/Combobox
```javascript
async setComboboxOptionByContent(combobox_title, option_title) {
  await this.page
    .getByRole('combobox', { name: combobox_title })
    .selectOption({ label: option_title, exact: true });
}
```

---

## 8. Wait Strategies

### Explicit Waits
```javascript
// Wait for element to be available
await this.fileInput.waitFor();
await this.continueBtn.waitFor();

// Wait for specific text
await this.page.getByText('editor to load').waitFor();
```

### Page State Waits
```javascript
// Wait for navigation
await page.goto('/templates?tab=saved');
await page.waitForLoadState('networkidle');

// Wait for frame to load
await this.page
  .frameLocator(`iframe[title="${audience_name}"]`)
  .getByRole('heading', { name: 'Audience' })
  .click();
```

---

## 9. Error Handling & Validation

### Success State Validation
```javascript
this.importSuccessHeader = page.getByRole('heading', {
  name: 'Your import was completed',
});

this.disconnectSuccessMessage = page.getByText('You disconnected your account');
```

### Error State Validation
```javascript
this.importFailHeader = page.getByRole('heading', {
  name: 'Your contacts failed to import',
});

this.importPartialFailHeader = page.getByRole('heading', {
  name: 'Your import encountered errors',
});

// Error modal
this.historyErrorModal = page.getByRole('dialog', { name: 'Import errors' });
this.historyErrorModalText = page.getByText(
  'Several errors were encountered. We suggest that you resolve errors before you',
);
```

### Retry & Refresh Patterns
```javascript
this.historyRetryButton = page.getByRole('button', { name: 'Retry' });
this.refresh = page.getByRole('button', { name: 'Refresh' });

// Clicking refresh in workflow
async clickRefresh() {
  await this.refresh.click();
}
```

---

## 10. Test Data Management

### Config File Paths
```javascript
// Use relative paths from project root
await this.fileInput.setInputFiles('config/contacts/sample_contacts.csv');
await this.fileInput.setInputFiles('config/contacts/mailbots_500_contacts.csv');
await this.fileInput.setInputFiles('config/contacts/sample_contacts.xlsx');
```

### Dynamic Test Data
```javascript
async selectStagedAudienceProfile(number_of_contacts, audience_name, contact_name) {
  // Use parameters to make tests flexible
  await this.page.getByRole('link', { name: `${number_of_contacts}` }).click();
  await this.page
    .frameLocator(`iframe[title="All subscribers of ${audience_name} \\| Helix Platform"]`)
    .getByRole('link', { name: `${contact_name}` })
    .click();
}
```

---

## 11. Helix Platform UI Component Patterns

### Banner Components
```javascript
// Hellbox banner
this.recommendationAudienceDashboardBanner = page.locator(
  "div[class*='marketing-ipd-tsa-widgets']>> div[class*='mc-hellobox-banner-wrapper']",
);

// Compressed banner
this.recommendationSegmentsCompressedBanner = page.locator(
  "div[class*='marketing-ipd-tsa-widgets']>> div[class*='mc-compressed-banner applied-helix-platform-theme align-right']",
);
```

### Badge Components
```javascript
this.recommendationAudienceDashboardBannerBadge = page.locator(
  "div[class*='mc-banner__copy']>> span[class*='mc-badge bg-radish']",
);
```

### Recommendation Components
```javascript
this.recommendationDashboardHeader = page.getByRole('heading', {
  name: 'Recommendations for you',
});

this.recommendationDashboardTitle = page.locator("div[class*='bannerContainer']>> h4");
this.recommendationBannerImg = page.locator("div[class*='bannerContainer']>> img");
```

---

## 12. Common Helix Platform Workflows

### Import Contacts Workflow
```javascript
async importContactsSelectFileNoUpdateNoSMS(fileLocation) {
  await this.fileRadio.click();
  await this.continueBtn.click();
  await this.fileInput.waitFor();
  await this.continueBtn.waitFor();
  await this.fileInput.setInputFiles(fileLocation);
  await this.continueBtn.click();
  await this.continueBtn.click();
  await this.continueBtn.click();
  await this.continueBtn.click();
  await this.finalizeImportBtn.click();
  await this.completeImportBtn.click();
}
```

### Disconnect Integration Workflow
```javascript
async disconnectIntegration() {
  await this.manageAppButton.click();
  await this.disconnectOptionButton.click();
  await this.disconnectRemoveRadioButton.click();
  await this.deleteInput.fill('DELETE');
  await this.disconnecteNowButton.click();
  await expect(this.disconnectSuccessMessage).toBeVisible();
}
```

---

## 13. Code Quality Guidelines

### ✅ DO
- Use async/await for all Playwright actions
- Define all locators in the constructor
- Use semantic role-based locators (`getByRole()`)
- Create reusable helper methods in POM classes
- Use descriptive variable names (`manageYourAudienceBtn` not `btn1`)
- Add explicit waits when needed (`waitFor()`)
- Use `exact: true` for precise text matching
- Handle iframes with `frameLocator()`

### ❌ DON'T
- Don't use complex CSS selectors unless absolutely necessary
- Don't hardcode wait times (`page.waitForTimeout(5000)`)
- Don't define locators inline in test methods
- Don't use generic selectors like `div.class > span`
- Don't skip `await` on async operations
- Don't rely on element position/index unless necessary

---

## 14. Generator-Specific Rules

When generating Playwright tests for Helix Platform:

1. **Always use** `page.getByRole()` first
2. **If text is unique**, use `page.getByText()` with `{ exact: true }`
3. **For form inputs**, use `page.getByLabel()`
4. **For dropdowns/combos**, use `getByRole('combobox')`
5. **For modals**, use `getByRole('dialog')`
6. **For navigation**, check for breadcrumbs or `getByRole('link')`
7. **For status indicators**, use exact text matching
8. **For complex workflows**, create helper methods that chain actions
9. **For iframes**, use `frameLocator()` with title attribute
10. **For waiting**, use explicit `waitFor()` on specific elements

---

## 15. Example Generated Test (Helix Platform Style)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Audience Import', () => {
  test('[AUD-001] Import contacts from CSV file @P0', async ({ page }) => {
    /**
     * Pre-conditions:
     * - User is logged in
     * - User has valid CSV file
     * - Audience exists
     */
    
    // Navigate to audience page
    await page.goto('/lists');
    
    // Start import workflow
    await page.getByRole('button', { name: 'Manage Audience' }).click();
    await page.getByRole('link', { name: 'Import contacts' }).click();
    
    // Select file upload option
    await page.locator('[data-testid="fileInput"]').click();
    await page.getByRole('button', { name: 'Continue' }).click();
    
    // Upload file
    await page.locator('input[type=file]').setInputFiles('config/contacts/test.csv');
    
    // Complete import
    await page.getByRole('button', { name: 'Continue' }).click();
    await page.getByRole('button', { name: 'Finalize Import' }).click();
    await page.getByRole('button', { name: 'Complete Import' }).click();
    
    // Verify success
    await expect(page.getByRole('heading', { name: 'Your import was completed' })).toBeVisible();
  });
});
```

---

**End of Application-Specific Playwright Patterns**


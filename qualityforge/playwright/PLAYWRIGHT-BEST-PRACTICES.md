# Playwright Best Practices

**Purpose**: Hard-coded reference guide for AI agents generating Playwright tests  
**Target Audience**: AI agents, automation engineers, QA team  
**Last Updated**: January 9, 2026

---

## Table of Contents
1. [Core Principles](#core-principles)
2. [Locator Strategy](#locator-strategy)
3. [Test Structure](#test-structure)
4. [Waiting & Timing](#waiting--timing)
5. [Assertions](#assertions)
6. [Authentication & Setup](#authentication--setup)
7. [Error Handling](#error-handling)
8. [API Testing](#api-testing)
9. [Code Quality](#code-quality)
10. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Core Principles

### 1. **Reliability Over Speed**
- Tests must be deterministic and repeatable
- Prefer explicit waits over fixed timeouts
- Use Playwright's built-in auto-waiting whenever possible

### 2. **Accessibility-First**
- Use accessible locators (role, label, text) as first choice
- This makes tests more resilient to UI changes
- Improves accessibility compliance

### 3. **Readability & Maintainability**
- Tests are code - apply software engineering best practices
- Clear test names that describe what is being tested
- Use comments to explain WHY, not WHAT

### 4. **Zero False Positives**
- **CRITICAL**: Tests must not pass when they should fail
- Always assert expected results explicitly
- Use specific assertions, not generic checks

---

## Locator Strategy

### Priority Order (ALWAYS FOLLOW)

#### 1. **Role-based locators** (Highest Priority)
```typescript
// BEST: Use getByRole for interactive elements
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('link', { name: 'Sign Up' }).click();
await page.getByRole('heading', { name: 'Welcome' });
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// Common roles:
// - button, link, textbox, checkbox, radio, combobox
// - heading, navigation, main, banner, contentinfo
```

#### 2. **Label-based locators** (Form Elements)
```typescript
// GOOD: Use getByLabel for form inputs
await page.getByLabel('Email address').fill('user@example.com');
await page.getByLabel('Password').fill('SecurePass123');
await page.getByLabel('Remember me').check();
```

#### 3. **Text-based locators** (Visible Text)
```typescript
// GOOD: Use getByText for elements with visible text
await page.getByText('Welcome back').waitFor();
await page.getByText('Success', { exact: true }).click();

// Partial match (use when exact text is dynamic)
await page.getByText(/Thank you/i).waitFor();
```

#### 4. **Test ID locators** (When Explicitly Mentioned)
```typescript
// ACCEPTABLE: Use getByTestId when data-testid is mentioned
await page.getByTestId('submit-button').click();
await page.getByTestId('user-profile-menu').click();

// Note: Only use when test case explicitly mentions data-testid attribute
```

#### 5. **CSS/XPath** (Last Resort)
```typescript
// USE SPARINGLY: Only when no better option exists
await page.locator('button.submit-btn').click();
await page.locator('//button[@class="submit"]').click();

// Add TODO comment explaining why this was necessary
// TODO: Refactor to use accessible locator once data-testid is added
```

### Locator Best Practices

#### Combine Locators for Specificity
```typescript
// GOOD: Combine locators to be more specific
await page
  .locator('form')
  .getByRole('button', { name: 'Submit' })
  .click();

await page
  .getByRole('navigation')
  .getByRole('link', { name: 'About' })
  .click();
```

#### Use Filter for Multiple Matches
```typescript
// ✅ GOOD: Filter locators when multiple elements match
await page
  .getByRole('listitem')
  .filter({ hasText: 'Active' })
  .first()
  .click();
```

#### Avoid Brittle Selectors
```typescript
// ❌ BAD: Too specific, breaks easily
await page.locator('div > div > ul > li:nth-child(3) > a').click();

// ✅ GOOD: Semantic and resilient
await page.getByRole('link', { name: 'Dashboard' }).click();
```

---

## Test Structure

### File Organization

```typescript
// File: login.spec.ts

import { test, expect } from '@playwright/test';

/**
 * Login Flow Tests
 * 
 * Tests user authentication including:
 * - Valid credentials login
 * - Invalid credentials handling
 * - Password reset flow
 * 
 * Related Test Cases: TC-001 through TC-005
 */

test.describe('Login Flow', () => {
  // Setup that runs before EACH test
  test.beforeEach(async ({ page }) => {
    await page.goto('https://app.example.com/login');
    await page.waitForLoadState('networkidle');
  });

  /**
   * Test Case: TC-001
   * Priority: P0 (Critical)
   * Category: Functional Testing
   */
  test('[TC-001] User can login with valid credentials @P0', async ({ page }) => {
    // Arrange: Setup test data
    const email = 'testuser@example.com';
    const password = 'Test123!';

    // Act: Perform actions
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Assert: Verify expected results
    await expect(page.getByText('Welcome back')).toBeVisible();
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('[TC-002] Login fails with invalid credentials @P1', async ({ page }) => {
    // Act
    await page.getByLabel('Email').fill('invalid@example.com');
    await page.getByLabel('Password').fill('WrongPassword');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Assert
    await expect(page.getByText('Invalid email or password')).toBeVisible();
    await expect(page).toHaveURL(/.*login/);
  });
});
```

### Describe Blocks (Grouping)

```typescript
// ✅ GOOD: Group related tests
test.describe('User Profile Management', () => {
  test.describe('Profile Updates', () => {
    test('User can update email address', async ({ page }) => {
      // ...
    });

    test('User can update password', async ({ page }) => {
      // ...
    });
  });

  test.describe('Profile Deletion', () => {
    test('User can delete account', async ({ page }) => {
      // ...
    });
  });
});
```

### Test Naming Convention

```typescript
// Format: [TEST-ID] Clear description @PRIORITY

// ✅ GOOD: Descriptive names with test ID and priority
test('[TC-001] User can successfully create new campaign @P0', async ({ page }) => {});
test('[TC-015] Dashboard displays user statistics correctly @P1', async ({ page }) => {});
test('[TC-042] API returns 404 for non-existent resources @P2', async ({ page }) => {});

// ❌ BAD: Vague or missing context
test('test1', async ({ page }) => {});
test('create campaign', async ({ page }) => {});
test('check dashboard', async ({ page }) => {});
```

---

## Waiting & Timing

### Built-In Auto-Waiting (PREFERRED)

```typescript
// ✅ BEST: Playwright auto-waits for these actions
await page.getByRole('button').click();  // Waits for: attached, visible, stable, enabled
await page.getByLabel('Email').fill('user@example.com');  // Waits for: attached, visible, enabled
await page.getByRole('link').hover();  // Waits for: attached, visible, stable

// No explicit waits needed! Playwright handles it.
```

### Explicit Waits (When Needed)

```typescript
// ✅ GOOD: Wait for element visibility
await page.getByText('Success').waitFor({ state: 'visible' });
await page.getByRole('button').waitFor({ state: 'attached' });

// ✅ GOOD: Wait for page load states
await page.goto('https://example.com');
await page.waitForLoadState('networkidle');  // Wait for network to be idle

// ✅ GOOD: Wait with assertions
await expect(page.getByText('Loading...')).toBeHidden();
await expect(page.getByText('Data loaded')).toBeVisible({ timeout: 10000 });
```

### Timeouts

```typescript
// ✅ GOOD: Increase timeout for slow operations
await expect(page.getByText('Report generated')).toBeVisible({
  timeout: 30000  // 30 seconds for slow report generation
});

// ✅ GOOD: Reduce timeout for quick checks
await expect(page.getByText('Cached data')).toBeVisible({
  timeout: 2000  // 2 seconds for cached data
});
```

### Anti-Pattern: Fixed Waits

```typescript
// ❌ BAD: NEVER use fixed timeouts
await page.waitForTimeout(5000);  // Brittle and slow
await new Promise(resolve => setTimeout(resolve, 3000));  // NO!

// ✅ GOOD: Wait for specific conditions
await expect(page.getByText('Done')).toBeVisible();
```

---

## Assertions

### Visibility Assertions

```typescript
// ✅ GOOD: Check element visibility
await expect(page.getByText('Success')).toBeVisible();
await expect(page.getByRole('button', { name: 'Submit' })).toBeVisible();

// ✅ GOOD: Check element is hidden
await expect(page.getByText('Loading...')).toBeHidden();
await expect(page.getByText('Error')).not.toBeVisible();
```

### Text Assertions

```typescript
// ✅ GOOD: Exact text match
await expect(page.getByRole('heading')).toHaveText('Welcome');

// ✅ GOOD: Partial text match
await expect(page.getByRole('heading')).toContainText('Welcome');

// ✅ GOOD: Regex match for dynamic content
await expect(page.getByTestId('user-count')).toHaveText(/\d+ users online/);
```

### Value Assertions (Form Inputs)

```typescript
// ✅ GOOD: Check input values
await expect(page.getByLabel('Email')).toHaveValue('user@example.com');
await expect(page.getByLabel('Age')).toHaveValue('25');

// ✅ GOOD: Check checkbox/radio state
await expect(page.getByLabel('Remember me')).toBeChecked();
await expect(page.getByLabel('Remember me')).not.toBeChecked();
```

### Attribute Assertions

```typescript
// ✅ GOOD: Check element attributes
await expect(page.getByRole('link')).toHaveAttribute('href', '/dashboard');
await expect(page.getByRole('button')).toHaveAttribute('disabled');
await expect(page.getByRole('button')).not.toHaveAttribute('disabled');
```

### URL Assertions

```typescript
// ✅ GOOD: Check URL after navigation
await expect(page).toHaveURL('https://app.example.com/dashboard');
await expect(page).toHaveURL(/.*dashboard/);  // Regex match

// ✅ GOOD: Check URL contains parameter
await expect(page).toHaveURL(/.*\?tab=settings/);
```

### State Assertions

```typescript
// ✅ GOOD: Check element state
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByRole('button')).toBeDisabled();
await expect(page.getByRole('textbox')).toBeEditable();
await expect(page.getByRole('textbox')).not.toBeEditable();
```

### Soft Assertions (Multiple Checks)

```typescript
// ✅ GOOD: Use soft assertions for multiple checks
test('Dashboard displays all user info', async ({ page }) => {
  // All assertions are checked even if one fails
  await expect.soft(page.getByText('John Doe')).toBeVisible();
  await expect.soft(page.getByText('john@example.com')).toBeVisible();
  await expect.soft(page.getByText('Premium Member')).toBeVisible();
  await expect.soft(page.getByText('Joined: 2024')).toBeVisible();
});
```

---

## Authentication & Setup

### Global Setup (Reuse Authentication)

```typescript
// File: auth.setup.ts

import { test as setup } from '@playwright/test';

const authFile = '.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('https://app.example.com/login');
  await page.getByLabel('Email').fill('testuser@example.com');
  await page.getByLabel('Password').fill('Test123!');
  await page.getByRole('button', { name: 'Sign In' }).click();
  
  // Wait for authentication to complete
  await page.waitForURL('**/dashboard');
  
  // Save authentication state
  await page.context().storageState({ path: authFile });
});
```

### Use Stored Authentication

```typescript
// File: playwright.config.ts

export default defineConfig({
  projects: [
    // Setup project
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    
    // Tests use setup
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

### Per-Test Authentication

```typescript
// ✅ GOOD: Login in beforeEach for isolated tests
test.describe('Authenticated Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://app.example.com/login');
    await page.getByLabel('Email').fill('testuser@example.com');
    await page.getByLabel('Password').fill('Test123!');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await page.waitForURL('**/dashboard');
  });

  test('User can access settings', async ({ page }) => {
    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page).toHaveURL(/.*settings/);
  });
});
```

---

## Error Handling

### Retry Logic (Built-In)

```typescript
// ✅ GOOD: Playwright retries automatically
test('Flaky network request', async ({ page }) => {
  // Playwright will retry this action if it fails
  await page.getByRole('button', { name: 'Load Data' }).click();
  
  // Will retry assertion up to 5 seconds (default timeout)
  await expect(page.getByText('Data loaded')).toBeVisible();
});
```

### Custom Retry Logic

```typescript
// ✅ GOOD: Custom retry for specific scenarios
async function retryAction(page: Page, action: () => Promise<void>, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await action();
      return;  // Success
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;  // Last attempt failed
      await page.waitForTimeout(1000);  // Brief pause before retry
    }
  }
}

test('Retry flaky action', async ({ page }) => {
  await retryAction(page, async () => {
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Success')).toBeVisible({ timeout: 5000 });
  });
});
```

### Error Screenshots (Auto-Captured)

```typescript
// File: playwright.config.ts

export default defineConfig({
  use: {
    screenshot: 'only-on-failure',  // Auto-capture on failure
    video: 'retain-on-failure',     // Auto-record on failure
    trace: 'retain-on-failure',     // Auto-trace on failure
  },
});
```

### Try-Catch for Expected Errors

```typescript
// ✅ GOOD: Handle expected errors gracefully
test('Handle network errors', async ({ page }) => {
  try {
    await page.goto('https://app.example.com/dashboard', { timeout: 5000 });
  } catch (error) {
    // Expected: Network might be slow
    console.log('Retrying navigation...');
    await page.goto('https://app.example.com/dashboard', { timeout: 10000 });
  }
  
  await expect(page).toHaveURL(/.*dashboard/);
});
```

---

## API Testing

### Using Playwright Request Context

```typescript
// ✅ GOOD: API testing with Playwright
test.describe('API Tests', () => {
  test('GET /api/users returns user list', async ({ request }) => {
    const response = await request.get('https://api.example.com/users');
    
    // Assert status code
    expect(response.status()).toBe(200);
    
    // Assert response body
    const users = await response.json();
    expect(users).toHaveLength(10);
    expect(users[0]).toHaveProperty('id');
    expect(users[0]).toHaveProperty('name');
  });

  test('POST /api/users creates new user', async ({ request }) => {
    const response = await request.post('https://api.example.com/users', {
      data: {
        name: 'John Doe',
        email: 'john@example.com'
      }
    });
    
    expect(response.status()).toBe(201);
    
    const user = await response.json();
    expect(user.name).toBe('John Doe');
    expect(user.email).toBe('john@example.com');
    expect(user.id).toBeDefined();
  });
});
```

### API Authentication

```typescript
// ✅ GOOD: API tests with authentication
test('Authenticated API call', async ({ request }) => {
  // Get auth token
  const loginResponse = await request.post('https://api.example.com/login', {
    data: {
      email: 'testuser@example.com',
      password: 'Test123!'
    }
  });
  
  const { token } = await loginResponse.json();
  
  // Use token in subsequent requests
  const response = await request.get('https://api.example.com/profile', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  expect(response.status()).toBe(200);
});
```

---

## Code Quality

### TypeScript Types

```typescript
// ✅ GOOD: Use TypeScript for type safety
import { test, expect, Page } from '@playwright/test';

interface UserCredentials {
  email: string;
  password: string;
}

async function login(page: Page, credentials: UserCredentials): Promise<void> {
  await page.getByLabel('Email').fill(credentials.email);
  await page.getByLabel('Password').fill(credentials.password);
  await page.getByRole('button', { name: 'Sign In' }).click();
}

test('Login helper', async ({ page }) => {
  await page.goto('https://app.example.com/login');
  await login(page, { email: 'user@example.com', password: 'Test123!' });
  await expect(page).toHaveURL(/.*dashboard/);
});
```

### JSDoc Comments

```typescript
/**
 * Logs in a user with the provided credentials
 * 
 * @param page - Playwright Page object
 * @param email - User email address
 * @param password - User password
 * @throws {Error} If login fails
 * @example
 * await loginUser(page, 'user@example.com', 'Password123!');
 */
async function loginUser(page: Page, email: string, password: string): Promise<void> {
  await page.goto('https://app.example.com/login');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('**/dashboard');
}
```

### Extract Reusable Functions

```typescript
// ✅ GOOD: Extract common actions into helper functions

// File: helpers/navigation.ts
export async function navigateToDashboard(page: Page) {
  await page.goto('https://app.example.com/dashboard');
  await page.waitForLoadState('networkidle');
}

export async function navigateToSettings(page: Page) {
  await page.getByRole('link', { name: 'Settings' }).click();
  await expect(page).toHaveURL(/.*settings/);
}

// File: helpers/forms.ts
export async function fillLoginForm(page: Page, email: string, password: string) {
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
}

// Use in tests
import { navigateToDashboard } from './helpers/navigation';
import { fillLoginForm } from './helpers/forms';

test('Use helpers', async ({ page }) => {
  await navigateToDashboard(page);
  await fillLoginForm(page, 'user@example.com', 'Pass123!');
  await page.getByRole('button', { name: 'Sign In' }).click();
});
```

---

## Anti-Patterns to Avoid

### ❌ 1. Fixed Timeouts

```typescript
// ❌ BAD: Fixed timeouts are slow and brittle
await page.waitForTimeout(5000);
await new Promise(resolve => setTimeout(resolve, 3000));

// ✅ GOOD: Wait for specific conditions
await expect(page.getByText('Done')).toBeVisible();
```

### ❌ 2. Brittle CSS Selectors

```typescript
// ❌ BAD: Breaks easily with DOM changes
await page.locator('div.container > ul > li:nth-child(2) > a').click();

// ✅ GOOD: Use accessible locators
await page.getByRole('link', { name: 'Dashboard' }).click();
```

### ❌ 3. No Assertions

```typescript
// ❌ BAD: Action without verification (false positive risk)
await page.getByRole('button', { name: 'Submit' }).click();
// Test passes even if nothing happened!

// ✅ GOOD: Always assert expected results
await page.getByRole('button', { name: 'Submit' }).click();
await expect(page.getByText('Success')).toBeVisible();
```

### ❌ 4. Overly Long Tests

```typescript
// ❌ BAD: Tests multiple scenarios in one test
test('User flow', async ({ page }) => {
  // Login
  await page.goto('https://app.example.com/login');
  await page.getByLabel('Email').fill('user@example.com');
  // ... 50 more lines of actions
  // This should be multiple tests!
});

// ✅ GOOD: One test = one scenario
test('[TC-001] User can login', async ({ page }) => {
  // Only test login
});

test('[TC-002] User can create campaign', async ({ page }) => {
  // Only test campaign creation
});
```

### ❌ 5. Hard-Coded Test Data

```typescript
// ❌ BAD: Hard-coded data in tests
await page.getByLabel('Email').fill('john@example.com');

// ✅ GOOD: Use constants or test data files
const TEST_USER = {
  email: 'testuser@example.com',
  password: 'Test123!',
  name: 'Test User'
};

await page.getByLabel('Email').fill(TEST_USER.email);
```

### ❌ 6. Not Using Page Object Pattern for Complex Flows

```typescript
// ❌ BAD: Repeating selectors across tests
test('Test 1', async ({ page }) => {
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('pass');
  await page.getByRole('button', { name: 'Sign In' }).click();
});

test('Test 2', async ({ page }) => {
  await page.getByLabel('Email').fill('user2@example.com');
  await page.getByLabel('Password').fill('pass2');
  await page.getByRole('button', { name: 'Sign In' }).click();
});

// ✅ GOOD: Page Object Pattern for complex flows
class LoginPage {
  constructor(private page: Page) {}

  async login(email: string, password: string) {
    await this.page.getByLabel('Email').fill(email);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign In' }).click();
  }
}

test('Login test', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('user@example.com', 'pass');
});
```

---

## Summary Checklist

When generating Playwright tests, ensure:

- [ ] Use accessible locators (getByRole, getByLabel, getByText)
- [ ] Avoid fixed timeouts (waitForTimeout)
- [ ] Always assert expected results (no action without verification)
- [ ] Use async/await correctly
- [ ] Add JSDoc comments for complex functions
- [ ] Include test case ID and priority in test name
- [ ] Group related tests in describe blocks
- [ ] Use beforeEach for common setup
- [ ] Handle authentication properly
- [ ] Add TODO comments where manual refinement needed
- [ ] Follow code formatting standards
- [ ] Test one scenario per test
- [ ] Use soft assertions for multiple checks
- [ ] Leverage Playwright's auto-waiting
- [ ] Configure retries and timeouts appropriately

---

**For AI Agents**: This document represents the definitive best practices for Playwright test generation. Follow these patterns exactly when converting test cases to Playwright code. When in doubt, prefer accessibility and reliability over cleverness.


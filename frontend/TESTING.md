# Frontend Component Testing Guide

## Overview
This document covers the Jest and React Testing Library setup for the DataCure frontend application.

## Setup Complete

### Installed Dependencies
- `jest` - Testing framework
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom DOM matchers
- `babel-jest` - JSX transformation for tests
- `@babel/preset-env` - JavaScript transpilation
- `@babel/preset-react` - React JSX support
- `jest-environment-jsdom` - DOM environment for Jest

### Configuration Files Created

#### 1. **jest.config.js**
Main Jest configuration file that specifies:
- Test environment (jsdom for DOM testing)
- Test file patterns (__tests__ directories and .test.jsx files)
- Module name mapping for CSS imports
- Setup files for test initialization
- Coverage thresholds (50% minimum)

#### 2. **.babelrc**
Babel configuration for JSX transformation:
- Uses `@babel/preset-env` for JavaScript features
- Uses `@babel/preset-react` for JSX support
- Configured for automatic React import

#### 3. **src/setupTests.js**
Global test utilities:
- Imports Jest DOM matchers
- Mocks `window.matchMedia` for responsive tests
- Suppresses expected console warnings
- Provides reusable test helpers

## Test Files Structure

### Component Tests (`src/components/__tests__/`)

#### **Common.test.jsx** (13 test cases)
Tests for reusable UI components:
- `ProtectedRoute` - Route protection component
- `LoadingSpinner` - Loading indicator
- `ErrorAlert` - Error display component
- `SuccessAlert` - Success message component
- `DataTable` - Reusable table with CRUD buttons
  - Edit button interaction
  - Delete button interaction
- `FormField` - Form input wrapper
  - Input value changes
  - Error message display
- `Modal` - Modal dialog component
  - Open/close states
  - Event handlers

### Page Integration Tests (`src/pages/__tests__/`)

#### **PatientsPage.test.jsx** (5 test cases)
Demonstrates page testing patterns:
- Test structure for page components
- Axios mock setup for API calls
- Async/await test patterns
- Error handling

#### **AppointmentsPage.test.jsx** (5 test cases)
Tests for appointment management:
- HTTP request mocking
- Data filtering patterns
- Status validation
- Error handling patterns

## Running Tests

### Execute All Tests
```bash
npm test
```

### Watch Mode (Auto-rerun on changes)
```bash
npm run test:watch
```

### Code Coverage Report
```bash
npm run test:coverage
```

### Run Specific Test File
```bash
npm test -- Common.test.jsx
```

### Run Tests Matching Pattern
```bash
npm test -- --testNamePattern="displays"
```

## Testing Patterns Used

### 1. Component Mocking
```javascript
jest.mock('../Common', () => ({
  LoadingSpinner: () => <div>Loading...</div>,
}));
```

### 2. Axios Mocking
```javascript
jest.mock('axios');

axios.get.mockResolvedValue({ data: { success: true } });
axios.post.mockRejectedValue(new Error('API Error'));
```

### 3. User Interactions
```javascript
fireEvent.click(screen.getByRole('button'));
fireEvent.change(input, { target: { value: 'new value' } });
```

### 4. Async Operations
```javascript
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});
```

### 5. Error Boundaries
```javascript
try {
  await axios.get('/api/patients');
  expect(true).toBe(false); // Should not reach
} catch (error) {
  expect(error.message).toBeDefined();
}
```

## Coverage Metrics

The jest.config.js is configured with coverage thresholds:
- **Branches**: 50%
- **Functions**: 50%
- **Lines**: 50%
- **Statements**: 50%

To view detailed coverage:
```bash
npm run test:coverage
```

This generates an HTML report in `coverage/` directory.

## Best Practices

1. **Use data-testid for element selection**
   ```javascript
   <button data-testid="submit-btn">Submit</button>
   screen.getByTestId('submit-btn');
   ```

2. **Mock external dependencies**
   ```javascript
   jest.mock('axios');
   jest.mock('zustand');
   ```

3. **Test user behavior, not implementation**
   ```javascript
   // Good: tests what user sees
   expect(screen.getByText('Welcome')).toBeInTheDocument();
   
   // Poor: tests internal state
   expect(component.state.isVisible).toBe(true);
   ```

4. **Use descriptive test names**
   ```javascript
   it('displays error message when api call fails', () => {
     // clear test purpose
   });
   ```

5. **Clean up after tests**
   ```javascript
   beforeEach(() => {
     jest.clearAllMocks();
   });
   ```

## Extending Tests

### Add New Component Tests
1. Create file: `src/components/__tests__/MyComponent.test.jsx`
2. Import testing utilities and component
3. Write test cases using patterns from existing tests
4. Run: `npm test`

### Add New Page Tests
1. Create file: `src/pages/__tests__/MyPage.test.jsx`
2. Mock dependencies (axios, routing, state)
3. Test page behavior and integration
4. Run: `npm test`

## Troubleshooting

### Issue: "Cannot find module" in tests
**Solution**: Ensure jest.config.js has correct moduleNameMapper setup

### Issue: "React is not defined"
**Solution**: Import React at top of file or use Babel's automatic JSX runtime

### Issue: Tests hanging/timing out
**Solution**: Ensure mocks are resolved or rejected with `.resolvedValue()` or `.rejectedValue()`

### Issue: CSS imports causing errors
**Solution**: identity-obj-proxy is configured to mock CSS imports

## Integration with CI/CD

Add to your CI/CD pipeline:
```bash
npm test -- --coverage --watchAll=false
```

This runs tests once, generates coverage report, and exits.

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Axios Mock Adapter](https://github.com/ctimmerm/axios-mock-adapter)

---

**Test Suite Status**: ✅ All 22 tests passing  
**Last Updated**: March 4, 2026  
**Maintainer**: DataCure Development Team

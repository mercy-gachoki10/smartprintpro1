# SmartPrint Pro - Test Suite

Comprehensive test suite for the SmartPrint Pro application.

## Test Structure

```
tests/
├── __init__.py                  # Test package initialization
├── conftest.py                  # Pytest fixtures and configuration
├── test_authentication.py       # Authentication tests (signup, login, logout)
├── test_models.py              # Database model tests
├── test_routes.py              # Route and dashboard tests
├── test_orders.py              # Order management tests
├── test_vendor_workflow.py     # Vendor quote and order workflow tests
├── test_admin.py               # Admin functionality tests
└── test_integration.py         # End-to-end integration tests
```

## Test Coverage

### Authentication Tests (`test_authentication.py`)
- ✅ User signup (customer, vendor with service flags)
- ✅ Login/logout functionality
- ✅ Password validation
- ✅ Duplicate email prevention
- ✅ Inactive user handling
- ✅ Role-based access control

### Model Tests (`test_models.py`)
- ✅ Customer, Vendor, Admin models
- ✅ Order and OrderItem models
- ✅ Quote model
- ✅ Review model
- ✅ ServicePrice model
- ✅ Model relationships
- ✅ Calculated properties

### Route Tests (`test_routes.py`)
- ✅ Public routes (home, vendors, features)
- ✅ Customer dashboard
- ✅ Vendor dashboard
- ✅ Admin dashboard
- ✅ Error handlers (404, 403)

### Order Tests (`test_orders.py`)
- ✅ Order creation workflow
- ✅ Order viewing permissions
- ✅ Order status progression
- ✅ Price calculations
- ✅ Quote deadlines

### Vendor Workflow Tests (`test_vendor_workflow.py`)
- ✅ Quote submission and revision
- ✅ Quote acceptance/rejection
- ✅ Order assignment
- ✅ Service category matching
- ✅ Vendor signup integration (critical bug fix test)

### Admin Tests (`test_admin.py`)
- ✅ User management
- ✅ User activation/deactivation
- ✅ Password reset requests
- ✅ Admin access control
- ✅ Dashboard statistics

### Integration Tests (`test_integration.py`)
- ✅ Complete order lifecycle
- ✅ Multi-vendor quoting
- ✅ Vendor signup and order matching
- ✅ Review system
- ✅ File handling

## Running Tests

### Install Dependencies

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_authentication.py
pytest tests/test_vendor_workflow.py
```

### Run Specific Test Class

```bash
pytest tests/test_authentication.py::TestSignup
pytest tests/test_vendor_workflow.py::TestQuoteSubmission
```

### Run Specific Test

```bash
pytest tests/test_authentication.py::TestSignup::test_vendor_signup_success
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run with Verbose Output

```bash
pytest -v
```

### Run and Stop on First Failure

```bash
pytest -x
```

### Run with Print Statements Visible

```bash
pytest -s
```

## Test Fixtures

The test suite uses pytest fixtures defined in `conftest.py`:

- `app` - Flask application instance
- `client` - Test client for making requests
- `db_session` - Database session (auto-cleanup)
- `customer_user` - Test customer user
- `vendor_user` - Test vendor user
- `admin_user` - Test admin user
- `test_order` - Test order
- `test_order_with_items` - Test order with items
- `test_quote` - Test vendor quote
- `authenticated_customer` - Logged-in customer client
- `authenticated_vendor` - Logged-in vendor client
- `authenticated_admin` - Logged-in admin client

## Writing New Tests

### Example Test

```python
def test_customer_can_create_order(authenticated_customer, db_session):
    """Test customer can create a new order"""
    service = ServicePrice.query.first()
    
    response = authenticated_customer.post('/create-order', data={
        'items[1][service]': service.id,
        'items[1][quantity]': '10',
        'quote_duration': '24'
    })
    
    order = Order.query.filter_by(service_category=service.category).first()
    assert order is not None
    assert order.status == "pending"
```

## Continuous Integration

The test suite can be integrated with CI/CD pipelines:

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Critical Test Cases

### Vendor Service Matching Bug Fix
The test suite includes specific tests to verify the fix for the vendor signup bug:

```python
# tests/test_vendor_workflow.py::TestVendorServiceMatching::test_newly_signed_up_vendor_sees_matching_orders
```

This test ensures that vendors created via the signup form have their service flags properly set and can see matching orders.

## Test Database

Tests use an in-memory SQLite database that is created fresh for each test session. The database is automatically cleaned between tests to ensure test isolation.

## Troubleshooting

### Import Errors
If you get import errors, ensure you're running pytest from the project root:
```bash
cd /path/to/smartprintpro1
pytest
```

### Database Errors
If tests fail due to database errors, ensure:
1. All migrations are up to date
2. The TestingConfig in `config.py` is properly configured
3. No other process is using the test database

### Fixture Errors
If fixtures aren't found, ensure `conftest.py` is in the `tests/` directory.

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Use Fixtures**: Leverage fixtures for common setup/teardown
3. **Descriptive Names**: Test names should clearly describe what they test
4. **Assertions**: Include clear assertions with meaningful messages
5. **Coverage**: Aim for >80% code coverage
6. **Edge Cases**: Test both happy paths and error conditions

## Performance

The test suite typically completes in under 30 seconds. If tests are slow:
- Check for unnecessary database operations
- Ensure proper use of session-scoped fixtures
- Consider using marks to skip slow tests during development

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass before committing
3. Maintain or improve code coverage
4. Update this README if adding new test files

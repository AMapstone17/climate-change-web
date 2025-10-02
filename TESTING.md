# Testing

## Reports

Testing reports are automatically generated. These are published to GitHub Pages as part of the Continuous Integration
workflow.

To view them locally, open the `reports/` directory.

- `reports/testing/index.html` - test results
- `reports/coverage/index.html` - coverage report
- `reports/flake8/index.html` - linting report

## Testing Setup

The project uses `pytest` for testing. The tests are located in the `test/` directory.

To set up the testing environment, a separate test client is created. This is done so that the tests do not interfere
with the main application, and can use its own configuration.

The `TestConfig` class is passed directly into the `create_app` function. This allows for configuration such as the
database URI to be set, and CSRF to be explicitly disabled during testing.

Additionally, pytest fixtures are used to set up the test client and database. The `test_client` fixture creates a Flask
test client using the config class. The `init_empty_database` and `init_filled_database` fixtures create an empty
database and a database with test data, respectively. These fixtures can be passed into any test function that requires
them. The two database fixtures are set to a function scope. This means that the database is created and destroyed for
each test function that uses them, ensuring that the tests are isolated from each other.

## General Strategy

As well as passing cases, the tests also check for failing and edge cases. This ensures that the app is robust and can
handle unexpected inputs.

One good example of this is the unit tests for creating a new user. The tests check:

- good inputs, with all fields being valid,
- bad inputs, with some or all fields being invalid,
- edge cases, such as setting the password to be just the minimum length.

By testing all of these cases, it should increase the confidence that the app works as expected.

## Unit Tests

Unit tests test individual components of the project. They are located in the `tests/unit` directory.

These tests cover:

- [x] database connection
- [x] models
- [x] forms

### Strategy

Unit testing was performed in a logical and systematic manner. Firstly, a list of all components that needed to be
tested was created. This included the database connection, models, and each form used in the app. This allowed for easy
tracking of what had been tested and what still needed to be tested.

### Database connection

The database connection was tested by creating a test database and checking that the connection was successful.
Additionally, the tests check that inserting, updating, and deleting data from the database works as expected.

### Models

Each model in the app was tested. The tests check that initialising each model works as expected, and that various
fields and methods work as expected.

One example of this is the `LeaderboardEntry` model. It overrides the various logic methods to allow for easy
comparison between entries. The tests check that the comparison methods work as expected.

### Forms

The app makes use of `WTForms` for form validation. The unit tests for the forms goes through each form class,
sending various inputs to the form and checking that the validation works as expected.

The form tests make use of `pytest.mark.parametrize` to test multiple inputs at once. This allows one function to
test multiple inputs, reducing the amount of code needed.

Additionally, I created several dataclasses which massively reduced code duplication. The base class `BaseFormData`
contains `expected` and `submit` fields. `expected` is a boolean to indicate whether the form should be valid or not,
and `submit` is a common submit value for nearly every form in the app, so it is defined here. It also contains a
`to_data` method. This allows for easy conversion of the dataclass to a dictionary, which is used in the tests. It
removes any "private" fields, such as `_fill_otp` in `LoginFormData`. This field is used as a "meta" field, and allows
the parameterisation of the tests to fill in the OTP field. This is not needed in the dictionary, so it is removed.

## Integration Tests

Integration tests test how the components work together. They are located in the `tests/integration` directory.

These tests cover:

- Flask routes
    - [x] admin
    - [x] users
    - [x] education
    - [ ] quiz
    - [ ] groups
    - [x] home

### Strategy

Similar to the unit tests, integration tests were performed as systematically as possible. A list of all routes that
needed to be tested was created, which were taken directly from the various `views.py` files.

### Flask Routes

Testing Flask routes involved sending HTTP requests to the various endpoints and checking that the responses were as
expected. They also ensure that any side effects of the request are as expected, for example, a POST request to the
`/create_account` endpoint should, if successful, create a new user in the database.

A test fixture is defined which clears the browser session and logs out the user before each test. This ensures that
each test is isolated from the others and always starts from the same state.

### Security-related tests

These tests are the simplest integration tests. They check that routes can be accessed by only the correct users. For
example, each admin route should only be accessible by an admin user.

I created a helper function `test_login_required_endpoint` to reduce code duplication. The function first makes a
request to the endpoint without logging in. It checks that the status code is expected (which may differ based on the
endpoint, so this is a parameter). It then logs in as a user and makes the request again. It checks that the status code
is then as expected (usually 200, but again, this is a parameter). This function can be reused for any endpoint security
test, massively reducing code duplication.

For example, testing the admin edit questions endpoint is as simple as shown. The function simply calls the helper
function with the test client, the database fixture, and the endpoint to test. The default status code for a non-logged
in user is 401, and for a logged-in admin user, it is 200.

```python
def test_admin_edit_questions_security(self, test_client, init_filled_database):
    test_login_required_endpoint(test_client, init_filled_database, '/admin/edit_questions')
```

### Form submission tests

These tests are more complex. They check that the form submission works as expected. In addition to validating the
form (like in the unit tests), they also check that the form submission works as expected. For example, submitting a
form to create a new user should create a new user in the database.
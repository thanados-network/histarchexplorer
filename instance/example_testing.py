# Flask Test Configuration
# Copy this file to instance/testing.py and adjust the values if needed.

DATABASE_NAME = 'tng_test'


# General test settings
TESTING = True
WTF_CSRF_ENABLED = False  # Disable CSRF forms for easier testing
SECRET_KEY = 'my-secret-testing-key'

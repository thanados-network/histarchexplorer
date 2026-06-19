---
sessionId: session-260619-144255-1ukl
---

# Requirements

### Overview & Goals
The current test suite (163 tests) takes approximately 3 minutes to run, which exceeds the 60-second timeout limit for automated agents. This prevents agents from validating their changes effectively. The goal is to optimize the test suite to run faster and provide a way to run it in smaller, manageable chunks.

### Scope
- **In Scope**:
    - Mocking external API calls in tests.
    - Identifying and marking slow tests.
    - Implementing parallel test execution.
    - Optimizing database reset logic.
    - Providing batch execution support.
- **Out of Scope**:
    - Rewriting major parts of the application logic.
    - Reducing the total number of tests.

# Technical Design

### Current Implementation
- **API Calls**: Many tests make real HTTP requests to an external API (`https://thanados.openatlas.eu/api/`), introducing significant latency.
- **Slow Tests**: Specific tests like `test_admin_cache_routes` (59s) and `test_admin_refresh_system_cache` (43s) consume most of the execution time.
- **Database Resets**: The database is reset once per session using multiple `psql` subprocess calls.
- **Coverage**: Coverage collection adds overhead to every test run.

### Key Decisions
1. **Mock External APIs**: All tests should run against mocked API responses to ensure speed and reliability.
2. **Parallelize with `pytest-xdist`**: Use multiple CPU cores to run independent tests in parallel.
3. **Slow Test Markers**: Explicitly mark slow tests to allow skipping them during rapid development cycles.
4. **Batching**: Provide a way to run tests in chunks if the total time still exceeds 60 seconds.

### Proposed Changes
- **`tests/conftest.py`**:
    - Add a session-scoped fixture to mock `requests.get` or the `ApiAccess` / `SearchService` methods globally.
- **`tests/base.py`**:
    - Optimize `reset_test_database` to combine multiple SQL file applications into fewer subprocess calls.
- **`tests/.pytest.ini`**:
    - Update configuration to support markers and parallelization.
- **New `pytest.ini` (Root)**:
    - Centralize test configuration.
- **Slow Test Marking**:
    - Apply `@pytest.mark.slow` to the identified slow tests in `tests/test_admin.py`, `tests/test_admin_routes_extra.py`, etc.

### File Structure
- `tests/conftest.py`: Updated with global mocks.
- `tests/base.py`: Updated database reset logic.
- `pytest.ini`: New root-level configuration.
- `tests/.pytest.ini`: Updated or removed in favor of root `pytest.ini`.

# Testing

### Validation Approach
- Measure the total execution time of the test suite before and after optimizations.
- Ensure all tests still pass with mocked API responses.
- Verify that parallel execution works without database conflicts.

### Key Scenarios
- **Quick Run**: `pytest -m "not slow" -p no:cov` should finish within 10-20 seconds.
- **Full Run**: `pytest -n auto` (if xdist is used) should finish well within 60 seconds if possible.
- **Mock Validation**: Ensure tests that previously hit the external API now use mocks.

# Delivery Steps

### ✓ Step 1: Optimize and Mark Slow Tests
Optimize the test suite to run significantly faster.
- Identify and mark slow tests with `@pytest.mark.slow`.
- Update `tests/.pytest.ini` to exclude slow tests by default or provide a quick mode.
- Mock `requests.get` and `ApiAccess` methods in `tests/conftest.py` to avoid hitting external APIs.
- Optimize `reset_test_database` in `tests/base.py` to reduce subprocess overhead.

### ✓ Step 2: Parallelization and Configuration Improvements
Introduce parallel execution and coverage optimization.
- Add `pytest-xdist` to the project's dev dependencies.
- Configure `pytest` to support parallel execution where possible.
- Update `tests/.pytest.ini` to allow disabling coverage easily.
- Create a `pytest.ini` in the root directory to better control test execution.

### ✓ Step 3: Batch Execution Support
Provide scripts or clear instructions for running tests in batches to avoid agent timeouts.
- Add a helper script (e.g., `tests/run_tests.sh`) that runs tests in chunks or file-by-file.
- Update the documentation on how to run tests efficiently.
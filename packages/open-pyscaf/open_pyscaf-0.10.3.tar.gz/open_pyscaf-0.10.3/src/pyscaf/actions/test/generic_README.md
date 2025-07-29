## Pytest Integration

This project uses pytest, a powerful and flexible testing framework for Python that makes it easy to write simple and scalable tests. The project includes pytest-cov for comprehensive code coverage reporting.

### Features

- **Simple Test Discovery**: Automatically finds and runs test files and functions
- **Fixtures**: Reusable test data and setup/teardown logic
- **Parametrized Tests**: Run the same test with different inputs
- **Coverage Reporting**: Integration with pytest-cov for code coverage analysis
- **Rich Assertions**: Clear and informative assertion failures

### Common Commands

```bash
# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run tests with coverage report
poetry run pytest --cov=src

# Generate HTML coverage report
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_module.py

# Run tests matching a pattern
poetry run pytest -k "test_pattern"
```

### Project Structure

The project includes:
- `tests/`: Main testing directory
- `pytest.ini`: Configuration file with optimized settings
- `tests/__init__.py`: Package initialization for tests
- `tests/test_*.py`: Test modules following pytest conventions

### Development

To start testing:
1. Write tests in the `tests/` directory
2. Use descriptive test function names starting with `test_`
3. Run tests frequently during development
4. Check coverage to ensure code quality
5. Use fixtures for shared test setup

### Best Practices

- Write clear and descriptive test names
- Keep tests focused and simple
- Use fixtures for common setup logic
- Test edge cases and error conditions
- Maintain good test coverage
- Use markers to categorize tests

For more information, visit [pytest's official documentation](https://docs.pytest.org/en/stable/). 
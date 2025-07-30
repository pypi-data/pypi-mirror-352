import pytest
import json
import pytest

# filepath: pytest-argus-reporter/tests/test_pytest_argus_reporter.py
pytest_plugins = "pytester"


def test_argus_reporter_integration_with_staging(testdir):
    """
    Integration test for ArgusReporter with argus-staging environment.
    """
    # Mock the Argus staging endpoint
    # staging_url = "https://argus-staging.lab.dbaas.scyop.net/"
    # api_key="g1JssdaLLL10tnYkChmnT1mZgQc9N/zJqdRw+UvQlfgYc9Sjzn2BhxhRfQH7EaLM"

    # extra_headers = json.dumps({
    #   'CF-Access-Client-Id': '6dc52d0d9bcd6b8d4fdab43fa5a1da9e.access',
    #    'CF-Access-Client-Secret': '9bcd977bd9a54f49f299bd70b254d762cfba76b76848ac6c5730df921fed9264'
    # })

    # requests_mock.post(staging_url, status_code=201, text='{"status": "success"}')

    testdir.makeconftest("""
        from pytest_argus_reporter import ArgusReporter

        def pytest_plugin_registered(plugin, manager):
            if isinstance(plugin, ArgusReporter):
                plugin.base_url = "https://argus-staging.lab.dbaas.scyop.net/"
                plugin.api_key = "g1JssdaLLL10tnYkChmnT1mZgQc9N/zJqdRw+UvQlfgYc9Sjzn2BhxhRfQH7EaLM"
                plugin.test_type = "dtest"
                plugin.run_id = "d8b98921-4d85-4c72-bd06-32c2c7007438"

                plugin.extra_headers = {
                    'CF-Access-Client-Id': '6dc52d0d9bcd6b8d4fdab43fa5a1da9e.access',
                    'CF-Access-Client-Secret': '9bcd977bd9a54f49f299bd70b254d762cfba76b76848ac6c5730df921fed9264'
                }
    """)
    # Create a temporary pytest test module
    testdir.makepyfile(
        """
        def test_sample(request, argus_reporter):
            argus_reporter.append_test_data(request, {"key": "value"})
            assert True
        """
    )

    # Run pytest with ArgusReporter configured for staging
    result = testdir.runpytest(
        "--argus-post-reports",
        "-v",
        "-s",
    )

    # Assert the test passed
    result.stdout.fnmatch_lines(["*::test_sample PASSED*"])
    assert result.ret == 0

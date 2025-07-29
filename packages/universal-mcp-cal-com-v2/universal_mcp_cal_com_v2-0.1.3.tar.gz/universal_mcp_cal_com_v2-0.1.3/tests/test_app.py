import pytest
from unittest.mock import MagicMock
from universal_mcp_cal_com_v2.app import CalComV2App

from universal_mcp.utils.testing import (
    check_application_instance,
)

@pytest.fixture
def app_instance():
    mock_integration = MagicMock()
    mock_integration.get_credentials.return_value = {"access_token": "dummy_access_token"}
    return CalComV2App(integration=mock_integration)

def test_application(app_instance):
    check_application_instance(app_instance, app_name="cal-com-v2")

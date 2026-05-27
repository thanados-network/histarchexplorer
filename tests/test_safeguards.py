from unittest.mock import patch
from flask import url_for

def test_reset_safeguard_no_debug_no_testing(authenticated_client, app_instance):
    """Test that /reset is blocked when not in DEBUG or TESTING mode."""
    with patch.dict(app_instance.config, {'DEBUG': False, 'TESTING': False}):
        with patch('histarchexplorer.views.admin.make_reset') as mock_make_reset:
            response = authenticated_client.get('/reset', follow_redirects=True)
            assert b'Reset is only allowed in debug or testing mode.' in response.data
            mock_make_reset.assert_not_called()

def test_reset_safeguard_with_testing(authenticated_client, app_instance):
    """Test that /reset is allowed when in TESTING mode (and patched)."""
    # Note: app_instance.config['TESTING'] is likely True by default in tests
    with patch.dict(app_instance.config, {'TESTING': True}):
        with patch('histarchexplorer.views.admin.make_reset') as mock_make_reset:
            response = authenticated_client.get('/reset', follow_redirects=True)
            assert b'reset database' in response.data
            mock_make_reset.assert_called_once()

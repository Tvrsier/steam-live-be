import pytest
from pydantic import ValidationError

from src.lib.steam.steam_client import SteamRequestParams


def test_call_method_accepts_get():
    """Test that 'get' is a valid call_method value."""
    params = SteamRequestParams(call_method="get")
    assert params.call_method == "get"


def test_call_method_accepts_post():
    """Test that 'post' is a valid call_method value."""
    params = SteamRequestParams(call_method="post")
    assert params.call_method == "post"


def test_call_method_default_is_get():
    """Test that the default call_method value is 'get'."""
    params = SteamRequestParams()
    assert params.call_method == "get"


def test_call_method_rejects_invalid_value():
    """Test that invalid call_method values raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        SteamRequestParams(call_method="put")  # type: ignore[arg-type]
    
    # Verify that the error is about call_method field
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("call_method",)
    assert "Input should be 'get' or 'post'" in errors[0]["msg"]


def test_call_method_rejects_none():
    """Test that None is not accepted as call_method value."""
    with pytest.raises(ValidationError) as exc_info:
        SteamRequestParams(call_method=None)  # type: ignore[arg-type]
    
    # Verify that the error is about call_method field
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("call_method",)


def test_call_method_rejects_delete():
    """Test that 'delete' is not accepted as call_method value."""
    with pytest.raises(ValidationError) as exc_info:
        SteamRequestParams(call_method="delete")  # type: ignore[arg-type]
    
    # Verify that the error is about call_method field
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("call_method",)

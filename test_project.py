import pytest
from project_location import get_farm_input

def test_valid_inputs(monkeypatch):
    inputs = iter(["39.3999", "-8.2245", "2025-01-01", "2025-01-10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result == {
        "latitude": 39.3999,
        "longitude": -8.2245,
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
    }

def test_invalid_latitude(monkeypatch):
    inputs = iter(["100", "39.3999", "-8.2245", "2025-01-01", "2025-01-10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result["latitude"] == 39.3999

def test_invalid_longitude(monkeypatch):
    inputs = iter(["39.3999", "200", "-8.2245", "2025-01-01", "2025-01-10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result["longitude"] == -8.2245

def test_invalid_dates(monkeypatch):
    inputs = iter(["39.3999", "-8.2245", "2025-01-10", "2025-01-01", "2025-01-15"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result["end_date"] == "2025-01-15"

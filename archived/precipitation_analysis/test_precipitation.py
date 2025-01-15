import pandas as pd
import pytest
from precipitation_analysis import precipitation_data_avg

def test_precipitation_data_avg():
    # Create sample test data
    data_10_days = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
        'Precipitation': [1.0, 2.0, 0.5, 1.2, 3.4, 2.1, 0.7, 1.5, 2.8, 3.0],
        'TemperatureMax': [30, 29, 28, 27, 26, 25, 24, 23, 22, 21],
        'TemperatureMin': [15, 14, 13, 12, 11, 10, 9, 8, 7, 6],
    })
    
    data_45_days = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=45, freq='D'),
        'Precipitation': [1.0] * 45,
        'TemperatureMax': [30] * 45,
        'TemperatureMin': [15] * 45,
    })
    
    data_100_days = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'Precipitation': [0.5] * 100,
        'TemperatureMax': [25] * 100,
        'TemperatureMin': [10] * 100,
    })

    # Test for 10-day data (rolling window = 3)
    result_10_days = precipitation_data_avg(data_10_days)
    assert 'Rolling_Average' in result_10_days.columns
    assert len(result_10_days) == len(data_10_days)
    assert result_10_days['Rolling_Average'].iloc[2] == pytest.approx((1.0 + 2.0 + 0.5) / 3)
    assert 'TemperatureMax' not in result_10_days.columns
    assert 'TemperatureMin' not in result_10_days.columns

    # Test for 45-day data (rolling window = 7)
    result_45_days = precipitation_data_avg(data_45_days)
    assert len(result_45_days) == len(data_45_days)
    assert result_45_days['Rolling_Average'].iloc[6] == pytest.approx(1.0)  # Since all values are 1.0

    # Test for 100-day data (rolling window = 30)
    result_100_days = precipitation_data_avg(data_100_days)
    assert len(result_100_days) == len(data_100_days)
    assert result_100_days['Rolling_Average'].iloc[29] == pytest.approx(0.5)  # Since all values are 0.5

    # Test for correct handling of dropped columns
    assert 'TemperatureMax' not in result_45_days.columns
    assert 'TemperatureMin' not in result_45_days.columns
    assert 'TemperatureMax' not in result_100_days.columns
    assert 'TemperatureMin' not in result_100_days.columns

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 

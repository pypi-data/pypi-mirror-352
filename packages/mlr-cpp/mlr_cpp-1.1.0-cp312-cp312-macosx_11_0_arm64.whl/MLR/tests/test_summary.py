from MLR.mlr_wrapper import MLRWrapper
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "x1": [1, 2, 3, 4],
        "x2": [5, 6, 0, 8],
        "y": [14, 17, 6, 23] #3 + x1 + 2*x2
    })

@pytest.fixture
def sample_data_large():
    return pd.DataFrame({
        "x1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "x2": [5, 6, 0, 8, 3, 4, 5, 1, 2, 6],
        "y":  [14, 17, 6, 23, 14, 17, 20, 13, 12, 21]
    })


@pytest.fixture
def no_intercept_data():
    return pd.DataFrame({
        "x1": [1, 2, 3, 4],
        "x2": [5, 6, 0, 8],
        "y": [11, 14, 3, 20] # x1 + 2*x2
    })

@pytest.fixture
def insignificant_regressor_data():
    """
    Generates a dataset with one theoretically significant regressor (x1) 
    and one theoretically insignificant regressor (x2), but with extreme noise.

    The true model is:
        y = 3 + 2*x1 + 0.0001*x2 + noise

    - x1 is designed to be significant (coefficient = 2)
    - x2 is designed to be insignificant (coefficient ≈ 0)
    - However, extreme noise is added to distort signal and simulate spurious significance
    """
    np.random.seed(42)
    n = 100
    x1 = np.random.rand(n)  # Significant regressor
    x2 = np.random.rand(n)  # Insignificant regressor
    noise = np.random.normal(0, 0.1, n)
    y = 3 + 2*x1 + 0.0001*x2 + (noise * 100_000_000)  # Adds extreme noise to distort significance
    return pd.DataFrame({'x1': x1, 'x2': x2, 'y': y})


@pytest.fixture
def sample_data_2():
    x1 = np.array([1,2,3,4, 5])
    x2 = np.array([3,4,1,2,-1])
    x3 = np.array([2,3,5,7,4])
    y = 1 + x1 + 2*x2 - 0.0021*x3
    return pd.DataFrame({'x1':x1, 'x2':x2, "x3":x3, 'y':y})


@pytest.fixture
def noisy_data():
    np.random.seed(42)
    x1 = np.random.rand(100)
    x2 = np.random.rand(100)
    # y = 3 + 2*x1 - x2 + some noise
    noise = np.random.normal(0, 0.5, size=100)
    y = 3 + 2 * x1 - 1 * x2 + noise
    return pd.DataFrame({'x1': x1, 'x2': x2, 'y': y})


def test_equation_returns_str(sample_data):
    model = MLRWrapper(sample_data, 'y')
    model.fit()
    eqn = model.get_eqn()
    # print(eqn)
    assert isinstance(eqn ,str)

def test_equation_with_small_regressor(sample_data_2):
    model = MLRWrapper(sample_data_2, 'y')
    model.fit()
    eqn = model.get_eqn()
    print(eqn)
    assert isinstance(eqn ,str)

def test_residuals_shapes(sample_data):
    model = MLRWrapper(sample_data, 'y')
    model.fit()

    residuals = model.get_residuals()

    # Check residuals shape
    assert residuals.shape == model.Y.shape


def test_residuals_values(sample_data):
    model = MLRWrapper(sample_data, 'y')
    model.fit()
    
    residuals = model.get_residuals()
    model_X = sample_data.drop(columns=['y']) #should be a dataframe
    # Check values match y - y_pred
    expected_residuals = model.Y - model.predict(model_X)
    # print(residuals.flatten())
    assert np.allclose(residuals, expected_residuals, atol=1e-6)


def test_get_RSS_and_TSS_after_fit(sample_data):
    model = MLRWrapper(sample_data, "y")
    model.fit()
    rss = model.get_RSS()
    tss = model.get_TSS()
    # RSS should be >= 0, same for TSS
    assert isinstance(rss, (float,np.float64)) 
    assert isinstance(tss, (float,np.float64))
    assert rss >= 0
    assert tss >= 0

def test_get_RSS_and_TSS_before_fit_raises(sample_data):
    model = MLRWrapper(sample_data, "y")
    with pytest.raises(ValueError, match="Model not fit yet"):
        model.get_RSS()
    with pytest.raises(ValueError, match="Model not fit yet"):
        model.get_TSS()



def test_r_squared_raises_before_fit(sample_data):
    model = MLRWrapper(sample_data, target_col="y")
    with pytest.raises(ValueError, match="Model not fit yet"):
        model.get_R2()




def test_r_squared(sample_data):
    model = MLRWrapper(sample_data, target_col="y")
    model.fit()
    r2 = model.get_R2()
    # print(r2)
    # In this case, data is perfectly linear => R^2 should be ~1.0
    assert isinstance(r2, (float, np.float64))
    assert np.isclose(r2, 1.0, atol=1e-10)


def test_adjusted_r_squared(sample_data):
    model = MLRWrapper(sample_data, "y")
    model.fit()
    adj_r2 = model.get_AdjustedR2()
    assert isinstance(adj_r2, (float, np.float64))
    # Should also be very close to 1.0 for perfect linear data
    assert np.isclose(adj_r2, 1.0, atol=1e-10)


def test_mse_on_perfect_fit(sample_data):
    model = MLRWrapper(sample_data, "y")
    model.fit()
    mse = model.get_MSE()
    assert isinstance(mse, (float, np.float64))
    assert np.isclose(mse, 0.0, atol=1e-10)


def test_mae_on_perfect_fit(sample_data):
    model = MLRWrapper(sample_data, "y")
    model.fit()
    mae = model.get_MAE()
    assert isinstance(mae, (float, np.float64))
    assert np.isclose(mae, 0.0, atol=1e-10)


def test_adjusted_r_squared_on_noisy_data(noisy_data):
    model = MLRWrapper(noisy_data, 'y')
    model.fit()
    adj_r2 = model.get_AdjustedR2()
    assert isinstance(adj_r2, (float, np.float64))
    assert 0.0 < adj_r2 < 1.0  # Should be reasonable but not perfect


def test_mse_on_noisy_data(noisy_data):
    model = MLRWrapper(noisy_data, "y")
    model.fit()
    mse = model.get_MSE()
    assert isinstance(mse, (float, np.float64))
    assert mse > 0  # Not zero due to noise


def test_mae_on_noisy_data(noisy_data):
    model = MLRWrapper(noisy_data, "y")
    model.fit()
    mae = model.get_MAE()
    assert isinstance(mae, (float, np.float64))
    assert mae > 0  # Not zero due to noise

    
def test_ftest_is_positive_and_reasonable():
    df = pd.DataFrame({
        "x1": [1, 2, 3, 4, 5],
        "x2": [5, 5, 3, 4, 2],
        "y": [11, 12, 11, 12, 9]  # Linear and predictable
    })
    model = MLRWrapper(df, target_col="y")
    model.fit()

    f_stat = model.get_ftest()
    assert isinstance(f_stat, float)
    assert f_stat > 0  # F-statistic should be positive in valid model


def test_tstatistics_values_and_shape():
    df = pd.DataFrame({
        "x1": [1, 2, 3, 4, 5],
        "x2": [2, 6, 12, 20, 30],
        "y": [3, 8, 15, 24, 35]  # y = x1 + x2, perfect linear relationship
    })
    model = MLRWrapper(df, target_col="y")
    model.fit()

    t_stats = model.get_TStatistics()  # Fixed typo in method name
    
    # Check type and shape
    assert isinstance(t_stats, np.ndarray)
    assert t_stats.shape == (3,) or t_stats.shape == (3, 1)  # Accept either shape
    
    # Check for finite values
    assert np.all(np.isfinite(t_stats))
    
    # For perfect fit, t-stats should be either:
    # - Very large (significant coefficients)
    # - Very small (for intercept if data is centered)

    assert np.any((np.abs(t_stats) > 500)) 

def test_pvalues_on_perfect_fit(sample_data):
    model = MLRWrapper(sample_data, 'y')
    model.fit()
    pvalues = model.get_PValues()
    
    assert isinstance(pvalues, np.ndarray)
    assert pvalues.shape[0] == sample_data.shape[1]  # num of predictors + intercept
    
    # print(f"Coeff: {model.get_coefficients()}")
    # print("P-Values:", pvalues)
    # In a perfect linear fit, all relevant predictors should have small p-values
    assert np.any(pvalues < 0.05)  # Some should be significant



def test_pvalues_on_perfect_fit_no_intercept(no_intercept_data):
    model = MLRWrapper(no_intercept_data, 'y')
    model.fit()
    pvalues = model.get_PValues()
    
    assert isinstance(pvalues, np.ndarray)
    assert pvalues.shape[0] == no_intercept_data.shape[1]  # num of predictors + intercept
    
    # print(f"Coeff: {model.get_coefficients()}")
    # print("P-Values:", pvalues)
    # In a perfect linear fit, all relevant predictors should have small p-values
    assert np.any(pvalues < 0.05)  # Some should be significant

def test_pvalues_on_insignificant_regressor(insignificant_regressor_data):
    model = MLRWrapper(insignificant_regressor_data, "y")
    model.fit()
    pvalues = model.get_PValues()

    assert isinstance(pvalues, np.ndarray)
    assert pvalues.shape[0] == insignificant_regressor_data.shape[1]  # predictors + intercept
    
    # print(f"Model ceoff: {model.get_coefficients()}")
    # print(f"Tstatistics: {model.get_TStatistics()}")
    # print(f"P-values: {pvalues}")
    # x2 is insignificant; at least some might be > 0.05
    assert np.any(pvalues > 0.05)


def test_pvalues_before_fit_raises(sample_data):
    model = MLRWrapper(sample_data, "y")
    with pytest.raises(ValueError, match="Model not fit yet"):
        model.get_PValues()


def test_get_predictor_summary(sample_data):

    model = MLRWrapper(sample_data, target_col='y')
    model.fit()

    # Test without tstats
    summary = model.get_predictor_summary()
    assert isinstance(summary, pd.DataFrame)
    assert list(summary.columns) == ['coeffs', 'P Value']
    assert list(summary.index) == ['b0','x1', 'x2']
    assert isinstance(model.get_eqn(), str)
    assert model.get_eqn().strip() != ""


def test_get_predictor_summary_with_t_stats(sample_data):

    model = MLRWrapper(sample_data, target_col='y')
    model.fit()

    # Test without tstats
    summary = model.get_predictor_summary(tstats=True)
    assert isinstance(summary, pd.DataFrame)
    assert list(summary.columns) == ['Coeffs', 'P Value',"T Statistic"]
    assert list(summary.index) == ['b0','x1', 'x2']
    assert isinstance(model.get_eqn(), str)
    assert model.get_eqn().strip() != ""
    assert not summary['T Statistic'].isnull().any()



def test_get_model_tests(sample_data_large):
    #large dataset to prevent overfitting
    model = MLRWrapper(sample_data_large, target_col='y')
    model.fit()

    test_df = model.get_model_tests()

    # Check it's a DataFrame with correct index and columns
    assert isinstance(test_df, pd.DataFrame)
    assert list(test_df.index) == ['Values']

    expected_columns = [
        "Adjusted Rsquared", "Rsquared", "Mean Absolute Error",
        "Mean Squared Error", "F Test", "RSS", "TSS",
    ]
    print()
    print(f"Resiudals: {model.get_residuals()}")
    print(test_df)
    assert all(col in test_df.columns for col in expected_columns)

    # Check that values are floats and finite
    for col in expected_columns:
        val = test_df.loc['Values', col]
        assert isinstance(val, float)
        assert pd.notna(val)
        assert not pd.isna(val)
        assert abs(val) < 1e10 


def test_model_summary_structure(sample_data_large):
    model = MLRWrapper(sample_data_large, 'y')
    model.fit()
    model_eqn, predictor_df, test_df = model.get_model_summary(tstats=True)

    # Check types
    assert isinstance(model_eqn, str)
    assert isinstance(predictor_df, pd.DataFrame)
    assert isinstance(test_df, pd.DataFrame)

    # Check that key stats exist
    assert "Rsquared" in test_df.columns
    assert "Mean Absolute Error" in test_df.columns
    assert "F Test" in test_df.columns

    # Check that predictors are present
    assert predictor_df.shape[0] == 3  # intercept + 2 predictors
    assert "Coeffs" in predictor_df.columns
    assert "T Statistic" in predictor_df.columns
    assert "P Value" in predictor_df.columns

    # Equation sanity check
    assert "y = " in model_eqn
    assert "x1" in model_eqn and "x2" in model_eqn
import pytest
import pandas as pd
import numpy as np
from MLR.mlr_wrapper import MLRWrapper  


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "x1": [1, 2, 3, 4],
        "x2": [5, 6, 0, 8],
        "y": [11, 12, 2, 20] #x1 + 2*x2
    })

@pytest.fixture
def MLR_instance():
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'feature2': [2, 3, -1, 5],
        'target':[5, 7, 1, 11]
    })
    return MLRWrapper(df, 'target')

@pytest.fixture
def MLR_testData():
    X = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'feature2': [2, 3, -1, 5],})
    return X



@pytest.fixture
def noisy_data():
    np.random.seed(42)
    x1 = np.random.rand(100)
    x2 = np.random.rand(100)
    # y = 3 + 2*x1 - x2 + some noise
    noise = np.random.normal(0, 0.5, size=100)
    y = 3 + 2 * x1 - 1 * x2 + noise
    return pd.DataFrame({'x1': x1, 'x2': x2, 'y': y})


@pytest.fixture
def square_data():
    #returns a square matrix
    #statistically meaningless because it overfits the data
    return pd.DataFrame({
        "x1": [1, 2, 3,],
        "x2": [5, 6, 0,],
        "y": [12, 15, 4,] #x1 + 2*x2 + 1
    })

def test_predict_before_fit_raises(MLR_instance, MLR_testData):
    with pytest.raises(ValueError, match="Model not fit yet"):
        MLR_instance.predict(MLR_testData)

def test_fit_success(MLR_instance):
    MLR_instance.fit()
    assert MLR_instance.fitted



def test_fit_with_non_dataframe():
    # Pass a list instead of a DataFrame
    non_df_input = [[1, 2], [3, 4]]

    with pytest.raises(ValueError, match="Input df should be an instance of Pandas DataFrame"):
        MLRWrapper(non_df_input, target_col="y")


def test_predict_with_non_dataframe(sample_data):
    # sample_data is a fixture that returns a valid DataFrame with target_col
    model = MLRWrapper(sample_data, target_col="y")
    model.fit()
    
    non_df_input = [[1, 2], [3, 4]]  # This is not a pandas DataFrame

    with pytest.raises(ValueError, match="Predictor is not a Pandas DataFrame"):
        model.predict(non_df_input)


def test_predict_shape_is_1d_array(sample_data):
    # Initialize and fit the model
    model = MLRWrapper(sample_data, target_col="y")
    model.fit()

    # Create a 1D predictor row (with the same number of features as training data)
    one_row = pd.DataFrame([{"x1": 10, "x2": 20}])  # Shape (1, 2)

    # Predict using the 1D row
    prediction = model.predict(one_row)

    # Check prediction is returned as an array-like and has shape (1,) or (1, 1)
    assert prediction is not None
    assert prediction.shape in [(1,), (1, 1)]



def test_predict_with_wrong_shape():
    # Sample training data
    df = pd.DataFrame({
        "x1": [1, 2, 3, 0],
        "x2": [4, 1, 6, 1],
        "y": [9, 4, 15, 2] #x1 + 2*x2
    })

    # Train the model
    model = MLRWrapper(df, target_col="y")
    model.fit()

    #test predict with wrong number of features (e.g., only 1 column instead of 2)
    wrong_input = pd.DataFrame({
        "x1": [10, 11, 12, 9]  # Missing x2
    })

    with pytest.raises(ValueError, match="Data has different num of parameters than model parameters"):
        model.predict(wrong_input)



def test_fit_with_wrong_target_type():
    # Create a DataFrame with a non-numeric target column
    df = pd.DataFrame({
        "x1": [1, 2, 3],
        "x2": [4, 5, 6],
        "y": ["a", "b", "c"]  # Invalid target (strings instead of numbers)
    })

    with pytest.raises(ValueError, match="DataFrame can contain only numerical data"):
        MLRWrapper(df, target_col="y")
    

def test_fit_and_predict_large_dataset():
    np.random.seed(0)
    X = pd.DataFrame(np.random.randn(1000, 10), columns=[f'x{i}' for i in range(10)])
    true_coefs = np.random.randn(10)
    y = X.dot(true_coefs) + np.random.normal(0, 0.01, 1000)

    df = X.copy()
    df["y"] = y

    model = MLRWrapper(df, target_col="y")
    model.fit()
    preds = model.predict(X)

    # R² should be close to 1
    ss_res = np.sum((y - preds.flatten())**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - ss_res / ss_tot
    assert r2 > 0.99


def test_prediction_accuracy_on_linear_data():
    # Create a DataFrame with known linear relationship: y = 2*x1 + 3*x2 + 5
    np.random.seed(0)
    x1 = np.array([1,4,5, 9])
    x2 = np.array([0,4,6,-2])
    y = 1 * x1 + 2 * x2 + 5

    df = pd.DataFrame({
        "x1": x1,
        "x2": x2,
        "y": y
    })
    # Fit the model
    model = MLRWrapper(df, target_col="y")
    model.fit()

#     # Predict using the training data
    predictions = model.predict(df[["x1", "x2"]]).reshape(-1,1)
    y = y.reshape(-1,1)
    # Check if predictions are close to actual y
    np.testing.assert_allclose(predictions, y, atol=1e-4)


def test_multicolliner_data():
    # x1 = 3 - x2
    df = pd.DataFrame({
        "x1": [1, 2, 3, 4],
        "x2": [2, 1, 0, -1]
    })
    y = 2 + 3 * df["x1"] + 4 * df["x2"]
    df["y"] = y

    with pytest.raises(ValueError, match="Regression Data is collinear"):
        model = MLRWrapper(df, target_col="y")



def test_get_coefficients_matches_expected():
    # Create a simple dataset where the relationship is known: y = 2 + 3*x1 + 4*x2
    df = pd.DataFrame({
        "x1": [1, 2, 3, 4],
        "x2": [2, 1, 0, -2]
    })
    y = 2 + 3 * df["x1"] + 4 * df["x2"]
    df["y"] = y

    model = MLRWrapper(df, target_col="y")
    model.fit()
    coeffs = model.get_coefficients()
    predicted_output = np.array([2,3,4]).reshape(-1,1)
    assert np.allclose(coeffs,predicted_output,atol=1e-4)


def test_sufficient_data(square_data):
    with pytest.raises(ValueError, match="Insufficient Data for meaningful model"):
        model = MLRWrapper(square_data, target_col='y')

    
def test_pvalues_valid_output(sample_data):
    model = MLRWrapper(sample_data, 'y')
    model.fit()
    pvalues = model.get_PValues()
    
    # Ensure output is a numpy array
    assert isinstance(pvalues, np.ndarray)
    
    # Length should match number of predictors + intercept
    assert pvalues.shape[0] == sample_data.shape[1]

    # P-values should be between 0 and 1
    assert np.all((0 <= pvalues) & (pvalues <= 1))




def test_pvalues_before_fit_raises(sample_data):
    model = MLRWrapper(sample_data, "y")
    with pytest.raises(ValueError, match="Model not fit yet"):
        model.get_PValues()

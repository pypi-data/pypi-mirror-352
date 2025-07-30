import pandas as pd
import mlr_cpp
import numpy as np
from typing import Tuple

class MLRWrapper:
    """
        Wrapper for fit() using pandas dataframe
    """
    def __init__(self, df: pd.DataFrame, target_col: str):

        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input df should be an instance of Pandas DataFrame")
        if not target_col in df.columns:
            raise ValueError("Target column not in dataframe")
        
        if not self.isnumerical(df):
            raise ValueError("DataFrame can contain only numerical data")
        

        self.Y = df[[target_col]].to_numpy()
        self.X = df.drop(columns=[target_col]).to_numpy()


        #check if X is multicollinear

        self.predictors = [col for col in df.columns if col != target_col]

        self.target = target_col

        self.model = mlr_cpp.MLR(self.X, self.Y)

        if self.model.isCollinear():
            raise ValueError("Regression Data is collinear")
        
        if not self.model.hasSufficentData():
            raise ValueError("Insufficient Data for meaningful model")
        
        self.fitted = False


    def fit(self) -> None:
        """
            Pass our C++ fit method
        """
        self.model.fit()
        self.fitted = True


    def model_is_fit(self):
        return self.fitted
    
    #Decorator to check if the model is fit or not
    def requires_fit(method):
        def wrapper(self, *args, **kwargs):
            if not self.model_is_fit():
                raise ValueError("Model not fit yet")
            return method(self,*args, **kwargs)
        return wrapper


    @staticmethod
    #checks if the data is numerical or not
    def isnumerical(df: pd.DataFrame) -> bool:
        #returns False if there is at least one value that is not numerical
        return all([pd.api.types.is_numeric_dtype(df[col]) for col in df.columns])


    @requires_fit
    def predict(self, x:pd.DataFrame) -> np.ndarray:
        if not isinstance(x, pd.DataFrame):
            raise ValueError("Predictor is not a Pandas DataFrame")
        
        if x.shape[1] != self.X.shape[1]: #check if the data has the same number of columns as the data
            raise ValueError("Data has different num of parameters than model parameters")
        
        return self.model.predict(x.to_numpy())
    

    @requires_fit
    def get_coefficients(self) -> np.ndarray:
        """
            Get the coefficients of our model
        """
        return self.model.getCoefficients()
    
    @staticmethod 
    def get_rounded_with_tolerance_coeffs(coeffs: np.ndarray, atol: int, decimals: int)-> np.ndarray:
        """
            rounds the value of the coeffs to their nearest two digit if it is close to the absolute tolerance
        """
        rounded_coeffs = np.round(coeffs, decimals)
        is_close = np.isclose(coeffs, rounded_coeffs, atol=atol)
        #returns rounded coeffs if the value is close else the original coeffs
        return np.where(is_close, rounded_coeffs, coeffs)
        
    #TODO: correct the eqn string
    #make sure of the + sign
    #remove beta if value is close to 0.0
    @requires_fit
    def get_eqn(self, rounded:bool = True, atol:int = 1e-8, decimals:int = 4 ) -> str:
        """
            returns the eqn of the model
            does round up the value with absolute tolerance 1e-8
        """
        coeffs = self.get_coefficients().reshape(-1, 1)
        if rounded:
            coeffs = self.get_rounded_with_tolerance_coeffs(coeffs=coeffs, atol=atol, decimals=decimals)

        terms = []

        # Add intercept if not zero
        intercept = coeffs[0, 0]
        if abs(intercept) > atol:
            terms.append(f"{intercept}")

        # Add each term
        for coeff, predictor in zip(coeffs[1:, 0], self.predictors):
            sign = "+" if coeff >= 0 else "-"
            coeff_abs = abs(coeff)
            terms.append(f"{sign} {coeff_abs} * {predictor}")

        eqn = f"{self.target} = {' '.join(terms)}"
        return eqn
        
    @requires_fit
    def get_residuals(self) -> np.ndarray:
        return self.model.getResiduals()
    
    @requires_fit
    def get_RSS(self) -> np.float64:
        return self.model.getRSS()
    
    @requires_fit
    def get_TSS(self) -> np.float64:
        return self.model.getTSS()
    
    @requires_fit
    def get_R2(self) -> np.float64:
        return self.model.getR2()
    
    @requires_fit
    def get_AdjustedR2(self) -> np.float64:
        return self.model.getAdjustedR2()
    
    @requires_fit
    def get_MSE(self) -> np.float64:
        return self.model.getMSE()
    
    @requires_fit
    def get_MAE(self) -> np.float64:
        return self.model.getMAE()
    
    @requires_fit
    def get_ftest(self) -> np.float64:
        return self.model.Ftest()

    @requires_fit
    def get_TStatistics(self) -> np.float64:
        return self.model.getTStatistics().reshape(-1,1) #return shape (m,1)
    
    @requires_fit
    def get_PValues(self) -> np.ndarray:
        return self.model.getPValues().reshape(-1,1)
    
    @requires_fit
    def get_predictor_summary(self,tstats:bool = False) -> pd.DataFrame:
        """
            Returns the summary of the predictors including thier coeffs, p values and optionally t statistic
        """
        coeffs = self.get_coefficients().flatten()
        p_vals = self.get_PValues().flatten()
        t_stats = self.get_TStatistics().flatten()
        predictor_summary = {'Coeffs':coeffs, 'P Value':p_vals, 'T Statistic': t_stats} if tstats else {'coeffs':coeffs, 'P Value':p_vals}
        predictor_summary = pd.DataFrame(predictor_summary, index=(['b0'] + self.predictors))

        return predictor_summary
    

    def get_model_tests(self) -> pd.DataFrame:
        """
            Returns a dataframe containing the model tests
        """
        test_results = {"Adjusted Rsquared":self.get_AdjustedR2(), "Rsquared": self.get_R2(), "Mean Absolute Error": self.get_MAE(),
                        "Mean Squared Error":self.get_MSE(), "F Test": self.get_ftest(), "RSS":self.get_RSS(), "TSS":self.get_TSS(),
                        }
        return pd.DataFrame(test_results, index=['Values'])


    @requires_fit
    def get_model_summary(self, tstats = False)-> Tuple[str,pd.DataFrame, pd.DataFrame]:
        """
        Return the model eqn 
        and a dataframe containing the summary of the model
        Optionally return the t statistics of the predictors
        """
        model_eqn = self.get_eqn()
        predictor_summary = self.get_predictor_summary(tstats=tstats)
        model_tests = self.get_model_tests()
        return (model_eqn, predictor_summary, model_tests)


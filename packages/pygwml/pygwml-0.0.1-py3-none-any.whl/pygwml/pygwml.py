import pandas as pd
import numpy as np
import xgboost as xgb
from xgboost import XGBRegressor
from sklearn.metrics import r2_score
from sklearn.utils import resample
from scipy.spatial import distance
import libpysal
from esda import Moran
from sklearn.model_selection import train_test_split
from sklearn.neighbors import BallTree


class GXGB:
    '''
    Python 3 based implementation of Geographically Weighted XGBoost (GXGB).
    Parameters
    -------------------------
    kernel: {"adaptive", "fixed"}, default="adaptive"  
        Specifies the type of spatial kernel used to determine neighboring data points:  
        - "adaptive": Uses a fixed number of nearest neighbors to fit local models, regardless of distance.  
        - "fixed": Includes all neighbors within a specified fixed distance for local model fitting.
    bandwidth: int or float  
        Defines the spatial extent used to select neighbors for local model fitting:  
        - If `kernel="adaptive"`, it represents the number of nearest neighbors.  
        - If `kernel="fixed"`, it specifies the fixed distance threshold within which neighbors are considered.
    n_estimators: int (default=100)  
        Number of boosting rounds (trees).
    learning_rate / eta: float (default= 0.3)  
        Step size shrinkage (e.g., 0.01–0.3).
    max_depth: int (default=6)  
        Maximum depth of each tree.
    min_child_weight: float (default=1.0)  
        Minimum sum of weights needed in a child.
    subsample: float  (default=1.0)  
        Fraction of training samples used per tree.
    colsample_bytree: float  (default=1.0)  
        Subsample ratio of columns per tree.
    train_weighted: bool, default = True
        Whether samples are weighted based on distances for training local models. If False, samples are equally weighted.
    predict_weighted: bool, default = True
        Whether the ensemble of local models within the bandwidth is used and spatially weighted for producing local predictions. If False, only closest local model is used for producing local predictions.
    **kwargs : dict, optional
    
    Additional parameters for fitting the XGBoost Regressor Model. Some common parameters include:  
     colsample_bylevel: float  
       Subsample ratio of columns per level.
     colsample_bynode: float  
       Subsample ratio of columns per node.
     reg_alpha (alpha): float  
       L1 regularization on weights.
     reg_lambda (lambda): float  
       L2 regularization on weights.
     scale_pos_weight: float  
       Control for class imbalance (not common for regression).
     booster: str  
       Booster type: 'gbtree', 'gblinear', 'dart'.
     random_state / seed: int  
       Random number seed.
     n_jobs: int  
            Number of parallel threads.

Additional parameters can be found in the XGBoostRegressor parameters documentation at the link: https://xgboost.readthedocs.io/en/stable/parameter.html
    -------------------------
    '''
    def __init__(self, band_width, kernel="adaptive", n_estimators=100, learning_rate=0.3, 
                 colsample_bytree=1.0, subsample=1.0, min_child_weight=1.0, max_depth=6,
                 train_weighted=True, predict_weighted=True, random_state=None, **kwargs):
        self.kernel = kernel
        self.band_width = band_width
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.colsample_bytree = colsample_bytree
        self.subsample = subsample
        self.train_weighted = train_weighted
        self.predict_weighted = predict_weighted
        self.min_child_weight = min_child_weight
        self.max_depth = max_depth
        self.random_state = random_state
        self.xgb_params = kwargs
        self.local_models = []
        self.resampled = False  # default no resampling

    def fit(self, X_train, y_train, coords):
        '''
        Fit GXGB model
        Parameters
        ----------
        X_train: pd.DataFrame
            Independent variables (Features) of training samples.
        y_train: pd.Series
            Dependent variable (Target) of training samples.
        coords: pd.DataFrame
            2D coordinates of training samples (projected).
        Returns
        -------
        None
        '''
        # Reset index to ensure positional indices are valid for iloc
        X_train = X_train.reset_index(drop=True)
        y_train = y_train.reset_index(drop=True)
        
        self.train_data_columns = X_train.columns.tolist()
        
        coords_array = np.array(coords, dtype=np.float64)
        self.train_data_coords = coords_array
        self.distance_matrix = distance.cdist(coords_array, coords_array, 'euclidean')
        
        epsilon = 1e-10  # small value to avoid divide by zero
        
        n_samples = len(X_train)
        
        if self.train_weighted:
            if self.kernel == "adaptive":
                k = min(max(1, int(self.band_width)), n_samples)
                bandwidth_array = np.partition(self.distance_matrix, k - 1, axis=1)[:, k - 1] + epsilon
                self.weight_matrix = (1 - (self.distance_matrix / bandwidth_array[:, np.newaxis])**2)**2
                self.weight_matrix[self.distance_matrix > bandwidth_array[:, np.newaxis]] = 0
            elif self.kernel == "fixed":
                self.weight_matrix = (1 - (self.distance_matrix / self.band_width)**2)**2
                self.weight_matrix[self.distance_matrix > self.band_width] = 0
        
        self.local_models = []
        
        for i in range(n_samples):
            dist_arr = self.distance_matrix[i]
            
            if self.kernel == "adaptive":
                k = min(int(self.band_width), n_samples)
                idx = np.argpartition(dist_arr, k - 1)[:k]
                idx = idx[np.argsort(dist_arr[idx])]
            elif self.kernel == "fixed":
                idx = np.where(dist_arr < self.band_width)[0]
                idx = idx[np.argsort(dist_arr[idx])]
            
            # Defensive check to avoid empty or invalid index error
            if len(idx) == 0:
                # fallback to closest point (itself)
                idx = np.array([i])
            
            # Filter any indices out of bounds (safety)
            idx = idx[idx < n_samples]
            
            X_local = X_train.iloc[idx]
            y_local = y_train.iloc[idx]
            
            sample_weights = None
            if self.train_weighted:
                sample_weights = self.weight_matrix[i, idx]
            
            model = xgb.XGBRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                colsample_bytree=self.colsample_bytree,
                subsample=self.subsample,
                min_child_weight=self.min_child_weight,
                max_depth=self.max_depth,
                random_state=self.random_state,
                **self.xgb_params
            )
            
            if sample_weights is not None:
                model.fit(X_local, y_local, sample_weight=sample_weights)
            else:
                model.fit(X_local, y_local)
            
            self.local_models.append(model)

        # Fit global model on all training data (unweighted)
        self.global_model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            colsample_bytree=self.colsample_bytree,
            subsample=self.subsample,
            min_child_weight=self.min_child_weight,
            max_depth=self.max_depth,
            random_state=self.random_state,
            **self.xgb_params
        )
        self.global_model.fit(X_train, y_train)

    def predict(self, X_test, coords_test, local_weight=0.5):
        """
        Make predictions using the fitted GXGB model.

        Parameters
        ----------
        X_test: pd.DataFrame
            Independent variables of test samples.
        coords_test: pd.DataFrame
            Coordinates of test samples (projected).
        local_weight: float, default=0.5
            Weight for combining global and local predictions (0-1).

        Returns
        -------
        tuple: (combined_pred, global_pred, local_pred)
            combined_pred: Combined predictions
            global_pred: Global model predictions
            local_pred: Local model predictions
        """
        global_pred = self.global_model.predict(X_test)
        
        # Local model predictions matrix (samples x local models)
        local_preds = np.array([model.predict(X_test) for model in self.local_models]).T
        
        coords_test_arr = np.array(coords_test, dtype=np.float64)
        dist_matrix = distance.cdist(coords_test_arr, self.train_data_coords, 'euclidean')
        
        local_pred = np.zeros(len(X_test))
        if self.predict_weighted:
            if self.kernel == "adaptive":
                k = min(int(self.band_width), dist_matrix.shape[1])
                bandwidths = np.partition(dist_matrix, k - 1, axis=1)[:, k - 1] * 1.0000001
                weights = (1 - (dist_matrix / bandwidths[:, np.newaxis])**2)**2
                weights[dist_matrix > bandwidths[:, np.newaxis]] = 0
            elif self.kernel == "fixed":
                weights = (1 - (dist_matrix / self.band_width)**2)**2
                weights[dist_matrix > self.band_width] = 0
            
            for i in range(len(X_test)):
                if self.kernel == "adaptive":
                    idx = np.argpartition(dist_matrix[i], k - 1)[:k]
                else:
                    idx = np.where(dist_matrix[i] < self.band_width)[0]
                
                w = weights[i, idx]
                w_sum = w.sum()
                if w_sum == 0:
                    # fallback to closest point
                    closest_idx = np.argmin(dist_matrix[i])
                    local_pred[i] = local_preds[i, closest_idx]
                else:
                    w_normalized = w / w_sum
                    local_pred[i] = np.dot(local_preds[i, idx], w_normalized)
        else:
            closest_indices = np.argmin(dist_matrix, axis=1)
            local_pred = local_preds[np.arange(len(X_test)), closest_indices]
        
        combined_pred = local_weight * local_pred + (1 - local_weight) * global_pred
        return combined_pred, global_pred, local_pred

    def get_local_feature_importance(self):
        """
        Get local feature importance from XGBoost models.

        Returns
        -------
        pd.DataFrame
            Feature importance for each local model.
        """
        if not self.local_models:
            print("Model not trained yet")
            return None
        
        imp_data = []
        for i, model in enumerate(self.local_models):
            imp = model.feature_importances_
            imp_data.append([i] + list(imp))
        
        return pd.DataFrame(imp_data, columns=["model_index"] + self.train_data_columns)

    def get_globally_enhanced_local_feature_importances(self, normalize_local=True, normalize_global=True):
        """
    Returns a DataFrame of local feature importances multiplied element-wise
    by global feature importance.

    Parameters
    ----------
    normalize_local : bool, default=True
        Normalize local feature importance vectors (per sample) to sum to 1.
    normalize_global : bool, default=True
        Normalize global feature importance vector to sum to 1.

    Returns
    -------
    pd.DataFrame
        DataFrame of shape (n_samples, n_features) with enhanced feature importances.
        """
        if not self.local_models or self.global_model is None:
            raise ValueError("Models not fitted. Call `fit` first.")
    
        # Local importances matrix: (n_samples, n_features)
        local_importances = np.array([model.feature_importances_ for model in self.local_models])
        if normalize_local:
            local_importances = local_importances / local_importances.sum(axis=1, keepdims=True)
    
        # Global importance vector: (n_features,)
        global_importance = self.global_model.feature_importances_
        if normalize_global:
            global_importance = global_importance / global_importance.sum()
    
        # Element-wise multiply local importance by global importance per feature
        enhanced_importances = local_importances * global_importance
        return pd.DataFrame(enhanced_importances, columns=self.train_data_columns)

def ISA_op_bw(y, coords, bw_min=None, bw_max=None, step=1):
    '''
    Determine the optimal bandwidth by applying Incremental Spatial Autocorrelation (ISA).
Maximize Moran's I (spatial autocorr), hence it is good for bandwidth calcultaion 
when target is Statistical spatial analysis of Data.
Parameters:
----------
y : pandas.Series
    Target variable values for all data points.
coords : pandas.DataFrame
    Two-dimensional spatial coordinates for each data point (ideally in a projected coordinate system).
bw_min : int, optional
    Starting value for the bandwidth search range (default is 1).
bw_max : int, optional
    Ending value for the bandwidth search range (default is the total number of observations).
step : int, optional
    Increment step for bandwidth values during the search (default is 1).

Returns
-------
optimal_bandwidth : int
    Bandwidth value selected as optimal based on ISA analysis.
moran_I_value : float
    Moran's I statistic corresponding to the optimal bandwidth.
p_value : float
    Statistical significance (p-value) of the Moran's I at the optimal bandwidth.
    '''
    if bw_min is None:
        bw_min = 1
    if bw_max is None:
        bw_max = len(y)

    coords_list = [tuple(row) for row in coords.to_numpy()]
    kd = libpysal.cg.KDTree(np.array(coords_list))

    bandwidth_list, moran_I_list, z_score_list, p_value_list = [], [], [], []

    for current_bw in range(bw_min, bw_max, step):
        kw = libpysal.weights.KNN(kd, current_bw)
        moran_I = Moran(y, kw)
        bandwidth_list.append(current_bw)
        moran_I_list.append(moran_I.I)
        z_score_list.append(moran_I.z_norm)
        p_value_list.append(moran_I.p_norm)

    max_index = None
    max_zscore = float('-inf')
    for i in range(len(z_score_list)):
        if z_score_list[i] > max_zscore and p_value_list[i] < 0.05:
            max_zscore = z_score_list[i]
            max_index = i

    found_bandwidth = bandwidth_list[max_index]
    found_moran_I = moran_I_list[max_index]
    found_p_value = p_value_list[max_index]
    print(f"bandwidth: {found_bandwidth}, moran's I: {found_moran_I}, p-value: {found_p_value}")

    return found_bandwidth, found_moran_I, found_p_value


def search_bandwidth(X, y, coords,
                     n_estimators,
                     max_depth,
                     min_child_weight,
                     subsample,
                     train_weighted=True,
                     bw_min=None,
                     bw_max=None,
                     step=1,
                     test_size=0.2,
                     n_jobs=1,
                     random_state=None):
    """
Searches for the optimal spatial bandwidth for geographically weighted XGBoost regression.
Maximize predictive performance, hence it is useful to calculate bandwidth when tt otest
Validation-based model performance.
    Parameters
    ----------
    X : pd.DataFrame
        Input features.
    y : pd.Series
        Target variable.
    coords : pd.DataFrame or np.array
        Spatial coordinates of samples (shape: [n_samples, 2]).
    n_estimators : int
        Number of trees for XGBoost.
    max_depth : int
        Maximum tree depth for base learners.
    min_child_weight : int or float
        Minimum sum of instance weight needed in a child.
    subsample : float
        Subsample ratio of the training instances.
    train_weighted : bool, optional
        Whether to weight samples based on spatial proximity during training (default True).
    bw_min : int, optional
        Minimum bandwidth.
    bw_max : int, optional
        Maximum bandwidth.
    step : int, optional
        Step size for bandwidth.
    test_size : float, optional
        Proportion of data to hold out for validation.
    n_jobs : int, optional
        Number of parallel jobs for XGBoost (default 1).
    random_state : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict
        Contains DataFrame of bandwidths and scores and the best bandwidth.
    """
    records_num = X.shape[0]
    variables_num = X.shape[1]

    if bw_min is None:
        bw_min = max(round(records_num * 0.05), variables_num + 2, 20)
    if bw_max is None:
        bw_max = max(round(records_num * 0.95), variables_num + 2)

    bandwidths = []
    scores = []

    tree = BallTree(coords.values)

    for bw in range(bw_min, bw_max + 1, step):
        bandwidths.append(bw)

        # Get neighbors within bandwidth (distance radius)
        indices = tree.query_radius(coords.values, r=bw)

        weights = np.zeros(records_num)
        for i in range(records_num):
            # distances to neighbors of point i
            dists = np.linalg.norm(coords.values[indices[i]] - coords.values[i], axis=1)
            # Gaussian kernel weights for neighbors
            w = np.exp(- (dists ** 2) / (2 * (bw ** 2)))
            weights[i] = np.mean(w)

        sample_weights = weights if train_weighted else np.ones(records_num)

        X_train, X_test, y_train, y_test, sw_train, sw_test = train_test_split(
            X, y, sample_weights, test_size=test_size, random_state=random_state)

        model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_child_weight=min_child_weight,
            subsample=subsample,
            random_state=random_state
        )
        model.fit(X_train, y_train, sample_weight=sw_train)

        pred = model.predict(X_test)
        r2 = r2_score(y_test, pred)
        scores.append(r2)

    # Find best bandwidth
    best_bw_index = np.argmax(scores)
    best_bw = bandwidths[best_bw_index]
    best_score = scores[best_bw_index]

    print(f"Optimal bandwidth: {best_bw} with R2: {best_score:.4f}")
    return best_bw, best_score

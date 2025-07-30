# PyGWML (Geographically Weighted Machine Learning in Python)
Python 3 Based Implementation of Geographically Weighted Machine Learning Models such as:
 - GXGB (Geographically Weighted XGBoost).
 - GWMLP (Geographically Weighted Multi-layer Perceptrons).
 - GWRNN (Geographically Weighted RNN).
   
# Installation
You can directly install it with the command:
```python

$ pip install pygwml

```

# Potential issues and solutions
 - Pygwml requires the pacakge esda as a dependency for computing Moran's Index. We recommend users to install esda 2.5, and then Pygwml can be used smoothly with any additional action. If you use the latest version of esda 2.6, you will need to install matplotlib manually in order to import Pygwml successfully.
 - Libpysal is used specifically for the Incremental Spatial Autocorrelation (ISA) analysis to help find the optimal spatial bandwidth (ISA_op_bw function).  libpysal >= 4.4.0 is needed to be installed for this.

# Example 1: Implementation GXGB Model
Below shows an example on how to fit a GXGB model and use it to make predictions.
```python

from pygwml import GXGB
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

#Instantiate GXGB model with chosen parameters
model = GXGB(band_width=32, kernel="fixed", n_estimators=100, learning_rate=0.1)

#Fit model on training data
model.fit(X_train, y_train, coords_train)

#Predict on test data
local_weight = 0.5  # blend local and global predictions (adjust as needed)
y_pred, y_pred_global, y_pred_local = model.predict(X_test, coords_test, local_weight=local_weight)

#Evaluate performance
print("R2 score (combined):", r2_score(y_test, y_pred))
print("R2 score (global only):", r2_score(y_test, y_pred_global))
print("R2 score (local only):", r2_score(y_test, y_pred_local))

#(Optional) #Get Feature Importances
local_feature_importance=model.get_local_feature_importance()
local_feature_importance=model.global_model.feature_importances_
globally_enhanced_local_feature_importances=model.get_globally_enhanced_local_feature_importances()
```

# Parameters
If you want to learn more about the major parameters in this package, please refer to the Description of Parameters(https://github.com/moin-t/PyGWML/Description_Parameters).


# Authors
 - Moin tariq - AI for Digital Earth Lab, Shandong University, Jinan, China - Email: sci.mointariq@gmail.com, moin.tariq@mail.sdu.edu.cn , moin.bsma1810@iiu.edu.pk
 - Muhammad Irfan Haider Khan - Key Laboratory of Artificial Intelligence, Optics and Electronics (iOPEN), NWPU, Xi’an, Shaanxi, China - Email: vice.haider@gmail.com, irfankhan@mail.nwpu.edu.cn
   
# Project URL:
https://github.com/moin-t/PyGWML

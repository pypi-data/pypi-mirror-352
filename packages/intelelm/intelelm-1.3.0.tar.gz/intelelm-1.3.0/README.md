
<p align="center">
<img style="max-width:100%;" src="https://thieu1995.github.io/post/2023-08/intelelm.png" alt="IntelELM"/>
</p>

---

[![GitHub release](https://img.shields.io/badge/release-1.3.0-yellow.svg)](https://github.com/thieu1995/intelelm/releases)
[![Wheel](https://img.shields.io/pypi/wheel/gensim.svg)](https://pypi.python.org/pypi/intelelm) 
[![PyPI version](https://badge.fury.io/py/intelelm.svg)](https://badge.fury.io/py/intelelm)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/intelelm.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/intelelm.svg)
[![Downloads](https://static.pepy.tech/badge/intelelm)](https://pepy.tech/project/intelelm)
[![Tests & Publishes to PyPI](https://github.com/thieu1995/intelelm/actions/workflows/publish-package.yml/badge.svg)](https://github.com/thieu1995/intelelm/actions/workflows/publish-package.yml)
[![Documentation Status](https://readthedocs.org/projects/intelelm/badge/?version=latest)](https://intelelm.readthedocs.io/en/latest/?badge=latest)
[![Chat](https://img.shields.io/badge/Chat-on%20Telegram-blue)](https://t.me/+fRVCJGuGJg1mNDg1)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8249045.svg)](https://doi.org/10.5281/zenodo.8249045)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


**IntelELM** is an open-source Python library providing a framework for training Extreme Learning Machines (ELM) using 
Metaheuristic Algorithms. It is compatible with Scikit-Learn, enabling easy integration into existing machine learning
pipelines such as hyperparameter tuning, feature selection,...


---

## 🚀 Features

* **Free software:** GNU General Public License (GPL) V3 license
* **Provided Estimator**: `ElmRegressor`, `ElmClassifier`, `MhaElmRegressor`, `MhaElmClassifier`, `AutomatedMhaElmTuner`, `AutomatedMhaElmComparator`
* **Total Optimization-based ELM Regression**: > 200 Models 
* **Total Optimization-based ELM Classification**: > 200 Models
* **Supported datasets**: 54 (47 classifications and 7 regressions)
* **Supported performance metrics**: >= 67 (47 regressions and 20 classifications)
* **Supported objective functions (as fitness functions or loss functions)**: >= 67 (47 regressions and 20 classifications)
* **Documentation:** https://intelelm.readthedocs.io/
* **Python versions:** >= 3.8.x
* **Dependencies:** numpy, scipy, scikit-learn, pandas, mealpy, permetrics


## 📄 Citation Request

If you want to understand how Metaheuristic is applied to Extreme Learning Machine, you need to read the paper 
titled "A new workload prediction model using extreme learning machine and enhanced tug of war optimization". 
The paper can be accessed at the following [this link](https://doi.org/10.1016/j.procs.2020.03.063)


Please include these citations if you plan to use this library:

```bibtex
@article{van2025intelelm,
  title={IntelELM: A python framework for intelligent metaheuristic-based extreme learning machine},
  author={Van Thieu, Nguyen and Houssein, Essam H and Oliva, Diego and Hung, Nguyen Duy},
  journal={Neurocomputing},
  volume={618},
  pages={129062},
  year={2025},
  publisher={Elsevier},
  doi={10.1016/j.neucom.2024.129062}
}

@article{nguyen2020new,
  title={A new workload prediction model using extreme learning machine and enhanced tug of war optimization},
  author={Nguyen, Thieu and Hoang, Bao and Nguyen, Giang and Nguyen, Binh Minh},
  journal={Procedia Computer Science},
  volume={170},
  pages={362--369},
  year={2020},
  publisher={Elsevier},
  doi={10.1016/j.procs.2020.03.063}
}

@article{van2023mealpy,
  title={MEALPY: An open-source library for latest meta-heuristic algorithms in Python},
  author={Van Thieu, Nguyen and Mirjalili, Seyedali},
  journal={Journal of Systems Architecture},
  year={2023},
  publisher={Elsevier},
  doi={10.1016/j.sysarc.2023.102871}
}
```

## 📦 Installation

# Installation

Install the latest version from PyPI:

```bash
$ pip install intelelm
```

Check installed version:

```bash
$ python
>>> import intelelm
>>> intelelm.__version__
```

## 📚 Documentation & Tutorials

- **Documentation:** [https://intelelm.readthedocs.io/en/latest/](https://intelelm.readthedocs.io/en/latest/)
- **Tutorials:**
  - [Handwritten Digits Classification](./tutorials/example_hand_written_digits.ipynb)
  - [California Housing Price Regression](./tutorials/example_california_housing.ipynb)


## 🧪 Example Usage

* In this section, we will explore the usage of the IntelELM model with the assistance of a dataset. While all the 
preprocessing steps mentioned below can be replicated using Scikit-Learn, we have implemented some utility functions 
to provide users with convenience and faster usage.


```python
### Step 1: Importing the libraries
from intelelm import ElmRegressor, ElmClassifier, MhaElmRegressor, MhaElmClassifier, get_dataset

#### Step 2: Reading the dataset
data = get_dataset("aniso")

#### Step 3: Next, split dataset into train and test set
data.split_train_test(test_size=0.2, shuffle=True, random_state=100)

#### Step 4: Feature Scaling
data.X_train, scaler_X = data.scale(data.X_train, scaling_methods=("standard", "minmax"))
data.X_test = scaler_X.transform(data.X_test)

data.y_train, scaler_y = data.encode_label(data.y_train)   # This is for classification problem only
data.y_test = scaler_y.transform(data.y_test)

#### Step 5: Fitting ELM-based model to the dataset

##### 5.1: Use standard ELM model for regression problem
regressor = ElmRegressor(layer_sizes=(10, ), act_name="relu", seed=42)
regressor.fit(data.X_train, data.y_train)

##### 5.2: Use standard ELM model for classification problem 
classifer = ElmClassifier(layer_sizes=(10, ), act_name="tanh", seed=42)
classifer.fit(data.X_train, data.y_train)

##### 5.3: Use Metaheuristic-based ELM model for regression problem
print(MhaElmClassifier.SUPPORTED_OPTIMIZERS)
print(MhaElmClassifier.SUPPORTED_REG_OBJECTIVES)
opt_paras = {"name": "GA", "epoch": 10, "pop_size": 30}
regressor = MhaElmRegressor(layer_sizes=(10, ), act_name="elu", obj_name="RMSE", 
                            optim="BaseGA", optim_params=opt_paras, seed=42,
                            lb=None, ub=None, mode='single', n_workers=None, termination=None)
regressor.fit(data.X_train, data.y_train)

##### 5.4: Use Metaheuristic-based ELM model for classification problem
print(MhaElmClassifier.SUPPORTED_OPTIMIZERS)
print(MhaElmClassifier.SUPPORTED_CLS_OBJECTIVES)
opt_paras = {"name": "GA", "epoch": 10, "pop_size": 30}
classifier = MhaElmClassifier(layer_sizes=(10, ), act_name="elu", obj_name="KLDL", 
                              optim="BaseGA", optim_params=opt_paras, seed=42,
                              lb=None, ub=None, mode='single', n_workers=None, termination=None)
classifier.fit(data.X_train, data.y_train)

#### Step 6: Predicting a new result
y_pred = regressor.predict(data.X_test)

y_pred_cls = classifier.predict(data.X_test)
y_pred_label = scaler_y.inverse_transform(y_pred_cls)

#### Step 7: Calculate metrics using score or scores functions.
print("Try my AS metric with score function")
print(regressor.score(data.X_test, data.y_test, method="AS"))

print("Try my multiple metrics with scores function")
print(classifier.scores(data.X_test, data.y_test, list_methods=["AS", "PS", "F1S", "CEL", "BSL"]))

print("Try my evaluate functions")
print(regressor.evaluate(data.y_test, y_pred, list_metrics=("RMSE", "MAE", "MAPE", "NSE", "R2")))

#### Save results
regressor.save_loss_train(save_path="history", filename="loss_train.csv")
regressor.save_metrics(data.y_test, y_pred, list_metrics=("R2", "MAPE", "MAE", "MSE"), save_path="history", filename="metrics.csv")
```

A real-world dataset contains features that vary in magnitudes, units, and range. We would suggest performing 
normalization when the scale of a feature is irrelevant or misleading. Feature Scaling basically helps to normalize 
the data within a particular range.

---

## ❓ FAQ

### 1. How to list supported objective metrics?

Where do I find the supported metrics like above ["AS", "PS", "RS"]. What is that?
You can find it here: https://github.com/thieu1995/permetrics or use this

```python
from intelelm import MhaElmClassifier, MhaElmRegressor

print(MhaElmRegressor.SUPPORTED_REG_OBJECTIVES)
print(MhaElmClassifier.SUPPORTED_CLS_OBJECTIVES)
```

### 2. ValueError: Existed at least one new label in y_pred?
I got this type of error
```python
raise ValueError("Existed at least one new label in y_pred.")
ValueError: Existed at least one new label in y_pred.
``` 
How to solve this?

+ This occurs only when you are working on a classification problem with a small dataset that has many classes. For 
  instance, the "Zoo" dataset contains only 101 samples, but it has 7 classes. If you split the dataset into a 
  training and testing set with a ratio of around 80% - 20%, there is a chance that one or more classes may appear 
  in the testing set but not in the training set. As a result, when you calculate the performance metrics, you may 
  encounter this error. You cannot predict or assign new data to a new label because you have no knowledge about the 
  new label. There are several solutions to this problem.

- **1st: Use SMOTE to rebalance the dataset:**
- 
Use the SMOTE method to address imbalanced data and ensure that all classes have the same number of samples.

```python
import pandas as pd
from imblearn.over_sampling import SMOTE
from intelelm import Data

dataset = pd.read_csv('examples/dataset.csv', index_col=0).values
X, y = dataset[:, 0:-1], dataset[:, -1]

X_new, y_new = SMOTE().fit_resample(X, y)
data = Data(X_new, y_new)
```

- **2st: Try changing `random_state` in split_train_test:**

- Use different random_state numbers in split_train_test() function.

```python
import pandas as pd
from intelelm import Data

dataset = pd.read_csv('examples/dataset.csv', index_col=0).values
X, y = dataset[:, 0:-1], dataset[:, -1]
data = Data(X, y)
data.split_train_test(test_size=0.2, random_state=10)  # Try different random_state value 
```

### 3. Why don't MHA-based ELM models improve results?

When testing several algorithms based on Extreme Learning Machines (ELM), they all produce the same results. 
   Even during the training process, the global best solution remains unchanged.

+ This issue was identified in version <= v1.0.2 when the default values for the lower bound (lb) and upper bound 
  (ub) were set in the narrow range of (-1, 1). This limited range proved to be too small, causing all algorithms to 
  converge to local optima. Fortunately, this problem has been addressed in versions > v1.0.3, where the default 
  range has been extended to (-10., 10.). You also can define your own lb and ub ranges depend on your problem.
+ In traditional neural network like MLP, they weights (weights + biases) are typically initialized within the range 
  of (-1., 1.). However, during training using gradient-based methods, these values are updated, and there are no 
  strict bounds on them.
+ Meanwhile, in metaheuristic optimization, it's necessary to set boundaries for decision variables (weights) each 
  time a new search agent is formed. Therefore, if you define a narrow range, your optimizer may converge more 
  quickly, but it's more likely to get stuck in local optima (which explains why the global best value remains 
  unchanged during training). Moreover, in some cases, there might not even be a global optimum within that narrow 
  range. Conversely, if you set a wider range, the optimization process may be slower, and the global best value may 
  change more gradually. In such cases, you might need to increase the number of epochs, perhaps up to 1000, for the 
  optimizer to explore the solution space thoroughly.

```python
from intelelm import MhaElmClassifier

opt_paras = {"name": "GA", "epoch": 30, "pop_size": 30}
model = MhaElmClassifier(layer_sizes=(10, ), act_name="elu", obj_name="KLDL", 
                         optim="BaseGA", optim_params=opt_paras, verbose=True, seed=42,
                         lb=-10., ub=10., mode='single', n_workers=None, termination=None)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

## 🔗 Useful Links

- 📦 [Source Code](https://github.com/thieu1995/intelelm)
- 📖 [Documentation](https://intelelm.readthedocs.io/)
- ⬇️ [PyPI Releases](https://pypi.org/project/intelelm/)
- ❗ [Report Issues](https://github.com/thieu1995/intelelm/issues)
- 📝 [Changelog](https://github.com/thieu1995/MetaPerceptron/blob/master/ChangeLog.md)
- 💬 [Chat Group](https://t.me/+fRVCJGuGJg1mNDg1)


## 🤝 Related Projects

- [MEALPY](https://github.com/thieu1995/mealpy)
- [Metaheuristics](https://github.com/thieu1995/metaheuristics)
- [Opfunu](https://github.com/thieu1995/opfunu)
- [Enoppy](https://github.com/thieu1995/enoppy)
- [Permetrics](https://github.com/thieu1995/permetrics)
- [MetaCluster](https://github.com/thieu1995/MetaCluster)
- [Pfevaluator](https://github.com/thieu1995/pfevaluator)
- [AIIR Team](https://github.com/aiir-team)


---

Developed by: [Thieu](mailto:nguyenthieu2102@gmail.com?Subject=IntelELM_QUESTIONS) @ 2023

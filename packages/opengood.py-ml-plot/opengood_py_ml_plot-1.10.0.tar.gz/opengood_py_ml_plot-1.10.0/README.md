# Python Machine Learning (ML) Plot

[![Build](https://github.com/opengood-aio/py-ml-plot/workflows/build/badge.svg)](https://github.com/opengood-aio/py-ml-plot/actions?query=workflow%3Abuild)
[![Release](https://github.com/opengood-aio/py-ml-plot/workflows/release/badge.svg)](https://github.com/opengood-aio/py-ml-plot/actions?query=workflow%3Arelease)
[![CodeQL](https://github.com/opengood-aio/py-ml-plot/actions/workflows/codeql.yml/badge.svg)](https://github.com/opengood-aio/py-ml-plot/actions/workflows/codeql.yml)
[![Codecov](https://codecov.io/gh/opengood-aio/py-ml-plot/graph/badge.svg?token=WX6Er5S6Vj)](https://codecov.io/gh/opengood-aio/py-ml-plot)
[![Release Version](https://img.shields.io/github/release/opengood-aio/py-ml-plot.svg)](https://github.com/opengood-aio/py-ml-plot/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/opengood.py-ml-plot)](https://pypi.org/project/opengood.py-ml-plot/)
![Python](https://img.shields.io/pypi/pyversions/opengood.py-ml-plot)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/opengood-aio/py-ml-plot/master/LICENSE)

Modules containing reusable functions for machine learning visualization
plotting

## Compatibility

*  Python 3.13 or later

## Setup

### Add Dependency

```bash
python3 -m pip install opengood.py-ml-plot
```

**Note:** See *Release* version badge above for latest version.

## Features

### Classification Model Plotting

Display a classification model results visualization:

```python
import pandas as pd
from matplotlib.colors import ListedColormap
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from opengood.py_ml_plot import display_classification_plot

dataset = pd.read_csv("data.csv")
x = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

x_train, _, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

sc = StandardScaler()
x_train = sc.fit_transform(x_train)

classifier = LogisticRegression(random_state=0)
classifier.fit(x_train, y_train)

display_classification_plot(
    x_train,
    y_train,
    sc,
    classifier,
    ListedColormap(("salmon", "dodgerblue")),
    "Logistic Regression (Training Set)",
    "Age",
    "Estimated Salary",
)
```

---

# Development

## Python Virtual Environment

Create Python virtual environment:

```bash
cd ~/workspace/opengood-aio/py-ml-plot/.venv
python3 -m venv ~/workspace/opengood-aio/py-ml-plot/.venv
source .venv/bin/activate
```

## Install Packages

```bash
python3 -m pip install matplotlib
python3 -m pip install numpy
python3 -m pip install pandas
python3 -m pip install scikit-learn
```

## Create Requirements File

```bash
pip freeze > requirements.txt
```

## Run Tests

```bash
python -m pytest tests/
```


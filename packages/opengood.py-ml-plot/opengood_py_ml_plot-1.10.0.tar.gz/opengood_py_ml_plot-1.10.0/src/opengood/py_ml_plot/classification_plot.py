import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def display_classification_plot(
    x,
    y,
    feature_scaler: StandardScaler,
    classifier: LogisticRegression,
    cmap: ListedColormap,
    title,
    x_label,
    y_label,
):
    x_set, y_set = feature_scaler.inverse_transform(x), y
    x1, x2 = np.meshgrid(
        np.arange(start=x_set[:, 0].min() - 10, stop=x_set[:, 0].max() + 10, step=0.25),
        np.arange(
            start=x_set[:, 1].min() - 1000, stop=x_set[:, 1].max() + 1000, step=0.25
        ),
    )
    plt.contourf(
        x1,
        x2,
        classifier.predict(
            feature_scaler.transform(np.array([x1.ravel(), x2.ravel()]).T)
        ).reshape(x1.shape),
        alpha=0.75,
        cmap=cmap,
    )
    plt.xlim(x1.min(), x1.max())
    plt.ylim(x2.min(), x2.max())
    for i, j in enumerate(np.unique(y_set)):
        plt.scatter(x_set[y_set == j, 0], x_set[y_set == j, 1], c=cmap(i), label=j)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.show()
    return True

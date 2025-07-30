import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

X = np.linspace(-3, 3, 100)
y = np.sin(X) + np.random.normal(scale=.1, size=X.shape) # --> adding noise to the data

tau = 0.2 
y_pred = lowess(y, X, frac=tau, it=3)[:,1]

plt.scatter(X, y, label="Data", color='blue', alpha=.6)
plt.plot(X, y_pred, label=f"LOWESS (τ={tau} ", color='red', linewidth=2)
plt.xlabel("X")
plt.ylabel("y")
plt.legend()
plt.title("Locally weighted Regression")
plt.show()



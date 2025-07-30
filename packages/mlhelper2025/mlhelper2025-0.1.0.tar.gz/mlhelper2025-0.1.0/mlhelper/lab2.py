import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_california_housing


data = fetch_california_housing()

df = pd.DataFrame(data.data, columns=data.feature_names)

corr_matrix = df.corr()

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title("Correlation Matrix Heatmap")
plt.show()

sns.pairplot(df)
plt.title("Pairplot")
plt.show()
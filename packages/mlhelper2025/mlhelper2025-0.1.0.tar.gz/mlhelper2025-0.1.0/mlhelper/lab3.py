from sklearn.datasets import load_iris
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

data = load_iris()

df = pd.DataFrame(data.data, columns=data.feature_names)


df["Target"] = data.target

scatter = plt.scatter(df['sepal width (cm)'], df['sepal length (cm)'], c=df['Target'], cmap='viridis', edgecolor='k', alpha=0.7)
plt.legend(handles=scatter.legend_elements()[0], labels=list(data.target_names))


scaler = StandardScaler()
x_scaled = scaler.fit_transform(df.iloc[:,:-1])

pca = PCA(n_components=2)
x_pca = pca.fit_transform(x_scaled)


df2 = pd.DataFrame(x_pca, columns=["PC1", "PC2"])

explained_variance = pca.explained_variance_ratio

plt.figure(figsize=(8, 6))
scatter = plt.scatter(df2['PC1'], df2['PC2'], c=df['Target'], cmap='viridis', edgecolor='k', alpha=0.7)
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("PCA - Iris Dataset reduced to 2D")
plt.legend(handles=scatter.legend_elements()[0], labels=list(data.target_names))
plt.show()
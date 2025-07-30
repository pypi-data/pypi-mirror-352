#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, classification_report


# In[2]:


data = load_breast_cancer()
X = data.data # Features
y = data.target # True labels (0 = Malignant, 1 = Benign)


# In[3]:


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# In[4]:


kmeans = KMeans(n_clusters=2, random_state=42, n_init=10) # Fix warning by setting
n_init=10
y_kmeans = kmeans.fit_predict(X_scaled)


# In[5]:


print("Confusion Matrix:")
print(confusion_matrix(y, y_kmeans))


# In[6]:


print("\nClassification Report:")
print(classification_report(y, y_kmeans))


# In[7]:


pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)


# In[8]:


df = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])
df['Cluster'] = y_kmeans # Clustering result
df['True Label'] = y # Actual labels


# In[9]:


plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='PC1', y='PC2', hue='Cluster', palette='Set1', s=100,
edgecolor='black', alpha=0.7)
plt.title('K-Means Clustering of Breast Cancer Dataset')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend(title="Cluster")
plt.show()


# In[10]:


plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='PC1', y='PC2', hue='True Label', palette='coolwarm', s=100,
edgecolor='black', alpha=0.7)
plt.title('True Labels of Breast Cancer Dataset')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend(title="True Label")
plt.show()


# In[11]:


plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='PC1', y='PC2', hue='Cluster', palette='Set1', s=100,
edgecolor='black', alpha=0.7)
centers = pca.transform(kmeans.cluster_centers_) # Transform cluster centers to PCA space
plt.scatter(centers[:, 0], centers[:, 1], s=200, c='red', marker='X', label='Centroids')
plt.title('K-Means Clustering with Centroids')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend(title="Cluster")
plt.show()


# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from sklearn.datasets import fetch_olivetti_faces
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt


# In[2]:


data = fetch_olivetti_faces(shuffle=True, random_state=42)
X = data.data
y = data.target


# In[3]:


index = 36
image = X[index].reshape(64, 64)       
label = y[index]

plt.imshow(image, cmap='gray')
plt.title(f"Label: {label}")


# In[4]:


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


# In[5]:


model = GaussianNB()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)


# In[6]:


accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of Naive Bayes Classifier on Olivetti Faces: {accuracy * 100:.2f}%")


# In[7]:


num_samples = 5
print("\nTesting on a few samples:")
for i in range(num_samples):
    index = np.random.randint(0, len(X_test))
    sample = X_test[index].reshape(1, -1)
    image = X_test[index].reshape(64,64)
    true_label = y_test[index]
    predicted_label = model.predict(sample)[0]

    plt.subplots(figsize=(6,8))
    plt.imshow(image, cmap='gray')
    plt.title(f"Predicted Label: {predicted_label}")
    plt.axis('off')
    print(f"Sample {i+1} and Index {index}: True Label = {true_label}, Predicted Label = {predicted_label}")


# In[ ]:





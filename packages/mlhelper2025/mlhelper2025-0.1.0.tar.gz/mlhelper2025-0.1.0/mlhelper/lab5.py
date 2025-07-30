#!/usr/bin/env python
# coding: utf-8

# In[63]:


import pandas as pd
from sklearn.datasets import load_iris
import numpy as np
import matplotlib.pyplot as plt
from mlxtend.plotting import plot_decision_regions

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import confusion_matrix


# In[64]:


data = load_iris()
data


# In[65]:


df = pd.DataFrame(data.data, columns=data.feature_names)
df


# In[66]:


df["target"] = data.target
df


# In[67]:


X = df.iloc[:,:-1].values
y = df.iloc[:,-1].values
X,y


# In[68]:


scatter = plt.scatter(df['sepal width (cm)'], df['sepal length (cm)'], c=df['target'], cmap='coolwarm', edgecolor='k', alpha=0.7)
plt.legend(handles=scatter.legend_elements()[0], labels=list(data.target_names))


# In[69]:


X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=21,test_size=0.3)


# In[70]:


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

X_train_scaled


# In[71]:


import math
math.sqrt(len(y_train))


# In[72]:


classifier = KNeighborsClassifier(n_neighbors=11,metric='euclidean')


# In[73]:


classifier.fit(X_train,y_train)


# In[74]:


y_pred = classifier.predict(X_test)
y_pred


# In[75]:


cm = confusion_matrix(y_test,y_pred)
print(cm)


# In[76]:


print(accuracy_score(y_test,y_pred))


# In[77]:


y_test


# In[78]:


y_pred



import pandas as pd

df = pd.read_csv("./find_s.csv")
df


# In[22]:


attributes = df.iloc[:,:-1].values
target = df.iloc[:,-1].values


# In[23]:


hypothesis = None
for i , val in enumerate(target):
    if val.lower() == "yes":
        hypothesis = attributes[i].copy()
        break
    if hypothesis is None:
        print("No +ve instances")

print(f"Initial Hypothesis: {hypothesis}")


# In[24]:


for i in range(len(attributes)):
    if target[i].lower() == "yes":
        for j in range(len(hypothesis)):
            if hypothesis[j] != attributes[i][j]:
                hypothesis[j] = "?"
        print(hypothesis)

print(f"\nFinal Hypothesis: {hypothesis}")


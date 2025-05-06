import pandas as pd
df = pd.read_csv("cleaned.csv")


# print(df.head(), df.columns)

# new columns
df.columns = [
    'Country', 'GDP_Growth', 'Interest_Rate', 'Inflation_Rate', 'Unemployment_Rate',
    'Debt_to_GDP', 'Current_Account_to_GDP', 'Credit_Rating'
]


# df['Credit_Rating'].unique()
non_speculative = {
    'Aaa', 'Aa1', 'Aa2', 'Aa3', 'A1', 'A2', 'A3', 'Baa1', 'Baa2', 'Baa3',
    'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-'
}

df['Investment_Worthy'] = df['Credit_Rating'].apply(lambda x: 1 if x in non_speculative else 0) # non spec -> 1

#labeled 1 vs 0
# print(df['Investment_Worthy'].value_counts()) 


from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
# import numpy as np


valid_rows = ~df['Credit_Rating'].isin(['NR', 'SD', 'D', ''])
train_df = df[valid_rows].copy()
predict_df = df[~valid_rows].copy()


features = ['GDP_Growth', 'Interest_Rate', 'Inflation_Rate', 'Unemployment_Rate',
            'Debt_to_GDP', 'Current_Account_to_GDP']
X = train_df[features]
y = train_df['Investment_Worthy']

#scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, stratify=y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
X_predict = scaler.transform(predict_df[features])
predicted_labels = model.predict(X_predict)

df.loc[predict_df.index, 'Investment_Worthy'] = predicted_labels


predicted_df = df.loc[predict_df.index, ['Country', 'Investment_Worthy']]
print(df)


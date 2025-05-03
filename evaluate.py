import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report


df = pd.read_csv("cleaned.csv")

#encode credit ratings
rating_map = {
    'AAA': 7, 'AA+': 6, 'AA': 5, 'AA-': 4,
    'A+': 3, 'A': 2, 'A-': 1, 'BBB+': 0,
    'BBB': -1, 'BBB-': -2, 'BB+': -3, 'BB': -4,
    'BB-': -5, 'B+': -6, 'B': -7, 'B-': -8,
    'CCC+': -9, 'CCC': -10, 'CCC-': -11, 'CC': -12,
    'C': -13, 'D': -14, 'NR': -15
}
df['Credit Rating Score'] = df['Credit Rating'].map(rating_map)

#investment-worthiness
def is_good_investment(row):
    return (
        row['GDP Growth (%)'] >= 1.5 and
        0 < row['Inflation Rate (%)'] <= 4 and
        0 <= row['Interest Rate (%)'] <= 6 and
        row['Unemployment Rate (%)'] <= 5 and
        row['Government Debt to GDP (%)'] <= 70 and
        row['Current Account to GDP (%)'] >= 0 and
        row['Credit Rating Score'] >= 2
    )

df['Investment Worthy'] = df.apply(is_good_investment, axis=1).astype(int)


features = [
    'GDP Growth (%)', 'Inflation Rate (%)', 'Interest Rate (%)',
    'Unemployment Rate (%)', 'Government Debt to GDP (%)',
    'Current Account to GDP (%)', 'Credit Rating Score'
]
X = df[features]
y = df['Investment Worthy']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))


df['Investment Score'] = model.predict_proba(X)[:, 1]  # Probability of being "Good"
best_countries = df[df['Investment Score'] > 0.8].sort_values(by='Investment Score', ascending=False)

print("Top Countries for Investment:\n")
print(best_countries[['Country', 'Investment Score']])

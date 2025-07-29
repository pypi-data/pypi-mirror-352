import pandas as pd
from sklearn.preprocessing import StandardScaler

def handle_missing_values(df):
    return df.fillna(df.median(numeric_only=True))

def scale_features(df):
    scaler = StandardScaler()
    numeric = df.select_dtypes(include=['number'])
    df[numeric.columns] = scaler.fit_transform(numeric)
    return df

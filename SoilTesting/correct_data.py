import pandas as pd

# File paths
input_path = r"e:\SRI PROJECT\AgriMitraAI\SoilTesting\data\dataset1.csv"
output_path = r"e:\SRI PROJECT\AgriMitraAI\SoilTesting\data\dataset1.csv"

try:
    print(f"Reading data from {input_path}...")
    df = pd.read_csv(input_path)

    # Logic: 
    # Output 0 -> Low
    # Output 1 -> Medium
    # Output 2 -> High
    
    mapping = {
        0: 'Low',
        1: 'Medium',
        2: 'High'
    }

    # Apply mapping
    print("Updating Soil_Fertility column...")
    df['Soil_Fertility'] = df['Output'].map(mapping)

    # Verify no NaN values were created (in case of unexpected Output values)
    if df['Soil_Fertility'].isnull().any():
        print("Warning: Some Output values were not 0, 1, or 2. Filling with 'Unknown'.")
        df['Soil_Fertility'] = df['Soil_Fertility'].fillna('Unknown')

    # Save
    df.to_csv(output_path, index=False)
    print(f"Success! file saved to {output_path}")
    print("\nSample check:")
    print(df[['Output', 'Soil_Fertility']].head(10))
    print(df[['Output', 'Soil_Fertility']].tail(10))

except Exception as e:
    print(f"Error: {e}")

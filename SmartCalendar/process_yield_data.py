import pandas as pd
import json
import os

def process_yield_to_json(csv_path, output_json_path):
    print(f"Reading Yield CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Strip whitespace from string columns
    df['Crop'] = df['Crop'].str.strip()
    df['State'] = df['State'].str.strip()
    df['Season'] = df['Season'].str.strip()
    
    # Calculate fertilizer per area since the CSV seems to have totals
    df['Fertilizer_per_Area'] = df['Fertilizer'] / df['Area']
    
    # Group by State, Crop, Season
    summary = df.groupby(['State', 'Crop', 'Season']).agg({
        'Yield': 'mean',
        'Annual_Rainfall': 'mean',
        'Fertilizer_per_Area': 'mean'
    }).reset_index()
    
    # Build nested dictionary
    # { State: { Crop: { Season: { data } } } }
    patterns = {}
    for _, row in summary.iterrows():
        state = row['State']
        crop = row['Crop']
        season = row['Season']
        
        if state not in patterns:
            patterns[state] = {}
        if crop not in patterns[state]:
            patterns[state][crop] = {}
            
        patterns[state][crop][season] = {
            "avg_yield": round(row['Yield'], 3),
            "avg_rainfall": round(row['Annual_Rainfall'], 1),
            "avg_fertilizer_intensity": round(row['Fertilizer_per_Area'], 2)
        }
    
    # Save as JSON
    with open(output_json_path, 'w') as f:
        json.dump(patterns, f, indent=4)
        
    print(f"Yield patterns saved to: {output_json_path}")
    print(f"Processed {len(summary)} state-crop-season combinations.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yield_csv = r"E:\SRI PROJECT\AgriMitraAI\SmartCalendar\data\crop_yield.csv"
    output_yield_json = os.path.join(current_dir, "data", "crop_yield_patterns.json")
    
    process_yield_to_json(yield_csv, output_yield_json)

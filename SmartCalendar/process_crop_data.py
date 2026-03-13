import pandas as pd
import json
import os

def process_csv_to_json(csv_path, output_json_path):
    print(f"Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Calculate group statistics (mean) for each crop label
    # We use mean as the representative value, but could also include min/max
    summary = df.groupby('label').agg({
        'N': ['mean', 'min', 'max'],
        'P': ['mean', 'min', 'max'],
        'K': ['mean', 'min', 'max'],
        'temperature': ['mean', 'min', 'max'],
        'humidity': ['mean', 'min', 'max'],
        'ph': ['mean', 'min', 'max'],
        'rainfall': ['mean', 'min', 'max']
    })
    
    # Flatten multi-index columns
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    
    # Convert to dictionary
    data_dict = summary.to_dict(orient='index')
    
    # Clean up the dictionary keys and values for better AI prompt integration
    processed_data = {}
    for crop, metrics in data_dict.items():
        processed_data[crop] = {
            "npk": {
                "Nitrogen": round(metrics['N_mean'], 2),
                "Phosphorous": round(metrics['P_mean'], 2),
                "Potassium": round(metrics['K_mean'], 2)
            },
            "environment": {
                "Temperature_range": f"{round(metrics['temperature_min'], 1)}-{round(metrics['temperature_max'], 1)}°C",
                "Humidity_range": f"{round(metrics['humidity_min'], 1)}-{round(metrics['humidity_max'], 1)}%",
                "pH_range": f"{round(metrics['ph_min'], 1)}-{round(metrics['ph_max'], 1)}",
                "Rainfall_ideal": f"{round(metrics['rainfall_mean'], 1)}mm"
            }
        }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    
    # Save as JSON
    with open(output_json_path, 'w') as f:
        json.dump(processed_data, f, indent=4)
        
    print(f"JSON data saved to: {output_json_path}")
    print(f"Processed {len(processed_data)} crops.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = r"E:\SRI PROJECT\AgriMitraAI\CropRecommendationSystem\Crop_recommendation.csv"
    output_file = os.path.join(current_dir, "data", "crop_requirements.json")
    
    process_csv_to_json(csv_file, output_file)


import pytest
import json
from api import app

def test_chat_endpoint():
    client = app.test_client()
    
    # Mock context data (similar to what /predict would return)
    context = {
        'recommended_crop': 'Rice',
        'confidence': '95.5%',
        'N': 80,
        'P': 40,
        'K': 40,
        'temperature': 26, # Celsius
        'humidity': 82, # %
        'ph': 6.5,
        'rainfall': 200 # mm
    }
    
    # Payload
    payload = {
        'message': 'Why is Rice recommended for my soil?',
        'context': context,
        'history': []
    }
    
    # Send request
    response = client.post('/chat', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    print("\n\n--- RESPONSE STATUS ---")
    print(response.status_code)
    
    print("\n--- RESPONSE BODY ---")
    data = response.get_json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert 'reply' in data
    
    # Test low confidence warning
    context['confidence'] = '40.0%'
    payload['context'] = context
    response_low_conf = client.post('/chat', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    print("\n--- LOW CONFIDENCE RESPONSE ---")
    print(json.dumps(response_low_conf.get_json(), indent=2))

if __name__ == "__main__":
    test_chat_endpoint()

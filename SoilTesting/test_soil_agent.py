
import sys
import os

# Add the directory to sys.path to import modules
sys.path.append(r"e:\SRI PROJECT\AgriMitraAI\SoilTesting")

from soil_agent import SoilAgent

def test_soil_agent():
    print("Initializing SoilAgent...")
    try:
        agent = SoilAgent()
        print("SoilAgent initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize SoilAgent: {e}")
        return

    # Sample context
    context = {
        "soil_type": "Clay",
        "fertility": "Medium",
        "input_params": {"N": 50, "P": 40, "K": 30, "pH": 6.5}
    }
    
    user_message = "What crops are suitable for this soil?"
    
    print("\n--- Testing Response Generation ---")
    print(f"User Message: {user_message}")
    print(f"Context: {context}")
    
    try:
        response = agent.generate_response(user_message, context)
        print("\n--- Agent Response ---")
        print(response)
        print("\n----------------------")
    except Exception as e:
        print(f"Failed to generate response: {e}")

if __name__ == "__main__":
    test_soil_agent()

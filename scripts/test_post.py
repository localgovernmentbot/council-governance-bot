import os
from atproto import Client

def test_bluesky_connection():
    """Test if we can connect to BlueSky"""
    
    # Get credentials from environment variables
    handle = os.environ.get('BLUESKY_HANDLE')
    password = os.environ.get('BLUESKY_PASSWORD')
    
    if not handle or not password:
        print("❌ Missing BlueSky credentials!")
        return False
    
    try:
        # Create client and login
        client = Client()
        client.login(handle, password)
        print("✅ Successfully connected to BlueSky!")
        
        # Post a test message
        client.send_post(text="🏛️ LocalGovernmentBot is being set up! This is a test post.")
        print("✅ Test post sent!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_bluesky_connection()
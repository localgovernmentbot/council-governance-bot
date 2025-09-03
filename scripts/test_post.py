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
        print("✅ Successfully authenticated to BlueSky (no post sent)")
        
        # Optional: fetch your own profile as a harmless check
        try:
            me = client.me
            print(f"Account: {me.did}")
        except Exception:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_bluesky_connection()

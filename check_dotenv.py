try:
    from dotenv import load_dotenv
    print("python-dotenv is installed")

    # Try to load .env file
    load_dotenv()
    print("Successfully loaded .env file")

    # Print environment variables
    import os
    print(f"FLASK_APP: {os.environ.get('FLASK_APP')}")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")
except ImportError:
    print("python-dotenv is not installed")
except Exception as e:
    print(f"Error: {str(e)}")

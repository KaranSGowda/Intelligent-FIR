try:
    from werkzeug.utils import secure_filename
    print(f"✅ Successfully imported werkzeug.utils.secure_filename")

    # Test the secure_filename function
    test_filename = "my file with spaces & special chars.txt"
    secure_name = secure_filename(test_filename)
    print(f"Original filename: {test_filename}")
    print(f"Secure filename: {secure_name}")
except ImportError as e:
    print(f"❌ Error importing werkzeug.utils: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

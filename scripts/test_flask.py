try:
    import flask
    print(f"Flask is installed. Version: {flask.__version__}")
except ImportError as e:
    print(f"Error importing Flask: {e}")

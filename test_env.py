import sys
sys.path.insert(0, r"f:\major stock market")

try:
    from backend.main import app
    print("SUCCESS: All imports resolved")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


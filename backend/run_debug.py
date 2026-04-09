import uvicorn
import os
import sys

# Ensure project root is in path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

print(f"DEBUG: sys.path: {sys.path}")
import backend1.main
print(f"DEBUG: backend1.main file: {backend1.main.__file__}")
print(f"DEBUG: Routes in app: {[r.path for r in backend1.main.app.routes]}")

if __name__ == "__main__":
    uvicorn.run("backend1.main:app", host="0.0.0.0", port=8000, reload=False)

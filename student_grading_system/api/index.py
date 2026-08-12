import sys
import os

# Add directory to sys.path so app.py can be imported seamlessly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
except ImportError:
    from api.app import app

if __name__ == '__main__':
    app.run(debug=True)

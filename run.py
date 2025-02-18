import os
from src.app import app
from dotenv import load_dotenv
load_dotenv()

PORT = os.getenv('PORT')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=PORT)
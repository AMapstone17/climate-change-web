
from dotenv import load_dotenv

from flaskapp import create_app

load_dotenv('.env.local')
app = create_app(None)

if __name__ == '__main__':
    app.run()

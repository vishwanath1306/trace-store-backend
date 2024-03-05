from init import initialize_flask_app
from models import database
from flask_migrate import Migrate

app = initialize_flask_app(__name__)
migrate = Migrate(app, database)

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
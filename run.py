from app import create_app, Config
from app.models import db


app = create_app(Config)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

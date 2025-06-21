from app import create_app, db
from app.models import User, Roaster, Bean

app = create_app()

with app.app_context():
    print("=== Users ===")
    for user in User.query.all():
        print(user)

    print("\n=== Roasters ===")
    for roaster in Roaster.query.all():
        print(roaster.to_dict())

    print("\n=== Beans ===")
    for bean in Bean.query.all():
        print(bean.to_dict())

import datetime
import os
from sqlalchemy.orm import Session
from services.db_service import Base, engine
from models import User, Target, Measurement, Role
from auth import Hash


def create_test_entities():
    admin_role = Role(id=1, role_type="admin")
    premium_role = Role(id=2, role_type="premium")
    user_role = Role(id=3, role_type="user")
    test_admin_user = User(
        id=1, username="test_admin", role_id=1, email="admin@test.com", password=Hash.bcrypt("admin"), targets=[],
        height=166.5,
        weight=80
    )
    test_user = User(
        id=2, username="test_user", role_id=3, email="user@test.com", password=Hash.bcrypt("user"), targets=[],
        height=166.5,
        weight=80
    )
    test_target_for_admin = Target(
        id=1, user_id=1, name="test_individual_target", target_weight=65,
        end_date=datetime.date(2010, 10, 31),
        start_date=datetime.date(2010, 10, 1), reached=False, public=False, measurements=[]
    )
    test_target_for_user = Target(
        id=2, user_id=2, name="test_individual_target", target_weight=65,
        end_date=datetime.date(2010, 10, 31),
        start_date=datetime.date(2010, 10, 1), reached=False, public=False, measurements=[]
    )

    test_measurement = Measurement(
        id=1, target_id=1, weight=78.5, measurement_date=datetime.date(2010, 10, 1)
    )

    with Session(engine) as session:
        session.add(admin_role)
        session.add(premium_role)
        session.add(user_role)
        session.add(test_admin_user)
        session.add(test_user)
        session.add(test_target_for_admin)
        session.add(test_target_for_user)
        session.add(test_measurement)
        session.commit()


if __name__ == '__main__': # Works with app-test docker service
    db_path = os.getenv("DATABASE_URL").split('///')[1]  # DATABASE_URL: sqlite:///. ...
    if not os.path.exists(db_path):
        Base.metadata.create_all(bind=engine)
        create_test_entities()

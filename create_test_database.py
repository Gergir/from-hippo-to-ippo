import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from services.db_service import engine
from models import User, Target, Measurement, Role
from auth import Hash


def create_test_entities():
    admin_role = Role(id=1, role_type="admin")
    premium_role = Role(id=2, role_type="premium")
    user_role = Role(id=3, role_type="user")
    test_user = User(
        id=1, username="test_admin", role_id=1, email="test@test.com", password=Hash.bcrypt("test"), targets=[],
        height=166.5,
        weight=80
    )
    test_target = Target(
        id=1, user_id=1, name="test_target", target_weight=65,
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
        session.add(test_user)
        session.add(test_target)
        session.add(test_measurement)
        session.commit()


if __name__ == '__main__':
        create_test_entities()

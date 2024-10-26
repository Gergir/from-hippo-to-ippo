# Queries from db
from sqlalchemy.orm import Session
from models import Role, User, Target, Measurement


def find_all_roles(db: Session) -> list[Role]:
    return db.query(Role).all()


def find_role(db: Session, role_id: int) -> Role:
    return db.query(Role).filter(Role.id == role_id).first()


def find_role_by_name(db: Session, role_name: str) -> Role:
    return db.query(Role).filter(Role.role_type == role_name).first()


def find_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def find_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()


def find_user_by_name(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def find_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


def find_all_targets(db: Session, user_id: int | None = None) -> list[Target]:
    if user_id is not None:
        return db.query(Target).filter(Target.user_id == user_id).all()
    return db.query(Target).all()


def find_target(db: Session, target_id: int, user_id: int) -> Target:
    return db.query(Target).join(Target.user).filter(Target.id == target_id, User.id == user_id).first()


def find_target_by_name(db: Session, target_name: str) -> Target:
    return db.query(Target).filter(Target.name == target_name).first()


def find_all_measurements(db: Session, target_id: int | None = None, user_id: int | None = None) -> list[Measurement]:
    if user_id is not None and target_id is not None:
        return db.query(Measurement).join(Measurement.target).join(Target.user).filter(
            Target.id == target_id, User.id == user_id
        ).all()
    if user_id is not None:
        return db.query(Measurement).join(Measurement.target).join(Target.user).filter(User.id == user_id).all()
    return db.query(Measurement).all()


def find_measurement(db: Session, measurement_id: int, target_id, user_id: int) -> Measurement:
    return db.query(Measurement).join(Measurement.target).join(Target.user).filter(
        Measurement.id == measurement_id, Target.id == target_id, User.id == user_id
    ).first()

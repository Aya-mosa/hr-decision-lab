from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from app.db import Base


class ScenarioORM(Base):
    __tablename__ = "scenarios"
    scenario_id = Column(String, primary_key=True)
    level = Column(String, nullable=False)
    category = Column(String, nullable=False)
    data_json = Column(Text, nullable=False)


class DecisionORM(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    scenario_id = Column(String, nullable=False)
    level = Column(String, nullable=False)
    chosen_option_id = Column(String, nullable=False)
    archetype_label = Column(String, nullable=False)


class AdminUserORM(Base):
    __tablename__ = "admin_users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)


class AdminSessionORM(Base):
    __tablename__ = "admin_sessions"
    token = Column(String, primary_key=True)
    admin_id = Column(String, ForeignKey("admin_users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)


class InviteORM(Base):
    __tablename__ = "invites"
    id = Column(String, primary_key=True)
    batch_id = Column(String, nullable=False, index=True)
    admin_id = Column(String, ForeignKey("admin_users.id"), nullable=False)
    invite_type = Column(String, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    level = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="pending")
    session_id = Column(String, nullable=True)
    consented = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)

"""
SQLAlchemyモデル定義
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class User(Base):
    """ユーザーモデル"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="member")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assigned_to_user")
    team_members = relationship("TeamMember", back_populates="user")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="created_by_user")

    def __repr__(self):
        return f"<User {self.username}>"


class Team(Base):
    """チームモデル"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="team")

    def __repr__(self):
        return f"<Team {self.name}>"


class TeamMember(Base):
    """チームメンバー（中間テーブル）"""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")  # admin, manager, member
    joined_at = Column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_members")

    def __repr__(self):
        return f"<TeamMember {self.user_id} in {self.team_id}>"


class TaskStatus(str, enum.Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """タスク優先度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    """タスクモデル"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="pending")
    priority = Column(String(20), default="medium")
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # リレーションシップ
    team = relationship("Team", back_populates="tasks")
    assigned_to_user = relationship("User", foreign_keys=[assigned_to], back_populates="tasks")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")

    def __repr__(self):
        return f"<Task {self.title}>"


class ActivityLog(Base):
    """アクティビティログ"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    description = Column(Text)
    entity_type = Column(String(50))  # task, team, user
    entity_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ActivityLog {self.action}>"

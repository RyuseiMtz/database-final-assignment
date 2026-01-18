"""
CRUD操作（Create, Read, Update, Delete）
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.models import Team, TeamMember, Task, User, ActivityLog


# ==================== チーム関連 ====================

def create_team(db: Session, name: str, description: str = None) -> Team:
    """チームを作成"""
    team = Team(name=name, description=description)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team(db: Session, team_id: int) -> Team:
    """チームを取得"""
    return db.query(Team).filter(Team.id == team_id).first()


def get_all_teams(db: Session) -> list:
    """全チームを取得"""
    return db.query(Team).all()


def update_team(db: Session, team_id: int, name: str = None, description: str = None) -> Team:
    """チームを更新"""
    team = get_team(db, team_id)
    if not team:
        return None
    
    if name:
        team.name = name
    if description is not None:
        team.description = description
    
    team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(team)
    return team


def delete_team(db: Session, team_id: int) -> bool:
    """チームを削除"""
    team = get_team(db, team_id)
    if not team:
        return False
    
    db.delete(team)
    db.commit()
    return True


# ==================== チームメンバー関連 ====================

def add_team_member(db: Session, team_id: int, user_id: int, role: str = "member") -> TeamMember:
    """チームメンバーを追加"""
    # 既に存在するか確認
    existing = db.query(TeamMember).filter(
        and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    ).first()
    
    if existing:
        return existing
    
    member = TeamMember(team_id=team_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_team_members(db: Session, team_id: int) -> list:
    """チームのメンバーを取得"""
    return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()


def remove_team_member(db: Session, team_id: int, user_id: int) -> bool:
    """チームメンバーを削除"""
    member = db.query(TeamMember).filter(
        and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    ).first()
    
    if not member:
        return False
    
    db.delete(member)
    db.commit()
    return True


def update_team_member_role(db: Session, team_id: int, user_id: int, role: str) -> TeamMember:
    """チームメンバーのロールを更新"""
    member = db.query(TeamMember).filter(
        and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    ).first()
    
    if not member:
        return None
    
    member.role = role
    db.commit()
    db.refresh(member)
    return member


# ==================== タスク関連 ====================

def create_task(db: Session, title: str, team_id: int, created_by: int, 
                description: str = None, assigned_to: int = None, 
                status: str = "pending", priority: str = "medium", 
                due_date: datetime = None) -> Task:
    """タスクを作成"""
    task = Task(
        title=title,
        description=description,
        team_id=team_id,
        assigned_to=assigned_to,
        status=status,
        priority=priority,
        due_date=due_date,
        created_by=created_by
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # アクティビティログを記録
    log_activity(db, created_by, "create_task", f"タスク '{title}' を作成しました", "task", task.id)
    
    return task


def get_task(db: Session, task_id: int) -> Task:
    """タスクを取得"""
    return db.query(Task).filter(Task.id == task_id).first()


def get_team_tasks(db: Session, team_id: int, status: str = None, assigned_to: int = None) -> list:
    """チームのタスクを取得"""
    query = db.query(Task).filter(Task.team_id == team_id)
    
    if status:
        query = query.filter(Task.status == status)
    
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
    return query.order_by(Task.created_at.desc()).all()


def get_user_tasks(db: Session, user_id: int) -> list:
    """ユーザーに割り当てられたタスクを取得"""
    return db.query(Task).filter(Task.assigned_to == user_id).order_by(Task.created_at.desc()).all()


def update_task(db: Session, task_id: int, user_id: int, **kwargs) -> Task:
    """タスクを更新"""
    task = get_task(db, task_id)
    if not task:
        return None
    
    updated_fields = []
    for key, value in kwargs.items():
        if hasattr(task, key) and value is not None:
            old_value = getattr(task, key)
            if old_value != value:
                setattr(task, key, value)
                updated_fields.append(f"{key}: {old_value} → {value}")
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    # アクティビティログを記録
    if updated_fields:
        log_activity(db, user_id, "update_task", f"タスク '{task.title}' を更新しました: {', '.join(updated_fields)}", "task", task.id)
    
    return task


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """タスクを削除"""
    task = get_task(db, task_id)
    if not task:
        return False
    
    task_title = task.title
    db.delete(task)
    db.commit()
    
    # アクティビティログを記録
    log_activity(db, user_id, "delete_task", f"タスク '{task_title}' を削除しました", "task", task_id)
    
    return True


def get_task_statistics(db: Session, team_id: int) -> dict:
    """タスク統計を取得"""
    tasks = get_team_tasks(db, team_id)
    
    total = len(tasks)
    pending = len([t for t in tasks if t.status == "pending"])
    in_progress = len([t for t in tasks if t.status == "in_progress"])
    completed = len([t for t in tasks if t.status == "completed"])
    cancelled = len([t for t in tasks if t.status == "cancelled"])
    
    high_priority = len([t for t in tasks if t.priority == "high"])
    medium_priority = len([t for t in tasks if t.priority == "medium"])
    low_priority = len([t for t in tasks if t.priority == "low"])
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "cancelled": cancelled,
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }


# ==================== アクティビティログ関連 ====================

def log_activity(db: Session, user_id: int, action: str, description: str = None, 
                 entity_type: str = None, entity_id: int = None) -> ActivityLog:
    """アクティビティをログに記録"""
    log = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_activity_logs(db: Session, user_id: int = None, limit: int = 50) -> list:
    """アクティビティログを取得"""
    query = db.query(ActivityLog)
    
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    return query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()

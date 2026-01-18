"""
Streamlitメインアプリケーション（簡略版）
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PAGE_CONFIG, APP_NAME
from backend.database import SessionLocal, init_db
from backend.auth import authenticate_user, create_user
from backend.crud import (
    get_all_teams, create_team, get_team_members, add_team_member,
    get_team_tasks, create_task, update_task, delete_task, get_task_statistics
)

# ページ設定
st.set_page_config(**PAGE_CONFIG)

# スタイル
st.markdown("""
    <style>
    .main { padding: 2rem; }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """セッション状態を初期化"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None


def login_page():
    """ログインページ"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("📋 " + APP_NAME)
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["ログイン", "新規登録"])
        
        with tab1:
            st.subheader("ログイン")
            username = st.text_input("ユーザー名")
            password = st.text_input("パスワード", type="password")
            
            if st.button("ログイン"):
                if username and password:
                    db = SessionLocal()
                    try:
                        user = authenticate_user(db, username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user.id
                            st.session_state.username = user.username
                            st.success("ログインしました！")
                            st.rerun()
                        else:
                            st.error("ユーザー名またはパスワードが正しくありません")
                    except Exception as e:
                        st.error(f"エラー: {str(e)}")
                    finally:
                        db.close()
                else:
                    st.warning("ユーザー名とパスワードを入力してください")
        
        with tab2:
            st.subheader("新規登録")
            new_username = st.text_input("ユーザー名 (新規)")
            new_email = st.text_input("メールアドレス")
            new_full_name = st.text_input("フルネーム")
            new_password = st.text_input("パスワード (新規)", type="password")
            new_password_confirm = st.text_input("パスワード (確認)", type="password")
            
            if st.button("登録"):
                if not (new_username and new_email and new_password and new_password_confirm):
                    st.warning("全ての項目を入力してください")
                elif new_password != new_password_confirm:
                    st.error("パスワードが一致しません")
                elif len(new_password) < 6:
                    st.error("パスワードは6文字以上である必要があります")
                else:
                    db = SessionLocal()
                    try:
                        user = create_user(
                            db,
                            username=new_username,
                            email=new_email,
                            password=new_password,
                            full_name=new_full_name
                        )
                        st.success("登録が完了しました。ログインしてください。")
                    except ValueError as e:
                        st.error(str(e))
                    finally:
                        db.close()


def main_app():
    """メインアプリケーション"""
    # サイドバー
    with st.sidebar:
        st.title("📋 メニュー")
        st.write(f"**ユーザー**: {st.session_state.username}")
        st.markdown("---")
        
        page = st.radio(
            "ページを選択",
            ["ダッシュボード", "タスク管理", "チーム管理", "分析"]
        )
        
        if st.button("ログアウト"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.success("ログアウトしました")
            st.rerun()
    
    # ページの表示
    if page == "ダッシュボード":
        show_dashboard()
    elif page == "タスク管理":
        show_task_management()
    elif page == "チーム管理":
        show_team_management()
    elif page == "分析":
        show_analytics()


def show_dashboard():
    """ダッシュボードページ"""
    st.title("📊 ダッシュボード")
    
    db = SessionLocal()
    try:
        teams = get_all_teams(db)
        
        if not teams:
            st.info("チームがまだ作成されていません。チーム管理ページでチームを作成してください。")
            return
        
        # チーム選択
        team_names = [t.name for t in teams]
        selected_team_name = st.selectbox("チームを選択", team_names, key="dashboard_team_select")
        selected_team = next(t for t in teams if t.name == selected_team_name)
        
        # 統計情報
        stats = get_task_statistics(db, selected_team.id)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総タスク数", stats["total"])
        with col2:
            st.metric("未開始", stats["pending"])
        with col3:
            st.metric("進行中", stats["in_progress"])
        with col4:
            st.metric("完了", stats["completed"])
        
        st.markdown("---")
        
        # タスク一覧
        st.subheader("📋 最近のタスク")
        tasks = get_team_tasks(db, selected_team.id)
        
        if tasks:
            task_data = []
            for task in tasks[:10]:
                task_data.append({
                    "タスク": task.title,
                    "ステータス": task.status,
                    "優先度": task.priority,
                    "期限": task.due_date.strftime("%Y-%m-%d") if task.due_date else "-"
                })
            
            df = pd.DataFrame(task_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("タスクがありません")
    
    finally:
        db.close()


def show_task_management():
    """タスク管理ページ"""
    st.title("📝 タスク管理")
    
    db = SessionLocal()
    try:
        teams = get_all_teams(db)
        
        if not teams:
            st.info("チームがまだ作成されていません")
            return
        
        # チーム選択
        team_names = [t.name for t in teams]
        selected_team_name = st.selectbox("チームを選択", team_names, key="task_team_select")
        selected_team = next(t for t in teams if t.name == selected_team_name)
        
        # タブ
        tab1, tab2, tab3 = st.tabs(["タスク一覧", "新規タスク", "タスク編集"])
        
        with tab1:
            st.subheader("タスク一覧")
            
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox("ステータスで絞り込み", ["全て", "pending", "in_progress", "completed", "cancelled"], key="status_filter")
            with col2:
                priority_filter = st.selectbox("優先度で絞り込み", ["全て", "high", "medium", "low"], key="priority_filter")
            
            tasks = get_team_tasks(db, selected_team.id)
            
            if status_filter != "全て":
                tasks = [t for t in tasks if t.status == status_filter]
            if priority_filter != "全て":
                tasks = [t for t in tasks if t.priority == priority_filter]
            
            if tasks:
                for task in tasks:
                    with st.expander(f"📌 {task.title}"):
                        st.write(f"**説明**: {task.description or 'なし'}")
                        st.write(f"**ステータス**: {task.status}")
                        st.write(f"**優先度**: {task.priority}")
                        
                        if task.due_date:
                            st.write(f"**期限**: {task.due_date.strftime('%Y-%m-%d')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("削除", key=f"delete_{task.id}"):
                                delete_task(db, task.id, st.session_state.user_id)
                                st.success("タスクを削除しました")
                                st.rerun()
            else:
                st.info("タスクがありません")
        
        with tab2:
            st.subheader("新規タスク作成")
            
            title = st.text_input("タスク名")
            description = st.text_area("説明")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                status = st.selectbox("ステータス", ["pending", "in_progress", "completed", "cancelled"], key="new_task_status")
            with col2:
                priority = st.selectbox("優先度", ["low", "medium", "high"], key="new_task_priority")
            with col3:
                due_date = st.date_input("期限")
            
            if st.button("タスクを作成"):
                if title:
                    create_task(
                        db,
                        title=title,
                        team_id=selected_team.id,
                        created_by=st.session_state.user_id,
                        description=description,
                        status=status,
                        priority=priority,
                        due_date=datetime.combine(due_date, datetime.min.time())
                    )
                    st.success("タスクを作成しました")
                    st.rerun()
                else:
                    st.error("タスク名を入力してください")
        
        with tab3:
            st.subheader("タスク編集")
            
            tasks = get_team_tasks(db, selected_team.id)
            task_titles = [t.title for t in tasks]
            
            if task_titles:
                selected_task_title = st.selectbox("編集するタスク", task_titles, key="edit_task_select")
                selected_task = next(t for t in tasks if t.title == selected_task_title)
                
                new_title = st.text_input("タスク名", value=selected_task.title, key="edit_task_title")
                new_description = st.text_area("説明", value=selected_task.description or "", key="edit_task_desc")
                new_status = st.selectbox("ステータス", ["pending", "in_progress", "completed", "cancelled"], 
                                         index=["pending", "in_progress", "completed", "cancelled"].index(selected_task.status), key="edit_task_status")
                new_priority = st.selectbox("優先度", ["low", "medium", "high"],
                                           index=["low", "medium", "high"].index(selected_task.priority), key="edit_task_priority")
                
                if st.button("更新"):
                    update_task(
                        db,
                        selected_task.id,
                        st.session_state.user_id,
                        title=new_title,
                        description=new_description,
                        status=new_status,
                        priority=new_priority
                    )
                    st.success("タスクを更新しました")
                    st.rerun()
            else:
                st.info("編集するタスクがありません")
    
    finally:
        db.close()


def show_team_management():
    """チーム管理ページ"""
    st.title("👥 チーム管理")
    
    db = SessionLocal()
    try:
        tab1, tab2 = st.tabs(["チーム一覧", "新規チーム"])
        
        with tab1:
            st.subheader("チーム一覧")
            
            teams = get_all_teams(db)
            
            if teams:
                for team in teams:
                    with st.expander(f"🏢 {team.name}"):
                        st.write(f"**説明**: {team.description or 'なし'}")
                        
                        members = get_team_members(db, team.id)
                        st.write(f"**メンバー数**: {len(members)}")
                        
                        if members:
                            st.write("**メンバー一覧**:")
                            for member in members:
                                st.write(f"- {member.user.full_name or member.user.username} ({member.role})")
            else:
                st.info("チームがありません")
        
        with tab2:
            st.subheader("新規チーム作成")
            
            team_name = st.text_input("チーム名")
            team_description = st.text_area("説明")
            
            if st.button("チームを作成"):
                if team_name:
                    team = create_team(db, name=team_name, description=team_description)
                    # 作成者をメンバーに追加
                    add_team_member(db, team.id, st.session_state.user_id, role="admin")
                    st.success("チームを作成しました")
                    st.rerun()
                else:
                    st.error("チーム名を入力してください")
    
    finally:
        db.close()


def show_analytics():
    """分析ページ"""
    st.title("📈 分析・可視化")
    
    db = SessionLocal()
    try:
        teams = get_all_teams(db)
        
        if not teams:
            st.info("チームがありません")
            return
        
        team_names = [t.name for t in teams]
        selected_team_name = st.selectbox("チームを選択", team_names)
        selected_team = next(t for t in teams if t.name == selected_team_name)
        
        stats = get_task_statistics(db, selected_team.id)
        
        # グラフ表示
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ステータス別タスク数")
            
            status_data = {
                "未開始": stats["pending"],
                "進行中": stats["in_progress"],
                "完了": stats["completed"],
                "キャンセル": stats["cancelled"]
            }
            
            st.bar_chart(status_data)
        
        with col2:
            st.subheader("優先度別タスク数")
            
            priority_data = {
                "高": stats["high_priority"],
                "中": stats["medium_priority"],
                "低": stats["low_priority"]
            }
            
            st.bar_chart(priority_data)
        
        # 完了率
        st.subheader("完了率")
        st.progress(stats["completion_rate"] / 100)
        st.write(f"{stats['completion_rate']:.1f}%")
    
    finally:
        db.close()


# メイン処理
if __name__ == "__main__":
    init_session_state()
    
    # データベースを初期化
    try:
        init_db()
    except:
        pass  # 既に初期化されている場合
    
    if st.session_state.authenticated:
        main_app()
    else:
        login_page()

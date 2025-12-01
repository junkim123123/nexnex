"""
Authentication Utilities for NexSupply AI
회원가입, 로그인, 사용자 관리 기능
"""

import streamlit as st
import hashlib
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# 사용자 데이터 저장 경로
USERS_FILE = Path("data/users.json")

def ensure_users_file():
    """users.json 파일이 없으면 생성"""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

def hash_password(password: str) -> str:
    """비밀번호를 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict[str, Dict[str, Any]]:
    """사용자 데이터 로드"""
    ensure_users_file()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"사용자 데이터 로드 실패: {e}")
        return {}

def save_users(users: Dict[str, Dict[str, Any]]):
    """사용자 데이터 저장"""
    ensure_users_file()
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"사용자 데이터 저장 실패: {e}")
        raise

def register_user(email: str, password: str, name: Optional[str] = None) -> tuple[bool, str]:
    """
    새 사용자 등록
    
    Returns:
        (success: bool, message: str)
    """
    if not email or not password:
        return False, "이메일과 비밀번호를 모두 입력해주세요."
    
    if '@' not in email or '.' not in email.split('@')[1]:
        return False, "올바른 이메일 형식이 아닙니다."
    
    if len(password) < 6:
        return False, "비밀번호는 최소 6자 이상이어야 합니다."
    
    users = load_users()
    
    if email.lower() in users:
        return False, "이미 등록된 이메일입니다."
    
    users[email.lower()] = {
        'email': email.lower(),
        'password_hash': hash_password(password),
        'name': name or email.split('@')[0],
        'created_at': str(os.path.getmtime(USERS_FILE)) if USERS_FILE.exists() else None
    }
    
    try:
        save_users(users)
        logger.info(f"새 사용자 등록: {email}")
        return True, "회원가입이 완료되었습니다!"
    except Exception as e:
        logger.error(f"사용자 등록 실패: {e}")
        return False, f"회원가입 중 오류가 발생했습니다: {str(e)}"

def authenticate_user(email: str, password: str) -> tuple[bool, Optional[str]]:
    """
    사용자 인증
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    if not email or not password:
        return False, "이메일과 비밀번호를 모두 입력해주세요."
    
    users = load_users()
    user = users.get(email.lower())
    
    if not user:
        # Secrets에서 authorized_users 확인 (기존 방식 지원)
        try:
            authorized_users = st.secrets.get('general', {}).get('authorized_users', [])
            for auth_user in authorized_users:
                user_email = auth_user.get('email', '')
                user_password = auth_user.get('password', '')
                
                # 와일드카드 이메일 지원
                email_match = (user_email == "*" or email.lower() == user_email.lower())
                password_match = (password == user_password)
                
                if email_match and password_match:
                    return True, None
        except:
            pass
        
        return False, "이메일 또는 비밀번호가 올바르지 않습니다."
    
    if user['password_hash'] != hash_password(password):
        return False, "이메일 또는 비밀번호가 올바르지 않습니다."
    
    return True, None

def get_current_user() -> Optional[Dict[str, Any]]:
    """현재 로그인된 사용자 정보 반환"""
    if not st.session_state.get('logged_in'):
        return None
    
    email = st.session_state.get('user_email')
    if not email:
        return None
    
    users = load_users()
    return users.get(email.lower())

def logout():
    """로그아웃"""
    st.session_state['logged_in'] = False
    st.session_state['user_email'] = None
    st.session_state['user_name'] = None

def is_logged_in() -> bool:
    """로그인 상태 확인"""
    return st.session_state.get('logged_in', False)


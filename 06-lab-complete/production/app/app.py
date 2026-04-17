from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from openai import OpenAI

sys.path.append(str(Path(__file__).resolve().parent))

from src.auth import build_demo_users, create_access_token, decode_token, verify_password
from src.config import AppConfig, load_config


st.set_page_config(page_title="AI Chat Secure", page_icon=":robot_face:", layout="wide")


def init_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("jwt_token", None)
    st.session_state.setdefault("claims", None)


def clear_session() -> None:
    st.session_state["messages"] = []
    st.session_state["jwt_token"] = None
    st.session_state["claims"] = None


def ensure_claims(config: AppConfig) -> dict | None:
    token = st.session_state.get("jwt_token")
    if not token:
        return None

    try:
        claims = decode_token(token, config.jwt_secret)
    except Exception:
        clear_session()
        return None

    st.session_state["claims"] = claims
    return claims


def login_view(config: AppConfig) -> None:
    st.markdown("## Đăng nhập")
    st.caption("Tài khoản demo: admin/admin123 hoặc user/user123")

    with st.form("login-form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Đăng nhập", use_container_width=True)

    if not submitted:
        return

    users = build_demo_users(config)
    user = users.get(username)
    if not user or not verify_password(password, user["password"]):
        st.error("Thông tin đăng nhập không hợp lệ.")
        return

    token = create_access_token(
        {"sub": username, "role": user["role"]},
        config.jwt_secret,
        config.jwt_exp_minutes,
    )
    st.session_state["jwt_token"] = token
    st.session_state["claims"] = decode_token(token, config.jwt_secret)
    st.rerun()


def sidebar_view(config: AppConfig, claims: dict) -> None:
    with st.sidebar:
        st.markdown("## Phiên đăng nhập")
        st.write(f"User: `{claims['sub']}`")
        st.write(f"Role: `{claims['role']}`")

        if claims["role"] == "admin":
            st.code(st.session_state["jwt_token"], language="text")
            st.success("Admin có thể xem JWT token và cấu hình model.")
            st.write(f"Model hiện tại: `{config.openai_model}`")
        else:
            st.info("User có thể chat nhưng không được xem JWT token.")

        if st.button("Đăng xuất", use_container_width=True):
            clear_session()
            st.rerun()


def chat_view(config: AppConfig, claims: dict) -> None:
    st.markdown("# Secure Streamlit Chat")
    st.caption("Chat với OpenAI API sau khi đăng nhập bằng JWT.")

    if not config.openai_api_key:
        st.warning("Thiếu OPENAI_API_KEY. Hãy thêm biến môi trường trước khi chat.")
        return

    client = OpenAI(api_key=config.openai_api_key)

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Nhập câu hỏi của bạn")
    if not prompt:
        return

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_message = (
        "You are a helpful assistant for a secure Streamlit app. "
        f"The authenticated user role is {claims['role']}."
    )
    api_messages = [{"role": "system", "content": system_message}, *st.session_state["messages"]]

    try:
        response = client.responses.create(model=config.openai_model, input=api_messages)
        answer = response.output_text
    except Exception as exc:
        answer = f"OpenAI API error: {exc}"

    st.session_state["messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)


def main() -> None:
    config = load_config()
    init_state()
    claims = ensure_claims(config)

    if not claims:
        login_view(config)
        return

    sidebar_view(config, claims)
    chat_view(config, claims)


if __name__ == "__main__":
    main()

import streamlit as st
from openai import OpenAI

st.title("🤖 나의 AI 챗봇")

# 사이드바에서 API Key 입력
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
mood_options = ["😊 행복", "😐 보통", "😢 슬픔", "😡 화남", "😴 피곤", "🤯 스트레스"]
selected_mood = st.sidebar.selectbox("현재 기분을 선택하세요", mood_options)

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 현재 기분 표시
st.info(f"현재 선택된 기분: {selected_mood}")

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요"):
    if not api_key:
        st.error("⚠️ 사이드바에서 API Key를 입력해주세요!")
    else:
        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            client = OpenAI(api_key=api_key)
            messages_to_send = [
                {
                    "role": "system",
                    "content": f"사용자의 현재 기분은 '{selected_mood}'입니다.",
                },
                *st.session_state.messages,
            ]
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_to_send,
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

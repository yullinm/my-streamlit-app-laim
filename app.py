from __future__ import annotations

import requests
import streamlit as st


st.set_page_config(
    page_title="심리테스트 영화 추천",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
    .app-header {
        background: linear-gradient(90deg, #1f1c2c 0%, #928DAB 100%);
        padding: 2.5rem 2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
    }
    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .app-header p {
        margin-top: 0.5rem;
        font-size: 1.05rem;
        opacity: 0.9;
    }
    .pill {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        background-color: rgba(255, 255, 255, 0.18);
        font-size: 0.85rem;
        margin-right: 0.5rem;
    }
    .card {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    .movie-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .movie-meta {
        color: #5c677d;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    .reason {
        background: #f0f4ff;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        color: #2b3a67;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .question-card {
        border: 1px solid #edf0f6;
        border-radius: 16px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        background: #fbfcff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-header">
        <span class="pill">TMDB 연동</span>
        <span class="pill">심리테스트 기반</span>
        <h1>🎬 당신의 취향을 읽는 영화 추천</h1>
        <p>간단한 질문에 답하면, 검증된 인기작 5편을 바로 추천해드려요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tmdb_api_key = st.sidebar.text_input("TMDB API Key", type="password")
st.sidebar.markdown(
    """
    **API 안내**
    - TMDB API Key를 입력하면 추천 결과를 확인할 수 있어요.
    - 입력한 키는 저장되지 않습니다.
    """
)

genre_mapping = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}

questions = [
    {
        "question": "주말에 가장 하고 싶은 활동은?",
        "options": {
            "신나는 액티비티를 즐기고 싶다": "액션",
            "친구들과 유쾌하게 웃고 싶다": "코미디",
            "혼자서 감성적인 시간을 보내고 싶다": "드라마",
            "새로운 기술이나 미래 이야기에 끌린다": "SF",
        },
    },
    {
        "question": "이야기에서 가장 중요한 요소는?",
        "options": {
            "강렬한 사건과 전개": "액션",
            "가볍고 즐거운 분위기": "코미디",
            "인물의 성장과 감정선": "드라마",
            "로맨틱한 감정": "로맨스",
        },
    },
    {
        "question": "상상 속 세계에 대한 호기심은?",
        "options": {
            "미래 기술과 우주가 궁금하다": "SF",
            "마법과 신비한 세계를 좋아한다": "판타지",
            "현실적인 이야기가 더 좋다": "드라마",
            "일상의 소소한 재미가 좋다": "코미디",
        },
    },
    {
        "question": "기분 전환이 필요할 때 가장 선호하는 영화 스타일은?",
        "options": {
            "통쾌한 액션": "액션",
            "따뜻한 로맨스": "로맨스",
            "마법 같은 판타지": "판타지",
            "뭉클한 드라마": "드라마",
        },
    },
    {
        "question": "친구에게 영화를 추천한다면?",
        "options": {
            "긴장감 넘치는 액션": "액션",
            "웃음이 가득한 코미디": "코미디",
            "감동적인 드라마": "드라마",
            "설레는 로맨스": "로맨스",
        },
    },
]


def get_recommendation_reason(selected_genre: str, top_choices: list[str]) -> str:
    reasons = {
        "액션": "긴장감 넘치는 전개와 속도감 있는 장면을 좋아하는 성향이 보여요.",
        "코미디": "웃음과 여유를 중요하게 생각하는 답변이 많았어요.",
        "드라마": "감정선과 이야기의 깊이를 중시하는 선택이 돋보였어요.",
        "SF": "새로운 세계와 미래에 대한 호기심이 강하게 드러났어요.",
        "로맨스": "따뜻한 감정과 설렘을 원하는 답변이 많았어요.",
        "판타지": "현실을 넘어서는 상상력을 즐기는 성향이 느껴져요.",
    }
    base_reason = reasons.get(selected_genre, "당신의 답변에서 이 장르의 선호도가 높게 나타났어요.")
    if top_choices:
        return f"{base_reason} 특히 '{top_choices[0]}' 선택이 큰 영향을 줬어요."
    return base_reason


def fetch_movies(api_key: str, genre_id: int) -> list[dict]:
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "vote_count.desc",
        "vote_count.gte": 500,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])[:5]


left, right = st.columns([1.2, 1])

with left:
    st.markdown('<div class="section-title">📝 심리테스트 질문</div>', unsafe_allow_html=True)
    answers: list[str] = []
    with st.form("mood_test"):
        for idx, question in enumerate(questions, start=1):
            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            answer = st.radio(
                f"{idx}. {question['question']}",
                list(question["options"].keys()),
                key=f"question_{idx}",
            )
            st.markdown("</div>", unsafe_allow_html=True)
            answers.append(answer)
        submitted = st.form_submit_button("결과 보기")

with right:
    st.markdown('<div class="section-title">✨ 추천 흐름</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="card">
            <p><strong>1.</strong> 질문에 답하기</p>
            <p><strong>2.</strong> 취향 장르 분석</p>
            <p><strong>3.</strong> TMDB 인기작 5편 추천</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="card">
            <p><strong>Tip.</strong> 추천 결과는 투표 수가 충분한 작품 위주로 선별돼요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if submitted:
    if not tmdb_api_key:
        st.error("TMDB API Key를 사이드바에 입력해주세요.")
        st.stop()

    genre_scores = {genre: 0 for genre in genre_mapping}
    top_choices = []
    for answer, question in zip(answers, questions):
        genre = question["options"][answer]
        genre_scores[genre] += 1
        top_choices.append(answer)

    selected_genre = max(genre_scores, key=genre_scores.get)
    genre_id = genre_mapping[selected_genre]

    st.markdown("---")
    st.markdown('<div class="section-title">🎯 결과 요약</div>', unsafe_allow_html=True)
    st.success(f"당신에게 어울리는 장르는 **{selected_genre}** 입니다!")
    st.caption(get_recommendation_reason(selected_genre, top_choices))

    try:
        movies = fetch_movies(tmdb_api_key, genre_id)
    except requests.RequestException:
        st.error("TMDB에서 데이터를 불러오지 못했어요. API Key 또는 네트워크 상태를 확인해주세요.")
        st.stop()

    if not movies:
        st.info("추천할 영화를 찾지 못했어요. 다른 장르로 다시 시도해보세요.")
    else:
        st.markdown('<div class="section-title">🍿 추천 영화 5편</div>', unsafe_allow_html=True)
        for movie in movies:
            poster_path = movie.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            title = movie.get("title", "제목 없음")
            rating = movie.get("vote_average", "N/A")
            overview = movie.get("overview", "줄거리 정보가 없습니다.")

            st.markdown('<div class="card">', unsafe_allow_html=True)
            cols = st.columns([1, 3])
            with cols[0]:
                if poster_url:
                    st.image(poster_url, use_column_width=True)
                else:
                    st.write("포스터 없음")
            with cols[1]:
                st.markdown(f'<div class="movie-title">{title}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="movie-meta">평점: {rating}</div>', unsafe_allow_html=True)
                st.write(overview)
                st.markdown(
                    '<div class="reason">이 영화를 추천하는 이유: 대중성과 평점이 모두 검증된 작품이에요.</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

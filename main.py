import streamlit as st
import pandas as pd
import altair as alt

# -------------------------------
# 1. 데이터 로드
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# -------------------------------
# 2. UI 구성
# -------------------------------
st.set_page_config(page_title="MBTI 세계 분포", layout="wide")
st.title("🌍 MBTI 유형별 국가 분석 대시보드")
st.markdown("특정 MBTI 유형을 선택하면, 해당 유형이 **가장 높은 국가 TOP 10**을 시각적으로 보여줍니다.")

# 선택 위젯
mbti_cols = [col for col in df.columns if col != "Country"]
selected_type = st.selectbox("분석할 MBTI 유형을 선택하세요:", mbti_cols, index=0)

# -------------------------------
# 3. 분석 처리
# -------------------------------
top10 = (
    df[["Country", selected_type]]
    .sort_values(by=selected_type, ascending=False)
    .head(10)
)

# -------------------------------
# 4. 시각화 (Altair)
# -------------------------------
chart = (
    alt.Chart(top10)
    .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x=alt.X(f"{selected_type}:Q", title=f"{selected_type} 비율", sort="descending"),
        y=alt.Y("Country:N", sort="-x", title="국가"),
        color=alt.Color(f"{selected_type}:Q", scale=alt.Scale(scheme="tealblues")),
        tooltip=["Country", selected_type],
    )
    .properties(
        width=700,
        height=400,
        title=f"🌎 {selected_type} 유형이 높은 국가 TOP 10"
    )
)

# -------------------------------
# 5. 결과 출력
# -------------------------------
st.altair_chart(chart, use_container_width=True)

# 수치 테이블도 함께 표시
st.markdown("### 📊 데이터 보기")
st.dataframe(top10.style.background_gradient(cmap="Blues"))

# -------------------------------
# 6. 추가 기능 (선택)
# -------------------------------
st.markdown("---")
st.markdown("📈 데이터 출처: countriesMBTI_16types.csv  
💡 제작: Streamlit + Altair | 시각화 색상 테마: TealBlues")

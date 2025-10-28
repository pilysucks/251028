import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="World Renewables Dashboard", layout="wide")
st.title("🌱 World Renewable Energy Mix by Country")
st.markdown(
    "샘플 CSV를 사용하거나 본인의 CSV를 업로드하여 국가별 재생에너지 비중을 비교할 수 있습니다. "
    "Altair로 시각적으로 보기 좋은 차트를 제공합니다."
)

# -----------------------
# 데이터 로드: 업로드 우선, 없으면 로컬 파일을 시도
# -----------------------
uploaded = st.file_uploader("📂 CSV 파일 업로드 (선택). 없으면 샘플 파일를 사용합니다.", type=["csv"])
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"파일을 읽는 중 오류 발생: {e}")
        st.stop()
else:
    # 기본 로컬 파일명 (앱 코드와 같은 디렉터리에 두세요)
    local_path = "renewables_by_country.csv"
    try:
        df = pd.read_csv(local_path)
        st.info(f"로컬 샘플 파일을 불러왔습니다: `{local_path}`")
    except FileNotFoundError:
        st.error(
            "기본 CSV 파일을 찾을 수 없습니다. 앱 디렉터리에 `renewables_by_country.csv`를 두거나 파일을 업로드해주세요."
        )
        st.stop()

# -----------------------
# 데이터 검사 및 전처리 (유연하게 컬럼 허용)
# -----------------------
expected_cols = ["Country"]
# detect pct columns automatically (columns that end with _pct or are numeric except Country)
pct_cols = [c for c in df.columns if c.lower().endswith("_pct")]
if not pct_cols:
    # fallback: numeric columns except Country
    pct_cols = [c for c in df.columns if c != "Country" and pd.api.types.is_numeric_dtype(df[c])]

if "Country" not in df.columns:
    st.error("데이터에 'Country' 컬럼이 필요합니다.")
    st.stop()

st.sidebar.header("설정")
metric = st.sidebar.selectbox("비교할 항목 선택", pct_cols, index=0)
view_mode = st.sidebar.radio("보기 모드", ["Top 10 국가 (막대)", "스택형 막대 (국가 비교)", "상세 테이블"])

# -----------------------
# 시각화: Top 10 막대 (Altair)
# -----------------------
if view_mode == "Top 10 국가 (막대)":
    top10 = df[["Country", metric]].sort_values(by=metric, ascending=False).head(10)
    chart = (
        alt.Chart(top10)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X(f"{metric}:Q", title=f"{metric} (%)"),
            y=alt.Y("Country:N", sort="-x", title="Country"),
            color=alt.Color(f"{metric}:Q", scale=alt.Scale(scheme="tealblues")),
            tooltip=["Country", alt.Tooltip(f"{metric}:Q", format=".2f")]
        )
        .properties(width=800, height=450, title=f"Top 10 Countries by {metric}")
    )
    st.altair_chart(chart, use_container_width=True)
    st.markdown("### 데이터 (Top 10)")
    st.dataframe(top10.reset_index(drop=True).style.format({metric: "{:.2f}"}))

# -----------------------
# 스택형 막대: 여러 항목을 한눈에
# -----------------------
elif view_mode == "스택형 막대 (국가 비교)":
    # allow user to pick multiple components to stack
    stack_cols = st.multiselect("스택할 항목 선택", pct_cols, default=pct_cols[:3])
    if not stack_cols:
        st.warning("하나 이상의 항목을 선택하세요.")
    else:
        # pick top N countries by total of selected components
        df["selected_sum"] = df[stack_cols].sum(axis=1)
        top_n = st.slider("상위 N개 국가 표시", min_value=5, max_value=min(50, len(df)), value=10)
        top_df = df.sort_values("selected_sum", ascending=False).head(top_n)

        # convert to long format for Altair stacked bar
        long = top_df[["Country"] + stack_cols].melt(id_vars="Country", var_name="Source", value_name="Pct")

        chart = (
            alt.Chart(long)
            .mark_bar()
            .encode(
                x=alt.X("sum(Pct):Q", title="Percentage"),
                y=alt.Y("Country:N", sort="-x"),
                color=alt.Color("Source:N", title="Energy Source"),
                tooltip=["Country", "Source", alt.Tooltip("Pct:Q", format=".2f")]
            )
            .properties(width=900, height=30 * top_n, title="Stacked Renewable Mix (Top countries)")
        )
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(top_df.drop(columns=["selected_sum"]).reset_index(drop=True).style.format({c: "{:.2f}" for c in stack_cols}))

# -----------------------
# 상세 테이블
# -----------------------
else:
    st.markdown("### 전체 데이터")
    st.dataframe(df.style.format({c: "{:.2f}" for c in pct_cols}))

# -----------------------
# 하단: 설명 및 다운로드
# -----------------------
st.markdown("---")
st.markdown(
    "앱 사용 팁:  \n"
    "- CSV는 `Country` 컬럼과 비율(%) 혹은 숫자형 컬럼들이 포함되어야 합니다.  \n"
    "- 업로드 없이 기본 샘플을 사용하려면 같은 디렉터리에 `renewables_by_country.csv` 파일을 둡니다.  \n"
)
# provide a download link for currently loaded data
@st.cache_data
def convert_df_to_csv(dframe):
    return dframe.to_csv(index=False).encode("utf-8")

csv_data = convert_df_to_csv(df)
st.download_button("📥 현재 데이터 CSV 다운로드", data=csv_data, file_name="renewables_by_country_used.csv", mime="text/csv")

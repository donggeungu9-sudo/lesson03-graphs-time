

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data():
# 1년치(365일) 일별 박스오피스 10위권 기록을 불러옵니다.
df = pd.read_csv(DATA_URL)
# 여덟 자리 숫자로 된 날짜 열을 진짜 날짜로 바꿉니다.
df["날_짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
return df

df = load_data()


st.header("1. 한 영화의 흥행 곡선")

드롭다운으로 영화를 고릅니다.

movie_list = sorted(df["영화명"].unique())
movie = st.selectbox("영화를 고르세요", movie_list)

one = df[df["영화명"] == movie].sort_values("날짜")
fig1 = px.line(one, x="날짜", y="일관객", markers=True)
fig1.update_traces(hovertemplate="날짜 %{x|%Y-%m-%d}



관객 %{y:,}명")
st.plotly_chart(fig1, use_container_width=True)

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

st.markdown("---")


st.header("2. 관객수 상위 5개 영화 흥행 비교")


top5_movies = (
df.groupby("영화명")["일관객"]
.sum()
.nlargest(5)
.index
)
df_top5 = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
df_top5,
x="날짜",
y="일관객",
color="영화명",
markers=True
)
fig2.update_traces(hovertemplate="영화명: %{fullData.name}



날짜: %{x|%Y-%m-%d}



관객: %{y:,}명")
st.plotly_chart(fig2, use_container_width=True)

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

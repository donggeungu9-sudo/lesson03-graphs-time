import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    # 1년치(365일) 일별 박스오피스 10위권 기록을 불러옵니다.
    df = pd.read_csv(DATA_URL)
    # 여덟 자리 숫자로 된 날짜 열을 진짜 날짜로 바꿉니다.
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
    return df


df = load_data()

# ── 그래프 1. 영화 하나의 흥행 곡선 ──────────────────────────
st.header("1. 한 영화의 흥행 곡선")

# 드롭다운으로 영화를 고릅니다.
movie_list = sorted(df["영화명"].unique())
movie = st.selectbox("영화를 고르세요", movie_list)

one = df[df["영화명"] == movie].sort_values("날짜")
fig1 = px.line(one, x="날짜", y="일관객", markers=True)
fig1.update_traces(hovertemplate="날짜 %{x|%Y-%m-%d}<br>관객 %{y:,}명<extra></extra>")
st.plotly_chart(fig1, use_container_width=True)

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 2. 상위 5개 영화 흥행 곡선 비교 ──────────────────
st.header("2. 상위 5개 영화 흥행 비교")

# 기간 내 일관객 합계가 가장 큰 5편 선정
top5_movies = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
df_top5 = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(df_top5, x="날짜", y="일관객", color="영화명", markers=True)
fig2.update_traces(
    hovertemplate="영화: %{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>관객: %{y:,}명<extra></extra>"
)
st.plotly_chart(fig2, use_container_width=True)

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 3. 일별 총 관객수 추이 (영역 그래프) ──────────────
st.header("3. 일별 총 관객수 추이")

# 날짜별로 그날 10위권 일관객의 합계를 구합니다.
daily_total = df.groupby("날짜", as_index=False)["일관객"].sum()
daily_total = daily_total.sort_values("날짜")

# 합계가 가장 컸던 날 3일을 찾습니다.
top3_days = daily_total.nlargest(3, "일관객")

fig3 = px.area(daily_total, x="날짜", y="일관객")
fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>총 관객: %{y:,}명<extra></extra>"
)

# 합계가 가장 컸던 날 3일을 그래프 위에 표시하고 날짜를 적어 줍니다.
for _, row in top3_days.iterrows():
    d_str = row["날짜"].strftime("%Y-%m-%d")
    val = row["일관객"]
    fig3.add_annotation(
        x=row["날짜"],
        y=val,
        text=f"{d_str}<br>({val:,}명)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="red",
        font=dict(color="red", size=10),
    )

st.plotly_chart(fig3, use_container_width=True)

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 4. 영화별 총 관객수 TOP 10 (가로 막대그래프) ─────────
st.header("4. 영화별 총 관객수 TOP 10")

# 영화별 총 관객수 합계와 10위권 진입 일수(데이터 개수) 계산
movie_stats = (
    df.groupby("영화명")
    .agg(
        총관객수=("일관객", "sum"),
        진입일수=("날짜", "count"),
    )
    .reset_index()
)

# 관객이 많은 순으로 상위 10편 추출
top10_df = movie_stats.nlargest(10, "총관객수").sort_values("총관객수", ascending=True)

fig4 = px.bar(
    top10_df,
    x="총관객수",
    y="영화명",
    orientation="h",
    text="총관객수",
    hover_data={"진입일수": True, "총관객수": ":,"},
)

# y축(영화명) 순서를 관객수 많은 순이 위로 오도록 설정
fig4.update_layout(yaxis=dict(categoryorder="array", categoryarray=top10_df["영화명"].tolist()))
fig4.update_traces(
    texttemplate="%{x:,}명",
    textposition="outside",
    hovertemplate="영화명: %{y}<br>총 관객수: %{x:,}명<br>10위권 진입 일수: %{customdata[0]}일<extra></extra>",
)
st.plotly_chart(fig4, use_container_width=True)

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 5. 월 × 요일별 일관객 합계 히트맵 ──────────────
st.header("5. 월 × 요일별 관객수 히트맵")

# 날짜에서 월과 요일 추출
df_hm = df.copy()
df_hm["월"] = df_hm["날짜"].dt.month.astype(str) + "월"
df_hm["요일번호"] = df_hm["날짜"].dt.dayofweek  # 0: 월요일 ~ 6: 일요일
days_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
days_dict = {i: name for i, name in enumerate(days_order)}
df_hm["요일"] = df_hm["요일번호"].map(days_dict)

# 월 × 요일별 일관객 합계 피벗 테이블 생성
heatmap_data = (
    df_hm.groupby(["월", "요일", "요일번호"], as_index=False)["일관객"]
    .sum()
    .sort_values(["월", "요일번호"])
)

# 월 순서 정렬을 위한 리스트 (데이터에 존재하는 월 순서대로)
months_order = sorted(df_hm["날짜"].dt.month.unique())
months_str_order = [f"{m}월" for m in months_order]

fig5 = px.imshow(
    heatmap_data.pivot(index="요일", columns="월", values="일관객").reindex(index=days_order, columns=months_str_order),
    labels=dict(x="월", y="요일", color="일관객 합계"),
    color_continuous_scale="Reds",
    aspect="auto",
)
fig5.update_traces(hovertemplate="월: %{x}<br>요일: %{y}<br>일관객 합계: %{z:,}명<extra></extra>")
st.plotly_chart(fig5, use_container_width=True)

st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 섹션 6. 날짜별 박스오피스 순위 ──────────────────────────
st.header("6. 날짜별 박스오피스 순위표")

# 고를 수 있는 가장 늦은 날짜는 어제까지 (오늘 건 집계 전)
max_date = df["날짜"].max().date()
yesterday = datetime.date.today() - datetime.timedelta(days=1)
default_date = min(max_date, yesterday)
min_date = df["날짜"].min().date()

selected_date = st.date_input(
    "날짜를 고르세요",
    value=default_date,
    min_value=min_date,
    max_value=max_date,
)

# 선택한 날짜의 데이터 필터링
day_df = df[df["날짜"].dt.date == selected_date].sort_values("순위")

if day_df.empty:
    st.warning("그날은 아직 집계 전입니다")
else:
    display_rows = []
    for _, row in day_df.iterrows():
        rank_inten = row.get("rankInten", 0)
        if rank_inten > 0:
            rank_arrow = f"🔴 ▲{rank_inten}"
        elif rank_inten < 0:
            rank_arrow = f"🔵 ▼{abs(rank_inten)}"
        else:
            rank_arrow = "-"

        movie_name = row["영화명"]
        if row["누적관객"] >= 1000000:
            movie_name = f"🏆 {movie_name}"

        display_rows.append(
            {
                "순위": row["순위"],
                "전일대비": rank_arrow,
                "영화명": movie_name,
                "일관객": f"{row['일관객']:,}명",
                "누적관객": f"{row['누적관객']:,}명",
                "스크린수": f"{row['스크린수']:,}개",
                "상영횟수": f"{row['상영횟수']:,}회",
            }
        )

    st.dataframe(
        pd.DataFrame(display_rows), hide_index=True, use_container_width=True
    )

st.caption("이 표로 알 수 있는 것: (한 문장으로 적어 보세요)")

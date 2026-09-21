import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
page_title="영화 데이터 그래프 도감 1 - 시간",
page_icon="🎬",
layout="wide"
)


st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("1년치(365일) 일별 박스오피스 10위권 기록을 바탕으로 시간 흐름에 따른 영화 데이터를 시각화하는 공간입니다.")


@st.cache_data
def load_data():
url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
df = pd.read_csv(url, dtype={"날짜": str})

df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

for col in ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")
        
return df



try:
df = load_data()
except Exception as e:
st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
st.stop()




st.markdown("---")
st.header("📈 구역 1: 영화별 일관객 변화 (선 그래프)")
st.markdown("특정 영화를 선택하여 1년 동안의 일일 관객수 변화 추이를 확인합니다.")

if not df.empty and "영화명" in df.columns:
# 영화 목록 정렬 (데이터에 존재하는 고유 영화명)
movie_list = sorted(df["영화명"].dropna().unique())

# 드롭다운 생성 (기본값으로 첫 번째 영화 선택 혹은 안내)
selected_movie = st.selectbox("영화를 선택하세요", movie_list, key="selected_movie_zone1")

if selected_movie:
    # 선택한 영화의 데이터 필터링 및 날짜순 정렬
    movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")
    
    if not movie_df.empty:
        # 플롯리(Plotly) 선 그래프 생성
        fig = px.line(
            movie_df,
            x="날짜",
            y="일관객",
            markers=True,
            title=f"'{selected_movie}' 날짜별 일관객 변화",
            labels={"날짜": "날짜", "일관객": "일일 관객수"}
        )
        
        # 마우스 호버 설정 및 디자인 다듬기
        fig.update_traces(
            hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
        )
        fig.update_layout(
            xaxis_title="날짜",
            yaxis_title="일관객 수",
            hovermode="x unified"
        )
        
        # 그래프 출력
        st.plotly_chart(fig, use_container_width=True)
        
        # '이 그래프로 알 수 있는 것' 문구 자리
        st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'은(는) 상영 기간 동안 관객수가 특정 시기에 집중되거나 완만한 유지세를 보이는 등 고유한 흥행 주기 패턴을 나타냅니다.")
    else:
        st.warning("선택한 영화의 데이터가 존재하지 않습니다.")


else:
st.warning("데이터에 영화명 정보가 없습니다.")




st.markdown("---")
st.markdown("### 🔮 앞으로 추가될 구역 안내")
st.caption("새로운 시간별·장르별·비교 그래프들이 이 아래에 순차적으로 업데이트될 예정입니다.")

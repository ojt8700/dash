import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ページ設定
st.set_page_config(layout="centered")
st.title("📈 月次指標推移")

# データ読み込み
github_csv_url = "https://raw.githubusercontent.com/ojt8700/dash/main/getuji.csv"
try:
    df = pd.read_csv(github_csv_url)
except Exception as e:
    st.error(f"CSVの読み込みに失敗しました: {e}")
    st.stop()

# 整形
df["date"] = pd.to_datetime(df["date"], format="%Y/%m/%d", errors="coerce")
df["market"] = df["market"].astype(str).str.strip()

# プレビュー
st.subheader("🔍 データ preview")
st.dataframe(df.head(), use_container_width=True)

# UI
with st.expander("📊 表示設定（クリックで開く）", expanded=True):
    markets = sorted(df["market"].dropna().unique())
    default_index = 1 if len(markets) >= 1 else 0

    col1, col2 = st.columns(2)
    with col1:
        left1 = st.selectbox("左軸 主", options=["なし"] + markets, index=default_index)
        left2 = st.selectbox("左軸 副", options=["なし"] + markets, index=0)
    with col2:
        right1 = st.selectbox("右軸 主", options=["なし"] + markets, index=0)
        right2 = st.selectbox("右軸 副", options=["なし"] + markets, index=0)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        left_range_input = st.text_input("左軸レンジ (例：100-200)", value="")
    with col4:
        right_range_input = st.text_input("右軸レンジ (例：50-150)", value="")

# 関数：マーケット名でフィルタ
def get_df(market_name):
    if market_name != "なし":
        return df[df["market"] == market_name]
    else:
        return pd.DataFrame()

# 各軸のデータ取得
df_l1 = get_df(left1)
df_l2 = get_df(left2)
df_r1 = get_df(right1)
df_r2 = get_df(right2)

# ❗データなし警告
if df_l1.empty and df_l2.empty and df_r1.empty and df_r2.empty:
    st.warning("📌 表示対象の指標が選ばれていません。左軸または右軸にデータを選択してください。")

# グラフ生成
fig = make_subplots(specs=[[{"secondary_y": True}]])

# データが1つでもある場合はプロット
if not df_l1.empty:
    fig.add_trace(go.Scatter(x=df_l1["date"], y=df_l1["price"], name=f"{left1} (左主)", mode="lines+markers", line=dict(color="blue")), secondary_y=False)
if not df_l2.empty:
    fig.add_trace(go.Scatter(x=df_l2["date"], y=df_l2["price"], name=f"{left2} (左副)", mode="lines+markers", line=dict(color="cyan", dash="dash")), secondary_y=False)
if not df_r1.empty:
    fig.add_trace(go.Scatter(x=df_r1["date"], y=df_r1["price"], name=f"{right1} (右主)", mode="lines+markers", line=dict(color="red")), secondary_y=True)
if not df_r2.empty:
    fig.add_trace(go.Scatter(x=df_r2["date"], y=df_r2["price"], name=f"{right2} (右副)", mode="lines+markers", line=dict(color="orange", dash="dot")), secondary_y=True)

# ❗何もプロットされていない場合は注釈を表示
if df_l1.empty and df_l2.empty and df_r1.empty and df_r2.empty:
    fig.add_annotation(
        text="📉 データが選択されていません",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray")
    )

# 軸レンジパース
def parse_range(inp):
    try:
        parts = inp.split('-')
        if len(parts) == 2:
            lo = float(parts[0].strip())
            hi = float(parts[1].strip())
            return [lo, hi]
    except:
        pass
    return None

left_range = parse_range(left_range_input)
right_range = parse_range(right_range_input)

# 軸設定
fig.update_yaxes(title_text="左軸価格", secondary_y=False, range=left_range)
fig.update_yaxes(title_text="右軸価格", secondary_y=True, range=right_range)
fig.update_xaxes(title_text="年月")

# グラフ外観設定
fig.update_layout(
    title_text="📊 月次指標推移",
    height=400,
    margin=dict(l=10, r=10, t=40, b=80),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5,
        font=dict(size=10)
    ),
    font=dict(size=12),
)

# 不要なモードバー削除
config = {
    "displayModeBar": True,
    "modeBarButtonsToRemove": [
        "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"
    ],
    "displaylogo": False
}

# グラフ表示
st.plotly_chart(fig, use_container_width=True, config=config)

# ✅ リセットボタン
if st.button("🔄 グラフ表示をリセット"):
    st.experimental_rerun()

# 元データ表示
with st.expander("📅 月次データを表示"):
    st.dataframe(df, use_container_width=True)

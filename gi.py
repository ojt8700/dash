import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("月次指標推移（左右各２軸+レンジ指定）")

# GitHub 上の CSV ファイルを読み込み
github_csv_url = "https://raw.githubusercontent.com/ojt8700/dash/main/getuji.csv"
try:
    df = pd.read_csv(github_csv_url)
except Exception as e:
    st.error(f"CSVの読み込みに失敗しました: {e}")
    st.stop()

df["date"] = pd.to_datetime(df["date"], format="%Y/%m/%d", errors="coerce")
df["market"] = df["market"].astype(str).str.strip()

st.subheader("データ preview（最初の数行）")
st.dataframe(df.head())

# サイドバーで左右それぞれ２市場まで選択
with st.sidebar:
    st.header("指標選択（左軸２本／右軸２本）")
    markets = sorted(df["market"].dropna().unique())
    # 左軸
    left1 = st.selectbox("左軸 主", options=["なし"] + markets)
    left2 = st.selectbox("左軸 副", options=["なし"] + markets)
    # 右軸
    right1 = st.selectbox("右軸 主", options=["なし"] + markets)
    right2 = st.selectbox("右軸 副", options=["なし"] + markets)

    st.markdown("---")
    st.header("Y軸レンジを指定（任意）")
    # 左軸レンジ
    left_range_input = st.text_input("左軸レンジ (例：100-200)", value="")
    # 右軸レンジ
    right_range_input = st.text_input("右軸レンジ (例：50-150)", value="")

def get_df(market_name):
    if market_name != "なし":
        return df[df["market"] == market_name]
    else:
        return pd.DataFrame()

df_l1 = get_df(left1)
df_l2 = get_df(left2)
df_r1 = get_df(right1)
df_r2 = get_df(right2)

# グラフ作成: 左右に副軸ありの make_subplots
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 左軸 主
if not df_l1.empty:
    fig.add_trace(
        go.Scatter(x=df_l1["date"], y=df_l1["price"],
                   name=f"{left1} (左主)",
                   mode="lines+markers",
                   line=dict(color="blue")),
        secondary_y=False
    )
# 左軸 副
if not df_l2.empty:
    fig.add_trace(
        go.Scatter(x=df_l2["date"], y=df_l2["price"],
                   name=f"{left2} (左副)",
                   mode="lines+markers",
                   line=dict(color="cyan", dash="dash")),
        secondary_y=False
    )
# 右軸 主
if not df_r1.empty:
    fig.add_trace(
        go.Scatter(x=df_r1["date"], y=df_r1["price"],
                   name=f"{right1} (右主)",
                   mode="lines+markers",
                   line=dict(color="red")),
        secondary_y=True
    )
# 右軸 副
if not df_r2.empty:
    fig.add_trace(
        go.Scatter(x=df_r2["date"], y=df_r2["price"],
                   name=f"{right2} (右副)",
                   mode="lines+markers",
                   line=dict(color="orange", dash="dot")),
        secondary_y=True
    )

fig.update_layout(title_text="月次指標推移（左／右 各軸２本）")
fig.update_xaxes(title_text="年月")

# レンジ入力パース関数
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

# Y軸タイトルと範囲設定
# 左軸
fig.update_yaxes(
    title_text="左軸価格",
    secondary_y=False,
    range=left_range if left_range is not None else None
)
# 右軸
fig.update_yaxes(
    title_text="右軸価格",
    secondary_y=True,
    range=right_range if right_range is not None else None
)

fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

if st.checkbox("月次データ表示"):
    st.dataframe(df)

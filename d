import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("木材価格と経済指標の時系列比較")

# --- 木材価格データのアップロード ---
uploaded_price = st.file_uploader("木材価格データ (CSV) をアップロード", type="csv", key="price")
if not uploaded_price:
    st.info("最初に木材価格データをアップロードしてください")
    st.stop()
df_price = pd.read_csv(uploaded_price)

# --- 経済指標データのアップロード ---
uploaded_econ = st.file_uploader("経済指標データ (market、date、priceの形式) をアップロード", type="csv", key="econ")
if not uploaded_econ:
    st.info("経済指標データをアップロードしてください")
    st.stop()
df_econ = pd.read_csv(uploaded_econ)

# --- 日付処理 ---
df_price["date"] = pd.to_datetime(df_price["date"], format="%Y/%m/%d", errors="coerce")
df_econ["date"] = pd.to_datetime(df_econ["date"], format="%Y/%m/%d", errors="coerce")

for col in ["market", "species", "grade", "diameter", "length"]:
    if col in df_price.columns:
        df_price[col] = df_price[col].astype(str).str.strip()
if "market" in df_econ.columns:
    df_econ["market"] = df_econ["market"].astype(str).str.strip()

st.subheader("木材価格データ プレビュー")
st.dataframe(df_price.head())

st.subheader("経済指標データ プレビュー")
st.dataframe(df_econ.head())

# --- サイドバー ---
with st.sidebar:
    st.header("木材価格のフィルター条件（複数選択可）")
    sel_markets_price = st.multiselect("木材価格の市場を選択", options=sorted(df_price["market"].dropna().unique()))
    sel_species = st.multiselect("樹種を選択", options=sorted(df_price["species"].dropna().unique()))
    sel_grades = st.multiselect("グレードを選択", options=sorted(df_price["grade"].dropna().unique()))
    sel_diameters = st.multiselect("径級を選択", options=sorted(df_price["diameter"].dropna().unique()))
    sel_lengths = st.multiselect("長さを選択", options=sorted(df_price["length"].dropna().unique()))

    st.markdown("---")
    st.header("プロットする経済指標のmarketを選択 (右軸)")
    econ_markets = sorted(df_econ["market"].dropna().unique())
    sel_markets_econ = st.multiselect("経済指標のmarketを選択（複数可）", options=econ_markets, default=[])

    st.markdown("---")
    st.header("色分け用の軸（木材価格側）")
    color_options = ["なし"] + [col for col in ["market", "species", "grade", "diameter", "length"] if col in df_price.columns]
    color_by = st.selectbox("色分けする項目を選択", options=color_options)

# --- 木材価格データのフィルタリング ---
filtered_price = df_price.copy()
if sel_markets_price:
    filtered_price = filtered_price[filtered_price["market"].isin(sel_markets_price)]
if sel_species:
    filtered_price = filtered_price[filtered_price["species"].isin(sel_species)]
if sel_grades:
    filtered_price = filtered_price[filtered_price["grade"].isin(sel_grades)]
if sel_diameters:
    filtered_price = filtered_price[filtered_price["diameter"].isin(sel_diameters)]
if sel_lengths:
    filtered_price = filtered_price[filtered_price["length"].isin(sel_lengths)]
filtered_price = filtered_price.reset_index(drop=True)

st.subheader(f"絞り込み後の木材価格件数: {len(filtered_price)}")

# --- グラフ作成 ---
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 左軸：木材価格
if not filtered_price.empty:
    if color_by != "なし":
        groups = filtered_price.groupby(color_by)
    else:
        groups = [(None, filtered_price)]

    for group_name, group_df in groups:
        name = f"{group_name}" if group_name is not None else "木材価格"
        fig.add_trace(
            go.Scatter(
                x=group_df["date"],
                y=group_df["price"],
                name=name,
                mode="lines+markers",
            ),
            secondary_y=False,
        )

# 右軸：経済指標（marketごとに色分け）
if sel_markets_econ:
    filtered_econ = df_econ[df_econ["market"].isin(sel_markets_econ)]
    if not filtered_econ.empty:
        groups_econ = filtered_econ.groupby("market")
        for econ_market, econ_df in groups_econ:
            econ_df_sorted = econ_df.sort_values("date")
            fig.add_trace(
                go.Scatter(
                    x=econ_df_sorted["date"],
                    y=econ_df_sorted["price"],
                    name=f"経済指標: {econ_market}",
                    mode="lines+markers",
                    line=dict(dash="dash"),
                ),
                secondary_y=True,
            )
else:
    filtered_econ = pd.DataFrame()  # 空のDataFrame

# レイアウト調整
fig.update_layout(
    title_text="木材価格 vs 経済指標",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
fig.update_xaxes(title_text="年月")
fig.update_yaxes(title_text="木材価格", secondary_y=False)
fig.update_yaxes(title_text="経済指標価格", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# --- 表示オプション ---
if st.checkbox("木材価格データ（price列）を表示"):
    cols_to_show = ["date", "price"]
    if color_by != "なし" and color_by in filtered_price.columns:
        cols_to_show.append(color_by)
    st.dataframe(filtered_price[cols_to_show])

if st.checkbox("経済指標データを表示"):
    st.dataframe(filtered_econ)

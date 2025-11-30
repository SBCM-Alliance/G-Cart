import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(
    page_title="G-Cart | 公共事業マッチング",
    page_icon="🛒",
    layout="wide"
)

# --- 1. データ定義 (SBCM経済学に基づくモックデータ) ---

# 自分（ログイン中の社長）の設定
MY_COMPANY = {
    "name": "鈴木土木工業 (あなた)",
    "location": "柏市",
    "type": "土木一式",
    "capacity": 30000000,  # キャパ3000万円
    "credit": "A"
}

# 商品リスト（公共事業案件）
PROJECTS = [
    {
        "id": 101,
        "name": "市道123号線 舗装改修工事",
        "location": "柏市・北エリア",
        "budget": 50000000,  # 5,000万円
        "image": "🚧",
        "tags": ["土木", "舗装", "警備"],
        "desc": "生活道路の老朽化に伴う全面舗装。工期3ヶ月。"
    },
    {
        "id": 102,
        "name": "柏の葉公園 公衆トイレ新設",
        "location": "柏市・西エリア",
        "budget": 80000000,  # 8,000万円
        "image": "🏗️",
        "tags": ["建築", "水道", "電気"],
        "desc": "バリアフリー対応の公衆トイレ設置。SBCM推奨案件。"
    },
    {
        "id": 103,
        "name": "小学校 通学路ガードレール設置",
        "location": "柏市・中央",
        "budget": 15000000,  # 1,500万円
        "image": "🛡️",
        "tags": ["土木", "資材"],
        "desc": "児童の安全確保のための緊急工事。"
    }
]

# パートナー候補（地域の中小企業データベース）
PARTNERS = [
    {"name": "田中舗装ロード", "type": "舗装", "location": "柏市", "rating": 4.8, "capacity": 30000000},
    {"name": "柏警備保障", "type": "警備", "location": "柏市", "rating": 4.5, "capacity": 5000000},
    {"name": "松戸電気サービス", "type": "電気", "location": "松戸市", "rating": 4.2, "capacity": 20000000},
    {"name": "流山水道メンテナンス", "type": "水道", "location": "流山市", "rating": 4.6, "capacity": 15000000},
    {"name": "ちば建設資材", "type": "資材", "location": "柏市", "rating": 4.9, "capacity": 50000000},
]

# --- 2. UI構築 ---

# ヘッダー
st.title("🛒 G-Cart (Government Cart)")
st.caption(f"ログイン中: **{MY_COMPANY['name']}** | キャパシティ残: ¥{MY_COMPANY['capacity']:,} | エリア: {MY_COMPANY['location']}")
st.markdown("---")

# サイドバー（検索フィルタ）
with st.sidebar:
    st.header("🔍 案件検索")
    area_filter = st.selectbox("エリア", ["すべて", "柏市", "松戸市", "流山市"])
    type_filter = st.multiselect("工種カテゴリ", ["土木", "建築", "舗装", "電気", "水道"], default=["土木", "舗装"])
    st.info("💡 SBCMアルゴリズムにより、あなたのキャパシティと地域の富の残留率($R_{block}$)を最大化する案件を表示しています。")

# メイン画面：案件一覧 (Amazon風)
st.subheader("おすすめの公共事業")

cols = st.columns(3)
for i, proj in enumerate(PROJECTS):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"## {proj['image']}")
            st.markdown(f"### {proj['name']}")
            
            # 予算表示
            st.metric("発注金額 (予算)", f"¥{proj['budget']:,}")
            
            st.markdown(f"**場所:** {proj['location']}")
            st.markdown(f"**必要工種:** {', '.join(proj['tags'])}")
            
            # SBCM分析（あなたの会社単独で受けられるか？）
            shortage = proj['budget'] - MY_COMPANY['capacity']
            
            if shortage > 0:
                st.warning(f"⚠️ 単独受注不可 (不足: ¥{shortage:,})")
                button_label = "🤝 チームを組んで受注する"
                button_type = "primary"
            else:
                st.success("✅ 単独受注可能")
                button_label = "📦 今すぐ入札する"
                button_type = "secondary"

            # ボタン処理
            if st.button(button_label, key=f"btn_{proj['id']}", type=button_type):
                st.session_state['selected_project'] = proj
                st.rerun()

# --- 3. チーム結成モーダル (詳細画面) ---

if 'selected_project' in st.session_state:
    p = st.session_state['selected_project']
    
    st.markdown("---")
    st.header(f"🤝 チームビルディング: {p['name']}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### あなたの状況")
        st.info(f"あなたのキャパ: ¥{MY_COMPANY['capacity']:,}")
        st.error(f"案件予算: ¥{p['budget']:,}")
        
        needed = p['budget'] - MY_COMPANY['capacity']
        st.markdown(f"### ⚡ 不足キャパ: ¥{needed:,}")
        st.markdown("このままでは受注できません。以下のパートナーとJV（連合）を組みましょう。")

    with col2:
        st.markdown("### 🤖 AIレコメンド (SBCMマッチング)")
        st.markdown("**「この案件を見ている会社は、こんな会社と組んでいます」**")
        
        # マッチングロジック
        # 1. 不足している「タグ（工種）」を持っている
        # 2. 場所が近い（柏市優先）→ ストロー効果防止
        
        team_budget = MY_COMPANY['capacity']
        team_members = [MY_COMPANY['name']]
        
        for partner in PARTNERS:
            # 必要なタグを持っているか判定
            is_needed_type = partner['type'] in p['tags']
            # すでに足りているか
            is_budget_short = team_budget < p['budget']
            
            if is_needed_type and is_budget_short:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 2])
                    c1.markdown(f"**{partner['name']}** ({partner['type']})")
                    c1.caption(f"📍{partner['location']} | ⭐{partner['rating']}")
                    c2.metric("余力", f"¥{partner['capacity']:,}")
                    
                    if c3.button("連絡・オファー", key=f"offer_{partner['name']}"):
                        st.toast(f"{partner['name']} にオファーを送信しました！")
                        team_budget += partner['capacity']
                        team_members.append(partner['name'])

        # チーム結成状況
        st.markdown("---")
        progress = min(1.0, team_budget / p['budget'])
        st.progress(progress, text=f"チーム総力: ¥{team_budget:,} / 必要: ¥{p['budget']:,}")
        
        if team_budget >= p['budget']:
            st.success("🎉 基準クリア！このチームで入札可能です")
            if st.button("🚀 連合体(JV)として入札を確定する", type="primary"):
                st.balloons()
                st.markdown(f"""
                ### ✅ 入札完了
                スマートコントラクトが発行されました。
                - **元請け:** {', '.join(team_members)} (JV)
                - **地域内残留率($R_{{block}}$):** 98% (Excellent!)
                - **歪み指数($D_{{index}}$):** 1.02 (適正)
                
                東京のゼネコンを経由せず、地域に富が循環します。
                """)
        else:
            st.warning("あと少しキャパシティが足りません。他のパートナーを探してください。")

    # キャンセルボタン
    if st.button("一覧に戻る"):
        del st.session_state['selected_project']
        st.rerun()

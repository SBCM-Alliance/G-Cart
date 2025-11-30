import streamlit as st
import pandas as pd
import time

# --- 0. アプリ設定 ---
st.set_page_config(
    page_title="G-Cart | バーチャル・ゼネコン",
    page_icon="🏗️",
    layout="wide"
)

# ==========================================
# ⚙️ 設定エリア: 自分の環境に合わせて書き換えてください
# ==========================================

# 1. Googleスプレッドシートの「ウェブに公開」したCSV URL
# ※ テスト用にダミーデータが入ったシートを用意しています。
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtWE10eHmfLAKN-RmoNYL1Ypjt0C7XallxW3ilRrqphFloElxE7BPq32SzvNk5T2glaLcsSwcblH6w/pub?gid=0&single=true&output=csv" 
# (注意: 上記はダミーURLです。自分のURLがない場合は、下部の「ダミーデータ生成」が動きます)

# 2. GoogleフォームのURL (パートナー登録用)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTyYcQSVJIva0DSwU0agP5a-M07atLkcXyvBaKQOqADlKV2A/viewform?usp=sharing&ouid=105061654233557137452"

# 3. ログイン中のユーザー設定 (あなたの会社)
MY_COMPANY = {
    "name": "出木杉土木工業 (あなた)",
    "location": "柏市",
    "capacity": 30000000,  # 現在の施工余力: 3,000万円
}

# 4. 公共事業案件リスト (本来は役所APIから取得)
PROJECTS = [
    {
        "id": 101,
        "name": "市道123号線 舗装改修工事",
        "location": "柏市・北エリア",
        "budget": 50000000,
        "image": "🚧",
        "tags": ["舗装", "警備"],
        "desc": "生活道路の老朽化に伴う全面舗装。工期3ヶ月。"
    },
    {
        "id": 102,
        "name": "柏の葉公園 公衆トイレ新設",
        "location": "柏市・西エリア",
        "budget": 80000000,
        "image": "🚽",
        "tags": ["建築", "水道", "電気"],
        "desc": "バリアフリー対応の公衆トイレ設置。"
    },
    {
        "id": 103,
        "name": "小学校 通学路ガードレール設置",
        "location": "柏市・中央",
        "budget": 15000000,
        "image": "🛡️",
        "tags": ["土木", "資材"],
        "desc": "児童の安全確保のための緊急工事。"
    }
]

# ==========================================
# 🛠️ バックエンドロジック (SBCMエンジン)
# ==========================================

@st.cache_data(ttl=60)
def load_partners():
    """
    Googleスプレッドシートからパートナー企業を読み込む
    エラー時はデモ用のダミーデータを返す
    """
    try:
        df = pd.read_csv(SHEET_URL)
        # スプレッドシートのカラム名をアプリ用に統一
        # ※ フォームの質問項目に合わせて調整してください
        df = df.rename(columns={
            "会社名": "name",
            "得意工種": "type",
            "エリア": "location",
            "施工余力": "capacity"
        })
        return df.to_dict('records')
    except Exception:
        # シートがない場合のデモ用データ
        return [
            {"name": "田中舗装ロード", "type": "舗装", "location": "柏市", "capacity": 30000000},
            {"name": "柏警備保障", "type": "警備", "location": "柏市", "capacity": 5000000},
            {"name": "松戸電気サービス", "type": "電気", "location": "松戸市", "capacity": 20000000},
            {"name": "流山水道メンテナンス", "type": "水道", "location": "流山市", "capacity": 15000000},
            {"name": "ちば建設資材", "type": "資材", "location": "柏市", "capacity": 50000000},
            {"name": "常盤建築", "type": "建築", "location": "柏市", "capacity": 40000000},
        ]

# データをロード
PARTNERS = load_partners()

# セッション状態の初期化
if 'team' not in st.session_state:
    st.session_state['team'] = []
if 'team_budget' not in st.session_state:
    st.session_state['team_budget'] = MY_COMPANY['capacity']

# ==========================================
# 📱 フロントエンド (UI)
# ==========================================

# サイドバー
with st.sidebar:
    st.header("G-Cart メニュー")
    st.markdown(f"👤 **{MY_COMPANY['name']}**")
    st.markdown(f"💰 余力: ¥{MY_COMPANY['capacity']:,}")
    st.divider()
    
    st.markdown("### 仲間を増やす")
    st.markdown("知り合いの社長にこのURLを送ってください")
    st.link_button("📝 パートナー登録フォームへ", FORM_URL)
    
    st.divider()
    st.info("💡 **SBCM経済学**に基づき、地域内残留率($R_{block}$)が高くなるパートナーを優先表示しています。")

# メイン画面タイトル
st.title("🛒 G-Cart (Government Cart)")
st.caption("バーチャル・ゼネコンシステム powered by SBCM")

# --- 画面切り替えロジック ---

if 'selected_project' not in st.session_state:
    # ----------------------------------
    # 画面A: 公共事業一覧 (Amazon風)
    # ----------------------------------
    st.subheader("📦 おすすめの公共事業")
    
    cols = st.columns(3)
    for i, proj in enumerate(PROJECTS):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"## {proj['image']}")
                st.markdown(f"**{proj['name']}**")
                st.caption(f"📍 {proj['location']}")
                
                st.metric("予算", f"¥{proj['budget']:,}")
                
                # キャパ判定
                shortage = proj['budget'] - MY_COMPANY['capacity']
                
                if shortage > 0:
                    st.warning(f"⚠️ 単独不可 (不足 ¥{shortage:,})")
                    btn_label = "🤝 チーム結成"
                    btn_type = "primary"
                else:
                    st.success("✅ 単独受注可")
                    btn_label = "入札へ進む"
                    btn_type = "secondary"
                
                if st.button(btn_label, key=f"p_{proj['id']}", type=btn_type):
                    st.session_state['selected_project'] = proj
                    # チーム状態をリセット
                    st.session_state['team'] = []
                    st.session_state['team_budget'] = MY_COMPANY['capacity']
                    st.rerun()

else:
    # ----------------------------------
    # 画面B: チームビルディング (Tinder/マッチング風)
    # ----------------------------------
    p = st.session_state['selected_project']
    
    st.button("← 一覧に戻る", on_click=lambda: st.session_state.pop('selected_project'))
    st.markdown("---")
    
    col_L, col_R = st.columns([1, 1.5])
    
    with col_L:
        st.header(f"{p['image']} {p['name']}")
        st.markdown(f"**予算: ¥{p['budget']:,}**")
        st.markdown(f"**必要工種:** {', '.join(p['tags'])}")
        
        st.divider()
        st.subheader("現在のチーム状況")
        
        # プログレスバー
        progress = min(1.0, st.session_state['team_budget'] / p['budget'])
        st.progress(progress)
        st.markdown(f"**総キャパ: ¥{st.session_state['team_budget']:,}** / 必要: ¥{p['budget']:,}")
        
        # チームメンバー表示
        st.markdown("#### メンバー")
        st.text(f"👤 {MY_COMPANY['name']} (Owner)")
        for member in st.session_state['team']:
            st.text(f"🤝 {member['name']} ({member['type']})")

        if st.session_state['team_budget'] >= p['budget']:
            st.success("🎉 キャパシティクリア！")
            if st.button("🚀 バーチャルJVとして入札する", type="primary", use_container_width=True):
                st.balloons()
                time.sleep(1)
                st.toast("入札が完了しました！")
                st.success(f"""
                **入札完了**
                スマートコントラクトにより、受注金額は参加企業({len(st.session_state['team'])+1}社)に自動分配されます。
                - 地域内残留率: 98%
                - 中抜き: 0円
                """)
        else:
            st.warning(f"あと ¥{p['budget'] - st.session_state['team_budget']:,} 足りません")

    with col_R:
        st.subheader("🔍 AIパートナーレコメンド")
        st.info("あなたの不足キャパと工種を補う企業を検索しました")
        
        # マッチングロジック
        recommended_count = 0
        
        for partner in PARTNERS:
            # すでにチームにいたらスキップ
            if partner['name'] in [m['name'] for m in st.session_state['team']]:
                continue
            
            # 必要な工種を持っているか？
            is_needed = partner['type'] in p['tags']
            # 近所か？（ストロー効果防止）
            is_local = p['location'].split("・")[0] in partner['location']
            
            if is_needed:
                recommended_count += 1
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    
                    with c1:
                        st.markdown(f"**{partner['name']}**")
                        st.caption(f"🔧 {partner['type']} | 📍 {partner['location']}")
                        if is_local:
                            st.caption("✨ 地元企業 (SBCM推奨)")
                    
                    with c2:
                        st.metric("余力", f"¥{partner['capacity']//10000}万")
                    
                    with c3:
                        if st.button("オファー", key=f"add_{partner['name']}"):
                            st.session_state['team'].append(partner)
                            st.session_state['team_budget'] += partner['capacity']
                            st.rerun()
        
        if recommended_count == 0:
            st.write("条件に合うパートナーが見つかりませんでした。")

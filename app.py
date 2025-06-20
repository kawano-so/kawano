import streamlit as st
import pandas as pd
import datetime
import json
import os
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go

# ページ設定
st.set_page_config(
    page_title="睡眠時間管理アプリ",
    page_icon="😴",
    layout="wide"
)

# データファイルのパス
DATA_FILE = "sleep_data.json"

def load_data():
    """データを読み込む"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    """データを保存する"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_sleep_duration(bedtime, waketime):
    """睡眠時間を計算する"""
    # 日付をまたぐ場合を考慮
    if waketime < bedtime:
        # 翌日の起床時間として計算
        waketime_next_day = datetime.datetime.combine(
            datetime.date.today() + timedelta(days=1),
            waketime
        )
        bedtime_today = datetime.datetime.combine(
            datetime.date.today(),
            bedtime
        )
        duration = waketime_next_day - bedtime_today
    else:
        # 同日内の場合
        waketime_today = datetime.datetime.combine(
            datetime.date.today(),
            waketime
        )
        bedtime_today = datetime.datetime.combine(
            datetime.date.today(),
            bedtime
        )
        duration = waketime_today - bedtime_today
    
    return duration.total_seconds() / 3600  # 時間単位で返す

def get_sleep_advice(sleep_quality, sleep_duration, bedtime_hour):
    """睡眠に関するアドバイスを生成する"""
    advice = []
    
    # 睡眠の質に基づくアドバイス
    if sleep_quality <= 2:
        advice.append("😴 睡眠の質が低いようです。以下の改善策を試してみてください：")
        advice.append("• 就寝前1時間はスマートフォンやパソコンの使用を控える")
        advice.append("• 寝室の温度を18-22度に保つ")
        advice.append("• カフェインの摂取は午後2時以降控える")
        advice.append("• 軽いストレッチや瞑想を取り入れる")
    elif sleep_quality == 3:
        advice.append("😊 睡眠の質は普通です。さらに改善するために：")
        advice.append("• 規則正しい就寝・起床時間を心がける")
        advice.append("• 就寝前のリラックスタイムを作る")
    else:
        advice.append("✨ 良質な睡眠が取れています！この調子を維持しましょう")
    
    # 睡眠時間に基づくアドバイス
    if sleep_duration < 6:
        advice.append("⏰ 睡眠時間が不足しています。7-9時間の睡眠を目指しましょう")
    elif sleep_duration > 9:
        advice.append("⏰ 睡眠時間が長すぎる可能性があります。適度な睡眠時間を心がけましょう")
    
    # 就寝時間に基づくアドバイス
    if bedtime_hour > 24 or bedtime_hour < 6:  # 深夜0時以降または早朝6時前
        advice.append("🌙 就寝時間が遅いようです。22-23時頃の就寝を目指しましょう")
    elif bedtime_hour >= 22 and bedtime_hour <= 23:
        advice.append("👍 理想的な就寝時間です！")
    
    return advice

def main():
    st.title("😴 睡眠時間管理アプリ")
    st.markdown("---")
    
    # サイドバーでデータ入力
    st.sidebar.header("📝 睡眠データを記録")
    
    # 日付選択
    date = st.sidebar.date_input("日付", datetime.date.today())
    
    # 就寝時間
    bedtime = st.sidebar.time_input("就寝時間", datetime.time(23, 0))
    
    # 起床時間
    waketime = st.sidebar.time_input("起床時間", datetime.time(7, 0))
    
    # 睡眠の質（1-5段階）
    sleep_quality = st.sidebar.slider("睡眠の質", 1, 5, 3, help="1: とても悪い, 2: 悪い, 3: 普通, 4: 良い, 5: とても良い")
    
    # データ保存ボタン
    if st.sidebar.button("💾 データを保存"):
        sleep_duration = calculate_sleep_duration(bedtime, waketime)
        
        new_record = {
            "date": date.isoformat(),
            "bedtime": bedtime.strftime("%H:%M"),
            "waketime": waketime.strftime("%H:%M"),
            "sleep_duration": round(sleep_duration, 2),
            "sleep_quality": sleep_quality
        }
        
        data = load_data()
        
        # 同じ日付のデータがあれば更新、なければ追加
        existing_index = None
        for i, record in enumerate(data):
            if record["date"] == date.isoformat():
                existing_index = i
                break
        
        if existing_index is not None:
            data[existing_index] = new_record
            st.sidebar.success("データを更新しました！")
        else:
            data.append(new_record)
            st.sidebar.success("データを保存しました！")
        
        save_data(data)
        st.rerun()
    
    # メインエリア
    data = load_data()
    
    if not data:
        st.info("まだデータがありません。サイドバーから睡眠データを記録してください。")
        return
    
    # データフレームに変換
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # タブで表示を分ける
    tab1, tab2, tab3 = st.tabs(["📊 データ一覧", "📈 グラフ表示", "💡 AIアドバイス"])
    
    with tab1:
        st.header("睡眠データ一覧")
        
        # データテーブル表示
        display_df = df.copy()
        display_df['日付'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['就寝時間'] = display_df['bedtime']
        display_df['起床時間'] = display_df['waketime']
        display_df['睡眠時間'] = display_df['sleep_duration'].apply(lambda x: f"{x:.1f}時間")
        display_df['睡眠の質'] = display_df['sleep_quality'].apply(lambda x: "⭐" * x)
        
        st.dataframe(
            display_df[['日付', '就寝時間', '起床時間', '睡眠時間', '睡眠の質']],
            use_container_width=True
        )
        
        # 統計情報
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_duration = df['sleep_duration'].mean()
            st.metric("平均睡眠時間", f"{avg_duration:.1f}時間")
        
        with col2:
            avg_quality = df['sleep_quality'].mean()
            st.metric("平均睡眠の質", f"{avg_quality:.1f}/5")
        
        with col3:
            latest_duration = df.iloc[0]['sleep_duration']
            st.metric("最新の睡眠時間", f"{latest_duration:.1f}時間")
        
        with col4:
            latest_quality = df.iloc[0]['sleep_quality']
            st.metric("最新の睡眠の質", f"{latest_quality}/5")
    
    with tab2:
        st.header("睡眠データのグラフ")
        
        # 睡眠時間の推移
        fig_duration = px.line(
            df.sort_values('date'), 
            x='date', 
            y='sleep_duration',
            title='睡眠時間の推移',
            labels={'date': '日付', 'sleep_duration': '睡眠時間（時間）'}
        )
        fig_duration.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="推奨睡眠時間（7時間）")
        fig_duration.add_hline(y=9, line_dash="dash", line_color="green", annotation_text="推奨睡眠時間（9時間）")
        st.plotly_chart(fig_duration, use_container_width=True)
        
        # 睡眠の質の推移
        fig_quality = px.line(
            df.sort_values('date'), 
            x='date', 
            y='sleep_quality',
            title='睡眠の質の推移',
            labels={'date': '日付', 'sleep_quality': '睡眠の質'}
        )
        fig_quality.update_layout(yaxis=dict(range=[1, 5]))
        st.plotly_chart(fig_quality, use_container_width=True)
        
        # 睡眠時間と睡眠の質の相関
        fig_scatter = px.scatter(
            df, 
            x='sleep_duration', 
            y='sleep_quality',
            title='睡眠時間と睡眠の質の関係',
            labels={'sleep_duration': '睡眠時間（時間）', 'sleep_quality': '睡眠の質'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab3:
        st.header("AIからのアドバイス")
        
        if len(df) > 0:
            latest_record = df.iloc[0]
            
            # 最新のデータに基づくアドバイス
            st.subheader("📅 最新の睡眠データに基づくアドバイス")
            
            bedtime_hour = int(latest_record['bedtime'].split(':')[0])
            advice = get_sleep_advice(
                latest_record['sleep_quality'],
                latest_record['sleep_duration'],
                bedtime_hour
            )
            
            for item in advice:
                st.write(item)
            
            st.markdown("---")
            
            # 週間傾向に基づくアドバイス
            if len(df) >= 7:
                st.subheader("📊 週間傾向に基づくアドバイス")
                
                recent_week = df.head(7)
                avg_quality_week = recent_week['sleep_quality'].mean()
                avg_duration_week = recent_week['sleep_duration'].mean()
                
                if avg_quality_week < 3:
                    st.warning("⚠️ この1週間の睡眠の質が低下しています。生活習慣を見直してみましょう。")
                elif avg_quality_week >= 4:
                    st.success("✅ この1週間は良質な睡眠が取れています！")
                
                if avg_duration_week < 7:
                    st.warning("⚠️ この1週間の睡眠時間が不足気味です。早めの就寝を心がけましょう。")
                elif avg_duration_week >= 7 and avg_duration_week <= 9:
                    st.success("✅ 適切な睡眠時間を維持できています！")
                
                # 睡眠の一貫性をチェック
                bedtime_variance = recent_week['bedtime'].apply(lambda x: int(x.split(':')[0])).var()
                if bedtime_variance > 2:
                    st.warning("⚠️ 就寝時間にばらつきがあります。規則正しい生活リズムを心がけましょう。")
                else:
                    st.success("✅ 規則正しい就寝時間を維持できています！")

if __name__ == "__main__":
    main()


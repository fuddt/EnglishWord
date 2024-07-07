import streamlit as st
import pandas as pd
import sqlite3

st.title("英単語の一覧")
st.write("登録された英単語の一覧です。")

conn = sqlite3.connect("words.db", check_same_thread=False)
if 'words_list' not in st.session_state:
    try:
        st.session_state['words_list'] = pd.read_sql("SELECT * FROM words", conn)
    except Exception as e:
        st.error(f"データベースの読み込み中にエラーが発生しました: {e}")
    
column_config = {
    'id': st.column_config.TextColumn('ID', disabled=True),
    'word': st.column_config.TextColumn('Word'),
    'meaning': st.column_config.TextColumn('Meaning'),
    'sentence': st.column_config.TextColumn('Sentence'),
    'last_sent': st.column_config.TextColumn('Last Sent', disabled=True)
}

edited_df = st.data_editor(
    st.session_state['words_list'],
    column_config=column_config,
    hide_index=True,
    use_container_width=True,
    height=400,
    num_rows='dynamic'
)

# データフレームの中にIDにNoneが含まれている場合はIDを振り直してDBに保存し、rerunする
if edited_df['id'].isnull().sum() > 0:
    edited_df['id'] = range(1, len(edited_df) + 1)
    edited_df.to_sql("words", conn, if_exists="replace", index=False)
    st.rerun()

if st.button("更新"):
    try:
        st.session_state['words_list'] = edited_df
        st.session_state['words_list']['id'] = range(1, len(st.session_state['words_list']) + 1)
        st.session_state['words_list'].to_sql("words", conn, if_exists="replace", index=False)
        st.success("データベースが更新されました。")
        st.session_state['words_list'] = pd.read_sql("SELECT * FROM words", conn)
        st.rerun()
    except Exception as e:
        st.error(f"データベースの更新中にエラーが発生しました: {e}")
import streamlit as st
from word.word_register import insert_into_new_words

# OpenAI APIキーの設定

st.title("英単語登録アプリ")

input_text = st.text_area("英文を入力してください:", height=400)
if st.button("登録"):
    insert_into_new_words(input_text)
    # 英単語一覧のページを開いたことがある場合、セッションが残ってしまっていて、ページが更新されないため、セッションをリセットする
    if 'words_list' in st.session_state:
        st.rerun()

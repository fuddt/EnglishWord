import streamlit as st
from word.word_register import insert_into_new_words

# OpenAI APIキーの設定

st.title("英単語アプリ")


input_text = st.text_area("英文を入力してください:", height=400)
st.session_state["input_text"] = input_text

if st.button("登録"):
    insert_into_new_words(st.session_state["input_text"])
    if 'words_list' in st.session_state:
        del st.session_state['words_list']
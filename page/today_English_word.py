import streamlit as st
import random
import os
import pandas as pd
import pickle
from forgetting_curve.forgetting_curve import select_words, update_word_after_review

st.title("Today English Word")
st.write("Let's learn a English word today!")

# 出題された単語
if "todayEnglish" not in st.session_state:
    if os.path.exists("todayEnglish.pkl"):
        todayEnglish = pd.read_pickle("todayEnglish.pkl")
        st.session_state["todayEnglish"] = todayEnglish
        # 一度読み込んだら削除
        os.remove("todayEnglish.pkl")
    else:
        todayEnglish = select_words(10)
        st.session_state["todayEnglish"] = select_words(10)

# 正解の組み合わせを作る tuple (word, meaning)
if os.path.exists("correct_answer.pkl"):
    with open("correct_answer.pkl", "rb") as f:
        correct_answer = pickle.load(f)
        st.session_state["correct_answer"] = correct_answer
    os.remove("correct_answer.pkl")
else:
    if "correct_answer" not in st.session_state:
        correct_answer = list(zip(st.session_state["todayEnglish"]["word"].tolist(), st.session_state["todayEnglish"]["meaning"].tolist()))
        st.session_state["correct_answer"] = correct_answer


# 意味はシャッフルして表示
if os.path.exists("shuffled_meanings.pkl"):
    shuffled_meanings = pd.read_pickle("shuffled_meanings.pkl")
    st.session_state["shuffled_meanings"] = shuffled_meanings
    os.remove("shuffled_meanings.pkl")
else:
    if "shuffled_meanings" not in st.session_state:
        shuffled_meanings = st.session_state["todayEnglish"]['meaning'].tolist()
        st.session_state["shuffled_meanings"] = shuffled_meanings
        random.shuffle(st.session_state["shuffled_meanings"])

select_boxs = {}
selected_pairs = []
for word in st.session_state["todayEnglish"]['word']:
    select_boxs[word] = st.empty()
    selected_pair = select_boxs[word].selectbox(f"Select the meaning for '{word}':", options=[""] + st.session_state["shuffled_meanings"], key=word)
    selected_pairs.append((word, selected_pair))
    
if st.button("Submit"):
    correct_pairs = []
    incorrect_pairs = []

    for select_pair in selected_pairs:
        word, meaning = select_pair
        if meaning == "":  # 何も選択されていない場合はスキップ
            continue
        if select_pair in st.session_state["correct_answer"]:
            # 正解のペアを記録
            correct_pairs.append(select_pair)
            # 正解した単語のidを取得して、正解数を更新
            word_id = st.session_state["todayEnglish"].loc[st.session_state["todayEnglish"]['word'] == word, 'id'].values[0]
            update_word_after_review(word_id, is_correct=True)
            # 正解したセレクトボックスを削除
            select_boxs[word].empty()
            
        else:
            incorrect_pairs.append(select_pair)
            word_id = st.session_state["todayEnglish"].loc[st.session_state["todayEnglish"]['word'] == word, 'id'].values[0]
            update_word_after_review(word_id, is_correct=False)

    if correct_pairs:
        st.success(f"You correctly matched {len(correct_pairs)} pairs!")
        # 正解したペアを削除
        for word, meaning in correct_pairs:
            st.session_state["correct_answer"].remove((word, meaning))
            st.session_state["shuffled_meanings"].remove(meaning)
    else:
        st.warning("No correct pairs. Try again.")


st.number_input(
    "How many words do you remember?",
    min_value=1,
    max_value=30,
    step=1,
    value=10,
    placeholder=10,
    key="remembered_words",
)

if st.button("Reload"):
    st.session_state["todayEnglish"] = select_words(st.session_state["remembered_words"])
    st.session_state["shuffled_meanings"] = st.session_state["todayEnglish"]['meaning'].tolist()
    random.shuffle(st.session_state["shuffled_meanings"])
    st.session_state["correct_answer"] = list(zip(st.session_state["todayEnglish"]["word"].tolist(), st.session_state["todayEnglish"]["meaning"].tolist()))
    # 上記をpklファイルに保存
    pd.to_pickle(st.session_state["todayEnglish"], "todayEnglish.pkl")
    pd.to_pickle(st.session_state["todayEnglish"]["meaning"], "shuffled_meanings.pkl")
    with open("correct_answer.pkl", "wb") as f:
        pickle.dump(st.session_state["correct_answer"], f)
    st.retun()
    



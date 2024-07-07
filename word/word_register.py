from openai import OpenAI
from nltk.corpus import stopwords
from database.database import get_session, Word
import streamlit as st
import nltk
import os

client = OpenAI(api_key=st.secrets["openai"]["api_key"])


def initialize_nltk():
    """NLTKのリソースを初期化します"""
    nltk_data_path = "nltk_data"
    if not os.path.exists(nltk_data_path):
        os.makedirs(nltk_data_path)

    nltk.data.path.append(nltk_data_path)
    if not os.path.exists(os.path.join(nltk_data_path, "tokenizers/punkt")):
        nltk.download("punkt", quiet=True)
    if not os.path.exists(os.path.join(nltk_data_path, "corpora/stopwords")):
        nltk.download("stopwords", quiet=True)


def get_new_words(text):
    """テキストから未登録の単語を抽出します"""
    initialize_nltk()
    stop_words = set(stopwords.words("english"))
    words = nltk.word_tokenize(text)
    words = [word for word in words if word.isalpha() and word.lower() not in stop_words]

    # データベースに接続
    session = get_session()

    # 既に登録されている単語をデータベースから取得
    existing_words = set(word.word for word in session.query(Word).all())

    # 未登録の単語をフィルタリング
    new_words = [word for word in words if word.lower() not in existing_words]
    session.close()
    return new_words


def openai_chat_completions_create(new_words):
    """OpenAIに単語の詳細を問い合わせます"""
    text = ",".join(new_words)
    prompt = f"""
    次の英単語について意味と例文を提供してください:
    "{text}"

    出力形式:
    単語: <単語>
    意味: <意味>
    例文: <例文>
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """あなたは英語の初学者に対して、英単語を教える教師です。
以下のタスクを行ってください：  
1. 各単語について意味と例文を提供してください。 
出力形式: 
単語: <単語> 
意味: <意味> 
例文: <例文>""",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
        )
    except Exception as e:
        st.error(f"OpenAI APIリクエストに失敗しました: {e}")
        return []

    details_text = response.choices[0].message.content.strip()

    # 出力テキストをパースして単語、意味、例文のリストに変換
    word_details = []
    for detail in details_text.split("\n\n"):
        lines = detail.split("\n")
        if len(lines) >= 3:
            word = lines[0].replace("単語: ", "").strip()
            meaning = lines[1].replace("意味: ", "").strip()
            sentence = lines[2].replace("例文: ", "").strip()
            word_details.append({"word": word, "meaning": meaning, "sentence": sentence})

    return word_details


def insert_into_new_words(text):
    """新しい単語をデータベースに登録します"""
    batch_size = 25
    new_words = get_new_words(text)
    if not new_words:
        st.warning("新しい単語が見つかりませんでした。")
        return
    all_word_details = []
    for i in range(0, len(new_words), batch_size):
        word_batch = new_words[i : i + batch_size]
        if not word_batch:  # バッチが空の場合はスキップ
            continue
        word_details = openai_chat_completions_create(word_batch)
        all_word_details.extend(word_details)

    # データベースに保存
    session = get_session()
    try:
        print("all_word_details", all_word_details)
        for detail in all_word_details:
            print("detail", detail)
            if not session.query(Word).filter_by(word=detail["word"]).first():
                new_word = Word(word=detail["word"], meaning=detail["meaning"], sentence=detail["sentence"])
                session.add(new_word)
        session.commit()
        st.success(f"{len(all_word_details)} 単語を登録しました。")
    except Exception as e:
        session.rollback()
        st.error(f"データベースの操作中にエラーが発生しました: {e}")
    finally:
        session.close()

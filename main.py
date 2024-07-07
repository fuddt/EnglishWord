import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# ページ設定
st.set_page_config(page_title="英単語登録アプリ", page_icon=":material/thumb_up:")

# クッキーマネージャの初期化
cookies = EncryptedCookieManager(
    prefix="EnglishWord/streamlit-cookies-manager/",
    password=st.secrets["cookies"]["password"],
)
if not cookies.ready():
    st.spinner()
    st.stop()


# パスワード保護機能
def check_password():
    """ユーザーが正しいパスワードを入力した場合に `True` を返す。"""

    def password_entered():
        """ユーザーが入力したパスワードが正しいかどうかをチェックする。"""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            cookies["logged_in"] = "true"  # クッキーにログイン状態を保存
            cookies.save()
            del st.session_state["password"]  # パスワードを保存しない
        else:
            st.session_state["password_correct"] = False

    # セッションステートに"password_correct"と"password"キーを初期化
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "password" not in st.session_state:
        st.session_state["password"] = ""

    # すでにログイン状態のクッキーがあるか確認
    if cookies.get("logged_in") == "true":
        return True

    if "password_correct" not in st.session_state:
        # 初回実行時、パスワード入力を表示
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # パスワードが正しくない場合、入力とエラーメッセージを表示
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # パスワードが正しい場合
        return True


if check_password():
    # 認証後に表示するページの設定
    top = st.Page(page="page/top.py", title="英単語登録アプリ", icon=":material/app_registration:")
    show_data = st.Page(page="page/show_tables.py", title="英単語の一覧", icon=":material/database:")
    today_English_word = st.Page(page="page/today_English_word.py", title="Today English Word", icon=":material/quiz:")
    pg = st.navigation([top, show_data, today_English_word])
    pg.run()

    # サイドバーにログアウトボタンを追加
    with st.sidebar:
        if st.button("Log out"):
            cookies["logged_in"] = "false"
            cookies.save()
            st.rerun()  # ページをリロードしてログアウトを反映
else:
    st.write("Please enter the password to access the application.")

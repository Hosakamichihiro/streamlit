import streamlit as st

# HTMLとCSSを含むスタイルを記述
st.markdown("""
    <style>
    .custom-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    .custom-button:hover {
        background-color: #45a049;
    }
    .custom-button:active {
        background-color: #3e8e41;
        box-shadow: 0 5px #666;
        transform: translateY(4px);
    }
    </style>
    """, unsafe_allow_html=True)

# ボタンを作成し、カスタムクラスを適用
if st.button('カスタムボタン', key='button1'):
    st.write('カスタムボタンがクリックされました！')

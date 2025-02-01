import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def resize_image(image, new_width, new_height):
    """画像をリサイズする関数"""
    resized_image = image.resize((new_width, new_height))
    return resized_image

def rotate_image_pil(image, angle):
    """Pillow形式の画像を回転する関数"""
    return image.rotate(angle, expand=True)

def convert_to_pil(image_cv2):
    """OpenCV形式の画像をPillow形式に変換する関数"""
    if len(image_cv2.shape) == 2:  # グレースケールの場合
        return Image.fromarray(image_cv2)
    else:  # カラー画像の場合
        return Image.fromarray(cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB))

st.set_page_config(
    page_title="Image Processing App", 
    page_icon="C:/Users/保坂 陸太/Downloads/photo_16430626.png"
)

# Streamlitアプリの設定
st.title("画像処理アプリ")
st.subheader("画像をアップロードして処理を試してみてください。")

# サイドバーで操作の種類を選択
option = st.sidebar.selectbox(
    "操作を選択してください",
    ["オリジナル", "グレースケール", "ぼかし", "エッジ検出", "解像度アップ", "サイズ変更", "画像回転", "トリミング", "明るさ・コントラスト調整", "ノイズ除去"]
)

# 画像アップロード
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Pillowで画像を読み込む
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)
    image_np = np.array(image)
    image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    # 処理する画像の初期化
    processed_image = image_cv2

    # 選択された操作に応じて処理
    if option == "オリジナル":
        processed_image = image_cv2

    elif option == "グレースケール":
        processed_image = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)

    elif option == "ぼかし":
        ksize = st.sidebar.slider("ぼかしの強さ (奇数のみ)", 1, 21, 5, step=2)
        processed_image = cv2.GaussianBlur(image_cv2, (ksize, ksize), 0)

    elif option == "エッジ検出":
        threshold1 = st.sidebar.slider("閾値1", 0, 255, 50)
        threshold2 = st.sidebar.slider("閾値2", 0, 255, 150)
        processed_image = cv2.Canny(image_cv2, threshold1, threshold2)

    elif option == "解像度アップ":
        upscale_factor = st.sidebar.slider("拡大倍率", 1, 4, 2)
        width = image_cv2.shape[1] * upscale_factor
        height = image_cv2.shape[0] * upscale_factor
        processed_image = cv2.resize(image_cv2, (width, height), interpolation=cv2.INTER_CUBIC)

    elif option == "サイズ変更":
        new_width = st.sidebar.number_input("新しい幅を入力してください (px)", min_value=1, value=image.width)
        new_height = st.sidebar.number_input("新しい高さを入力してください (px)", min_value=1, value=image.height)
        if st.button("サイズを変更"):
            processed_image = resize_image(image, int(new_width), int(new_height))
            #st.image(processed_image, caption="リサイズされた画像", use_column_width=True)

    elif option == "画像回転":
        angle = st.sidebar.slider("回転角度を選択してください (度)", min_value=0, max_value=360, value=0, step=1)
        if st.button("画像を処理"):
            processed_image = rotate_image_pil(image, angle)
            #st.image(processed_image, caption="回転された画像", use_column_width=True)

    elif option == "トリミング":
    # 画像のサイズを取得
        img_width, img_height = image.size

        # トリミング範囲を選択
        x1 = st.sidebar.slider("X1 (左上のX座標)", 0, img_width, 0)
        y1 = st.sidebar.slider("Y1 (左上のY座標)", 0, img_height, 0)
        x2 = st.sidebar.slider("X2 (右下のX座標)", 0, img_width, img_width)
        y2 = st.sidebar.slider("Y2 (右下のY座標)", 0, img_height, img_height)

        # トリミング実行ボタン
        if st.button("トリミング実行"):
            # トリミング処理
            processed_image = image.crop((x1, y1, x2, y2))

    elif option == "明るさ・コントラスト調整":
        alpha = st.sidebar.slider("コントラスト", 0.5, 3.0, 1.0)
        beta = st.sidebar.slider("明るさ", -100, 100, 0)
        processed_image = cv2.convertScaleAbs(image_cv2, alpha=alpha, beta=beta)

    elif option == "ノイズ除去":
        strength = st.sidebar.slider("ノイズ除去の強さ", 1, 10, 3)
        processed_image = cv2.fastNlMeansDenoisingColored(image_cv2, None, strength, strength, 7, 21)

    # OpenCV形式の画像をPillow形式に変換
    if isinstance(processed_image, np.ndarray):
        processed_image_pil = convert_to_pil(processed_image)
    else:
        processed_image_pil = processed_image

    # 加工後の画像を表示
    st.image(processed_image_pil, caption="加工後の画像", use_column_width=True)

    # ダウンロード機能を追加
    buf = io.BytesIO()
    processed_image_pil.save(buf, format="PNG")
    byte_image = buf.getvalue()

    st.download_button(
        label="加工後の画像をダウンロード",
        data=byte_image,
        file_name="processed_image.png",
        mime="image/png"
    )
else:
    st.write("画像をアップロードしてください。")
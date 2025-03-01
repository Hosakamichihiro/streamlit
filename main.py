import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import os
import io
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import blackwhite, colorx, invert_colors

# --- 動画編集クラス ---
class VideoEditor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video = VideoFileClip(video_path)

    def trim(self, start, end):
        return self.video.subclip(start, end)

    def resize(self, width, height):
        return self.video.resize((width, height))

    def apply_filter(self, filter_type, brightness=1.0):
        if filter_type == "オリジナル":
            return self.video
        elif filter_type == "グレースケール":
            return blackwhite(self.video)
        elif filter_type == "セピア":
            return colorx(self.video, 0.5)
        elif filter_type == "明るさ調整":
            return colorx(self.video, brightness)
        elif filter_type == "色反転":
            return invert_colors(self.video)

    def extract_audio(self, output_path):
        self.video.audio.write_audiofile(output_path)

    def save_video(self, output_path):
        self.video.write_videofile(output_path, codec="libx264")


# --- 画像編集クラス ---
class ImageEditor:
    def __init__(self, image):
        self.image = image
        self.image_np = np.array(image)
        self.image_cv2 = cv2.cvtColor(self.image_np, cv2.COLOR_RGB2BGR)

    def grayscale(self):
        return cv2.cvtColor(self.image_cv2, cv2.COLOR_BGR2GRAY)

    def blur(self, ksize):
        return cv2.GaussianBlur(self.image_cv2, (ksize, ksize), 0)

    def edge_detection(self, threshold1, threshold2):
        return cv2.Canny(self.image_cv2, threshold1, threshold2)

    def resize(self, width, height):
        return cv2.resize(self.image_cv2, (width, height))

    def rotate(self, angle):
        return self.image.rotate(angle, expand=True)

    def brightness_contrast(self, alpha, beta):
        return cv2.convertScaleAbs(self.image_cv2, alpha=alpha, beta=beta)

    def convert_to_pil(self,image_cv2):
    
        if isinstance(image_cv2, Image.Image):  # 既にPIL形式なら変換せずそのまま返す
            return image_cv2
        elif len(image_cv2.shape) == 2:  # グレースケール画像
            return Image.fromarray(image_cv2)
        else:  # カラー画像
            return Image.fromarray(cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB))


# --- Streamlit UI ---
st.set_page_config(page_title="🎬 総合動画・画像編集アプリ", page_icon="🎬")

st.title("🎬 総合動画・画像編集アプリ")
option = st.sidebar.radio("編集するメディアを選択してください", ["動画編集", "画像編集"])

if option == "動画編集":
    st.subheader("🎬 動画編集ツール")
    uploaded_video = st.file_uploader("📂 動画をアップロードしてください", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_video is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(uploaded_video.read())
            video_path = temp_file.name

        video_editor = VideoEditor(video_path)
        st.video(uploaded_video)

        start_time = st.number_input("開始時間 (秒)", min_value=0.0, max_value=video_editor.video.duration, value=0.0)
        end_time = st.number_input("終了時間 (秒)", min_value=0.0, max_value=video_editor.video.duration, value=video_editor.video.duration)
        resize_width = st.number_input("新しい幅 (px)", min_value=100, max_value=video_editor.video.size[0], value=video_editor.video.size[0])
        resize_height = st.number_input("新しい高さ (px)", min_value=100, max_value=video_editor.video.size[1], value=video_editor.video.size[1])
        extract_audio = st.checkbox("🎵 音声を抽出")

        filter_option = st.selectbox("適用するフィルター", ["オリジナル", "グレースケール", "セピア", "明るさ調整", "色反転"])
        brightness = st.slider("明るさの強さ（1.0が通常）", 0.1, 2.0, 1.0, 0.1) if filter_option == "明るさ調整" else 1.0

        if st.button("編集を実行 🎬"):
            edited_video = video_editor.trim(start_time, end_time)
            edited_video = video_editor.resize(resize_width, resize_height)
            edited_video = video_editor.apply_filter(filter_option, brightness)

            output_video_path = os.path.join(tempfile.gettempdir(), "edited_video.mp4")
            edited_video.write_videofile(output_video_path, codec="libx264")

            st.video(output_video_path)
            with open(output_video_path, "rb") as file:
                st.download_button("📥 編集後の動画をダウンロード", file, "edited_video.mp4", "video/mp4")

            if extract_audio:
                audio_path = os.path.join(tempfile.gettempdir(), "extracted_audio.mp3")
                video_editor.extract_audio(audio_path)
                with open(audio_path, "rb") as audio_file:
                    st.download_button("🎵 抽出した音声をダウンロード", audio_file, "extracted_audio.mp3", "audio/mp3")

elif option == "画像編集":
    st.subheader("🖼️ 画像編集ツール")
    uploaded_image = st.file_uploader("📂 画像をアップロードしてください", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        image_editor = ImageEditor(image)
        st.image(image, caption="アップロードされた画像", use_container_width=True)

        edit_option = st.selectbox("適用する編集", ["オリジナル", "グレースケール", "ぼかし", "エッジ検出", "回転", "明るさ調整"])
        processed_image = image

        if edit_option == "グレースケール":
            processed_image = image_editor.grayscale()
        elif edit_option == "ぼかし":
            ksize = st.slider("ぼかしの強さ", 1, 21, 5, step=2)
            processed_image = image_editor.blur(ksize)
        elif edit_option == "エッジ検出":
            threshold1 = st.slider("閾値1", 0, 255, 50)
            threshold2 = st.slider("閾値2", 0, 255, 150)
            processed_image = image_editor.edge_detection(threshold1, threshold2)
        elif edit_option == "回転":
            angle = st.slider("回転角度", 0, 360, 0)
            processed_image = image_editor.rotate(angle)

        processed_image_pil = image_editor.convert_to_pil(processed_image)
        st.image(processed_image_pil, caption="加工後の画像", use_container_width=True)

        buf = io.BytesIO()
        processed_image_pil.save(buf, format="PNG")
        byte_image = buf.getvalue()

        st.download_button("📥 加工後の画像をダウンロード", data=byte_image, file_name="edited_image.png", mime="image/png")


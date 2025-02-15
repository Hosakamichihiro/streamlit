import streamlit as st
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import blackwhite, colorx, invert_colors
import tempfile
import os

st.set_page_config(page_title="🎨 動画フィルターアプリ", page_icon="🎬")

st.title("🎬 動画フィルターアプリ")
st.write("動画にフィルターを適用して、映像を加工できます！")

# 動画のアップロード
uploaded_file = st.file_uploader("📂 動画をアップロードしてください", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        video_path = temp_file.name

    # 動画を読み込む
    video = VideoFileClip(video_path)

    st.video(uploaded_file)

    st.write(f"🎥 動画の長さ: {video.duration:.2f} 秒")
    st.write(f"📏 解像度: {video.size[0]} x {video.size[1]}")

    # ---- フィルター選択 ----
    st.subheader("🎨 フィルターオプション")
    filter_option = st.sidebar.selectbox(
        "適用するフィルターを選択してください",
        ["オリジナル", "グレースケール", "セピア", "明るさ調整", "色反転"]
    )

    brightness = 1.0  # 初期値
    if filter_option == "明るさ調整":
        brightness = st.slider("明るさの強さ（1.0が通常）", 0.1, 2.0, 1.0, 0.1)

    # 🎨 フィルター適用ボタン
    if st.button("フィルターを適用 🎬"):
        st.write("⏳ フィルターを適用中...")

        # 🎨 フィルター処理
        if filter_option == "オリジナル":
            filtered_video = video
        elif filter_option == "グレースケール":
            filtered_video = blackwhite(video)
        elif filter_option == "セピア":
            filtered_video = colorx(video, 0.5)  # 色味をセピア風に変更
        elif filter_option == "明るさ調整":
            filtered_video = colorx(video, brightness)  # 明るさを調整
        elif filter_option == "色反転":
            filtered_video = invert_colors(video)  # 色を反転（ネガティブ風）

        # 動画の保存
        output_video_path = os.path.join(tempfile.gettempdir(), "filtered_video.mp4")
        filtered_video.write_videofile(output_video_path, codec="libx264")

        st.success("🎉 フィルター適用が完了しました！")

        # 🎥 編集後の動画を画面上で再生
        st.subheader("🎞 編集後の動画プレビュー")
        st.video(output_video_path)

        # 動画のダウンロードボタン
        with open(output_video_path, "rb") as file:
            st.download_button("📥 フィルター適用後の動画をダウンロード", file, "filtered_video.mp4", "video/mp4")

    # 動画リソースの解放
    video.close()
    os.remove(video_path)
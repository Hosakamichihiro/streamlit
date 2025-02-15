import streamlit as st
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import blackwhite, colorx, invert_colors
import tempfile
import os

st.set_page_config(page_title="🎬 総合動画編集アプリ", page_icon="🎬")

st.title("🎬 総合動画編集アプリ")
st.write("動画をアップロードし、様々なフィルターと編集機能を活用して映像を加工できます！")

# 動画のアップロード
uploaded_file = st.file_uploader("📂 動画ファイルをアップロードしてください", type=["mp4", "mov", "avi", "mkv"])

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

    # ---- 動画編集オプション ----
    st.subheader("✂️ 動画編集オプション")

    # 動画トリミング
    start_time = st.number_input("開始時間 (秒)", min_value=0.0, max_value=video.duration, value=0.0)
    end_time = st.number_input("終了時間 (秒)", min_value=0.0, max_value=video.duration, value=video.duration)

    # 解像度変更
    resize_width = st.number_input("新しい幅 (px)", min_value=100, max_value=video.size[0], value=video.size[0])
    resize_height = st.number_input("新しい高さ (px)", min_value=100, max_value=video.size[1], value=video.size[1])

    # 音声抽出
    extract_audio = st.checkbox("🎵 音声を抽出")

    # ---- フィルター選択 ----
    st.subheader("🎨 フィルターオプション")
    filter_option = st.sidebar.selectbox(
        "適用するフィルターを選択してください",
        ["オリジナル", "グレースケール", "セピア", "明るさ調整", "色反転"]
    )

    brightness = 1.0  # 初期値
    if filter_option == "明るさ調整":
        brightness = st.slider("明るさの強さ（1.0が通常）", 0.1, 2.0, 1.0, 0.1)

    # 編集開始ボタン
    if st.button("編集とフィルター適用を実行 🚀"):
        st.write("📽️ 編集処理を実行中...")

        # トリミング処理
        edited_video = video.subclip(start_time, end_time)

        # 解像度変更
        edited_video = edited_video.resize((resize_width, resize_height))

        # フィルター処理
        if filter_option == "オリジナル":
            filtered_video = edited_video
        elif filter_option == "グレースケール":
            filtered_video = blackwhite(edited_video)
        elif filter_option == "セピア":
            filtered_video = colorx(edited_video, 0.5)  # 色味をセピア風に変更
        elif filter_option == "明るさ調整":
            filtered_video = colorx(edited_video, brightness)  # 明るさを調整
        elif filter_option == "色反転":
            filtered_video = invert_colors(edited_video)  # 色を反転（ネガティブ風）

        # 保存
        output_video_path = os.path.join(tempfile.gettempdir(), "edited_filtered_video.mp4")
        filtered_video.write_videofile(output_video_path, codec="libx264")

        st.success("🎉 動画の編集とフィルター適用が完了しました！")

        # 編集後の動画プレビュー
        st.subheader("🎞 編集後の動画プレビュー")
        st.video(output_video_path)

        # 動画のダウンロードボタン
        with open(output_video_path, "rb") as file:
            st.download_button("📥 編集後の動画をダウンロード", file, "edited_filtered_video.mp4", "video/mp4")

        # 音声を抽出
        if extract_audio:
            audio_output_path = os.path.join(tempfile.gettempdir(), "extracted_audio.mp3")
            filtered_video.audio.write_audiofile(audio_output_path)

            with open(audio_output_path, "rb") as audio_file:
                st.download_button("🎵 抽出した音声をダウンロード", audio_file, "extracted_audio.mp3", "audio/mp3")

    # リソースの解放
    video.close()
    os.remove(video_path)
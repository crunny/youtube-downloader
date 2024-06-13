import os
from pytube import YouTube
from pytube.exceptions import PytubeError
import customtkinter as ctk
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio

# folder path where the downloaded file will be saved
output_folder_path = os.path.join(os.path.expanduser("~"), "Downloads")

# set theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("themes/dark-red.json")

# create root window
root = ctk.CTk()
root.title("YouTube Downloader - GitHub.com/crunny")
root.geometry("600x450")
root.resizable(False, False)

font_size = 16

# create widgets
url_label = ctk.CTkLabel(root, text="Enter YouTube URL:", font=("Poppins", font_size))
url_label.pack(pady=20)

url_entry = ctk.CTkEntry(root, width=400, font=("Poppins", font_size))
url_entry.pack(pady=10)

format_label = ctk.CTkLabel(root, text="Choose format:", font=("Poppins", font_size))
format_label.pack(pady=20)

format_var = ctk.StringVar(value="video")

video_radio = ctk.CTkRadioButton(
    root, text="Video", variable=format_var, value="Video", font=("Poppins", font_size)
)
video_radio.pack(pady=0)

audio_radio = ctk.CTkRadioButton(
    root, text="Audio", variable=format_var, value="Audio", font=("Poppins", font_size)
)
audio_radio.pack(pady=10)

progress_bar = ctk.CTkProgressBar(root, width=400)
progress_bar.pack(pady=20)
progress_bar.set(0)


# progress bar callback function
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    new_percentage = bytes_downloaded / total_size * 100

    current_percentage = progress_bar.get() * 100

    increment_size = (new_percentage - current_percentage) / 10

    for _ in range(10):
        current_percentage += increment_size
        progress_bar.set(current_percentage / 100)
        status_label.configure(text=f"Downloading... {int(current_percentage)}%")
        root.update()

    progress_bar.set(new_percentage / 100)
    status_label.configure(text=f"Downloading... {int(new_percentage)}%")


# download button callback function
def download():
    url = url_entry.get()
    format = format_var.get()
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        # audio streams are ordered by bitrate in descending order
        if format == "Audio":
            audio_streams = yt.streams.filter(only_audio=True).order_by("abr").desc()
            if audio_streams:
                # get the first audio stream (highest quality)
                audio = audio_streams.first()
                output_file_path = os.path.join(
                    output_folder_path, audio.default_filename
                )
                if os.path.exists(output_file_path):
                    status_label.configure(text="File already exists!")
                else:
                    status_label.configure(text="Downloading audio...")
                    audio.download(output_path=output_folder_path)
                    status_label.configure(text="Downloaded successfully!")
            else:
                status_label.configure(text="No audio streams available!")
        # video and audio streams are ordered by bitrate and resolution in descending order
        elif format == "Video":
            video_streams = (
                yt.streams.filter(type="video", progressive=False, file_extension="mp4")
                .order_by("resolution")
                .desc()
            )
            audio_streams = (
                yt.streams.filter(only_audio=True, file_extension="mp4")
                .order_by("abr")
                .desc()
            )

            if video_streams and audio_streams:
                # get the first video and audio streams (highest quality)
                video = video_streams.first()
                audio = audio_streams.first()

                video_output_path = os.path.join(output_folder_path, "video.mp4")
                audio_output_path = os.path.join(output_folder_path, "audio.mp4")

                try:
                    # download video and audio streams to temporary files
                    status_label.configure(text="Downloading video...")
                    video.download(output_path=output_folder_path, filename="video.mp4")

                    status_label.configure(text="Downloading audio...")
                    audio.download(output_path=output_folder_path, filename="audio.mp4")

                    final_output_path = os.path.join(
                        output_folder_path, f"{yt.title}.mp4"
                    )

                    status_label.configure(text="Merging video and audio...")
                    # merge video and audio files
                    ffmpeg_merge_video_audio(
                        video_output_path, audio_output_path, final_output_path
                    )
                finally:
                    # remove temporary files
                    if os.path.exists(video_output_path):
                        os.remove(video_output_path)
                    if os.path.exists(audio_output_path):
                        os.remove(audio_output_path)

                status_label.configure(text="Downloaded successfully!")
            else:
                status_label.configure(text="No video/audio streams available!")
    except PytubeError as e:
        status_label.configure(text=f"Pytube Error: {e}")
    except OSError as e:
        status_label.configure(text=f"OS Error: {e}")
    except Exception as e:
        status_label.configure(text=f"Error: {e}")


download_button = ctk.CTkButton(
    root,
    text="Download",
    font=("Poppins", font_size),
    command=download,
)
download_button.pack(pady=10)

status_label = ctk.CTkLabel(root, text="", font=("Poppins", font_size))
status_label.pack(pady=10)

# run the main event loop
root.mainloop()

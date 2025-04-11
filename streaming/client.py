import Pyro4
import base64
import os
import platform

def save_and_play(video_b64, filename):
    video_bytes = base64.b64decode(video_b64.encode("utf-8"))
    with open(filename, "wb") as f:
        f.write(video_bytes)

    system = platform.system()
    if system == "Windows":
        os.startfile(filename)
    elif system == "Darwin":
        os.system(f"open '{filename}'")
    elif system == "Linux":
        os.system(f"xdg-open '{filename}'")

def main():
    video_server = Pyro4.Proxy("PYRO:video.example@172.17.42.153:9090")

    print("[CLIENT] Getting video list...")
    videos = video_server.list_videos()
    if not videos:
        print("No videos found.")
        return

    for i, name in enumerate(videos):
        print(f"{i+1}. {name}")

    choice = int(input("Select a video: ")) - 1
    selected_video = videos[choice]

    print(f"[CLIENT] Requesting video '{selected_video}'...")
    video_b64 = video_server.get_processed_video(selected_video)

    if video_b64:
        filename = "received_" + selected_video
        save_and_play(video_b64, filename)
        print(f"Saved and played: {filename}")
    else:
        print("Failed to receive video.")

if __name__ == "__main__":
    main()

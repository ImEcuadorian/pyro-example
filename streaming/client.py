import os
import Pyro4
import tempfile
import base64

# Configuración Pyro4
Pyro4.config.SERIALIZER = "serpent"
Pyro4.config.SERIALIZERS_ACCEPTED.add("serpent")

def download_and_play(proxy, video_name):
    try:
        raw_data = proxy.get_entire_video(video_name)

        # 🔍 Mostrar información de depuración
        print(f"[DEBUG] Type of raw_data: {type(raw_data)}")
        print(f"[DEBUG] Keys: {list(raw_data.keys())}")

        if isinstance(raw_data, dict) and "data" in raw_data and "encoding" in raw_data:
            if raw_data["encoding"] == "base64":
                data = base64.b64decode(raw_data["data"])
            else:
                raise ValueError(f"[CLIENT ERROR] Unknown encoding: {raw_data['encoding']}")
        else:
            raise TypeError(f"[CLIENT ERROR] Unexpected format: {type(raw_data)}")

    except Exception as e:
        print(f"[CLIENT ERROR] Failed to download: {e}")
        return

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    with open(temp_file.name, "wb") as f:
        f.write(data)

    print(f"[CLIENT] Video saved to: {temp_file.name}")
    print("[CLIENT] Attempting to play...")

    try:
        os.startfile(temp_file.name)  # Windows
    except Exception as e:
        print(f"[CLIENT ERROR] Failed to play video: {e}")

def main():
    try:
        ns = Pyro4.locateNS(host="127.0.0.1", port=9091)
        uri = ns.lookup("video.nostream")
        proxy = Pyro4.Proxy(uri)
        proxy._pyroSerializer = "serpent"
    except Exception as e:
        print(f"[CLIENT ERROR] Connection failed: {e}")
        return

    videos = proxy.list_videos()
    if not videos:
        print("No videos available.")
        return

    print("Available videos:")
    for i, name in enumerate(videos):
        print(f"{i + 1}. {name}")

    try:
        idx = int(input("Select video number: ")) - 1
        video_name = videos[idx]
    except Exception:
        print("Invalid selection.")
        return

    size = proxy.get_video_size(video_name)
    print(f"[CLIENT] Video size: {size:,} bytes")
    download_and_play(proxy, video_name)

if __name__ == "__main__":
    main()

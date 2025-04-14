import os
import Pyro4
import tempfile
import base64
import time

CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB

Pyro4.config.SERIALIZER = "serpent"
Pyro4.config.SERIALIZERS_ACCEPTED.add("serpent")

def download_in_chunks(proxy, video_name, total_size):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    print(f"[CLIENT] Saving video to: {temp_file.name}")

    offset = 0
    with open(temp_file.name, "wb") as f:
        while offset < total_size:
            chunk = proxy.get_video_chunk(video_name, offset, CHUNK_SIZE)

            if chunk.get("encoding") != "base64":
                raise ValueError(f"Unknown encoding: {chunk.get('encoding')}")

            data = base64.b64decode(chunk["data"])
            f.write(data)

            offset += chunk["size"]
            percent = (offset / total_size) * 100
            print(f"[CLIENT] Downloaded: {offset:,}/{total_size:,} bytes ({percent:.2f}%)")

    return temp_file.name

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

    local_path = download_in_chunks(proxy, video_name, size)

    print("[CLIENT] Attempting to play...")
    try:
        os.startfile(local_path)  # Windows only
    except Exception as e:
        print(f"[CLIENT ERROR] Failed to play video: {e}")

if __name__ == "__main__":
    main()

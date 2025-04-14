import os
import Pyro4
import tempfile
import base64
import subprocess
import threading
import socket
from tqdm import tqdm

CHUNK_SIZE = 5 * 1024 * 1024  # 5MB
START_PLAY_AFTER = 20 * 1024 * 1024  # 20MB
FFPLAY_PATH = r"C:\ffmpeg\bin\ffplay.exe"

Pyro4.config.SERIALIZER = "serpent"
Pyro4.config.SERIALIZERS_ACCEPTED.add("serpent")

def download_chunks_streaming(proxy, video_name, total_size, temp_path, trigger_play_event):
    offset = 0
    with open(temp_path, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
        while offset < total_size:
            try:
                chunk = proxy.get_video_chunk(video_name, offset, CHUNK_SIZE)
                if chunk.get("encoding") != "base64":
                    raise ValueError(f"Unknown encoding: {chunk.get('encoding')}")
                data = base64.b64decode(chunk["data"])
                f.write(data)
                f.flush()

                offset += chunk["size"]
                pbar.update(chunk["size"])

                if offset >= START_PLAY_AFTER and not trigger_play_event.is_set():
                    trigger_play_event.set()
            except Exception as e:
                print(f"[CLIENT ERROR] Failed to download chunk at offset {offset}: {e}")
                break
    print("\n[CLIENT] Finished downloading.")

def play_with_ffplay(temp_path, trigger_play_event):
    print("[CLIENT] Waiting for 20MB before starting playback...")
    trigger_play_event.wait()
    print("[CLIENT] Starting playback...")
    subprocess.run([FFPLAY_PATH, "-autoexit", "-loglevel", "quiet", temp_path])

def main():
    try:
        ns = Pyro4.locateNS(host="127.0.0.1", port=9091)
        uri = ns.lookup("video.nostream")
        proxy = Pyro4.Proxy(uri)
        proxy._pyroSerializer = "serpent"
    except Exception as e:
        print(f"[CLIENT ERROR] Connection failed: {e}")
        return

    # Generar un ID de cliente único
    client_id = f"{socket.gethostname()}-{os.getpid()}"
    proxy.register_client(client_id)

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
        proxy.unregister_client(client_id)
        return

    size = proxy.get_video_size(video_name)
    print(f"[CLIENT] Video size: {size:,} bytes")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_path = temp_file.name
    temp_file.close()

    trigger_play_event = threading.Event()

    player_thread = threading.Thread(target=play_with_ffplay, args=(temp_path, trigger_play_event))
    player_thread.start()

    download_chunks_streaming(proxy, video_name, size, temp_path, trigger_play_event)

    player_thread.join()

    print("[CLIENT] Cleaning up...")
    try:
        os.remove(temp_path)
    except Exception as e:
        print(f"[CLIENT WARNING] Could not remove temp file: {e}")

    proxy.unregister_client(client_id)

if __name__ == "__main__":
    main()

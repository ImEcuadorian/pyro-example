import os
import base64
import Pyro4
from moviepy.editor import VideoFileClip


@Pyro4.expose
class VideoServer:
    def __init__(self, video_folder="pyro_vids"):
        self.video_folder = video_folder
        self.last_video_sent = None

    def list_videos(self):
        try:
            return [f for f in os.listdir(self.video_folder) if f.endswith(".mp4")]
        except Exception as e:
            return [f"Error: {e}"]

    def get_processed_video(self, video_name):
        path = os.path.join(self.video_folder, video_name)
        if not os.path.isfile(path):
            return None

        try:
            clip = VideoFileClip(path).subclip(0, 5)
            output_path = "processed_video.mp4"
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

            with open(output_path, "rb") as f:
                video_bytes = f.read()
                video_b64 = base64.b64encode(video_bytes).decode("utf-8")
                self.last_video_sent = video_name
                return video_b64
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            return None

    def get_last_video_name(self):
        return self.last_video_sent

def start_pyro_server(ip="172.17.42.153"):
    daemon = Pyro4.Daemon(host=ip)
    ns = Pyro4.locateNS()
    video_server = VideoServer()
    uri = daemon.register(video_server)
    ns.register("video.example", uri)

    print(f"[PYRO SERVER] Running at IP: {ip}")
    print(f"[PYRO SERVER] Registered as: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    start_pyro_server("172.17.42.153")
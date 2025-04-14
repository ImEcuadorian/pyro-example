import os
import Pyro4

Pyro4.config.SERIALIZER = "serpent"
Pyro4.config.SERIALIZERS_ACCEPTED.add("serpent")

@Pyro4.expose
class VideoServer:
    def __init__(self, video_folder="pyro_vids"):
        self.video_folder = video_folder

    def list_videos(self):
        return [f for f in os.listdir(self.video_folder) if f.endswith(".mp4")]

    def get_video_size(self, video_name):
        path = os.path.join(self.video_folder, video_name)
        return os.path.getsize(path)

    def get_entire_video(self, video_name):
        path = os.path.join(self.video_folder, video_name)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{video_name} not found.")
        with open(path, "rb") as f:
            print(f"[SERVER] Sending entire video: {video_name}")
            return f.read()

def start_pyro_server(ip="127.0.0.1"):
    daemon = Pyro4.Daemon(host=ip)
    ns = Pyro4.locateNS(host=ip, port=9091)
    uri = daemon.register(VideoServer())
    ns.register("video.nostream", uri)
    print(f"[SERVER] Pyro Video Server running at {ip}")
    daemon.requestLoop()

if __name__ == "__main__":
    start_pyro_server()

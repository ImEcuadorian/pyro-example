import Pyro4


@Pyro4.expose
class HelloWorld:

    def hello(self, name):
        return f"Hello, {name}!"

    def goodbye(self, name):
        return f"Goodbye, {name}!"


daemon = Pyro4.Daemon()
uri = daemon.register(HelloWorld)
print(f"Ready. Object uri = {uri}")
daemon.requestLoop()

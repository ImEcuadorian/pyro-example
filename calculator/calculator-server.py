import Pyro4


@Pyro4.expose
class Calculator:

    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y

    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero.")
        return x / y

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Calculator)
ns.register("example.calculator", uri)

print(f"Calculator is ready. Object uri = {uri}")
daemon.requestLoop()

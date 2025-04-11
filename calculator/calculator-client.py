import Pyro4

ns = Pyro4.locateNS()
uri = ns.lookup("example.calculator")
calculator = Pyro4.Proxy(uri)

# Example usage
print(calculator.add(1, 2))
print(calculator.subtract(5, 3))
print(calculator.multiply(4, 2))
print(calculator.divide(8, 2))
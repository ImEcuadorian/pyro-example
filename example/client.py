from tkinter.font import names

import Pyro4

uri = input("Enter the URI of the remote object: ")
hello_world = Pyro4.Proxy(uri)
name = input("Enter your name: ")
print(hello_world.hello(name))
print(hello_world.goodbye(name))
def test():
    print("hello")

things = []

def thing(**kwargs):
    things.append(kwargs)


thing()

for thing in things:
    test(**thing)

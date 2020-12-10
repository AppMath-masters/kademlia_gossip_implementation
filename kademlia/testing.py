storage = __import__('storage')
s = storage.Storage()
b = s.get_all()
print(b)

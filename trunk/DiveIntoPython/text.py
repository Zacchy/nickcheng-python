f = open("E:\\Music\\Vivian-Complicated.mp3", "rb")
print f.tell()
f.seek(-128, 2)
print f.tell()
tagData = f.read(128)
print tagData
print f.tell()

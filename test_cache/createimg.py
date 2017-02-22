# test
f = open('xxx.xx')
ln = os.path.getsize('xxx.xx') # get length
width = int(ln**0.5)
rem = ln % width
a = array.array("B") # uint8 array
a.fromfile(f, ln - rem)
f.close()
g = np.reshape(a, (len(a) / width, width))
g = np.uint8(g)
misc.imsave('xx.png', g)

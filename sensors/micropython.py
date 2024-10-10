# Workaround for use of micropython "const" function to define data in Flash
# so it can be tested in CPython
try:
    from micropython import const
    print("micropython const imported")
except ImportError:
    print("micropython const not imported - substitute")
    def const(item):
        return item
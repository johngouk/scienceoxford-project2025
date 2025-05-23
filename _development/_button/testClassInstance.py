class classTest():
    ST_NOW = 2
    class1 = 2
    @classmethod
    def classf(cls):
        print(cls.class1)
    def f(self):
        print(self.class1)
    FSM = [(ST_NOW,f)]
        
print("try class method")
classTest.classf()
print("set class variable")
classTest.classvar = 99
print("classTest.classvar",classTest.classvar)
print("try instance method")
c = classTest()
c.f()
print("c.classvar",c.classvar)
print(c.FSM)

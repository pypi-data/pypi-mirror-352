# intently throw a syntax error
# to test the error handling of the python provider
print("Hello World")

# raise SyntaxError("BIEM")

def f20():
    raise SyntaxError("BIEM")

def f19():
    f20()

def f18():
    f19()

def f17():
    f18()

def f16():
    f17()

def f15():
    f16()

def f14():
    f15()

def f13():
    f14()

def f12():
    f13()

def f11():
    f12()

def f10():
    f11()

def f9():
    f10()

def f8():
    f9()

def f7():
    f8()

def f6():
    f7()

def f5():
    f6()

def f4():
    f5()

def f3():
    f4()

def f2():
    f3()

# produce a big call stack to test the error handling of the python provider
def f1():
    f2()
    
f1()
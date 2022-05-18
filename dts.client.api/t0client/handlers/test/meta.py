

class A(type):
    def __new__(cls, name, bases, attrs):
        print('-----------')
        print(cls)
        print(name)
        print(bases)
        print(attrs)
        print('-----------')
        return type.__new__(cls, name, bases, attrs)

class B(object):
    def __new__(cls, *args, **kwargs):
        print(cls)


def test1(age,sex,*args,**kwargs):
    print('age',age)
    print('sex',sex)
    print('args',args)
    print('kwargs',kwargs)

def test2(age,sex,*args,job,name):
    print('age', age)
    print('sex', sex)
    print('job', job)
    print('name', name)
    print('args',args)





# class B(object):
#     def __init__(self,*args,**kwargs):
#         print('----------b_init----------')
#         print(args,kwargs)
#         print('----------b_init----------')
#         super(B,self).__init__(*args,**kwargs)
#
#     def __new__(cls, *args, **kwargs):
#         print('----------b_new----------')
#         print(cls,args,kwargs)
#         print('----------b_new----------')
#         return super(B,cls).__new__(cls,*args,**kwargs)
#
#     def __call__(self, *args, **kwargs):
#         print('----------b_call----------')
#         print(self, args, kwargs)
#         print('----------b_call----------')

class C(dict,B,metaclass=A):
    def __new__(cls, *args, **kwargs):
        print('c_new')
        return super().__new__(cls,*args,**kwargs)
    def __init__(self):
        print('c_init')



if __name__ == '__main__':
    print('main')
    # b = B()
    # b()
    # b.t = 1
    c = C()
    c['a']=1
    print(c.get('a'))
    print('----')
    print(type(c))
    print(type(C))
    print(type(B))
    print(type(object))
    # print(dir(c))
    # print(dir(type))
    # print(dir(object))
    # print(type(object))
    # print(type(type))
    # print(getattr(type,'mro'))

    print('-----------------')
    test1(5,'m',2013,10,cls='小2',tomm='小5')
    test1(6,'f',*(2013,10),**{'aaa':111,'bbb':222})
    test1(*(5,'m',2013,10,22),**{'aaa':111,'bbb':222})

    print('-----------------')
    test2(7,'m','kkk',name='lishuai',job='php')

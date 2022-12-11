class a:
    def __init__(self, dic):
        self.dd = dic
        self.dd[3] = 'df'
        dic = {'d': 'dfd'}


def c(dic):
    dic[34] ='dd'

if __name__ == "__main__":
    f = {}
    g = f
    f.update({'3': 'dd'})
    print(g)
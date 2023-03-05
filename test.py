dic = {'pos': {'x': 1, 'y': 2}}
class dic1:
    def __init__(self):
        self.dic = dic

dic_ob = dic1()
print(dic_ob)
print(dic)
print([[dic['pos']['x']], [dic['pos']['y']]])
class Variable:
    def __init__(self, var_int):
        self.name = var_int
        self.value = None
        self.implied_by_roots = []
        self.stage = None
        self.VSIDS_score = {True: 0,
                            False: 0}
        self.antecedent = None
        self.imply_q = 0

    def __int__(self):
        if(self.value is True):
            return self.name
        elif(self.value is False):
            return -self.name
        return None

    def __str__(self):
        ret = ''
        if(self.value == False):
            ret = '-{}@{} -> {}, {}'.format(self.name,self.stage,list(map(int,self.implied_by_roots)), self.imply_q)
        elif(self.value == True):
            ret = '{}@{} -> {}, {}'.format(self.name,self.stage,list(map(int,self.implied_by_roots)), self.imply_q)
        else:
            ret = '${}@{} -> {}, {}'.format(self.name,self.stage,list(map(int,self.implied_by_roots)), self.imply_q)
        return ret

    def reset(self):
        self.value = None
        self.implied_by_roots = []
        self.stage = None
        self.antecedent = None
        self.imply_q = 0

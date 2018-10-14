from variable import Variable

class Literal:
    def __init__(self, var, sign):
        self.var = var
        self.sign = sign

    def __str__(self):
        #print("literal : {} with sign {} and value {}".format(self.var.name,self.sign, self.var.value))
        if self.var.value is not None:
            return '{} {}{}'.format(self.var.value == self.sign, ' ' if self.sign == True else ' -',self.var.name)
        if self.sign:
            return '{}'.format(self.var.name)
        else:
            return '{}'.format(-self.var.name)

    def value(self):
        if self.var.value is None:
            return None
        return (self.sign == self.var.value)

    def conflictsWith(self, literal):
        return  self.var is literal.var and self.sign != literal.sign

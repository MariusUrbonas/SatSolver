from variable import Variable
from random import shuffle

class Model:
    def __init__(self, variable_name_set):
        self.unassigned_variables = []
        self.variables = []
        self.variables_dict = {}
        for var_name in variable_name_set:
            variable_obj = Variable(var_name)
            self.variables_dict[var_name] = variable_obj
            self.unassigned_variables.append(variable_obj)
            self.variables.append(variable_obj)
        shuffle(self.unassigned_variables)
        shuffle(self.variables)
        self.stage = 0
        self.imply_q = 0
        self._UIP_stack = []

    def __str__(self):
        ret_str = '================MODEL====================\n'
        ret_str += 'unassinged vars: {}'.format(list(map(lambda x: (x.name , max(x.VSIDS_score[True],x.VSIDS_score[False])), self.unassigned_variables)))
        ret_str += '\n'
        for var in self.variables_dict:
            ret_str += str(self.variables_dict[var]) + '\n'
        ret_str += '========================================'
        return ret_str

    def get_var_obj(self, var):
        return self.variables_dict[var]

    def all_variables_assigned(self):
        return len(self.unassigned_variables) == 0

    def _get_implication_roots(self, clause):
        impl_roots = []
        for lit in clause.literals:
            for root in lit.var.implied_by_roots:
                if root not in impl_roots:
                    impl_roots.append(root)
        return impl_roots

    def _get_implication_UIPs(self, clause):
        impl_UIPs = []
        for lit in clause.literals:
            for root in lit.var.implied_by_roots:
                if root not in impl_UIPs:
                    impl_UIPs.append(root)
        return impl_UIPs

    def update_VSIDS(self, learnt_clauses):
        for var in self.variables:
            var.VSIDS_score[True] *= 0.95
            var.VSIDS_score[False] *= 0.95
        for clause in learnt_clauses:
            for lit in clause.literals:
                lit.var.VSIDS_score[lit.sign] += 1
        self.unassigned_variables.sort(key = lambda x: max(x.VSIDS_score[True],x.VSIDS_score[False]), reverse=True)

    def backup(self, curr_Stage ,back_up_to_stage):
        reset_stack = []
        for bc_stage in range(curr_Stage, back_up_to_stage, -1):
            for var in self.variables:
                if var.stage == bc_stage:
                    reset_stack.append(var)
                    var.reset()
                    self.unassigned_variables.append(var)
        self.stage = back_up_to_stage
        return reset_stack

    def update_variable(self, var, value, stage):
        self.unassigned_variables.remove(var)
        self.stage = stage
        var.value = value
        var.stage = stage
        var.implied_by_roots = [var]
        var.implied_by = [var]
        var.is_UIP = True
        self.imply_q = 0

    def update_propogated(self, var, value, stage, clause, is_UIP):
        self.unassigned_variables.remove(var)
        var.value = value
        var.stage = stage
        roots = self._get_implication_roots(clause)
        if roots == []:
            var.implied_by_roots = [var]
            var.imply_q = 0
        else:
            var.implied_by_roots = roots
            self.imply_q += 1
            var.imply_q = self.imply_q
        var.antecedent = clause
        self.imply_q += 1
        var.imply_q = self.imply_q

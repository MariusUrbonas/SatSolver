from clause import Clause
from model import Model

class Sentence:
    def __init__(self, clause_list, model):
        self.clauses = [Clause(cl, model, _id) for (_id, cl) in enumerate(clause_list,0)]
        self.learnt_clauses = []
        self.watched_var_dict = self._make_dict()
        self._make_dict()

    def _make_dict(self):
        cl_dict = {}
        for clause in self.clauses:
            for watched_lit in clause.watched_literals():
                if watched_lit.var in cl_dict:
                    cl_dict[watched_lit.var].append(clause)
                else:
                    cl_dict[watched_lit.var] = [clause]
        return cl_dict

    def __str__(self):
        ret_str = '==================SENTENCE====================\n'
        for clause in self.clauses:
            ret_str += str(clause.id) + ' '*(5-len(str(clause.id))) + str(clause) + ('<-----UNIT'if clause.is_unit() else '') + '\n'
        ret_str += '---------------------------------------------\n'
        for clause in self.learnt_clauses:
            ret_str += str(clause.id) + ' '*(5-len(str(clause.id))) + str(clause) + ('<-----UNIT'if clause.is_unit() else '') + '\n'
        ret_str += '==============================================\n'
        return ret_str

    def all_clauses(self):
        return self.clauses + self.learnt_clauses

    def next_unit_batch(self):
        unit_clauses = [clause for clause in self.all_clauses() if clause.is_unit()]
        if(len(unit_clauses)==0):
            return (None, False)
        is_UIP = len(unit_clauses) == 1
        return (unit_clauses, is_UIP)

    def add_learnt_clauses(self, clauses, model, reset_stack):
        self.reset_watched_lits(reset_stack)
        for clause in clauses:
            clause.update_watched_literal()
            clause.update_watched_literal()
            for lit in clause.watched_literals():
                if lit.var in self.watched_var_dict:
                    self.watched_var_dict[lit.var].append(clause)
                else:
                    self.watched_var_dict[lit.var] = [clause]
            self.learnt_clauses.append(clause)

    def reset_watched_lits(self, stack):
        for clause in self.all_clauses():
            if clause.possibly_out_of_date():
                lits = clause.watched_literals()
                for lit in lits:
                    if(lit.value() == False):
                        new_var = clause.update_watched_literal()
                        if(new_var != None):
                            self.watched_var_dict[lit.var].remove(clause)
                            if lit.var in self.watched_var_dict:
                                self.watched_var_dict[new_var].append(clause)
                            else:
                                self.watched_var_dict[new_var] = [clause]


    def get_clauses_with(self, var):
        if var in self.watched_var_dict:
            return self.watched_var_dict[var]
        return []

    def update(self, var):
        if(var in self.watched_var_dict):
            clauses = list(self.watched_var_dict[var])
            for clause in clauses:
                self.watched_var_dict[var].remove(clause)
                new_watched_var = clause.update_watched_literal()
                if new_watched_var is None:
                    self.watched_var_dict[var].append(clause)
                elif new_watched_var in self.watched_var_dict:
                    self.watched_var_dict[new_watched_var].append(clause)
                else:
                    self.watched_var_dict[new_watched_var] = [clause]

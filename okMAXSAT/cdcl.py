import itertools
from model import Model
from sentence import Sentence
from clause import Clause
from operator import attrgetter
import random

class CDCL:
    def __init__(self, input_file, heuristic):
        if input_file is not None:
            clause_list = self.read_input(input_file)
        variable_set = set(map(abs, itertools.chain.from_iterable(clause_list)))
        self.model = Model(variable_set)
        self.sentence = Sentence(clause_list, self.model)
        self.root_stage = 0
        self.heuristic = heuristic

    def read_input(self, input_file):
        _sentence = []
        has_param = False
        intermediate = []
        with open(input_file, 'r') as f:
            for line in f:
                if has_param:
                    l = line.split()
                    if len(l) == 0:
                        continue
                    if l[0] == '%':
                        break
                    parsed_line = list(map(int, l))
                    if(parsed_line[-1] == 0):
                        intermediate.extend(parsed_line)
                        _sentence.append(intermediate[:-1])
                        intermediate = []
                    else:
                        intermediate.extend(parsed_line)
                elif line[:5] == 'p cnf':
                    params = list(map(int, line[5:].split()))
                    num_lit = params[0]
                    num_clauses = params[1]
                    has_param = True
        return _sentence

    def check(self, ans):
        vl = []
        for cl in self.sentence.clauses:
            vl.append(cl.is_true())
        return all(vl)

    def solve(self):
        stage = 0
        pick_var = 0
        self.conflicts = 0
        self.propogations = 0
        self.dec = 0
        while(not self.model.all_variables_assigned()):
            #self.DEBUG()
            (is_conflict, conflict_clause) = self._unit_propogation(stage)
            if(not self.model.all_variables_assigned()):
                if(is_conflict):
                    #print("conflicts")
                    learnt_clauses, backtrack_stage = self._analyze_conflict(conflict_clause, stage)
                    if(backtrack_stage == self.root_stage - 1):
                        return 'UNSAT'
                    reset_watched_lit_stack = self.model.backup(stage, backtrack_stage)
                    self.sentence.add_learnt_clauses(learnt_clauses, self.model, reset_watched_lit_stack)
                    self.model.update_VSIDS(learnt_clauses)
                    stage = backtrack_stage
                    self.conflicts += 1
                else:
                    if self._restart(pick_var):
                        reset_watched_lit_stack = self.model.backup(stage, -1)
                        self.sentence.reset_watched_lits(reset_watched_lit_stack)
                        stage = 0
                        pick_var += 1
                        print('reset')
                    else:
                        #if(pick_var%200 == 0):
                            #self.DEBUG()
                        stage += 1
                        pick_var += 1
                        self.dec += 1
                        value, var = self.pick_branching_variable()
                        self.model.update_variable(var, value, stage)
                        self.sentence.update(var)
        return self.model.variables

    def stats(self):
        return {'Decisions': self.dec,
                'Propagaions': self.propogations,
                'Conflicts': self.conflicts}

    def DEBUG(self):
        print(self.model)
        print(self.sentence)

    def _restart(self, counter):
        return (counter%1000 == 0 and counter > 0)

    def pick_branching_variable(self):
        if self.heuristic == 'RAND':
            var = random.choice(self.model.unassigned_variables)
            sign = random.choice([True,False])
        if self.heuristic == 'VSIDS':
            var = self.model.unassigned_variables[0]
            sign = True if var.VSIDS_score[True] > var.VSIDS_score[False] else False
        return sign, var

    def _check_conflict(self, literal):
        conf_list = [literal.conflictsWith(clause.get_unit()) for clause in self.sentence.all_clauses() if clause.is_unit()]
        return any(conf_list)

    def _unit_propogation(self, stage):
        (clauses, is_UIP) = self.sentence.next_unit_batch()
        while clauses != None:
            clause = clauses.pop()
            if(not clause.is_unit()):
                if(len(clauses) == 0):
                    (clauses, is_UIP) = self.sentence.next_unit_batch()
            else:
                literal = clause.get_unit()
                if(self._check_conflict(literal)):
                    return (True, clause)
                self.model.update_propogated(literal.var, literal.sign,stage , clause, is_UIP)
                self.propogations += 1
                self.sentence.update(literal.var)
                if(len(clauses) == 0):
                    (clauses, is_UIP) = self.sentence.next_unit_batch()
        return (False, None)

    def _analyze_conflict(self, confl_clause, stage):

        def find_conflicting_clause_pairs():
            conf_literal = confl_clause.get_unit()
            clauses = self.sentence.get_clauses_with(conf_literal.var)
            pos_lit = []
            neg_lit = []
            for clause in clauses:
                if(clause.is_unit()):
                    if(clause.get_unit() is conf_literal):
                        pos_lit.append(clause)
                    elif(clause.get_unit().conflictsWith(conf_literal)):
                        neg_lit.append(clause)
            return [item for item in itertools.product(pos_lit, neg_lit)]

        def reached_1_UIP(intermediate_lit_list, stage):
            return len(list(filter(lambda x: x.stage == stage, intermediate_lit_list))) <= 1

        def resolved_clause(i_lit_list, stage):
            while not reached_1_UIP(i_lit_list, stage):
                curr_sec_vars = list(filter(lambda x: x.stage == stage, i_lit_list))
                resolve_var = max(curr_sec_vars, key=attrgetter('imply_q'))
                if (resolve_var.antecedent != None):
                    i_lit_list = list(set(resolve_var.antecedent.variables()).union(set(i_lit_list)))
                    i_lit_list.remove(resolve_var)
                    #print('+++', list(map(str, i_lit_list)))
                else:
                     break
            return i_lit_list

        confl_clause_pairs = find_conflicting_clause_pairs()
        conf_var = confl_clause.get_unit().var
        learnt_clauses = []
        for (clauseA, clauseB) in confl_clause_pairs:
            var_list = list(set(clauseA.variables()).union(clauseB.variables()))
            var_list.remove(conf_var)
            if(len(var_list) == 0):
                return ([], -1)
            roots = var_list
            to_remove = []
            for var in var_list:
                 if var != var.implied_by_roots[0]:
                        if (set(var.implied_by_roots).issubset(set(roots))):
                            to_remove.append(var)
            for var in to_remove:
                roots.remove(var)
            #print(list(map(str, roots)))
            learnt_clause = resolved_clause(roots,stage)
            max_stage = max([var.stage for var in learnt_clause])
            new_vars = list(map(lambda x: -x,map(int, learnt_clause)))
            backtrack_stage = []
            learnt_clauses = []
            if(len(learnt_clause) == 1):
                learnt_clauses.append(Clause(new_vars, self.model, len(self.sentence.all_clauses())))
                backtrack_stage.append(max_stage-1)
            else:
                learnt_clause.sort(key=lambda x: x.stage, reverse=True)
                backtrack_stage.append(learnt_clause[1].stage)
                learnt_clauses.append(Clause(new_vars, self.model, len(self.sentence.all_clauses())))
        bc_stage = min(backtrack_stage)
        return learnt_clauses, bc_stage

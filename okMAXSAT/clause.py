from literal import Literal

class Clause:
    def __init__(self, lit_list, model, _id):
        self.literals = [Literal(model.get_var_obj(abs(lit_num)), lit_num > 0) for lit_num in lit_list]
        self._length = len(lit_list)
        self.id = _id
        if( self._length >= 2):
            self._watched_lit = self.literals[:2]
        else:
            self._watched_lit = [self.literals[0]]

    def __str__(self):
        index = [l for l in self.literals if l in self._watched_lit]
        lit =[[str(l)] if l in index else str(l) for l in self.literals]
        return '{} watched lits : {}'.format(lit, list(map(str, index)))

    def watched_literals(self):
        return self._watched_lit

    def variables(self):
        return [lit.var for lit in self.literals]

    def is_unit(self):
        wlit_values = [lit.value() for lit in self._watched_lit]
        if(self._length>1):
            return (None in wlit_values) and (False in wlit_values)
        else:
            return (None in wlit_values)

    def possibly_out_of_date(self):
        wlit_values = [not lit.value() for lit in self._watched_lit]
        return any(wlit_values)

    def get_unit(self):
        if(self._watched_lit[0].value() == None):
            return self._watched_lit[0]
        return self._watched_lit[1]

    def is_true(self):
        wlit_values = [lit.value() for lit in self._watched_lit]
        return any(wlit_values)

    def _find_next_literal_to_watch(self):
        unit_lit = [literal for literal in self.literals if (((literal.value() is None) or (literal.value() is True)) and (literal not in self._watched_lit))]
        try:
            return unit_lit[0]
        except Exception as inst:
            return None

    def update_watched_literal(self):
        if(self._length < 2 or any(map(lambda x: x.value(), self._watched_lit)) or all(map(lambda x: x.value() == None, self._watched_lit))):
            return
        new_literal_to_watch = self._find_next_literal_to_watch()
        if(new_literal_to_watch is not None):
            if(self._watched_lit[0].value() is False):
                self._watched_lit[0] = new_literal_to_watch
            else:
                self._watched_lit[1] = new_literal_to_watch
            return new_literal_to_watch.var
        return None

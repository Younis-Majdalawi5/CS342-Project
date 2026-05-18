from model import Automaton, EPSILON
from graphics import StateItem

class RegexToNFA:
    # Convert regex to NFA

    def __init__(self):
        self.counter = 0  # state counter

    def new_state_name(self):
        # create unique state name
        name = f"q{self.counter}"
        self.counter += 1
        return name

    def precedence(self, op):
        # operator priority
        if op == "*": return 3
        if op == ".": return 2
        if op == "|": return 1
        return 0

    def is_symbol(self, ch):
        # check if character is symbol
        return ch.isalnum() or ch == EPSILON

    def add_concat_operators(self, regex):
        # add missing concatenation dots
        regex = regex.replace(" ", "")
        result = []

        for i, ch in enumerate(regex):
            result.append(ch)

            if i + 1 < len(regex):
                nxt = regex[i + 1]

                if (self.is_symbol(ch) or ch == ")" or ch == "*") and \
                   (self.is_symbol(nxt) or nxt == "("):
                    result.append(".")

        return "".join(result)

    def to_postfix(self, regex):
        # convert infix regex to postfix
        regex = self.add_concat_operators(regex)

        output = []
        stack = []

        for ch in regex:

            if self.is_symbol(ch):
                output.append(ch)

            elif ch == "(":
                stack.append(ch)

            elif ch == ")":

                while stack and stack[-1] != "(":
                    output.append(stack.pop())

                if not stack:
                    raise ValueError("Regex Error: Mismatched parentheses.")

                stack.pop()

            elif ch in ["|", ".", "*"]:

                while stack and stack[-1] != "(" and \
                      self.precedence(stack[-1]) >= self.precedence(ch):

                    output.append(stack.pop())

                stack.append(ch)

            else:
                raise ValueError(f"Regex Error: Unsupported character '{ch}'")

        while stack:

            if stack[-1] == "(":
                raise ValueError("Regex Error: Mismatched parentheses.")

            output.append(stack.pop())

        return output

    def add_nfa_state(self, automaton, name):
        # add state to automaton
        item = StateItem(name, 0, 0)
        automaton.add_state(item)
        return item

    def add_edge(self, automaton, src, symbol, dst):
        # add transition between states
        automaton.add_transition(
            automaton.states[src],
            symbol,
            automaton.states[dst]
        )

    def build_from_regex(self, regex):
        # build NFA from postfix regex

        self.counter = 0

        postfix = self.to_postfix(regex)

        automaton = Automaton(is_dfa=False)

        stack = []

        for token in postfix:

            if self.is_symbol(token):

                # create simple transition
                start = self.new_state_name()
                end = self.new_state_name()

                self.add_nfa_state(automaton, start)
                self.add_nfa_state(automaton, end)

                self.add_edge(automaton, start, token, end)

                stack.append((start, end))

            elif token == ".":

                # connect two NFAs
                if len(stack) < 2:
                    raise ValueError("Invalid concatenation.")

                s2, e2 = stack.pop()
                s1, e1 = stack.pop()

                self.add_edge(automaton, e1, EPSILON, s2)

                stack.append((s1, e2))

            elif token == "|":

                # union operation
                if len(stack) < 2:
                    raise ValueError("Invalid union operation.")

                s2, e2 = stack.pop()
                s1, e1 = stack.pop()

                start = self.new_state_name()
                end = self.new_state_name()

                self.add_nfa_state(automaton, start)
                self.add_nfa_state(automaton, end)

                self.add_edge(automaton, start, EPSILON, s1)
                self.add_edge(automaton, start, EPSILON, s2)

                self.add_edge(automaton, e1, EPSILON, end)
                self.add_edge(automaton, e2, EPSILON, end)

                stack.append((start, end))

            elif token == "*":

                # repetition using *
                if len(stack) < 1:
                    raise ValueError("Invalid star operation.")

                s, e = stack.pop()

                start = self.new_state_name()
                end = self.new_state_name()

                self.add_nfa_state(automaton, start)
                self.add_nfa_state(automaton, end)

                self.add_edge(automaton, start, EPSILON, s)
                self.add_edge(automaton, start, EPSILON, end)

                self.add_edge(automaton, e, EPSILON, s)
                self.add_edge(automaton, e, EPSILON, end)

                stack.append((start, end))

        if len(stack) != 1:
            raise ValueError("Invalid regular expression structure.")

        start, end = stack.pop()

        automaton.set_start(automaton.states[start])
        automaton.set_accept(automaton.states[end])

        self.auto_layout(automaton)

        return automaton

    def auto_layout(self, automaton):
        # arrange states on screen

        if not automaton.start_state:
            return

        depths = {}

        queue = [(automaton.start_state, 0)]

        depths[automaton.start_state] = 0

        while queue:

            current, d = queue.pop(0)

            state_obj = automaton.states[current]

            for targets in state_obj.transitions.values():

                for target in targets:

                    if target not in depths:
                        depths[target] = d + 1
                        queue.append((target, d + 1))

        levels = {}

        for state, d in depths.items():

            if d not in levels:
                levels[d] = []

            levels[d].append(state)

        center_y = 350
        start_x = 100

        x_spacing = 130
        y_spacing = 110

        for d in sorted(levels.keys()):

            nodes = levels[d]

            x = start_x + (d * x_spacing)

            num_nodes = len(nodes)

            start_y = center_y - ((num_nodes - 1) * y_spacing / 2)

            for i, state_name in enumerate(nodes):

                y = start_y + (i * y_spacing)

                automaton.states[state_name].setPos(x, y)
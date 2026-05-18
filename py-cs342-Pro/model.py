from collections import deque

EPSILON = "ε"

class Automaton:
    # core model for the FA it handles states, transitions, rule validation, and string simulation.

    def __init__(self, is_dfa=True):
        self.states = {}  # Dictionary with state_name : stateObject as keys and values
        self.start_state = None
        self.accept_states = set() #empty set
        self.is_dfa = is_dfa 

    def add_state(self, state):
        self.states[state.name] = state  # make new state

    def set_start(self, state):
        # Defines the initial state and makes sure only one start state exists by unsetting the previous one if necessary.

        if self.start_state and self.start_state != state.name:
            old = self.states.get(self.start_state)
            if old:
                old.set_start(False)
        self.start_state = state.name
        state.set_start(True)

    def set_accept(self, state):
        state.set_accept(True)
        self.accept_states.add(state.name)  # mark given state as an accept state.

    def add_transition(self, from_state, symbol, to_state):
        # add transition between two states and enforces DFA constraints
        if symbol.lower() in ["epsilon", "eps"]:
            symbol = EPSILON

        if self.is_dfa and symbol == EPSILON:
            raise ValueError("DFA Error: Cannot contain epsilon (ε) transitions.")

        # ensure no multiple paths for same symbol
        if self.is_dfa:
            existing_targets = from_state.transitions.get(symbol, []) # checks exisitng for symbol
            if existing_targets and to_state.name not in existing_targets: # if there are existing and it is not in existing
                raise ValueError(f"DFA Error: State '{from_state.name}' already has a transition for '{symbol}'.")

        from_state.transitions.setdefault(symbol, [])
        if to_state.name not in from_state.transitions[symbol]: # create transition dict for from state and if to state not in from state transitions add it
            from_state.transitions[symbol].append(to_state.name)

    def alphabet(self):
        symbols = set()
        for state in self.states.values():  # scans all transitions to build the automatons input alphabet
            for symbol in state.transitions.keys():
                if symbol != EPSILON:
                    symbols.add(symbol)
        return sorted(symbols)

    def validate(self):
        """
        Performs a error check on the automaton's design
        Checks for completeness, structural integrity, and strict DFA compliance
        Returns a list of error messages
        """
        errors = []
        if not self.states:
            errors.append("Validation Error: No states exist in the automaton.")
        if not self.start_state:
            errors.append("Validation Error: A Start state must be defined.")
        if not self.accept_states:
            errors.append("Validation Error: At least one Accept state must be defined.")

        # check for transitions to non-existent states
        for state in self.states.values():
            for symbol, targets in state.transitions.items():
                for target in targets:
                    if target not in self.states:
                        errors.append(f"Broken Link: Transition from {state.name} points to unknown state {target}.")

        # DFA-specific rules
        if self.is_dfa:
            alphabet = self.alphabet()
            for state in self.states.values():
                for symbol, targets in state.transitions.items():# no epsilon and no ambiguous transitions
                    if symbol == EPSILON:
                        errors.append(f"DFA Rule Violation: State '{state.name}' has an epsilon transition.")
                    if len(targets) > 1:
                        errors.append(
                            f"DFA Rule Violation: State '{state.name}' has multiple paths for symbol '{symbol}'.")

                # every state must have a path for every symbol in the automatons alphabet
                missing_symbols = [sym for sym in alphabet if
                                   sym not in state.transitions or not state.transitions[sym]]
                if missing_symbols:
                    errors.append(
                        f"DFA Rule Violation: State '{state.name}' is missing transitions for symbols: {missing_symbols}. In a DFA, every state must have a transition for every symbol in the alphabet.")

        return errors

    def epsilon_closure(self, state_names): # computes the ε-closure for a set of states using a Stack-based Depth First Search.
        closure = set(state_names)
        stack = list(state_names)
        while stack:
            current = stack.pop()
            state = self.states.get(current)
            if not state:
                continue
            for nxt in state.transitions.get(EPSILON, []):
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return closure

    def simulate_dfa(self, input_str):
        """
        Simulates the processing of a string through a DFA.
        Requires a single deterministic path. Returns a boolean result and the trace log.
        """
        current = self.start_state
        if not current:
            return False, [] # no steps taken

        trace = [f"Start at: {current}"]
        for char in input_str:
            state = self.states.get(current)
            if not state or char not in state.transitions:
                trace.append(f"Rejected: No transition from '{current}' on symbol '{char}'")
                return False, trace
            current = state.transitions[char][0]# only take the first target since it is dfa
            trace.append(f"Read '{char}' -> go to {current}")

        is_accepted = current in self.accept_states # returns bool value
        trace.append(f"Ended at '{current}'. Accepted? {is_accepted}")
        return is_accepted, trace

    def simulate_nfa(self, input_str):
        """
        Simulates the processing of a string through an NFA by u
        """
        if not self.start_state:
            return False, []

        current_states = self.epsilon_closure({self.start_state}) # initial state includes its epsilon closure
        trace = [f"Start (with ε-closure): {sorted(current_states)}"]

        for char in input_str:
            next_states = set()
            for state_name in current_states:
                state = self.states.get(state_name) # get the next state
                if state:
                    next_states.update(state.transitions.get(char, []))

            current_states = self.epsilon_closure(next_states)# apply epsilon closure to the resulting states
            trace.append(f"Read '{char}' -> current possible states: {sorted(current_states)}")

        # accept if any of the parallel current paths reached an accepted state
        accepted = any(s in self.accept_states for s in current_states)
        trace.append(f"Final possible states: {sorted(current_states)}. Accepted? {accepted}")
        return accepted, trace

    def simulate(self, input_str):
        # tries to simulate the automaton depending on type
        if self.is_dfa:
            return self.simulate_dfa(input_str)
        return self.simulate_nfa(input_str)

    def generate_language(self, max_length):#Generates all valid strings accepted by the automaton up to max length using bfs
        alphabet = self.alphabet()
        accepted_strings = []
        queue = deque([""])  # starts with an empty string

        while queue: #loop until no more strings
            s = queue.popleft()

            accepted, _ = self.simulate(s) # check if the current string is accepted by machines
            if accepted:
                accepted_strings.append(s if s else EPSILON) # add to accepted strings


            if len(s) < max_length: # continue building strings if under the max length limit
                for symbol in alphabet:
                    queue.append(s + symbol)

        # remove duplicates and sort by length and then alphabetically
        return sorted(list(set(accepted_strings)), key=lambda x: (len(x), x))
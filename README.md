# CS342-Project - Report

## Project: Automata Simulator with Regular Expression Language Generation

**Team Members:** 
1. Younis Majdalawi - 2022901093
2. محمدخير مازن بني طه  2022901070
3. محمد وسيم محمد غنيم 2023901055
4. محمد العمري - 404

## 1. Introduction

The objective of this project is to bridge the gap between the theoretical concepts of Computation Theory and practical software engineering. We have designed and implemented a comprehensive, interactive Automata Simulator capable of constructing, validating, and simulating Deterministic Finite Automata (DFA) and Non-Deterministic Finite Automata (NFA).

Furthermore, the application integrates an advanced Regex Engine that parses Regular Expressions and converts them into an equivalent NFA using Thompson's Construction. Finally, a language generation module is included to enumerate valid strings accepted by the automaton up to a specified length.

## 2. System Architecture & Modular Design

To ensure a clean, maintainable, and scalable codebase, the project was developed using Python (with PyQt5 for the GUI) and strictly adheres to Object-Oriented Programming (OOP) principles. The system is divided into four main independent modules:

- **`model.py` (Core Logic Engine):** Contains the fundamental classes `State`, `Transition`, and `Automaton`. It is strictly responsible for maintaining the mathematical model, enforcing structural constraints (Validation), and executing the simulation (Epsilon Closures, string parsing).
    
- **`regex_engine.py` (Compiler & Converter):** Implements the logic required to parse regular expressions. It uses the Shunting-Yard algorithm to convert infix expressions to postfix, and Thompson's Construction to build the NFA. It also features a custom BFS layout algorithm for visual alignment.
    
- **`graphics.py` (Visual Components):** Contains the `StateItem` class extending `QGraphicsItem`. It handles all GUI-related logic, including drawing states, color-coding (Start/Accept), and calculating precise trigonometric coordinates for transition arrows.
    
- **`main.py` (Controller & UI):** Serves as the main entry point. It constructs the PyQt5 interface, binds user interactions (button clicks) to the core logic, and acts as the bridge between the UI and the underlying models.
    

## 3. Core Algorithms Explanation

Our implementation relies on several robust algorithms to ensure absolute mathematical correctness:

### 3.1 Strict DFA Validation

Before simulation, the `validate()` method verifies structural integrity. For DFAs, it enforces strict completeness and determinism. It checks that no ε-transitions exist, ensures no state has duplicate outgoing paths for the same symbol, and verifies that _every_ state has exactly one transition for _every_ symbol present in the alphabet.

### 3.2 Simulation Engine (Epsilon Closure)

The NFA simulation tracks multiple concurrent paths. We implemented an `epsilon_closure(states)` algorithm using a Stack-based Depth-First Search (DFS). Before reading any input character, the engine computes the ε-closure of the current states, reads the symbol, transitions to the next states, and applies the ε-closure again. The string is accepted if any of the final concurrent states is a valid accept state.

### 3.3 Thompson's Construction (Regex to NFA)

Converting a Regex to an NFA involves two algorithmic steps:

1. **Shunting-Yard Algorithm:** Converts the infix regular expression (e.g., `(a|b)*`) into postfix notation, injecting explicit concatenation operators (`.`) where necessary.
    
2. **Thompson's Templates:** Evaluates the postfix expression using a Stack. It applies standard NFA templates (Union, Concatenation, Kleene Star) by connecting smaller NFA blocks using ε-transitions, preserving the mathematical integrity of Thompson's original algorithms.
    

### 3.4 Language Generation (BFS Traversal)

To generate the accepted language up to a maximum length $L$, we implemented a Breadth-First Search (BFS) using a Queue. Starting with an empty string, the algorithm appends alphabet symbols, simulates each generated string, and records it if accepted. BFS ensures that strings are generated in lexicographical order based on length.

### 3.5 Auto-Layout Rendering

To prevent the generated NFA states from overlapping visually, a Level-based BFS algorithm was implemented. It calculates the depth of each state relative to the start state, groups states by depth level, and renders them on the canvas in a hierarchical "Diamond Shape," calculating appropriate $(X, Y)$ coordinates for perfect symmetry.

## 4. Examples & Test Cases

To prove the correctness of our simulator, several test cases were executed:

- **Example 1 (DFA Validation):** * _Setup:_ We created a state $q_0$ transitioning to $q_1$ on symbol `a`. The alphabet is `{a, b}`.
    
    - _Result:_ The validator successfully rejected the DFA, throwing the error: `State 'q0' is missing transitions for symbols: ['b']`, proving our completeness check works perfectly.
        
- **Example 2 (NFA Simulation):**
    
    - _Setup:_ An NFA with an $\epsilon$-transition from the start state to an accept state.
        
    - _Input:_ Empty String `""` (or `ε`).
        
    - _Result:_ Successfully accepted, confirming the ε-closure algorithm processes empty inputs correctly.
        
- **Example 3 (Regex to NFA):**
    
    - _Input:_ `(a|b)*abb`
        
    - _Result:_ The engine successfully generated the exact Thompson's NFA equivalent, complete with all necessary $\epsilon$-transitions, and laid it out symmetrically on the canvas. _(Include a screenshot of the Regex NFA here)_ ``
        

## 5. Challenges & Solutions

During development, we encountered several technical challenges:

1. **State Overlapping in GUI:** Initial implementations of the Regex-to-NFA converter placed all states at coordinate $(0,0)$, creating a visual mess.
    
    - _Solution:_ We engineered the custom Level-based BFS layout algorithm mentioned above, transforming chaotic structures into clean, readable graphs.
        
2. **Empty String Inputs:** Users needed a way to input $\epsilon$ for transitions without typing standard characters.
    
    - _Solution:_ We updated the UI to accept specific keywords (`eps`, `epsilon`) and mapped them in the backend to a global `EPSILON` constant to differentiate them from standard alphabet characters like `e`.
        

## 6. Conclusion

This project successfully transitions abstract computational theory into a tangible, interactive tool. By strictly implementing DFA/NFA constraints, Thompson's construction, and robust simulations, we solidified our understanding of finite automata and improved our software engineering and algorithm design skills.

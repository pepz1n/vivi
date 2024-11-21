import tkinter as tk
from tkinter import messagebox, scrolledtext


class FiniteAutomaton:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.initialState = None
        self.acceptStates = set()

    def addState(self, state, isInitial=False, isAccept=False):
        self.states.add(state)
        if isInitial:
            self.initialState = state
        if isAccept:
            self.acceptStates.add(state)

    def addTransition(self, fromState, symbol, toState):
        if fromState not in self.transitions:
            self.transitions[fromState] = {}
        if symbol not in self.transitions[fromState]:
            self.transitions[fromState][symbol] = set()
        self.transitions[fromState][symbol].add(toState)

    def validateString(self, inputString):
        currentStates = {self.initialState}
        for symbol in inputString:
            nextStates = set()
            for state in currentStates:
                if state in self.transitions and symbol in self.transitions[state]:
                    nextStates.update(self.transitions[state][symbol])
            currentStates = nextStates
        return bool(currentStates & self.acceptStates)


def grammarToAutomaton(grammarRules, startSymbol):
    fa = FiniteAutomaton()
    for rule in grammarRules:
        left, right = rule.split("->")
        left = left.strip()
        fa.addState(left, isInitial=(left == startSymbol))
        productions = right.split("|")
        for production in productions:
            production = production.strip()
            if production == "ε":
                fa.addState(left, isAccept=True)
            elif len(production) == 1:  # Terminal only
                fa.addState("accept", isAccept=True)
                fa.addTransition(left, production, "accept")
            else:
                terminal, nonTerminal = production[0], production[1:]
                fa.addState(nonTerminal)
                fa.addTransition(left, terminal, nonTerminal)
    return fa


class GrammarSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Gramática Regular e Autômato Finito")

        tk.Label(root, text="Definição da Gramática Regular (uma regra por linha):").pack()
        self.grammarInput = scrolledtext.ScrolledText(root, width=50, height=10)
        self.grammarInput.pack()

        tk.Label(root, text="Símbolo Inicial:").pack()
        self.startSymbolEntry = tk.Entry(root, width=10)
        self.startSymbolEntry.pack()

        tk.Label(root, text="Strings para testar (separadas por vírgula):").pack()
        self.testStringsEntry = tk.Entry(root, width=50)
        self.testStringsEntry.pack()

        self.runButton = tk.Button(root, text="Testar Strings", command=self.runSimulation)
        self.runButton.pack(pady=10)

        tk.Label(root, text="Resultados:").pack()
        self.resultOutput = scrolledtext.ScrolledText(root, width=50, height=10, state="disabled")
        self.resultOutput.pack()

    def runSimulation(self):
        grammarText = self.grammarInput.get("1.0", tk.END).strip()
        startSymbol = self.startSymbolEntry.get().strip()
        testStrings = self.testStringsEntry.get().strip().split(",")

        if not grammarText or not startSymbol or not testStrings:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        grammarRules = grammarText.splitlines()
        try:
            automaton = grammarToAutomaton(grammarRules, startSymbol)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar a gramática: {e}")
            return

        results = []
        for string in testStrings:
            string = string.strip()
            if automaton.validateString(string):
                results.append(f"'{string}' -> Aceita")
            else:
                results.append(f"'{string}' -> Rejeitada")

        self.resultOutput.config(state="normal")
        self.resultOutput.delete("1.0", tk.END)
        self.resultOutput.insert(tk.END, "\n".join(results))
        self.resultOutput.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = GrammarSimulatorApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import messagebox, scrolledtext
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FiniteAutomaton:
    def __init__(self, deterministic=None):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.initialState = None
        self.acceptStates = set()
        self.deterministic = deterministic

    def addState(self, state, isInitial=False, isAccept=False):
        self.states.add(state)
        if isInitial:
            self.initialState = state
        if isAccept:
            self.acceptStates.add(state)

    def addTransition(self, fromState, symbol, toState):
        if fromState not in self.transitions:
            self.transitions[fromState] = {}
        if symbol in self.transitions[fromState]:
            self.deterministic = False
        else:
            self.transitions[fromState][symbol] = toState

    def validateString(self, inputString):
        if not inputString:
            return self.initialState in self.acceptStates

        currentStates = {self.initialState}
        for symbol in inputString:
            nextStates = set()
            for state in currentStates:
                if state in self.transitions and symbol in self.transitions[state]:
                    nextStates.add(self.transitions[state][symbol])
            currentStates = nextStates
        return bool(currentStates & self.acceptStates)

    def describe(self):
        """Gera a descrição textual do autômato."""
        description = []
        description.append(f"Estados: {', '.join(self.states)}")
        description.append(f"Alfabeto: {', '.join(self.alphabet)}")
        description.append(f"Estado Inicial: {self.initialState}")
        description.append(f"Estados de Aceitação: {', '.join(self.acceptStates)}")
        description.append(f"Autômato Determinístico: {'Sim' if self.deterministic else 'Não'}")
        description.append("Transições:")
        for state, transitions in self.transitions.items():
            for symbol, target in transitions.items():
                description.append(f"  {state} -- {symbol} --> {target}")
        return "\n".join(description)

    def generateGraph(self):
        """Gera o grafo visual do autômato."""
        G = nx.DiGraph()
        for state, transitions in self.transitions.items():
            for symbol, target in transitions.items():
                G.add_edge(state, target, label=symbol)

        pos = nx.spring_layout(G)
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        return plt

def grammarToAutomaton(grammarRules, startSymbol):
    fa = FiniteAutomaton(deterministic=True)
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
                fa.alphabet.add(terminal)
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

        self.graphButton = tk.Button(root, text="Gerar Grafo", command=self.generateGraph)
        self.graphButton.pack(pady=5)

        tk.Label(root, text="Definição do Autômato e Resultados:").pack()
        self.resultOutput = scrolledtext.ScrolledText(root, width=50, height=15, state="disabled")
        self.resultOutput.pack()

    def runSimulation(self):
        grammarText = self.grammarInput.get("1.0", tk.END).strip()
        startSymbol = self.startSymbolEntry.get().strip()
        testStrings = self.testStringsEntry.get().strip().split(",")

        if not grammarText or not startSymbol:
            messagebox.showerror("Erro", "Os campos de gramática e símbolo inicial devem ser preenchidos.")
            return

        grammarRules = grammarText.splitlines()
        try:
            self.automaton = grammarToAutomaton(grammarRules, startSymbol)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar a gramática: {e}")
            return

        description = self.automaton.describe()

        results = []
        for string in testStrings:
            string = string.strip()
            if not string:
                continue
            if self.automaton.validateString(string):
                results.append(f"'{string}' -> Aceita")
            else:
                results.append(f"'{string}' -> Rejeitada")

        self.resultOutput.config(state="normal")
        self.resultOutput.delete("1.0", tk.END)
        self.resultOutput.insert(tk.END, description + "\n\n")
        self.resultOutput.insert(tk.END, "\n".join(results))
        self.resultOutput.config(state="disabled")

    def generateGraph(self):
        if not hasattr(self, 'automaton'):
            messagebox.showerror("Erro", "Por favor, execute a simulação primeiro.")
            return

        plt = self.automaton.generateGraph()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = GrammarSimulatorApp(root)
    root.mainloop()

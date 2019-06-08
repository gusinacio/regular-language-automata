import pickle
import string


# Representação de Automato Finito
class FiniteAutomata:
    def __init__(self, automata=None, initial=0, accepting=None):
        # Se está recebendo um automato significa que ele já foi carregado
        # Se nao, inicia um novo dict
        if automata is None:
            self.automata = {}
        else:
            self.automata = automata
        self.initial = str(initial)
        if accepting is None:
            self.accepting = set()
        else:
            self.accepting = accepting

    def setInitial(self, state):
        self.initial = str(state)

    def isInitial(self, state):
        return self.initial == str(state)

    def addAccepting(self, state):
        self.accepting.add(str(state))

    def isAccepting(self, state):
        return state in self.accepting

    def removeAccepting(self, state):
        self.accepting.remove(str(state))

    def addState(self, state):
        self.automata[str(state)] = {}

    def hasState(self, state):
        return str(state) in self.automata

    # Para remover o estado, nós tentamos remove-lo das transições para não ocorrer problemas
    # Primeiro tentamos remover o estado do set(), se der erro ele cai no except e remove apenas a string
    def removeState(self, state):
        del self.automata[str(state)]
        for x in self.automata:
            keys = list(self.automata[x].keys())
            while keys:
                c = keys.pop()
                try:
                    if state in self.automata[x][c]:
                        self.automata[x][c].remove(str(state))
                except:
                    if state == self.automata[x][c]:
                        del self.automata[x][c]
        if self.isAccepting(state):
            self.removeAccepting(state)

    def getStates(self):
        return self.automata.keys()

    def getChars(self):
        chars = set()
        for x in self.automata.values():
            for y in x.keys():
                chars.add(y)
        chars = list(chars)
        chars.sort()
        return chars

    def addTransiction(self, state, char, to):
        self.automata[str(state)][char] = str(to)

    def removeTransiction(self, state, char):
        self.automata[str(state)].pop(char)

    def save(self, file):
        with open(file, 'wb') as pickle_file:
            pickle.dump(self, pickle_file)

    # Carrega o automato finito a partir de um filename
    def load(self, file):
        with open(file, 'rb') as pickle_file:
            finiteAutomata = pickle.load(pickle_file)
            self.automata = finiteAutomata.automata
            self.initial = finiteAutomata.initial
            self.accepting = finiteAutomata.accepting

    def union(self, other):
        union_result = NDFiniteAutomata()
        start_state = 'q0'
        union_result.addState(start_state)
        union_result.setInitial(start_state)
        id = 1
        translateTable = {}
        for state in self.getStates():
            translateTable[state] = 'q' + str(id)
            union_result.addState(translateTable[state])
            id += 1
        for state in self.getStates():
            for char in self.getChars():
                if char in self.automata[state].keys():
                    toState = self.automata[state][char]
                    if isinstance(toState, str):
                        union_result.addTransiction(translateTable[state], char, translateTable[toState])
                    else:
                        for s in toState:
                            union_result.addTransiction(translateTable[state], char, translateTable[s])
        for accept in self.accepting:
            union_result.addAccepting(translateTable[accept])
        union_result.addTransiction(start_state, '&', translateTable[self.initial])
        translateTable = {}
        for state in other.getStates():
            translateTable[state] = 'q' + str(id)
            union_result.addState(translateTable[state])
            id += 1
        for state in other.getStates():
            for char in other.getChars():
                if char in other.automata[state].keys():
                    toState = other.automata[state][char]
                    if isinstance(toState, str):
                        union_result.addTransiction(translateTable[state], char, translateTable[toState])
                    else:
                        for s in toState:
                            union_result.addTransiction(translateTable[state], char, translateTable[s])
        for accept in other.accepting:
            union_result.addAccepting(translateTable[accept])
        union_result.addTransiction(start_state, '&', translateTable[other.initial])

        return union_result

    def intersect(self, other):
        self.complement()
        other.complement()
        automata = self.union(other)

        automata.complement()
        if automata.initial in automata.accepting:
            automata.accepting.remove(automata.initial)

        return automata

    def complement(self):
        final_states = [item for item in list(self.getStates()) if item not in self.accepting]
        self.accepting = final_states

    # Função para printar tabela no console
    def printTable(self):
        chars = self.getChars()
        print("      | \'" + "\' | \'".join(chars) + "' |")
        print("------", end='')
        for i in range(len(chars)):
            print("|-----", end='')
        print("|")
        states = list(self.getStates())
        states.sort()
        states.sort(key=len)
        for state in states:
            if state in self.accepting:
                print("*", end='')
            else:
                print(" ", end='')
            if state == self.initial:
                print("->", end='')
            else:
                print("  ", end='')
            print(state + "  |  ", end='')
            for c in chars:
                if c in self.automata[state]:
                    print(str(self.automata[state][c]) + "  |  ", end='')
                else:
                    print("-  |  ", end='')
            print()
        print()


# Automato Finito Não Deterministico filho de FiniteAutomata
class NDFiniteAutomata(FiniteAutomata):
    # Alteramos o addTransiction para suportar transições não deterministicas
    def addTransiction(self, state, char, to):
        if char not in self.automata[str(state)]:
            self.automata[str(state)][char] = set()
        self.automata[str(state)][char].add(str(to))

    # Determinizar
    def determinize(self):
        finite = DFiniteAutomata()
        chars = self.getChars()
        tState = []
        for state in self.getStates():
            tState.append({state})
        finite.setInitial(self.initial)
        while tState:
            stateList = list(tState.pop())
            init = False
            if len(stateList) == 1 and stateList[0] == self.initial:
                init = True
            (state, accept) = self.eClosure(stateList)
            s = getState(state)
            finite.addState(s)
            if init:
                finite.setInitial(s)
            if accept:
                finite.addAccepting(s)
            for char in chars:
                if char == '&':
                    continue
                trans = set()
                for toState in state:
                    if not char in self.automata[toState]:
                        continue
                    trans.update(self.automata[toState][char])
                if len(trans) == 0:
                    continue
                (fecho, accept) = self.eClosure(list(trans))
                newState = getState(fecho)
                if not newState in finite.automata and not newState in tState:
                    tState.append(fecho)
                finite.addTransiction(s, char, newState)
        return finite

    # Função e-fecho que retorna a lista de estados alcançaveis, e um boolean para saber se esse novo estado é de aceitação
    def eClosure(self, efecho):
        state = set()
        accept = False
        while efecho:
            to = efecho.pop()
            state.add(to)
            if to in self.accepting:
                accept = True
            if '&' in self.automata[to]:
                for x in self.automata[to]['&']:
                    if not x in state:
                        efecho.append(x)
        return (state, accept)

    # Implementação de aceitação de string
    # Primeiro crimaos um automato finito Deterministico temporario e retornamos se ele aceita
    def accepts(self, s):
        finite = self.determinize()
        return finite.accepts(s)


# Automato Finito Deterministico filho de FiniteAutomata
class DFiniteAutomata(FiniteAutomata):
    # Roda a String, caracter por caracter por todos os estados
    # Se cair em estado que não existe, retorna False
    # Se cair em estado que não é de aceitação, retorna False
    # Se cair em estado de aceitação, retorna True
    def accepts(self, s):
        state = self.initial
        try:
            for c in s:
                if not c in self.automata[state]:
                    return False
                state = self.automata[state][c]
        except:
            print("Malformed automata")
        return state in self.accepting

    # Converte o AFD para Gramatica Regular
    def convertRG(self):
        grammar = RegularGrammar('S')
        stateNum = 0
        letters = string.ascii_uppercase.replace('S', '')
        conversion = {}
        hasEmptyWord = False
        for x in self.automata:
            if self.isInitial(x):
                conversion[x] = 'S'
            elif not x in conversion:
                conversion[x] = letters[stateNum]
                stateNum += 1
            if self.isInitial(x) and self.isAccepting(x):
                hasEmptyWord = True
            for y in self.automata[x]:
                if not self.automata[x][y] in conversion:
                    conversion[self.automata[x][y]] = letters[stateNum]
                    stateNum += 1
                if self.isAccepting(self.automata[x][y]):
                    grammar.addProduction(conversion[x], y)
                grammar.addProduction(conversion[x], y, conversion[self.automata[x][y]])
        # Se a linguagem tiver palavra vazia (estado inicial é de aceitação)
        # Adiciona Palavra Vazia na Gramática
        if hasEmptyWord:
            grammar.addEmptyWord()
        return grammar

    def minimize(self):
        alcancancaveis = set()
        lista = [self.initial]
        while lista:
            state = lista.pop(0)
            alcancancaveis.add(state)
            for nt in self.getChars():
                if nt in self.automata[state]:
                    if self.automata[state][nt] in alcancancaveis:
                        continue
                    lista.append(self.automata[state][nt])

        inalcancaveis = [item for item in list(self.getStates()) if item not in alcancancaveis]
        for state in inalcancaveis:
            self.removeState(state)
        vivos = set(self.accepting)
        inverseAutomata = {}
        for state in self.getStates():
            for nt in self.getChars():
                if nt in self.automata[state]:
                    toState = self.automata[state][nt]
                    if toState not in inverseAutomata:
                        inverseAutomata[toState] = set()
                    inverseAutomata[toState].add(state)
        lista = list(vivos)
        while lista:
            state = lista.pop(0)
            vivos.add(state)
            if state in inverseAutomata:
                for fromState in inverseAutomata[state]:
                    if fromState not in vivos:
                        lista.append(fromState)
        mortos = [item for item in list(self.getStates()) if item not in vivos]
        for state in mortos:
            self.removeState(state)

        p = [list(self.accepting), [item for item in list(self.getStates()) if item not in self.accepting]]
        consistent = False
        while not consistent:
            consistent = True
            for sets in p:
                for symbol in self.getChars():
                    for sett in p:
                        temp = []
                        for q in sett:
                            if symbol in self.automata[q]:
                                to = self.automata[q][symbol]
                                if to in sets:
                                    if q not in temp:
                                        temp.append(q)
                        if temp and temp != sett:
                            consistent = False
                            p.remove(sett)
                            p.append(temp)
                            temp_t = list(sett)
                            for state in temp:
                                temp_t.remove(state)
                            p.append(temp_t)
        for state in p:
            if self.initial in state:
                self.setInitial(''.join(state))
                break
        final_states = []
        for state in p:
            for final_state in self.accepting:
                if final_state in state and ''.join(state) not in final_states:
                    final_states.append(''.join(state))
        self.accepting = final_states
        new_automata = {}
        for state in p:
            state_name = ''.join(state)
            new_automata[state_name] = {}
            for symbol in self.getChars():
                destiny = ''
                if symbol in self.automata[state[0]]:
                    for state2 in p:
                        if self.automata[state[0]][symbol] in state2:
                            destiny = ''.join(state2)
                if destiny:
                    new_automata[state_name][symbol] = destiny
        self.automata = new_automata

    def rename(self):
        result = DFiniteAutomata()
        start_state = 'q0'
        result.addState(start_state)
        result.setInitial(start_state)
        id = 1
        translateTable = {}
        for state in self.getStates():
            if state == self.initial:
                translateTable[state] = start_state
            else:
                translateTable[state] = 'q' + str(id)
                result.addState(translateTable[state])
                id += 1
        for state in self.getStates():
            for char in self.getChars():
                if char in self.automata[state].keys():
                    toState = self.automata[state][char]
                    if isinstance(toState, str):
                        result.addTransiction(translateTable[state], char, translateTable[toState])
                    else:
                        for s in toState:
                            result.addTransiction(translateTable[state], char, translateTable[s])
        for accept in self.accepting:
            result.addAccepting(translateTable[accept])
        self.initial = result.initial
        self.accepting = result.accepting
        self.automata = result.automata


class Grammar:

    def __init__(self, initial=''):
        self.productions = {}
        self.initial = initial.upper()

    def isInitial(self, nt):
        return nt.upper() == self.initial

    def setInitial(self, nt):
        self.initial = nt.upper()

    # Adiciona produção
    def addProduction(self, to, prod):
        if not to.upper() in self.productions:
            self.productions[to.upper()] = []
        if prod in self.productions[to.upper()]:
            return -1
        self.productions[to.upper()].append(prod)
        return len(self.productions[to.upper()]) - 1

    def removeProduction(self, to, prod):
        if not to.upper() in self.productions:
            return
        self.productions[to.upper()].remove(prod)
        if len(self.productions[to.upper()]) == 0:
            del self.productions[to.upper()]

    def printGrammar(self):
        for x in self.productions:
            print(str(x) + ": " + str(self.productions[x]))
        print()

    def save(self, file):
        with open(file, 'wb') as pickle_file:
            pickle.dump(self, pickle_file)

    def load(self, file):
        with open(file, 'rb') as pickle_file:
            gram = pickle.load(pickle_file)
            self.productions = gram.productions
            self.initial = gram.initial


# Gramatica Regular
class RegularGrammar(Grammar):

    def __init__(self, *args, **kwargs):
        super(RegularGrammar, self).__init__(*args, **kwargs)
        self.current = self.initial.upper()

    # Adiciona palavra vazia, criando um novo estado inicial, duplicando os itens e
    def addEmptyWord(self):
        duplicate = False
        for prod in self.productions[self.initial]:
            if len(prod) <= 1:
                continue
            if self.isInitial(prod[1]):
                duplicate = True
                break
        if duplicate:
            self.productions['Z'] = self.productions[self.initial].copy()
            self.initial = 'Z'
        self.productions[self.initial].append('&')
        self.cleanCurrent()

    # Adiciona produção
    # Se o simbolo terminal for &, e o simbolo for inicial roda função addEmptyWord()
    def addProduction(self, to, terminal, nonterminal=""):
        if not to.upper() in self.productions:
            self.productions[to.upper()] = []
        if terminal == '&':
            if len(self.productions) == 1:
                self.setInitial(to)
            if self.isInitial(to):
                self.addEmptyWord()
                return len(self.productions[self.initial]) - 1
            if len(self.productions[to.upper()]) == 0:
                del self.productions[to.upper()]
            return -1
        prod = terminal.lower() + nonterminal.upper()
        return super(RegularGrammar, self).addProduction(to, prod)

    def removeProduction(self, to, terminal, nonterminal=""):
        prod = terminal.lower() + nonterminal.upper()
        super(RegularGrammar, self).removeProduction(to, prod)

    # Geração de string com nao terminal e id da produção
    def generate(self, nt, prod):
        try:
            charac = self.productions[nt.upper()][prod]
            if charac == '&':
                charac = ''
            self.current = self.current.replace(nt.upper(), charac)
        except:
            print("Production '" + str(prod) + "' not found for non-terminal: " + str(nt))
        return self.current

    def currentTerminal(self):
        return not any(x.isupper() for x in self.current)

    def cleanCurrent(self):
        self.current = self.initial

    # Converte para AFND
    def convertAFND(self):
        afnd = NDFiniteAutomata()
        afnd.setInitial(self.initial)
        afnd.addState('@')
        afnd.addAccepting('@')
        for x in self.productions:
            afnd.addState(x)
            for prod in self.productions[x]:
                to = '@'
                if len(prod) > 1:
                    to = prod[1]
                afnd.addTransiction(x, prod[0], to)
        return afnd

    def load(self, file):
        super(RegularGrammar, self).load(file)
        self.current = self.initial


# Expressao Regular
class RegularExpression:
    def __init__(self, regex=''):
        self.regex = set()
        if regex:
            self.regex.add(regex)
        self.fecho = False

    def __str__(self):
        return '+'.join(list(self.regex))

    def clear(self):
        self.regex.clear()

    def isValid(self):
        stack = []
        dict = {')': '(', '}': '{', ']': '['}
        for c in str(self):
            if c == '(':
                stack.append(c)
            elif c == ')' and (len(stack) == 0 or not stack.pop() == '('):
                return False
        return len(stack) == 0

    def kleene(self):
        if self.fecho:
            return
        element = str(self)
        if len(element) > 1:
            element = '(' + element + ')'
        elif len(element) == 0:
            return
        element += '*'
        self.fecho = True
        self.clear()
        self.regex.add(element)

    def concatenate(self, regex2):
        if len(self.regex) > 1:
            element = '(' + str(self) + ')' + str(regex2)
            self.clear()
            self.regex.add(element)
        elif len(self.regex) == 1:
            self.regex.add(self.regex.pop() + str(regex2))
        else:
            self.regex.update(regex2.regex)
        self.fecho = False

    def union(self, regex2):
        self.regex.update(regex2.regex)
        self.fecho = False

    def save(self, file):
        with open(file, 'wb') as pickle_file:
            pickle.dump(self, pickle_file)

    def load(self, file):
        with open(file, 'rb') as pickle_file:
            regex = pickle.load(pickle_file)
            self.regex = regex.regex
            self.fecho = regex.fecho


def getState(l):
    if len(l) > 1:
        l = list(l)
        l.sort()
        return ''.join(l)
    else:
        return list(l)[0]
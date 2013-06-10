#-*- coding: utf-8 -*-
import sys
#lalalallala


regras = { }
terminais = [ ]
variaveis = [ ]
arquivo = []
varsCriadas =  { }
inicial = None
index = 0
# { S > NP , VP }
# [ 'S > NP VP' ]
# { "S" : "NP VP" }

gramatica = (variaveis,terminais,regras,inicial)

def achaTerminais(linhaTerminais):
    """
    Função que processa a linha de definição de terminais no arquivo e os salva
    na lista de terminais.
    """
    global terminais
    terminais.append(' ') # Resolvemos considerar espaços como terminais.
    terminais.append('&') # Palavra vazia deve ser considerada um terminal para
                          # que a função tokenize funcione corretamente
    for ter in linhaTerminais.strip('{ ,}\n').split(', '):
        terminais.append(ter)

def achaVariaveis(linhaVariaveis):
    """
    Função que processa a linha de definição de variáveis no arquivo e as salva
    na lista de variáveis.
    """
    global variaveis
    for var in linhaVariaveis.strip('{ ,}\n').split(', '):
        variaveis.append(var)

def formataArquivo(arq):
    """
    Remove comentários e espaços inúteis à direita de todas as linhas do arquivo.
    """
    global arquivo
    for line in arq:
        arquivo.append(line.partition('#')[0].strip())

def processaRegras(linhaInicial):
    """
    Processa as linhas de Regras do arquivo.
    """
    global arquivo
    for i in range(linhaInicial, len(arquivo)):
        # Tira os delimitadores da regra e os separadores de variáveis
        linha = arquivo[i].strip('{ ,}\n').replace(',', '')
        regra = linha.partition('}')[0]
        # Separa a regra em esquerda e direita.
        esquerda, dummy,  direita = regra.partition(' > ')
        try:
            if (regras[esquerda] == None): regras[esquerda] = []
        except KeyError:
            regras[esquerda] = []
        # Se a produção já foi processada, vai para a próxima
        if direita.strip() in regras[esquerda]:
            continue
        # Senão, adiciona nas produções daquela variável.
        regras[esquerda].append(direita.strip())
        
def found(word, listOfLists):
    """
    Função usada para achar o(s) lado(s) esquerdo(s) correspondentes a um certo
    lado direito.
    """
    for l in listOfLists:
        if word in tokenize(l): return True
    return False

def generatesVariable(var):
    """
    Função que diz se uma variável gera outra variável sozinha (usada na 
    simplificação de produções que transformam variáveis)
    """
    for x in regras[var]:
        if x in variaveis: return True
    return False
    
def excluiVazioRegra(esquerda, lTokens, regras, lVazios):
    """
    Se uma regra leva a variáveis que levam à palavra vazia, cria produções 
    que "simulam" a palavra vazia seguindo o algoritmo do texto
    """
    # Se chegou em variáveis unitárias, não há mais o que substituir.
    if len(lTokens) == 1: return []
    # Acha, dentre todas as variáveis que geram palavra vazia, quais estão nesta
    # regra.
    vaziosNaRegra = [t for t in lVazios if t in lTokens]
    # Forma a palavra novamente a partir dos seus tokens.
    direita = ''.join(lTokens)
    # Cria uma lista com n entradas, onde n é o número de variáveis que levam 
    # à palavra vazia nesta regra.
    lista = [0 for x in vaziosNaRegra]
    for i in range(len(lista)):
        # Para cada entrada da lista, substitui a variável correspondente pela 
        # string vazia.
        s = direita.replace(vaziosNaRegra[i], '', 1)
        # Põe de volta na lista.
        lista[i] = s
    for x in lista:
        # Chama recursivamente para cada uma das entradas da nova lista e junta
        # todos os resultados.
        for y in excluiVazioRegra(esquerda, tokenize(x), regras, lVazios):
            if y not in lista:
                lista.append(y)
    return lista
    
def tiraVazios(regras):
    """
    Simplificação das produções vazias da gramática.
    """
    # Acha todas as variáveis que levam à palavra vazia
    levamEmVazio = [key for key, value in regras.items() if found("&", value)]
    for x in levamEmVazio:
        # Tira as produções que levam no vazio dessas variáveis.
        regras[x].remove('&')
    # Percorre todas as regras...
    for esquerda, direita in regras.items():
        for d in direita:
            # Separa cada lado direito em tokens.
            t = tokenize(d)
            for x in t:
                # Se algum dos tokens leva na palavra vazia:
                if x in levamEmVazio:
                    # Exclui o vazio dessa regra e, como excluiVazioRegra retorna a lista
                    # de produções que devem ser adicionadas às regras, adiciona-as.
                    for var in excluiVazioRegra(esquerda, t, regras, levamEmVazio):
                        if var not in regras[esquerda]:
                            regras[esquerda].append(var)

def tiraTransfVariaveis(regras):
    """
    Remoção de produções que substituem variáveis.
    """
    controle = []
    # Popula controle com todas as variáveis que são geradas sozinhas por alguma outra.
    for r,s in regras.items():
        for x in s:
            if x in variaveis:
                controle.append(x)
    # Enquanto ainda existirem variáveis sozinhas do lado direito de produções:
    while controle != []:
        # Percorre todas as regras da gramática
        for esquerda, direita in regras.items():
            for d in direita:
                # Se algum lado direito está no controle
                if d in controle:
                    # Remove esta produção tanto da gramática quanto do controle
                    regras[esquerda].remove(d)
                    controle.remove(d)
                    # Adiciona as produções da variável removida às produções da
                    # variável atual.
                    for x in regras[d]:
                        if not (x in regras[esquerda]):
                            regras[esquerda].append(x)
                            # IMPORTANTE: Se adicionou uma variável, põe ela
                            # de volta no controle. Isto garante que o algoritmo
                            # funciona corretamente.
                            if x in variaveis:
                                controle.append(x)

def simplify(regras):
    """
    Simplifica a gramática. Roda os algoritmos de exclusão de produções vazias 
    e produções que substituem variáveis.
    """
    # Produções vazias.
    tiraVazios(regras)
    # Produções que substituem variáveis.
    tiraTransfVariaveis(regras)
    


 
def tokenize(string):
    """
    Função mágica que aplica a técnica de "maximal munch" para quebrar a string 
    em variáveis e terminais (ou seja, tokens).
    """
    buff = ""
    tokens = []
    i = 0
    while i < len(string):
        if buff+string[i] in variaveis:
            while (i < len(string)) and (buff+string[i] in variaveis):
                buff = buff + string[i]
                i += 1
            tokens.append(buff)
            buff = ""
        elif buff+string[i] in terminais:
            while (i < len(string)) and (buff+string[i] in terminais):
                buff = buff + string[i]
                i += 1
            tokens.append(buff)
            buff = ""
        else:
            buff += string[i]
            i += 1
    return tokens


def isCNF(regras):
    """
    Assumindo que a gramática está simplificada, diz se ela está ou não na Forma
    Normal de Chomsky.
    """
    deliciaDeLista = []
    # deliciaDeLista é preechida com todos os lados direitos de todas as regras.
    for esquerda, direita in regras.items():
        for d in direita:
            if d not in deliciaDeLista: deliciaDeLista.append(d)
    for x in deliciaDeLista:
        t = tokenize(x)
        # Se o lado direito possuir somente um token, assume-se que é um terminal,
        # já que a gramática está simplificada.
        if len(t) == 1: continue
        # Se há mais do que 2 tokens, a gramática não está na FNC
        elif len(t) > 2 : return False
        # Se há exatamente 2 tokens, deve-se garantir que os dois são variáveis.
        else:
            # quantasVar é uma lista com todos os tokens que são variáveis
            quantasVar = [y for y in t if y in variaveis] # BLACK MAGICS
            # Se são exatamente duas, está ok
            if len(quantasVar) == 2: continue
            # Senão, já não está na FNC.
            else: return False
    return True


def createVariable(token):
    """
    Função que cria uma variável intermediária que gera um terminal, usada para
    transformar uma gramática para FNC.
    """
    var = "_" + token + "_"
    # A nova variável terá como nome o símbolo terminal precedido e sucedido por 
    # um underscore.
    if var in variaveis: return var
    else:
        variaveis.append(var)
        regras[var] = [token]
        return var

def substTerminal(term, var):
    """
    Função que substitui um terminal por sua variável correspondente em todas as
    regras cujo lado direito tem tamanho maior ou igual a dois.
    """
    global regras
    for esquerda, direita in regras.items():
        for d in direita:
            t = tokenize(d)
            if len(t) >= 2:
                if term in t:
                    t[t.index(term)] = var
                    s = ''.join(t)
                    regras[esquerda].remove(d)
                    #print s
                    regras[esquerda].append(s)
            else: continue

def chomskyfy(esquerda, lTokens, regras):
    """
    Função que dada uma regra do tipo X -> X1X2X3...XN, transforma a regra para
    que tenha lado direito de tamanho 2, formado por duas variáveis.
    A implementação varre o lado direito da regra de trás para frente, agrupando
    as variáveis duas a duas e criando variáveis intermediárias para produzi-las
    até que sobrem somente duas variáveis do lado direito.
    """
    global index

    newVarName = ""
    oldVarName = ""
    
    
    while True:
        # Se há somente duas variáveis do lado direito, cria a regra que as gera
        if len(lTokens) == 2:
            regras[esquerda].append(''.join(lTokens))
            return
        # Se há mais do que duas variáveis do lado direito:
        else:                        
            # Pega as duas últimas variáveis
            s = lTokens[-2] + lTokens[-1]
            # Cria uma nova variável auxiliar
            newVarName = "_V" + str(index) + "_"
            # Se este agrupamento de variáveis ainda não foi feito
            if (s not in varsCriadas.keys()):
                # Cria a variável auxiliar nova
                varsCriadas[s] = newVarName

            else:
                # Senão usa a que já foi criada.
                newVarName=varsCriadas[s]
            # Retira as variáveis agrupadas dos tokens
            del lTokens[-2]
            del lTokens[-1]
            # Põe a nova variável auxiliar como um token
            lTokens.append(newVarName)
            try:
                # Se esta produção ainda não foi criada.
                if s not in regras[newVarName]:
                    # Adiciona nas produções da variável auxiliar
                    regras[newVarName].append(s)
                # Se já existe, não anda com o índice para a numeração ficar 
                # bonita.
                else: index -= 1
            # Se houve KeyError é porque essa entrada não existe no dicionário ainda
            except KeyError:
                # Então cria e não anda com o índice.
                regras[newVarName] = [s]
            variaveis.append(newVarName)
            oldVarName = newVarName
        index += 1
## TODO : FNC ##

def transformToCNF(regras):
    """
    Transforma uma gramática simplificada para a Forma Normal de Chomsky.
    """
    # Enquanto não estiver na forma normal de Chomsky...
    while not isCNF(regras):
        # Pega os lados direitos e, para todo lado direito de tamanho maior ou 
        # igual a 2, substitui os terminais nele presentes por variáveis auxiliares.
        for esquerda, direita in regras.items():
            for d in direita:
                t = tokenize(d)
                if len(t) >= 2:
                    for token in t:
                        if token in terminais:
                            substTerminal(token, createVariable(token))
        copy = regras.items()
        # Depois transforma todos os lados direitos para que tenham tamanho no máximo
        # igual a 2.
        for esquerda, direita in copy:
            for d in direita:
                t = tokenize(d)
                if len(t) >= 3:
                    regras[esquerda].remove(d)
                    chomskyfy(esquerda, t, regras)
formataArquivo(sys.stdin)

rang = range(len(arquivo))
for i in rang:

    if arquivo[i] == "Terminais":
        achaTerminais(arquivo[i+1])


    elif arquivo[i] == "Variaveis":
        achaVariaveis(arquivo[i+1])

    elif arquivo[i] == "Inicial":
        inicial = arquivo[i+1].strip('{ ,}\n').split(', ')[0] #OMG

    elif arquivo[i] == "Regras":
        processaRegras(i+1)
        break
    
#### AWWWWWWW  YEAAAAAAAA
simplify(regras)
transformToCNF(regras)

for x in regras.keys():
    print x, ' :', regras[x] 


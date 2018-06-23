import numpy as np
class Resample(object):
    def __init__(self, state, norm):
        self.state = np.asarray(state)
        self.state = self.state / norm if norm else self.state
        self.cumsum = self.state.cumsum()
        self.cumsum[-1] = 1 # garantir que a soma termina em 1
    def pick(self, type="multinomial"):
        if(type=="multinomial"):
            self.state = sorted(self.state)
            indices = np.searchsorted(self.cumsum, np.random.random(len(self.state)))
        elif(type=="systematic"):
            N = len(self.state)
            # DIVIDIR EM N PARTES SELECIONANDO O MESMO RANDOM PARA TODOS
            posicoes = (np.random.random(N) + range(N)) / N
            indices = np.zeros(N, int)
            i, j = 0, 0
            while(i<N):
                if(posicoes[i] < self.cumsum[j]):
                    indices[i] = j
                    i+=1
                else:
                    j+=1
        elif(type=="stratified"):
            N = len(self.state)
            # DIVIDIR EM N PARTES SELECIONANDO UM RANDOM PARA CADA PARTE
            posicoes = (np.random.random() + np.arange(N)) / N
            indices = np.zeros(N, int)
            i, j = 0, 0
            while(i<N):
                if(posicoes[i] < self.cumsum[j]):
                    indices[i] = j
                    i+=1
                else:
                    j+=1
        else: # residual
            pass
        return indices


def main():
    lista = [1,2,3,4,5]
    r = Resample(lista, sum(lista))
    print(r.pick("systematic"))
    print(r.pick("stratified"))
    print(r.pick())

if __name__ == '__main__':
    main()
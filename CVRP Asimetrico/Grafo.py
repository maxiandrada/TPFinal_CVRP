from Vertice import Vertice
from Arista import Arista
import sys
import re
import math 
import copy
import numpy as np
from time import time 
class Grafo:
    def __init__(self, M, D,G=None,vacio=False):
        if G is None:
            self._costoAsociado = 0
            self._V = []
            self._A = []
            self._IdAristasUnicas = []
            self._grado = len(M)
            self._matrizDistancias = M
            self._demanda = D
            self._demandaAcumulada = []
            if(M!=[] and D!=[]):
                self.cargarDesdeMatriz(M, D)
        else:
            if vacio:
                self._V = []
                self._A = []
            else:
                self._V = G.getV()
                self._A = G.getA()
            self._AristasUnicas = []
            self._costoAsociado = 0
            self._grado = len(M)
            self._matrizDistancias = M
            self._demanda = D
            self._demandaAcumulada = []
            self._idListAristas = []

    def getGrado(self):
        return self._grado
    def addIdListAristas(self, id):
        self._idListAristas.append(id)
    def borraIdListAristas(self):
        self._idListAristas = []
    def getIdListAristas(self):
        return self._idListAristas
    def extendIdListAristas(self, IdList):
        self._idListAristas.extend(IdList)
    def getIdAristasUnicas(self):
        return self._IdAristasUnicas

    def getDemandaAcumulada(self):
        return self._demandaAcumulada
    
    def cargarDesdeAristas(self, A):
        #t = time()
        self._A = A
        V = []
        cap = 0
        costo = 0
        demAcum = 0
        self._demandaAcumulada = []
        self.borraIdListAristas()
        for a in A:
            v = a.getOrigen()
            V.append(v)
            costo += a.getPeso()
            cap += self._demanda[v.getValue()-1]
            demAcum += v.getDemanda()
            self._demandaAcumulada.append(demAcum)
            self.addIdListAristas(a.getId())
        self._V = V
        self._costoAsociado = costo
        # print(f"CargaDesdeAristas: {time()-t}")
        return cap
    
    def setDemanda(self, D):
        self._demanda = D
    def setA(self, A):
        self._A = A
        V = []
        for v in A:
            V.append(v.getOrigen())
        self._V = V
    def setV(self, V):
        self._V = V
    def getA(self):
        return self._A
    def getAristasUnicas(self):
        return self._AristasUnicas
    def getV(self):
        return self._V
    def getCostoAsociado(self):
        return self._costoAsociado
    def setCostoAsociado(self, costoAsociado):
        self._costoAsociado = costoAsociado
    def __lt__(self, otro):
        return (self._costoAsociado < otro.__costoAsociado and self.__class__ == otro.__class__)
    def __le__(self, otro):
        return (self._costoAsociado <= otro.__costoAsociado and self.__class__ == otro.__class__)
    def __gt__(self, otro):
        return (self._costoAsociado > otro.__costoAsociado and self.__class__ == otro.__class__)
    def __ge__(self, otro):
        return (self._costoAsociado >= otro.__costoAsociado and self.__class__ == otro.__class__)
    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self._costoAsociado == other.__costoAsociado)
    def __ne__(self, other):
        return (self.__class__ == other.__class__ and self._costoAsociado != other.__costoAsociado)

    def __str__(self):
        salida = ""
        V = self.getV()
        #Muestra la primera fila con los vertices
        if(len(self._matrizDistancias) == len(self.getV())):
            for i in range(0,len(V)):
                if(V[i]>=10):
                    salida += "        " +  str(V[i])
                else:
                    salida += "        " +  str(V[i]) + " "

            salida = salida + "\n"
            for i in range(0,len(V)):
                if(V[i] >= 10):
                    salida += str(V[i]) + "    "
                else:
                    salida += str(V[i]) + "     "
                for j in range(0,len(V)):
                    if(self._matrizDistancias[i][j]==999999999999):
                        salida += str(0) + "         "
                    else:
                        salida += str(self._matrizDistancias[i][j]) + "    "
                salida = salida + "\n"
        else:
            for i in range(0,len(V)):
                salida += str(V[i]) + "         "

            salida = salida + "\n"
            for i in V:
                salida += str(i) + "    "
                for j in V:
                    indice = self.getCostoArista(Arista(i,j,0))
                    salida += str(self.getA()[indice].getPeso()) + "    "
                salida = salida + "\n"
        return salida
    
    def __repr__(self):
        if(self != None):
            return str(self.getV)
    
    #Compara entre 2. Se fija si hay aristas de A contenidas en si misma. Si hay aristas, se detiene
    def contieneA(self,A):
        sigue = True
        i = 0
        n = len(self.getA())
        while((sigue == True) and i < n):
            if(self.getA()[i].tieneOrigen(A.getOrigen()) and self.getA()[i].tieneDestino(A.getDestino())):
                sigue = False
                i=n
            i+=1
        return not(sigue)

    def getCostoArista(self, A):
        sigue = True
        i = 0
        n = len(self.getA())
        while((sigue == True) and i < n):
            if(self.getA()[i].tieneOrigen(A.getOrigen()) and self.getA()[i].tieneDestino(A.getDestino())):
                sigue = False
            i+=1
        return i-1

    def getAristaMinima(self,listaAristas):
        minimo = listaAristas[0]
        for i in listaAristas:
            if(i.getPeso() < minimo.getPeso()):
                minimo = i

        return minimo

    #Carga desde una secuencia de enteros
    def cargaVertices(self, secuencia, sinVerticeInicial):
        V = []
        
        if(sinVerticeInicial):
            for x in secuencia:
                V.append(Vertice(int(x)+1, self._demanda[x]))
        else:
            for x in secuencia:
                V.append(Vertice(int(x), self._demanda[x-1]))
                    
        return V

    def cargaGrafoDesdeSec(self, secuencia):
        if(len(self._V)!=0):
            self._V = []
        else:
            V = self._V
        if(len(self._A)!=0):
            self._A = []
        if(len(self._demandaAcumulada)!=0):
            self._demandaAcumulada = []
        costo = 0
        demAcum = 0
        cap = 0
        self.borraIdListAristas()
        for i in range(0, len(secuencia)):
            x = secuencia[i]
            V.append(Vertice(int(x), self._demanda[x-1]))

            if i>0:
                Vfila = V[i-1]
                Vcol = V[i]
                fila = Vfila.getValue()-1
                col = Vcol.getValue()-1
                dist = self.getMatriz()[fila][col] #Referencias en la matriz
                new_edge = Arista(Vfila, Vcol, dist)
                new_edge.setId(fila, col, len(self._matrizDistancias))
                self._A.append(new_edge)
                self.addIdListAristas(new_edge.getId())
                demAcum += new_edge.getOrigen().getDemanda()
                self._demandaAcumulada.append(demAcum)
                costo+=dist
                cap += Vfila.getDemanda()
        self.setV(V)
        Vfila = V[-1]
        Vcol = V[0]
        fila = Vfila.getValue()-1
        col = 0
        dist = self.getMatriz()[fila][col]
        new_edge = Arista(Vfila, Vcol, dist)
        new_edge.setId(fila, col, len(self._matrizDistancias))
        self._A.append(new_edge)
        self.addIdListAristas(new_edge.getId())
        demAcum += new_edge.getOrigen().getDemanda()
        self._demandaAcumulada.append(demAcum)
        costo+=dist
        cap += Vfila.getDemanda()
        self._costoAsociado = costo

        return cap

    def cargaAristas(self):
        A=[]
        cantV = len(self._V)
        for row in range(1,cantV):
            for col in range(1, cantV):
                arista_aux = Arista(row,col,self._matrizDistancias[row][col])
                A.append(arista_aux)
        
        #print("Aristas: \n",A)
        return A

    def aristaConOrigen(self, V):
        for i in range(0, len(self._A)):
            if (self._A[i].tieneOrigen(V)):
                return i

    def aristasConOrigen(self, V):
        salida = []
        for arista in self.getA():
            if((arista.tieneOrigen(V)) == True):
                salida.append(arista)

        return salida

    def aristaConDestino(self, V):
        for i in range(0, len(self._A)):
            if (self._A[i].tieneDestino(V)):
                return i

    def aristasConDestino(self, V):
        salida = []
        for arista in self.getA():
            if((arista.tieneDestino(V)) == True):
                salida.append(arista)
        return salida
    
    def addCliente(self, secuencia):
        self._V = self.cargaVertices(secuencia, True)
        self._A = self.cargaAristas()

    #Cargar las aristas
    def cargarDesdeMatriz(self, Matriz, Demanda):
        for fila in range(0, len(Matriz)):
            self._V.append(Vertice(fila+1, Demanda[fila]))    #V=[1,3,4] A=[(1,3)(3,4)] => sol 1->3->4->5->2
            for columna in range(0, len(Matriz[fila])):
                aux = Arista(Vertice(fila+1, Demanda[fila]),Vertice(columna+1, Demanda[columna]),(Matriz[fila][columna]))
                aux.setId(fila, columna, len(Matriz))
                self._A.append(aux)
                # if columna!= fila and columna > fila:
                #     self._IdAristasUnicas.append(aux.getId())

    def getVerticeInicio(self):
        return self._A[0].getOrigen()

    def getMatriz(self):
        return self._matrizDistancias
    
    def setMatriz(self, M):
        self._matrizDistancias = M

    #Para que cargue desde una secuencia de vertices por ej. s1= [1,3,4,5,8,9,6,7] -> s2=[1,3,9,5,8,4,6,7]
    def cargarDesdeSecuenciaDeVertices(self,seq:list):
        self._V = seq
        if(len(self._A)!=0):
            self._A = []
        if(len(self._demandaAcumulada)!=0):
            self._demandaAcumulada = []
        costo = 0
        demAcum = 0
        cap = 0
        new_edge = None
        self.borraIdListAristas()
        for i in range(0,len(seq)):
            if i < len(seq)-1:
                fila = seq[i].getValue()-1
                col = seq[i+1].getValue()-1
                dist = self.getMatriz()[fila][col]
                new_edge = Arista(seq[i], seq[i+1], dist)
                new_edge.setId(fila, col, len(self._matrizDistancias))
                self.getA().append(new_edge)
                self.addIdListAristas(new_edge.getId())
            else:
                fila = seq[i].getValue()-1
                col = 0
                dist = self.getMatriz()[fila][col]
                new_edge = Arista(seq[i], seq[0], dist)
                new_edge.setId(fila, col, len(self._matrizDistancias))
                self.getA().append(new_edge)
                self.addIdListAristas(new_edge.getId())
            demAcum += new_edge.getOrigen().getDemanda()
            self._demandaAcumulada.append(demAcum)
            costo+=dist
            cap += seq[i].getDemanda()
        self._costoAsociado = costo

        return cap

    def getCostoSecVert(self, secV):
        costo = 0
        vAnt = secV[0]
        # print("Sec V: "+str(secV))
        for vSig in secV[1:]:
            # print("Vant: "+str(vAnt))
            # print("Vsig: "+str(vSig))
            costoArista = self._matrizDistancias[vAnt.getValue()-1][vSig.getValue()-1]
            costo += costoArista
            vAnt = vSig
        # print("Costo: ", costo)

        return costo

    def getCostoAristaInv(self, A):
        # print("Ant: "+str(A))
        # A_cp = copy.deepcopy(A)
        # A_cp = self.invertirArista(A_cp)
        # print("Inv: "+str(A_cp))
        costo = self._matrizDistancias[A.getDestino().getValue()-1][A.getOrigen().getValue()-1]
         
        return costo

    def invertirArista(self, A):
        A.invertir()
        peso = self._matrizDistancias[A.getOrigen().getValue()-1][A.getDestino().getValue()-1]
        A.setPeso(peso)

        return A

    def incrementaFrecuencia(self):
        for x in range(0,len(self.getA())):
            self.getA()[x].incFrecuencia()

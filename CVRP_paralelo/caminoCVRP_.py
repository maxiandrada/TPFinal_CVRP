import copy

class camino():
    def __init__(self, s, g, demandas, capacidad):
        self.__demandas = demandas
        self.__capacidad = capacidad
        if not (self.chequeaFactibilidad(s) and self.chequeaFactibilidad(g)):
            raise Exception("SolucionesInfactibles")
        else:
            self.__s = s
            self.__g = g
            self.__indS = [0,1] #(ruta, vertice)
            self.__indG = [0,1]
            self.__cond1 = self.igualesTam()
            self.__cond2 = self.igualesRec()

    def chequeaFactibilidad(self, p):
        i = 0
        while i < len(p) and self.__chequeaFactibilidadRuta(p[i]):
            i+=1
        return False if i < len(p) else True

    def getInd(self): #retorna tupla
        return self.__indS

    def igualesTam(self):
        i = 0
        while i < len(self.__s) and len(self.__s[i]) == len(self.__g[i]):
            i += 1
        if i<len(self.__s):
            return False
        else:
            return True

    def igualesRec(self):
        indS = [0,1]
        indG = [0,1]
        band = True
        while band and indS!= None and indG!=None:
            if self.__s[indS[0]][indS[1]] != self.__g[indG[0]][indG[1]]:
                band = False
            indS = self.incIndS(indS)
            indG = self.incIndG(indG)
        if band:
            return True
        else:
            return False

    def pathRelinking (self):
        # print ("----inicio pr----")
        aux1 = -1
        aux2 = -1
        if not self.iguales():
            if not self.__cond2:
                aux1 = self.__s[self.__indS[0]][self.__indS[1]]
                aux2 = self.__g[self.__indG[0]][self.__indG[1]]
                self.__s[self.__indS[0]][self.__indS[1]] = self.__g[self.__indG[0]][self.__indG[1]]

                indS=self.incIndS(self.__indS) 
                indG=self.incIndG(self.__indG)
                if indS!=None and indG!=None:
                    # print ("Los indices no son None")
                    self.__indS=self.incIndS(self.__indS) 
                    self.__indG=self.incIndG(self.__indG)            
                    # print ("indices:"+str(self.__indS)+str(self.__indG))
                    band = True
                    while indS!=None and band:
                        if self.__s[indS[0]][indS[1]] == aux2:
                            self.__s[indS[0]][indS[1]] = aux1
                            band = False
                        else:
                            indS = self.incIndS(indS)
                    self.__cond2 = self.igualesRec()
                    if indS!= None and self.__chequeaFactibilidadRuta(self.__s[self.__indS[0]]) and self.__chequeaFactibilidadRuta(self.__s[indS[0]]):
                        print ("entro 1")
                        return self.__s
                    else:
                        print ("entro 2")
                        return self.pathRelinking()
                else:
                    print ("entro 3")
                    self.__cond2 = self.igualesRec()
                    return self.__s
            elif not self.__cond1:
                i = 0
                b = True
                while b and i < len(self.__s):
                    if len(self.__s[i]) < len(self.__g[i]):
                        aux3=self.__s[i+1].pop(1)
                        self.__s[i].append(aux3)
                        b = False
                        b2 = self.__chequeaFactibilidadRuta(self.__s[i]) and self.__chequeaFactibilidadRuta(self.__s[i+1])
                    elif len(self.__s[i]) > len(self.__g[i]):
                        aux3 = self.__s[i].pop(-1)
                        self.__s[i+1].insert(1, aux3)
                        b = False
                        b2 = self.__chequeaFactibilidadRuta(self.__s[i]) and self.__chequeaFactibilidadRuta(self.__s[i+1])
                    else:
                        i+=1
                self.__cond1 = self.igualesTam()
                if b2:
                    print ("entro 4")
                    return self.__s
                else:
                    print ("entro 5")
                    return self.pathRelinking()
            else:
                print ("Ya llegamos a la solución guía")
                return []
        else:
            print ("Ya llegamos a la solución guía")
            return []

    def __chequeaFactibilidadRuta(self, ruta):
        acu = 0.0
        # print (str(ruta))
        cad = "acu = "
        for i in range(len(ruta)):
            acu += self.__demandas[ruta[i]-1]
            cad += str(self.__demandas[ruta[i]-1])
        # print (cad)
        return False if acu > self.__capacidad else True

    def incIndS(self, indS):
        ind = copy.deepcopy(indS)
        if ind != None:
            if ind[1]+1 < len(self.__s[ind[0]]):
                ind[1]+=1
                return ind
            else:
                if ind[0]+1 < len(self.__s):
                    ind[0]+=1
                    ind[1]=1
                    return ind
                else:
                    return None #es el último de la secuencia
        else:
            return None

    def incIndG(self, indG):
        ind = copy.deepcopy(indG)
        if ind != None:
            if ind[1]+1 < len(self.__g[ind[0]]):
                ind[1]+=1
                return ind
            else:
                if ind[0]+1 < len(self.__g):
                    ind[0]+=1
                    ind[1]=1
                    return ind
                else:
                    return None #es el último de la secuencia
        else:
            return None

    def iguales(self):
        if self.__cond1 and self.__cond2:
            return True
        else:
            return False
    

#### SECCION DE PRUEBAS ####
# s = [[1,4,5,2],[1,9,8,3],[1,6,7,10]]

# g = [[1,2,3],[1,4,5,6,7],[1,8,9,10]]
# try:
#     caminito = camino(s, g, [0.0,2.0,4.0,2.0,5.0,6.0,7.0,6.0,3.0,4.0,7.0], 20)
#     c = caminito.pathRelinking()
#     ind =[0,1]
#     while c!=[]:
#         print (str(c)+str(caminito.iguales()))
#         c = caminito.pathRelinking()

#     print (str(caminito.iguales()))
# except Exception as e:
#     print (e)


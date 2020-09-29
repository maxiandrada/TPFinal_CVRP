from Vertice import Vertice
from Arista import Arista
from Grafo import Grafo
from Solucion import Solucion
from Tabu import Tabu
import random 
import sys
import re
import math 
import copy
import numpy as np
from clsTxt import clsTxt
from time import time

class CVRP:
    #def __init__(self, M, D, nroV, capac, archivo, carpeta, solI, tADD, tDROP, tiempo, porcentaje, optimo):
    def __init__(self, M, D, nroV, capac, solI, tADD, tDROP, tiempo):
        self._G = Grafo(M, D)                #Grafo original
        self.__S = Solucion(M, D, sum(D))    #Solucion general del CVRP
        self.__Distancias = M                #Mareiz de distancias
        self.__Demandas = D                  #Demandas de los clientes
        self.__capacidadMax = capac          #Capacidad max por vehiculo
        self.__rutas = []                    #Soluciones por vehiculo (lista de soluciones)
        self.__nroVehiculos = nroV           #Nro de vehiculos disponibles
        self.__tipoSolucionIni = solI        #Tipo de solucion inicial (Clark & Wright, Vecino cercano, Secuencial o al Azar)
        self.__beta = 1                      #Parametro de dispersion
        self.__umbralMin = 0                 #Umbral de granularidad minimo
        self.__optimosLocales = []           #Lista de optimos locales 
        self.__tenureADD =  tADD             
        self.__tenureMaxADD = int(tADD*1.7)
        self.__tenureDROP =  tDROP
        self.__tenureMaxDROP = int(tDROP*1.7)
        self.__tiempoMaxEjec = float(tiempo)
        self.__S.setCapacidadMax(self.__capacidadMax)
        tiempoIni = time()
        self.__rutas = self.__S.rutasIniciales(self.__tipoSolucionIni, self.__nroVehiculos, self.__Demandas, self.__capacidadMax)
        # print("tiempo solucion inicial: ", time()-tiempoIni)
        self.__tiempoMaxEjec = self.__tiempoMaxEjec - ((time()-tiempoIni)/60)
        tiempoIni = time()
        print("\nSolucion Inicial:")
        self.__S = self.cargaSolucion(self.__rutas)
        print(str(self.__S.getV()))
        # print("tiempo solucion inicial: ", time()-tiempoIni)
        print("Nro vehiculos: ", self.__nroVehiculos)

    #Carga la solucion general a partir de las rutas
    def cargaSolucion(self, rutas):
        # t = time()
        S = Solucion(self.__Distancias, self.__Demandas, sum(self.__Demandas),self._G, True)
        cap = 0
        costoTotal = 0
        sol_ini = ""
        
        #print("+-+-++-+-++-+-++-+-+Rutas+-+-++-+-++-+-++-+-+")
        for i in range(0, len(rutas)):
            s = rutas[i]
            try:
                costoTotal += float(s.getCostoAsociado())
            except AttributeError:
                print("s: "+str(s))
                print("rutas: "+str(rutas))
                print("i: ", i)
                #a = 1/0
            cap += s.getCapacidad()
            S.getA().extend(s.getA())
            S.getV().extend(s.getV())
            idList = s.getIdListAristas()
            S.extendIdListAristas(idList)
            # sol_ini+="\nRuta #"+str(i+1)+": "+str(s.getV())
            #sol_ini+="\nAristas: "+str(s.getA())
            # sol_ini+="\nCosto asociado: "+str(s.getCostoAsociado())+"      Capacidad: "+str(s.getCapacidad())+"\n"
        # sol_ini+="\n--> Costo total: "+str(costoTotal)+"          Capacidad total: "+str(cap)
        # print(sol_ini)
        # print("+-+-++-+-++-+-++-+-++-+-++-+-++-+-++-+-+")
        costoTotal = round(costoTotal, 3)
        S.setCostoAsociado(costoTotal)
        S.setCapacidad(cap)
        S.setCapacidadMax(self.__capacidadMax)

        # print(f"cargaSolucion: {time()-t}")
        return S

    #Umbral de granularidad: phi = Beta*(c/(n+k))
    #Beta = 1  parametro de dispersion. Sirve para modificar el grafo disperso para incluir la diversificación y la intensificación
    #          durante la búsqueda.
    #c = valor de una sol. inicial
    #k = nro de vehiculos
    #n = nro de clientes
    def calculaUmbral(self, costo):
        c = costo
        k = self.__nroVehiculos
        n = len(self.__Distancias)-1
        phi = c/(n+k)
        phi = phi*self.__beta
        return round(phi,3)

    #+-+-+-+-+-+-+- Empezamos con Tabu Search +-+-+-+-+-+-+-+-+#
    #lista_tabu: tiene objetos de la clase Tabu (una arista con su tenure)
    #Lista_permitidos: o grafo disperso tiene elementos del tipo Arista que no estan en la lista tabu y su distancia es menor al umbral
    #nuevas_rutas: nuevas rutas obtenidas a partir de los intercambios
    #nueva_solucion: nueva solucion obtenida a partir de los intercambios
    #rutas_refer: rutas de referencia que sirve principalmente para evitar estancamiento, admitiendo una solucion peor y hacer los intercambios
    #             a partir de esas
    #solucion_refer: idem al anterior
    #tiempoIni: tiempo inicial de ejecucion - tiempoMax: tiempo maximo de ejecucion - tiempoEjecuc: tiempo de ejecución actual
    #iteracEstancamiento: iteraciones de estancamiento para admitir una solución peor, modificar Beta y escapar del estancamiento
    #iterac: cantidad de iteraciones actualmente
    def tabuSearch(self):
        lista_tabu = []
        ind_permitidos = np.array([], dtype = int)
        rutas_refer = copy.deepcopy(self.__rutas)
        nuevas_rutas = rutas_refer
        solucion_refer = copy.deepcopy(self.__S)
        nueva_solucion = solucion_refer
        nuevo_costo = self.__S.getCostoAsociado()
        S = []
        G = []
        
        #Atributos de tiempo e iteraciones
        tiempoIni = time()
        tiempoMax = float(self.__tiempoMaxEjec*60)
        tiempoEstancamiento = tiempoIni
        tiempoEjecuc = 0
        iteracEstancamiento = 1
        #iteracEstancamiento_Opt = 1
        iteracEstancMax = 300
        iterac = 1
        indOptimosLocales = -2
        umbral = self.calculaUmbral(self.__S.getCostoAsociado())
        cond_Optimiz = True
        cond_Estancamiento = False
        condPathRelinking = False
        condEstancPathRelinking = True
        condPeorSolucionNueva = False
        iteracEstancamientoPR = 0
        iteracPR = 0
        tiempo = time()

        Aristas_Opt = np.array([], dtype = object)
        for EP in self._G.getA():
            if EP.getPeso() <= umbral:
                Aristas_Opt = np.append(Aristas_Opt, EP)
                ind_permitidos = np.append(ind_permitidos, EP.getId())
        ind_AristasOpt = copy.deepcopy(ind_permitidos)
        
        self.__optimosLocales.append(nuevas_rutas)
        
        while(tiempoEjecuc < tiempoMax):
            if cond_Optimiz:
                ind_permitidos = self.getPermitidos(Aristas_Opt, umbral, solucion_refer)    #Lista de elementos que no son tabu
                self.__umbralMin = 0

            cond_Optimiz = False
            ADD = []
            DROP = []
            
            ind_random = np.arange(0,len(ind_permitidos))
            random.shuffle(ind_random)
            
            indRutas = []
            indAristas = []
            
            nuevo_costo, k_Opt, indRutas, indAristas, aristasADD, aristasDROP, ind_permitidos = nueva_solucion.evaluarOpt(self._G.getA(), ind_permitidos, ind_random, rutas_refer, cond_Estancamiento)
            nuevo_costo = round(nuevo_costo, 3)

            tenureADD = self.__tenureADD
            tenureDROP = self.__tenureDROP
            costoSolucion = self.__S.getCostoAsociado()

            #Si encontramos una mejor solucion que la tomada como referencia
            if(nuevo_costo < solucion_refer.getCostoAsociado() and aristasADD != []):
                cad = "\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Iteracion %d  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n" %(iterac)
                
                nuevas_rutas = nueva_solucion.swap(k_Opt, aristasADD[0], rutas_refer, indRutas, indAristas)
                nueva_solucion = self.cargaSolucion(nuevas_rutas)

                if(nuevo_costo != nueva_solucion.getCostoAsociado()):
                    print("\n\nERROR!!!!!!")
                    print("ADD: "+str(aristasADD)+"     DROP: "+str(aristasDROP)+"\n\n")
                    print("nueva solucion:"+str(nueva_solucion.getV()))
                    print("solucion refer:"+str(solucion_refer.getV()))
                    
                    print("\nRutas ahora")
                    for i in range(0, len(rutas_refer)):
                        x = rutas_refer[i]
                        print("ruta #%d: %s" %(i, str(x.getV())))
                    print("nuevo costo: ", nuevo_costo,"          getCostoAsociado: ", nueva_solucion.getCostoAsociado())
                    a = 1/0
                                
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                
                #Si la nueva solucion es mejor que la obtenida hasta el momento
                if(nuevo_costo < costoSolucion):
                    tiempoTotal = time()-tiempoEstancamiento
                    print(cad)
                    cad = "\nLa solución anterior duró " + str(int(tiempoTotal/60))+"min "+ str(int(tiempoTotal%60))
                    cad += "seg    -------> Nuevo optimo local. Costo: "+str(nuevo_costo)
                    
                    self.__S = nueva_solucion
                    self.__rutas = nuevas_rutas
                    self.__beta = 1
                    tiempoEstancamiento = time()

                    if(len(self.__optimosLocales) >= 20):
                        self.__optimosLocales.pop(0)
                    self.__optimosLocales.append(self.__rutas)

                    indOptimosLocales = -2
                    cond_Estancamiento = False
                    print(cad)
                    condPathRelinking = False
                    condEstancPathRelinking = True
                    iteracEstancamientoPR = 0
                    iteracPR = 0
                # else:
                #     cad += "\nSolucion peor. Costo: "+str(nueva_solucion.getCostoAsociado())
                # cad += "\nLista tabu: "+str(lista_tabu)
                
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                tenureADD = self.__tenureMaxADD
                tenureDROP = self.__tenureMaxDROP
                cond_Optimiz = True
                iteracEstancamiento = 1
                iteracEstancMax = 300

            #Si se estancó, tomamos a beta igual a 2
            elif(iteracEstancamiento > iteracEstancMax and self.__beta < 2  and ind_permitidos != []):
                tiempoTotal = time()-tiempoEstancamiento
                print("Se estancó durante %d min %d seg. Incrementanos Beta para diversificar" %(int(tiempoTotal/60), int(tiempoTotal%60)))
                self.__beta = 2
                self.__umbralMin = umbral
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                cond_Optimiz = True
                #cond_Estancamiento = True
                iteracEstancamiento = 1
                iteracEstancMax = 200
            
            #Si se estancó con la sol anterior y el Beta incrementado, aplicamos Path Relinking
            elif(iteracEstancamiento > iteracEstancMax and len(self.__optimosLocales) >= indOptimosLocales*(-1) and ind_permitidos != [] and not condPeorSolucionNueva):
                cad = "\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Iteracion %d  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n" %(iterac)
                
                if condPathRelinking or not condEstancPathRelinking:
                    if iteracPR < 2:
                        nuevas_rutas = self.pathRelinking(S, G)
                    else:
                        nuevas_rutas = []
                    
                    if(nuevas_rutas == []):
                        condEstancPathRelinking = True
                        condPathRelinking = False
                    else:
                        condEstancPathRelinking = False
                        condPathRelinking = True
                        nueva_solucion = self.cargaSolucion(nuevas_rutas)
                        costo = nueva_solucion.getCostoAsociado()
                        tiempoTotal = time()-tiempoEstancamiento
                        cad = "Se estancó durante %d min %d seg. Aplicamos path relinking para admitir otro optimo local" %(int(tiempoTotal/60), int(tiempoTotal%60))
                        print(cad + "-->    Costo: "+str(costo))

                        iteracPR += 1
                        self.__beta = 1
                        self.__umbralMin = 0

                if (not condPathRelinking and condEstancPathRelinking):
                    G = copy.deepcopy(self.__optimosLocales[indOptimosLocales+1])
                    
                    nuevas_rutas = self.__optimosLocales[indOptimosLocales]
                    nueva_solucion = self.cargaSolucion(nuevas_rutas)
                    costo = nueva_solucion.getCostoAsociado()

                    self.__umbralMin = 0
                    umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())

                    if iteracEstancamientoPR < 2:
                        S = copy.deepcopy(self.__optimosLocales[indOptimosLocales])
                        tiempoTotal = time()-tiempoEstancamiento
                        cad = "Se estancó durante %d min %d seg. Admitimos el penultimo optimo local " %(int(tiempoTotal/60), int(tiempoTotal%60))
                        print("\n"+ cad + "-->    Costo: "+str(costo))
                        iteracEstancamientoPR += 1
                    else:
                        condPeorSolucionNueva = True
                        auxCond = True

                    indOptimosLocales -= 1
                    self.__beta = 3
                    condPathRelinking = True
                    condEstancPathRelinking = False
                    cond_Estancamiento = False
                    iteracPR = 0

                if(len(self.__optimosLocales)-1 <= indOptimosLocales*(-1)):
                    print("\nReiniciamos la lista de Optimos Locales\n")
                    condPathRelinking = False
                    condEstancPathRelinking = True
                    iteracEstancamientoPR = 0
                    condPeorSolucionNueva = True
                    indOptimosLocales = -2
                    
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                umbral = self.calculaUmbral(costo)
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                cond_Optimiz = True
                iteracEstancamiento = 1
                iteracEstancMax = 500
                # cond_Estancamiento = True

            #Si se estancó con path Relinking tomamos el proximo peor
            elif iteracEstancamiento > iteracEstancMax and aristasADD != [] and ind_permitidos != []:
                try:
                    nuevas_rutas = nueva_solucion.swap(k_Opt, aristasADD[0], rutas_refer, indRutas, indAristas)
                except IndexError:
                    print("%d-Opt Opcion: %d"%(k_Opt[0], k_Opt[1]))
                    print("ADD: "+str(aristasADD))
                    print("DROP: "+str(aristasDROP))
                    print("Permitidos: "+str(ind_permitidos))
                    print("\nRutas: "+str(nueva_solucion.getV()))
                    print("Fallo")

                nueva_solucion = self.cargaSolucion(nuevas_rutas)
                rutas_refer = nuevas_rutas
                solucion_refer = nueva_solucion
                S = nuevas_rutas

                costo = nueva_solucion.getCostoAsociado()
                tiempoTotal = time()-tiempoEstancamiento
                print("\nSe estancó durante %d min %d seg. Tomamos la primera solucion peor -->     Costo: %f" %(int(tiempoTotal/60), int(tiempoTotal%60), costo))
            
                self.__beta = 1
                self.__umbralMin = 0
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                tenureADD = self.__tenureMaxADD
                tenureDROP = self.__tenureMaxDROP
                cond_Optimiz = True
                iteracEstancamiento = 1
                iteracEstancMax = 300
                #indOptimosLocales = -2
                condPeorSolucionNueva = False
                iteracEstancamientoPR = 0

            #Si se terminaron los permitidos
            elif(ind_permitidos == []):
                cad = "\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Iteracion %d  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n" %(iterac)
                cad += "Se terminaron los permitidos"
                nuevas_rutas = nueva_solucion.swap(k_Opt, aristasADD[0], rutas_refer, indRutas, indAristas)
                nueva_solucion = self.cargaSolucion(nuevas_rutas)
                
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                cond_Optimiz = True
                self.__beta = 3
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                # Aristas = Aristas_Opt
                umbral = self.calculaUmbral(costo)
            
            #Si no pasa nada, tomamos la ruta y sol de referencia
            else:
                nuevas_rutas = rutas_refer
                nueva_solucion = solucion_refer

            #Añado y elimino de la lista tabu
            if (aristasADD != []):
                ADD.append(Tabu(aristasADD[0], tenureADD))
                for i in range(0, len(aristasDROP)):
                    DROP.append(Tabu(aristasDROP[i], tenureDROP))
                self.decrementaTenure(lista_tabu, ind_permitidos)
                lista_tabu.extend(DROP)
                lista_tabu.extend(ADD)
            else:
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                cond_Optimiz = True
            
            tiempoEjecuc = time()-tiempoIni
            iterac += 1
            iteracEstancamiento += 1
        #Fin del while. Imprimo los valores obtenidos
        
        self.escribirDatosFinales(tiempoIni, iterac, tiempoEstancamiento)
        
        return self.__S.solucionToJSON(), self.__S.getCostoAsociado()
        
    def getPermitidos(self, Aristas, umbral, solucion):
        AristasNuevas = []
        ind_permitidos = np.array([], dtype = int)
        claves = [hash(a) for a in solucion.getA()]
        dictA = dict(zip(claves, solucion.getA()))
        idListAristas = solucion.getIdListAristas()
        #No tengo en consideracion a las aristas que exceden el umbral y las que pertencen a S

        #print("Aristas en Solución \n",str(solucion.getA()))
        for EP in Aristas:
            pertS = False
            h = hash(EP)
            hInverso = hash(solucion.invertirArista(EP))
            try:
                arista = dictA[h]
            except KeyError:
                arista = None

            try:
                aristaInv = dictA[hInverso]
            except KeyError:
                aristaInv = None 

            if arista is not None:
                pertS = True
                del dictA[h]

            if aristaInv is not None:
                pertS = True
                del dictA[hInverso]

            if(not pertS and self.__umbralMin <= EP.getPeso() and EP.getPeso() <= umbral and EP.getId() not in idListAristas):
            # if not pertS and self.__umbralMin <= EP.getPeso() and EP.getPeso() <= umbral:
                AristasNuevas.append(EP)
                ind_permitidos = np.append(ind_permitidos, EP.getId())
        
                # for a in solucion.getA():
                #     if a == EP:
                #         print("Error")
                #         print(EP)
                #         print("Id_EP: ", EP.getId())
        
        # ind_permitidos = np.unique(ind_permitidos)
        
        #print("Aristas Nuevas:\n ",str(AristasNuevas))
        return ind_permitidos
    
    #Decrementa el Tenure en caso de que no sea igual a -1. Si luego de decrementar es 0, lo elimino de la lista tabu
    def decrementaTenure(self, lista_tabu, ind_permitidos):
        i=0
        while (i < len(lista_tabu)):
            elemTabu=lista_tabu[i]
            elemTabu.decrementaT()
            if(elemTabu.getTenure()==0):
                ind_permitidos = np.append(ind_permitidos, elemTabu.getElemento().getId())
                lista_tabu.pop(i)
                i-=1
            i+=1

    def pathRelinking(self, S, G):
        '''
        (con mismo tamaño)
        Antes:
        S -> r1: 1-2-3-4-5   r2: 1-6-7-8-9-10
        G -> r1: 1-2-5-4-6   r2: 1-3-9-10-7-8
        Despues:
        S -> r1: 1-2-5-4-3   r2: 1-6-7-8-9-10
        G -> r1: 1-2-5-4-6   r2: 1-3-9-10-7-8
        (con distinto tamaño)
        Antes:
        S -> r1: 1-2-3-4-5   r2: 1-6-7-8-9-10
        G -> r1: 1-2-5-4     r2: 1-3-9-10-7-8-6
        Despues:
        S -> r1: 1-2-5-4-3   r2: 1-6-7-8-9-10
        G -> r1: 1-2-5-4     r2: 1-3-9-10-7-8-6
        '''
        #indS e indG = [Ri, Vi] mostraran el indice de la 1ra ruta y el 1er vertice el cual difieran
        #IndDistTam: indica la primera ruta de S que tiene un distinto
        #sigIndS: el ind del vertice de S para realizar el swap
        #rutasInfactibles: conjunto de indices de las rutas que son infactibles
        esFactible = False
        igualRec = False
        indDistTam = -1    
        sigIndS = [0,1]
        indS = [0,1]
        indG = [0,1]
        newS = []
        rutasInfactibles = set()
        indDistTam = self.igualesTam(S, G, indDistTam)
        
        if not igualRec:
            igualRec, indS, indG = self.igualesRec(S, G, indS, indG)
            
        while not esFactible:    
            #No son de igual recorrido
            if not igualRec:
                V_S = S[indS[0]].getV()
                V_G = G[indG[0]].getV()
                sigIndS = self.buscarSigVertice(S, G[indG[0]].getV()[indG[1]])
                
                #Si los vertices a cambiar de S pertenecen a la misma ruta
                if sigIndS[0] == indS[0]:
                    aristaAux = copy.copy(V_S[indS[1]])
                    V_S[indS[1]] = V_G[indG[1]]
                    V_S[sigIndS[1]] = aristaAux
                    capS = S[indS[0]].cargarDesdeSecuenciaDeVertices(V_S)
                    S[indS[0]].setCapacidad(capS)
                    if rutasInfactibles == set():
                        esFactible = True
                
                #No pertenecen a la misma ruta
                else:
                    newS, esFactible, rutasInfactibles = self.__S.swap_4optPR(indS[0], sigIndS[0], indS[1], sigIndS[1], S, rutasInfactibles)
                    
                    if esFactible and rutasInfactibles == set():
                        esFactible = True
                        S = newS
                    else:
                        esFactible = False
                    
                igualRec, indS, indG = self.igualesRec(S, G, indS, indG)
            
            #Son de igual recorrido
            else:          
                if rutasInfactibles == set():
                    esFactible = True

                if indDistTam == -1:
                    esFactible = True
                    break

                ind = indDistTam
                V_S = S[ind].getV()
                proxInd = ind+1
                V_sigS = S[proxInd].getV()
                
                #S: 1-2-3       1-4-5-6-7
                #G: 1-2-3-4-5   1-6-7
                if len(G[ind].getV()) > len(S[ind].getV()):
                    while len(V_sigS) == 1:
                        proxInd+=1
                        V_sigS = S[proxInd].getV()
                    aristaAux = V_sigS.pop(1)
                    V_S.append(aristaAux)
                
                #S: 1-2-3-4-5  1-6-7
                #G: 1-2-3      1-4-5-6-7
                else:
                    aristaAux = V_S.pop(-1)
                    V_sigS.insert(1, aristaAux)
                
                capS = S[ind].cargarDesdeSecuenciaDeVertices(V_S)
                S[ind].setCapacidad(capS)
                
                capSigS = S[proxInd].cargarDesdeSecuenciaDeVertices(V_sigS)
                S[proxInd].setCapacidad(capSigS)
                
                if capS > self.__capacidadMax or capSigS > self.__capacidadMax:
                    if capS > self.__capacidadMax:
                        rutasInfactibles = rutasInfactibles | set({ind})
                    else:
                        rutasInfactibles = rutasInfactibles - set({ind})

                    if capSigS > self.__capacidadMax:
                        rutasInfactibles = rutasInfactibles | set({ind+1})
                    else:
                        rutasInfactibles = rutasInfactibles - set({ind+1})
                else:
                    rutasInfactibles = rutasInfactibles - set({ind, ind+1})
                
                indDistTam = self.igualesTam(S, G, indDistTam)

        return [] if (indDistTam == -1 and igualRec) else S

    #Son de iguales Tamaño y/o Recorrido
    def igualesTam(self, S, G, indDistTam):
        i = 0
        
        while i < self.__nroVehiculos:
            S_V = S[i].getV()
            G_V = G[i].getV()
            lenSV = len(S_V)
            lenGV = len(G_V)
            if lenSV != lenGV:
                indDistTam = i
                break
            i+=1
        
        return indDistTam if i < self.__nroVehiculos else -1

    def igualesRec(self, S, G, indS, indG):
        igualRec = True
        
        while igualRec and indS!=None and indG!=None:
            S_V = S[indS[0]].getV()
            G_V = G[indG[0]].getV()
            lenSV = len(S_V)
            lenGV = len(G_V)
            
            if S_V[indS[1]] != G_V[indG[1]]:
                #print("S_V: "+str(S_V))
                #print("G_V: "+str(G_V))
                igualRec = False
            else:
                indS = self.incInd(indS, lenSV)
                indG = self.incInd(indG, lenGV)

            # print("indS: "+str(indS))
            # print("indG: "+str(indG))

        return igualRec, indS, indG

    def getRutasInfact(self, S, indInfact):
        i = indInfact
        
        while i < self.__nroVehiculos:
            if S[i].getCapacidad() > self.__capacidadMax:
                break
            i+=1
        
        return i if i < self.__nroVehiculos else -1

    def incInd(self, ind, lenV):
        #indS
        #print("ind: "+str(ind))
        if ind[1]+1 < lenV:
            ind[1]+=1
            #print("ind: "+str(ind))
            return ind
        elif ind[0]+1 < self.__nroVehiculos:
            ind[0]+=1
            ind[1]=1
            #print("ind: "+str(ind))
            return ind
        else:
            return None #es el último de la secuencia
    
    def buscarSigVertice(self, S, vertG):
        sigIndS = [0,1]
        # print("Vert G: "+str(vertG))
        # print("S: "+str(S))
        while sigIndS != None:
            lenVS = len(S[sigIndS[0]].getV())
            vertS = S[sigIndS[0]].getV()[sigIndS[1]]
            #print("vertS: "+str(vertS))
            if  vertS == vertG:
                return sigIndS
            sigIndS = self.incInd(sigIndS, lenVS)
            #print("ind: "+str(sigIndS))
        print("No encontre el vertice")
        print(S)
        print(vertG)
        a = 1/0

    def escribirDatosFinales(self, tiempoIni, iterac, tiempoEstancamiento):
        print("\nMejor solucion obtenida: "+str(self.__rutas) + "       costo: "+str(self.__S.getCostoAsociado()))
        tiempoTotal = time() - tiempoIni
        print("\nTermino!! :)")
        print("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg\n")


import re
import math
import time
from CVRP import CVRP
# from CVRPparalelo import CVRPparalelo
from Vertice import Vertice

import os
from os import listdir
from os.path import isfile, join
import ntpath

def cargarDesdeFile(pathArchivo):
    #+-+-+-+-+-Para cargar la distancias+-+-+-+-+-+-+-+-
    
    optimo = []
    
    archivo = open(pathArchivo,"r")
    lineas = archivo.readlines()
    
    #Busco la posiciones de...
    try:
        indSeccionCoord = lineas.index("NODE_COORD_SECTION\n")
        lineaEOF = lineas.index("DEMAND_SECTION\n")
    except ValueError:
        try:
            indSeccionCoord = lineas.index("NODE_COORD_SECTION \n")
            lineaEOF = lineas.index("DEMAND_SECTION \n")
        except ValueError:
            indSeccionCoord = lineas.index("NODE_COORD_SECTION\t\n")
            lineaEOF = lineas.index("DEMAND_SECTION\t\n")
    #Linea optimo y nro de vehiculos
    lineaOptimo = [x for x in lineas[0:indSeccionCoord] if re.search(r"COMMENT+",x)][0]
    parametros = re.findall(r"[0-9]+",lineaOptimo)
    
    nroVehiculos = int(float(parametros[0]))
    optimo = float(parametros[1])

    #Cargo la capacidad
    lineaCapacidad = [x for x in lineas[0:indSeccionCoord] if re.search(r"CAPACITY+",x)][0]
    parametros = re.findall(r"[0-9]+",lineaCapacidad)

    capacidad = float(parametros[0])
    print("Capacidad: "+str(capacidad))

    coordenadas = []
    #Separa las coordenadas en una matriz, es una lista de listas (vertice, coordA, coordB)
    for i in range(indSeccionCoord+1, lineaEOF):
        textoLinea = lineas[i]
        textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de linea
        splitLinea = textoLinea.split(" ") #Divide la linea por " "
        print ("Debuging: \n"+str(splitLinea))
        if(splitLinea[0]==""):
            coordenadas.append([splitLinea[1],splitLinea[2],splitLinea[3]]) #[[v1,x1,y1], [v2,x2,y2], ...]
        else:
            coordenadas.append([splitLinea[0],splitLinea[1],splitLinea[2]]) #[[v1,x1,y1], [v2,x2,y2], ...]
    matrizDist = cargaMatrizDistancias(coordenadas)
    
    #+-+-+-+-+-+-+-Para cargar la demanda+-+-+-+-+-+-+-
    seccionDemanda = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEMAND_SECTION+",x)][0]
    indSeccionDemanda = lineas.index(seccionDemanda)
    
    seccionEOF = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEPOT_SECTION+",x)][0]
    indLineaEOF = lineas.index(seccionEOF)

    demandas = []
    for i in range(indSeccionDemanda+1, indLineaEOF):
        textoLinea = lineas[i]
        textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de linea
        splitLinea = textoLinea.split() #Divide la linea por " " 
        demandas.append(float(splitLinea[1]))

    return nroVehiculos, optimo, capacidad, matrizDist, demandas
def cargaMatrizDistancias(coordenadas):
    matriz = []
    #Arma la matriz de distancias. Calculo la distancia euclidea
    for coordRow in coordenadas:
        fila = []            
        for coordCol in coordenadas:
            x1 = float(coordRow[1])
            y1 = float(coordRow[2])
            x2 = float(coordCol[1])
            y2 = float(coordCol[2])
            dist = distancia(x1,y1,x2,y2)
            
            #Para el primer caso. Calculando la distancia euclidea entre si mismo da 0
            if(dist == 0):
                dist = 999999999999 #El modelo no deberia tener en cuenta a las diagonal, pero por las dudas
            fila.append(dist)

        #print("Fila: "+str(fila))    
        matriz.append(fila)
    return matriz    #retorna una matriz de distancia
def distancia(x1,y1,x2,y2):
    return round(math.sqrt((x1-x2)**2+(y1-y2)**2),3)
def cargarDesdeFile2(pathArchivo):
        #+-+-+-+-+-Para cargar la distancias+-+-+-+-+-+-+-+-
        optimo = []
        archivo = open(pathArchivo,"r")
        lineas = archivo.readlines()
        
        #Busco la posiciones de...
        try:
            indSeccionCoord = lineas.index("NODE_COORD_SECTION \n")
            lineaEOF = lineas.index("DEMAND_SECTION \n")
        except ValueError:
            try:
                indSeccionCoord = lineas.index("NODE_COORD_SECTION\n")
                lineaEOF = lineas.index("DEMAND_SECTION\n")
            except ValueError:
                indSeccionCoord = lineas.index("NODE_COORD_SECTION\t\n")
                lineaEOF = lineas.index("DEMAND_SECTION\t\n")
                
        #Linea optimo y nro de vehiculos
        lineaOptimo = [x for x in lineas[0:indSeccionCoord] if re.search(r"COMMENT+",x)][0]
        parametros = re.findall(r"[0-9]+",lineaOptimo)
        
        nroVehiculos = (int(float(parametros[0])))
        optimo = (float(parametros[1]))

        #Cargo la capacidad
        lineaCapacidad = [x for x in lineas[0:indSeccionCoord] if re.search(r"CAPACITY+",x)][0]
        parametros = re.findall(r"[0-9]+",lineaCapacidad)

        capacidad=(float(parametros[0]))
        print("Capacidad: "+str(capacidad))

        #Lista donde irán las coordenadas (vertice, x, y)
        coordenadas = []
        #Separa las coordenadas en una matriz, es una lista de listas (vertice, coordA, coordB)
        for i in range(indSeccionCoord+1, lineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split() #Divide la línea por " " 
            if(splitLinea[0]==""):
                coordenadas.append([splitLinea[1],splitLinea[2],splitLinea[3]]) #[[v1,x1,y1], [v2,x2,y2], ...]
            else:
                coordenadas.append([splitLinea[0],splitLinea[1],splitLinea[2]]) #[[v1,x1,y1], [v2,x2,y2], ...]
        #print("coordenadas: "+str(coordenadas))
        matrizDist = cargaMatrizDistancias(coordenadas)
        
        #+-+-+-+-+-+-+-Para cargar la demandas+-+-+-+-+-+-+-
        seccionDemanda = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEMAND_SECTION+",x)][0]
        indSeccionDemanda = lineas.index(seccionDemanda)
        
        seccionEOF = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEPOT_SECTION+",x)][0]
        indLineaEOF = lineas.index(seccionEOF)

        demandas = []
        for i in range(indSeccionDemanda+1, indLineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split() #Divide la línea por " " 
            try:
                demandas.append(float(splitLinea[1]))
            except:
                splitLinea = textoLinea.split()
                demandas.append(float(splitLinea[1]))
        return nroVehiculos, optimo, capacidad, matrizDist, demandas     

# direccion = "/home/alumno/tpfinal_v2/MPIv3/cvrp/Instancias/Set M/M-n200-k16.vrp"
direccion = "C:\\Users\\Maxi\\Documents\\UNSA\\LAS\\5to Año\\1er cuatrimestre\\Optativa (Opt. Conc. y Paralela)\\Proyectos\\TPFinal_CVRP\\Instancias\\Set A\\A-n32-k5.vrp"

nombre = "A-n32-k5.vrp"

nroVehiculos, optimo, capacidad, matrizDist, demandas = cargarDesdeFile2(direccion)
tenureADD = int(len(matrizDist)**(1/2.0))
tenureDROP = int(len(matrizDist)**(1/2.0))+1
time = 6.0
#cvrp = CVRP(matrizDist, demandas, nroVehiculos, capacidad, nombre+"_"+str(time)+"min", 'secuencial_', 0, tenureADD, tenureDROP, time, 0.1, optimo)
inf = float("inf")
matrizDist = [[inf, 2 , 3 , 4 , 5 , 6 , 3.2, 4.4, 5.9, 2, 1, 0.1],
              [7, inf , 8 , 9 , 10, 1.1, 3.3, 4.5,6.1, 3, 2, 0.3],
              [12, 13 ,inf, 14, 15, 1.6, 3.4, 4.6,6.3, 4, 3, 0.4],
              [17, 18 , 19,inf, 20, 21, 3.5, 4.7, 6.5, 5, 4, 0.5],
              [22, 23 , 24, 25,inf, 26, 3.6, 4.8, 6.7, 6, 5, 0.6],
              [27, 28 , 29, 30, 31,inf, 3.7, 4.9, 6.9, 7, 6, 0.7],
              [38, 39 , 40, 41, 42, 43,inf, 5.0,  7.1, 8, 7, 0.8],
              [51, 52 , 54, 55, 56, 57, 5.8,inf,  7.3, 9, 8, 0.9],
              [75, 76 , 77, 78, 79, 80, 8.1, 8.2,inf, 10, 9, 1.1],
              [12, 13 , 14, 15, 16, 17, 1.8, 19, 20, inf, 4, 1.2],
              [1.2,1.3,1.4,1.5,1.6,1.7, 1.8,1.9,2.2,4.1 ,inf, 1.3],
              [1.4,1.5,1.6,1.7,1.8,1.8, 2.1, 2 ,2.3,2.4 ,2.5, inf]
            ]
demandas =    [ 0, 1  ,  1,  1,  1,  1,  1,  1,  1, 0, 0, 0]
capacidad = 6
cvrp = CVRP(matrizDist, demandas, 2, capacidad, "prueba"+str(time)+"min", 'secuencial', 0, tenureADD, tenureDROP, time, 0, 1)

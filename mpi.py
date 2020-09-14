import re
import math
import time
# from CVRP import CVRP
from CVRPparalelo import CVRPparalelo
from Vertice import Vertice

import os
from os import listdir
from os.path import isfile, join
import ntpath
import sys
import numpy as np
from mpi4py import MPI


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
        indSeccionCoord = lineas.index("NODE_COORD_SECTION \n")
        lineaEOF = lineas.index("DEMAND_SECTION \n")
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
        splitLinea = textoLinea.split(" ") #Divide la linea por " " 
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
            if(dist == 0 and float(coordRow[0])==float(coordCol[0])):
                dist = float("inf")
            fila.append(dist)

        #print("Fila: "+str(fila))
        matriz.append(fila)
    return np.array(matriz)

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

comm = MPI.COMM_WORLD
direccion = sys.argv[1]

nombre = os.path.basename(direccion)
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    nroVehiculos, optimo, capacidad, matrizDist, demandas = cargarDesdeFile2(direccion)

    # tenureADD = int(len(matrizDist)**(1/2.0))
    # tenureDROP = int(len(matrizDist)**(1/2.0))+1
    tenureADD = 4
    tenureDROP = 4
    solucionInicial = 0
    time = sys.argv[2]
    cvrp = CVRPparalelo(
        matrizDist,
        demandas,
        nroVehiculos,
        capacidad,
        nombre+"_"+str(time)+"min", 'mpi_',
        solucionInicial, 
        tenureADD, 
        tenureDROP, 
        time, 
        0.1, 
        optimo,
        rank=rank
        )
    print("Calculando rutas iniciales en nodo root")
    rutas = cvrp.calculaRutasIniciales()
    print("Se cargaron rutas iniciales en nodo root")
    dic = {'nroVehiculos':nroVehiculos, 'optimo':optimo, 'capacidad':capacidad, 'matrizDist':matrizDist, 'demandas':demandas, "solInicial": rutas}
    for r in range(1,size):
        print(f"enviando datos a nodo {r} ")
        comm.send(dic,dest=r)
    
    cvrp.setRutasIniciales(rutas)
    cvrp.tabuSearch()
    
else:
    dic = comm.recv()
    nroVehiculos = dic['nroVehiculos']
    optimo = dic['optimo']
    capacidad = dic['capacidad']
    matrizDist = dic['matrizDist']
    demandas = dic['demandas']
    rutas = dic['solInicial']

    # tenureADD = int(len(matrizDist)**(1/2.0))
    # tenureDROP = int(len(matrizDist)**(1/2.0))+1
    tenureADD = 4
    tenureDROP = 4
    solucionInicial = 0
    time = sys.argv[2]
    print("Creando Instancias CVRP en nodo ", rank)
    cvrp = CVRPparalelo(
        matrizDist,
        demandas,
        nroVehiculos,
        capacidad,
        nombre+"_"+str(time)+"min", 'mpi_',
        solucionInicial, 
        tenureADD, 
        tenureDROP, 
        time, 
        1.0, 
        optimo,
        rutasIniciales=rutas,
        rank = rank)


    cvrp.tabuSearch()

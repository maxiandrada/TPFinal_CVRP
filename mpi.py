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
import glob
from mpi4py import MPI

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def findAll(match, exc, path):
    lista = []
    if exc == "none":
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.find(match) != -1 and f.endswith(".vrp"):
                    lista.append(os.path.join(root, f))
    else:
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.find(match) != -1 and f.endswith(".vrp") and f.lower().find(exc.lower())==-1:
                    lista.append(os.path.join(root, f))
    return lista

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

def ejecutaParalelismo(direccion, tiempo):
    comm = MPI.COMM_WORLD
    nombre = os.path.basename(direccion)
    size = comm.Get_size()
    rank = comm.Get_rank()
    if rank == 0:
        t = time.time()
        timeObj = time.localtime(t)
        subcarpeta = '%d-%d-%d_%d:%d:%d' % (timeObj.tm_mday, timeObj.tm_mon, timeObj.tm_year, timeObj.tm_hour, timeObj.tm_min, timeObj.tm_sec)
        nroVehiculos, optimo, capacidad, matrizDist, demandas = cargarDesdeFile2(direccion)
        if tiempo == None:
            tiempo = int(len(matrizDist)**0.7)
        tenureADD = int(len(matrizDist)**(1/2.0))
        tenureDROP = int(len(matrizDist)**(1/2.0))+1
        solucionInicial = 0
        cvrp = CVRPparalelo(
            matrizDist,
            demandas,
            nroVehiculos,
            capacidad,
            subcarpeta,
            nombre[:-4]+"_nodo"+str(rank)+"_"+str(tiempo)+"min", 'paralelismo',
            solucionInicial, 
            tenureADD, 
            tenureDROP, 
            tiempo, 
            -10.0,
            optimo,
            rank=rank
            )
        print("Calculando rutas iniciales en nodo root")
        rutas = cvrp.calculaRutasIniciales()
        print("Se cargaron rutas iniciales en nodo root")
        dic = {'nroVehiculos':nroVehiculos, 'optimo':optimo, 'capacidad':capacidad, 'matrizDist':matrizDist, 'demandas':demandas, "solInicial": rutas, "subcarpeta": subcarpeta, "tiempo":tiempo}
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
        subcarpeta = dic['subcarpeta']
        tiempo = dic["tiempo"]

        tenureADD = int(len(matrizDist)**(1/2.0))
        tenureDROP = int(len(matrizDist)**(1/2.0))+1
        solucionInicial = 0
        print("Creando Instancias CVRP en nodo ", rank)
        cvrp = CVRPparalelo(
            matrizDist,
            demandas,
            nroVehiculos,
            capacidad,
            subcarpeta,
            nombre[:-4]+"_nodo"+str(rank)+"_"+str(tiempo)+"min", 'mpi',
            solucionInicial, 
            tenureADD, 
            tenureDROP, 
            tiempo, 
            -10.0, 
            optimo,
            rutasIniciales=rutas,
            rank = rank
            )
        cvrp.tabuSearch()


match = str(sys.argv[1])
exc = str(sys.argv[2])
try:
    tiempo = sys.argv[3]
except IndexError:
    tiempo = None
for f in findAll(match, exc, os.getcwd()):
    print ("AHORA SE EJECUTARÁ LA INSTANCIA :\n"+f)
    ejecutaParalelismo(f, tiempo)
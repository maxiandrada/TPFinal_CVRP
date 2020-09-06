import re
import math
from time import time
from CVRP import CVRP
from Vertice import Vertice
import os
from os import listdir
from os.path import isfile, join
import ntpath
import DB
import sqlite3
import json
import numpy as np
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize, QRunnable,pyqtSlot, QObject, pyqtSignal,QThread, QThreadPool
from PyQt5.QtGui import QPen, QBrush
from PyQt5.Qt import Qt
from PyQt5.QtGui import QDoubleValidator
import PySide2
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

class Hilo(QThread):
    progreso = pyqtSignal(int)

    def run(self):
        contador = 0
        while contador < 100:
            contador+=1

            time.sleep(0.3)
            self.progreso.emit(contador)

class GUI(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        #Conexión base de datos
        self.conn = DB.DB()

        self.setMinimumSize(QSize(1000, 600))
        self.setWindowTitle("Capacited Vehicle Routing Problem - Tabu Search")

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.gridLayout = QGridLayout(self)
        self.centralWidget.setLayout(self.gridLayout)
        self.seleccionarProblema()
        self.threadpool = QThreadPool()
        self.rutasDict = {}
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def seleccionarProblema(self):
        self.centralWidget
        #Botón resolver instancia
        self.boton1 = QPushButton("ResolverInstancia")
        self.boton1.clicked.connect(lambda: self.ventanaResolverInstancia())

        #Botón Ver resultados
        self.boton2 = QPushButton("Ver Resultados")
        self.gridLayout.addWidget(self.boton1,0,3)
        self.gridLayout.addWidget(self.boton2,1,3)

        #Botón para abrir ventana para cargar sets
        self.botonNuevoSet = QPushButton("Nuevo Set")
        self.gridLayout.addWidget(self.botonNuevoSet, 1,0)
        self.botonNuevoSet.clicked.connect(self.ventanaCargaSet)

        #Botón para abrir ventana para cargar ventanas
        self.botonNuevaInstancia = QPushButton("Nueva Instancias")
        self.gridLayout.addWidget(self.botonNuevaInstancia, 1,1)
        self.botonNuevaInstancia.clicked.connect(self.ventanaCargaInstancia)

        self.gridLayout.setContentsMargins(4,4,4,2)

        self.barra = QProgressBar()
        self.gridLayout.addWidget(self.barra)
        
        self.boton2.clicked.connect(self.iniciarBarra)

        self.tablaSetProblemas()
        self.tablaIntancias()

    def iniciarBarra(self):
        self.hilo = Worker(lambda x: x)
        self.hilo.signals.progreso.connect(self.establecerProgresoBarra)
        self.threadpool.start(self.hilo) 


    def establecerProgresoBarra(self,valor):
        self.barra.setValue(valor)

    def ventanaCargaInstancia(self):
        #Definiciones
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        instancias, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Archivos VRP (*.vrp)", options=options)
        if instancias:
            for i in instancias:
                self.cargarDesdeFile(i)
                filaInstancia = (self.nombreArchivo, int(self.cantidadClientes), self.__nroVehiculos, json.dumps(self.__demanda), self.__capacidad, self.__optimo, json.dumps(self.coordenadas))

                print(filaInstancia)
                idFila = DB.insert_instancia(self.conn,filaInstancia)
                print(int(self.setSeleccionado))
                print(idFila)
                DB.insert_instanciaXSet(self.conn, (idFila, int(self.setSeleccionado)))

    def ventanaCargaSet(self):
        #Definiciones
        self.ventanaCargarSet = QDialog()
        self.ventanaCargarSet.setWindowTitle("Cargar Nuevo Conjunto")
        self.ventanaCargarSet.setModal(True)
        self.ventanaCargarSet.gridLayout = QGridLayout(self.ventanaCargarSet)
        labelNombreSet = QLabel("Ingresar Nombre Set")
        textEditNombreSet = QLineEdit(self.ventanaCargarSet)
        botonOK = QPushButton("OK")
        botonCancelar = QPushButton("Cancelar")
        #fijar en layout
        self.ventanaCargarSet.gridLayout.addWidget(labelNombreSet,1,1)
        self.ventanaCargarSet.gridLayout.addWidget(textEditNombreSet,1,2)
        self.ventanaCargarSet.gridLayout.addWidget(botonOK,2,1)
        self.ventanaCargarSet.gridLayout.addWidget(botonCancelar,2,2)
        #Eventos
        botonOK.clicked.connect(lambda: self.cargarSetDB(textEditNombreSet.text()))
        botonCancelar.clicked.connect(lambda: self.ventanaCargarSet.close())
        self.ventanaCargarSet.exec()

    def cargarSetDB(self,nombre):
        if(nombre!=""):
            print("NOMBRE; ", nombre)
            DB.insert_set(self.conn,(nombre,))
            self.tablaSetProblemas()
            self.ventanaCargarSet.close()
        else:
            error_dialog = QErrorMessage()
            error_dialog.setWindowTitle("ERROR")
            error_dialog.showMessage('Debe ingresar un nombre')
            error_dialog.exec()

    def tablaSetProblemas(self):
        self.tablaSetProblema = QTableWidget()
        self.tablaSetProblema.setColumnCount(2)
        filasSets = DB.select_sets(self.conn)
        #print(filasSets)
        self.tablaSetProblema.setRowCount(len(filasSets))
        self.tablaSetProblema.setHorizontalHeaderLabels(["ID Set",'Nombre Set'])
        for i in range(len(filasSets)):
            self.tablaSetProblema.setItem(i,0, QTableWidgetItem(str(filasSets[i][0])))
            self.tablaSetProblema.setItem(i,1, QTableWidgetItem(filasSets[i][1]))

        self.tablaSetProblema.setSelectionBehavior(QTableView.SelectRows)
        self.tablaSetProblema.itemSelectionChanged.connect(self.establecerSetSeleccionado)

        self.gridLayout.addWidget(self.tablaSetProblema,0,0,1,1,)


    def establecerSetSeleccionado(self):
        self.setSeleccionado = str(self.tablaSetProblema.selectedItems()[0].text())
        self.tablaIntancias()
        self.llenarTablaInstancias()



    def establecerInstanciaSeleccionada(self):
        self.instanciaSeleccionada = int(self.tablaInstancia.selectedItems()[0].text())
        print(self.instanciaSeleccionada)

    def tablaIntancias(self):
        self.tablaInstancia = QTableWidget()
        self.tablaInstancia.setSelectionBehavior(QTableView.SelectRows)
        self.gridLayout.addWidget(self.tablaInstancia,0,1,1,1)
        self.tablaInstancia.itemSelectionChanged.connect(self.establecerInstanciaSeleccionada)


    def llenarTablaInstancias(self):
        filasInstancias = DB.select_instanciaXSet(self.conn,self.setSeleccionado)
        #print(filasInstancias)

        self.tablaInstancia.setRowCount(len(filasInstancias))
        self.tablaInstancia.setColumnCount(6)
        self.tablaInstancia.setHorizontalHeaderLabels(["ID Instancia",'Nombre Instancia','Cantidad de Clientes',"Vehículos","Capacidad", "Optimo Conocido"])
        for i in range(len(filasInstancias)):
            self.tablaInstancia.setItem(i,0, QTableWidgetItem(str(filasInstancias[i][0])))
            self.tablaInstancia.setItem(i,1, QTableWidgetItem(filasInstancias[i][1]))
            self.tablaInstancia.setItem(i,2, QTableWidgetItem(str(filasInstancias[i][2])))
            self.tablaInstancia.setItem(i,3, QTableWidgetItem(str(filasInstancias[i][3])))
            self.tablaInstancia.setItem(i,4, QTableWidgetItem(str(filasInstancias[i][4])))
            self.tablaInstancia.setItem(i,5, QTableWidgetItem(str(filasInstancias[i][5])))

    def ventanaResolverInstancia(self):
        instancia = DB.select_instancia(self.conn,self.instanciaSeleccionada)[0]
        print(instancia)
        ventanaResolverInstancia = QDialog(self)
        ventanaResolverInstancia.setWindowTitle("Resolviendo "+ instancia[1])
        labelTitulo = QLabel(str(instancia[1]))
        labelTitulo.setFont(QtGui.QFont('Arial', 20))
        labelTitulo.setAlignment(QtCore.Qt.AlignCenter)
        layoutVRI = QGridLayout(ventanaResolverInstancia)
        ventanaResolverInstancia.setLayout(layoutVRI)
        layoutVRI.addWidget(labelTitulo,0,0)
        ventanaResolverInstancia.setGeometry(100,100,1100,600)
        ventanaResolverInstancia.setMinimumSize(QSize(1000, 600))
        #Gráfico
        coordenadas = json.loads(instancia[7])
        self.grafico = self.graficoInstancia(layoutVRI, coordenadas,1 , 0)
        #Layout Vertical Derecha
        layoutV= QVBoxLayout()
        layoutVG = QGridLayout()
        layoutVRI.addLayout(layoutV, 0, 1, 2, 1)
        layoutV.addLayout(layoutVG)
        #Solución Inicial
        labelSolucionInicial = QLabel("Seleccione Solución Inicial")
        cbSolucionInicial = QComboBox()
        cbSolucionInicial.addItems(["Clarke Wright", "Vecino Cercano", "Secuencial"])
        #Tenures
        labelTenureADD = QLabel("Tenure ADD")
        sbTenureADD = QSpinBox()
        sbTenureADD.setValue(int(len(coordenadas)**(1/2.0)))

        labelTenureDROP = QLabel("Tenure DROP")
        sbTenureDROP = QSpinBox()
        sbTenureDROP.setValue(int(len(coordenadas)**(1/2.0))+1)
        #Tiempo ejecución
        labelTiempoEjecucion = QLabel("Tiempo Ejecución")
        leTiempoEjecucion = QLineEdit()
        leTiempoEjecucion.setValidator(QDoubleValidator(0.0,100.0,2))
        leTiempoEjecucion.setText("0.1")
        labelMinutos = QLabel("Minutos")
        #Porcentaje de parada 
        labelParada = QLabel("Error respecto a óptimo conocido")
        sbParada = QSpinBox()
        #Boton resolver
        botonResolver = QPushButton("Resolver")
        botonVerResultados = QPushButton("Ver Resultados")


        layoutVG.addWidget(labelSolucionInicial,0,0)
        layoutVG.addWidget(cbSolucionInicial,0,1)
        layoutVG.addWidget(labelTenureADD,1,0)
        layoutVG.addWidget(sbTenureADD,1,1)
        layoutVG.addWidget(labelTenureDROP,1,2)
        layoutVG.addWidget(sbTenureDROP,1,3)
        layoutVG.addWidget(labelTiempoEjecucion,2,0)
        layoutVG.addWidget(leTiempoEjecucion,2,1)
        layoutVG.addWidget(labelMinutos,2,2)
        layoutVG.addWidget(labelParada,3,0)
        layoutVG.addWidget(sbParada,3,1)
        layoutVG.addWidget(botonResolver,4,2)
        layoutVG.addWidget(botonVerResultados,4,3)

        resolver = lambda : self.resolverCVRP(instancia,cbSolucionInicial,sbTenureADD,sbTenureDROP,leTiempoEjecucion,sbParada,coordenadas,self.conn)
        botonResolver.clicked.connect(resolver)
        ventanaResolverInstancia.show()


    def resolverCVRP(self, instancia, cbSolucionInicial, sbTenureADD, sbTenureDROP, leTiempoEjecucion, sbParada, coordenadas, db):
        #Parámetros iniciales ingresados por el usuario
        solucionInicial = cbSolucionInicial.currentIndex()
        tenureADD = sbTenureADD.value()
        tenureDROP = sbTenureDROP.value()
        tiempo = float(leTiempoEjecucion.text())
        porcentaje = sbParada.value() 
        #Datos de la instancia
        idInstancia = instancia[0]
        self.n = instancia[2]
        self.k = instancia[3]
        self.D = json.loads(instancia[4])
        self.C = instancia[5]
        optimo = instancia[6]
        self.coordenadas = json.loads(instancia[7])
        self.M = self.cargaMatrizDistancias(self.coordenadas)
        cvrp = CVRP(self.M, self.D, self.k, self.C, solucionInicial, tenureADD, tenureDROP, tiempo, optimo, self.coordenadas, porcentaje,idInstancia)
        self.dibujarRutaInicial(cvrp.getRutas())
        self.hiloGrafico = Worker(cvrp.tabuSearch)
        self.hiloGrafico.signals.ruta.connect(self.dibujarRutasNuevas)
        self.hiloGrafico.signals.rutaLista.connect(self.dibujarRutaInicial)
        cvrp.setHilo(self.hiloGrafico )
        self.threadpool.start(self.hiloGrafico) 
        self.dibujarRutaInicial(cvrp.getRutas())
 
        


         


    # def graficoInstancia(self,layout,coordenadas,row,col):
    #     figure = plt.figure(figsize=(4, 4), dpi=100)
    #     figure.set_facecolor("none")
        
    #     ax = figure.add_subplot(111)
    #     canvas = FigureCanvas(figure)
    #     layout.addWidget(canvas,row,col)
        
    #     for coord in coordenadas:
    #         if(coord[0]==1):
    #             ax.scatter(coord[1],coord[2], s=20  , c=['#ff1902'])
    #         else:
    #             ax.scatter(coord[1],coord[2], s=10, c=['#000000'])

    #     canvas.draw()
    #     return ax

    def graficoInstancia(self,layout,coordenadas,row,col):
        w1 = pg.PlotWidget()
        #w1 = view.addPlot()
       #QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256, QtCore.qrand() % 256
        for coord in coordenadas:
            s = pg.ScatterPlotItem([coord[1]], [coord[2]], size=10, pen=pg.mkPen(None))  
            if coord[0] == 1:
                s.setBrush(QBrush(QtGui.QColor(255,0,0)))
            else:
                s.setBrush(QBrush(QtGui.QColor(255,255,255)))
            w1.addItem(s)
        layout.addWidget(w1)

        return w1
    #Obtengo los datos de mis archivos .vrp
    def cargarDesdeFile(self,pathArchivo):
        #+-+-+-+-+-Para cargar la distancias+-+-+-+-+-+-+-+-
        archivo = open(pathArchivo,"r")
        lineas = archivo.readlines()
        self.nombreArchivo = os.path.basename(archivo.name)
        self.nombreArchivo = self.nombreArchivo.split(".")[0]
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

        self.__nroVehiculos = int(float(parametros[0]))
        self.__optimo = float(parametros[1])

        #Cargo la capacidad
        lineaCapacidad = [x for x in lineas[0:indSeccionCoord] if re.search(r"CAPACITY+",x)][0]
        parametros = re.findall(r"[0-9]+",lineaCapacidad)

        self.__capacidad = float(parametros[0])
        print("Capacidad: "+str(self.__capacidad))

        #Lista donde irán las coordenadas (vertice, x, y)
        coord = []
        #Separa las coordenadas en una matriz, es una lista de listas (vertice, coordA, coordB)
        for i in range(indSeccionCoord+1, lineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split() #Divide la línea por " "
            if(splitLinea[0]==""):
                coord.append([float(splitLinea[1]),float(splitLinea[2]),float(splitLinea[3])]) #[[v1,x1,y1], [v2,x2,y2], ...]
            else:
                coord.append([float(splitLinea[0]),float(splitLinea[1]),float(splitLinea[2])]) #[[v1,x1,y1], [v2,x2,y2], ...]
        #print("coordenadas: "+str(coordenadas))
        #self.cargaMatrizDistancias(coordenadas)
        self.coordenadas = coord

        #+-+-+-+-+-+-+-Para cargar la demanda+-+-+-+-+-+-+-
        seccionDemanda = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEMAND_SECTION+",x)][0]
        indSeccionDemanda = lineas.index(seccionDemanda)

        seccionEOF = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEPOT_SECTION+",x)][0]
        indLineaEOF = lineas.index(seccionEOF)

        demanda = []
        for i in range(indSeccionDemanda+1, indLineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split() #Divide la línea por " "
            try:
                demanda.append(float(splitLinea[1]))
            except:
                splitLinea = textoLinea.split()
                demanda.append(float(splitLinea[1]))
        #print(str(demanda))
        self.__demanda = demanda
        self.cantidadClientes = len(self.__demanda)

    def cargaMatrizDistancias(self, coordenadas):
        matriz = []
        #Arma la matriz de distancias. Calculo la distancia euclidea
        for coordRow in coordenadas:
            fila = []
            for coordCol in coordenadas:
                x1 = float(coordRow[1])
                y1 = float(coordRow[2])
                x2 = float(coordCol[1])
                y2 = float(coordCol[2])
                dist = self.distancia(x1,y1,x2,y2)

                #Para el primer caso. Calculando la distancia euclidea entre si mismo da 0
                if(dist == 0 and float(coordRow[0])==float(coordCol[0])):
                    dist = float("inf")
                fila.append(dist)

            #print("Fila: "+str(fila))
            matriz.append(fila)
        return np.array(matriz)

    def distancia(self, x1,y1,x2,y2):
        return math.sqrt((x1-x2)**2+(y1-y2)**2)



    def dibujarRutaInicial(self,rutas):
        #print("Ingresar Rutas : ",rutas)
        print("recibió ruta")
        i = 0
        t = time()

        self.grafico.clear()


        for r in rutas:
            x = [self.coordenadas[0][1]]
            y = [self.coordenadas[0][2]]
            for a in r.getA()[1:]:
                x.append(self.coordenadas[a.getOrigen().getValue()-1][1])
                y.append(self.coordenadas[a.getOrigen().getValue()-1][2])
            x += [self.coordenadas[0][1]]
            y += [self.coordenadas[0][2]]
            ruta = self.grafico.plot(x,y,pen=(i,self.k),symbol='o',symbolBrush=(i,self.k))
            self.rutasDict[i]=ruta
            i+=1
        x = [self.coordenadas[0][1]]
        y = [self.coordenadas[0][2]]
        deposito = self.grafico.plot(x, y, pen=(0,self.k), symbol='h', symbolSize=20, symbolBrush=(255,255,255))
        self.rutasDict[i+1]= deposito
        print(f"Se cargó el gráfico --> {time()-t} ")

    def dibujarRutasNuevas(self,R):
        indRutas = R["indRutas"] 
        rutas = R["rutas"]
        print("recibió ruta")
        

        t = time()
        self.grafico.clear()
        for d in self.rutasDict.keys():
            if d != indRutas[0] and d != indRutas[1]:
                self.grafico.addItem(self.rutasDict[d])

        i = 0
        for r in rutas:
            x = [self.coordenadas[0][1]]
            y = [self.coordenadas[0][2]]
            for a in r.getA()[1:]:
                x.append(self.coordenadas[a.getOrigen().getValue()-1][1])
                y.append(self.coordenadas[a.getOrigen().getValue()-1][2])
            x += [self.coordenadas[0][1]]
            y += [self.coordenadas[0][2]]
            ruta = self.grafico.plot(x,y,pen=(indRutas[i],self.k),symbol='o',symbolBrush=(indRutas[i],self.k))
            self.rutasDict[indRutas[i]] = ruta
            i+=1

        print(f"Se cargó el gráfico --> {time()-t} ")


class Worker(QRunnable):

    def __init__(self,funcion, *args, **kwargs):
        super(Worker, self).__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()      
        self.fn = funcion


    @pyqtSlot()
    def run(self):
        self.fn()




class WorkerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    ruta = pyqtSignal(dict)
    rutaLista = pyqtSignal(list)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = GUI()
    mainWin.show()
    sys.exit( app.exec_() )



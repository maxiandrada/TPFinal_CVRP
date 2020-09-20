import re
import sys
import json
import DB
if __name__== "__main__":
    path = sys.argv[1]
    archivoTxt = open(path, "r",encoding="latin-1")
    lineas = [linea for linea in archivoTxt.readlines()]
    rutas = []
    swapsStr = []
    costosRuta = []
    costosRutas = []
    iteraciones = []
    for i in range(len(lineas)):
         aux = re.findall(r"Nro de vehiculos:", lineas[i])
         if len(aux) != 0:
             k = int(lineas[i].split(" ")[3])

         aux = re.findall(r"Nro de clientes:", lineas[i])
         if len(aux) != 0:
             n = int(lineas[i].split(" ")[3])

         aux = re.findall(r"Cantidad de iteraciones:", lineas[i])
         if len(aux) != 0:
             cantidadIteraciones = int(lineas[i].split(" ")[3])

         aux = re.findall(r"Ruta #", lineas[i])
         if len(aux) != 0:
             rutas.append(lineas[i])

         aux = re.findall("Costo asociado: ", lineas[i])
         if len(aux) != 0:
             costosRuta.append(float(lineas[i].split(" ")[2]))

         aux = re.findall("Costo total: ", lineas[i])
         if len(aux) != 0:
             costosRutas.append(float(lineas[i].split(" ")[3]))

         aux = re.findall("Iteracion ", lineas[i])
         if len(aux) != 0:
            iteraciones.append(int(lineas[i].split(" ")[2]))

         aux = re.findall("Se estancó|([1-5]-Opt)", lineas[i])
         if len(aux) != 0:
             swapsStr.append(lineas[i])

         aux = re.findall("Solucion peor", lineas[i])
         if len(aux) != 0:
             swapsStr.append(lineas[i])

         aux = re.findall("Solucion inicial", lineas[i])
         if len(aux) != 0:
             solucionInicial = lineas[i].split(": ")[1].replace("\n", "")

         aux = re.findall("Costo Total", lineas[i])
         if len(aux) != 0:
             costoTotal = lineas[i].split(" ")[2]

         aux = re.findall("Desviación", lineas[i])
         if len(aux) != 0:
             desvio = float(lineas[i].split(": ")[3].replace("%\n", ""))

         aux = re.findall("Tiempo total:", lineas[i])
         if len(aux) != 0:
             tiempoTotal1 = lineas[i].split(" ")[2].replace("min", "")
             tiempoTotal2 = lineas[i].split(" ")[3].replace("seg", "")

    tiempoTotal = [int(tiempoTotal1), int(tiempoTotal2)]
    tiempoTotal = int(tiempoTotal[0]/60) + tiempoTotal[1]
    #Se procesan las rutas
    i = 0
    ruta = []
    rutasNuevas = []
    for r in rutas:
        if i < k:
            strRuta = re.findall("Ruta #[0-9]*: ", r)[0]
            R = r.replace(strRuta, "")
            R = R.replace("\n", "")
            ruta.append(json.loads(R))
            i+=1
        if i == k:
            rutasNuevas.append(ruta)
            i = 0
            ruta = []
    #Se le suma la primer y última iteración 
    iteraciones = [1] + iteraciones
    iteraciones.append(cantidadIteraciones)
    #Se procesan los swaps y demás movimientos
    for i in range(len(swapsStr)):
        swapsStr[i] = swapsStr[i].replace("-Opt Opcion:", "")
        swapsStr[i] = swapsStr[i].replace("\n", "")
        aux = re.findall("path relinking", swapsStr[i])
        if len(aux) != 0:
            swapsStr[i] = "PathRelinking"

        aux = re.findall("penultimo", swapsStr[i])
        if len(aux) != 0:
            swapsStr[i] = "penúltimo"

        aux = re.findall("peor", swapsStr[i])
        if len(aux) != 0:
            swapsStr[i] = "peor"

        aux = re.findall(r"[0-9] [\-]*[0-9]", swapsStr[i])
        if len(aux) != 0:
            splitStr = swapsStr[i].split(" ")
            swapsStr[i] = [int(splitStr[0]),int(splitStr[1])]

    swaps = [0]*4
    for s in swapsStr:
        if isinstance(s, list):
            if s[0] == 2:
                swaps[0]+= 1
            elif s[0] == 3:
                swaps[1]+= 1
            elif s[0] == 4:
                swaps[2] += 1
            elif s[0] == 5:
                swaps[3] += 1

    cantidadClientes = 0
    for r in rutasNuevas:
        cantidadClientes += len(r)

    swapsStr = [solucionInicial] + swapsStr
    swapsStr.append("NS")
    solucionDB = []
    while len(rutasNuevas) != 0:
        C = []
        for j in range(k):
            C.append(costosRuta.pop(0))
        origen = swapsStr.pop(0)
        s = (
            costosRutas.pop(0),
            json.dumps(rutasNuevas.pop(0)),
            json.dumps(origen),
            iteraciones.pop(0),
            json.dumps(C)
        )
        if  origen == "peor" or origen == "penúltimo":
            continue
        else:
            solucionDB.append(s)

    tenureADD = int(cantidadClientes * 0.05)
    tenureDROP = int(cantidadClientes * 0.05) +1
    resolucion = (cantidadIteraciones,
                  solucionDB[-1][0],
                  tenureADD,
                  tenureDROP,
                  desvio,
                  tiempoTotal,
                  json.dumps(swaps),
                  solucionInicial,
                  1
                  )

    conn = DB.DB()
    idRes = DB.insert_resolucion(conn, resolucion)
    for x in solucionDB:
        idSol = DB.insert_solucion(conn, x)
        DB.insert_solucionXResolucion(conn, (idRes, idSol))
 
    #print("Resolucion: \n", resolucion)
    #[print("Soluciones: \n ", x) for x in solucionDB]
    #print("k: ", k)
    #print("n: ", n)
    #print("costos ruta: ",len(costosRuta))
    #print("costos rutas: ",len(costosRutas))
    #print("iteraciones: ", len(iteraciones))
    #print("movimientos ",len(swapsStr))
    #print("rutas", len(rutasNuevas))

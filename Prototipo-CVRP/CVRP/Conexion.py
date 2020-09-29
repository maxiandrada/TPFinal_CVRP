from flask import Flask, request,jsonify,make_response,json
from flask_restful import Resource, Api
from flask_cors import CORS
from CVRP import CVRP
import requests
from Solucion import Solucion
app = Flask(__name__)
api = Api(app)
CORS(app)
matrices = {}

@app.route("/get/<matriz_id>")
def get(matriz_id):
    print("recibió", matriz_id)
    return matriz_id


@app.route('/post', methods = ['POST'])
def post():   
    nroVehiculos = json.loads(request.form['nroVehiculos'])
    demandas = json.loads(request.form['demandas'])
    capacidadMax = json.loads(request.form['capacidadMax'])
    puntos = json.loads(request.form['data'])
    puntos = convertirPuntos(puntos)
    matrizDistancias = calcularMatrizDistancias(puntos)
    demandas = [int(d) for d in demandas]
    matrizSimetrica(matrizDistancias)
    print(matrizDistancias)
    cvrp = CVRP(matrizDistancias,demandas,nroVehiculos,capacidadMax,0,3,4,0.05)
    rutas, costoAsociado = cvrp.tabuSearch()
    resp = json.dumps({
        "rutas":rutas,
        "costoAsociado":json.dumps(costoAsociado),
        })
    return resp

@app.route('/md', methods = ['POST'])
def getMatrizDistancias():
    puntos = json.loads(request.form['puntos'])
    puntos = convertirPuntos(puntos)
    matriz = calcularMatrizDistancias(puntos)

    print("MATRIZ: "+ str(matriz))
    return json.dumps({"matriz":matriz})


@app.route('/md2', methods = ['POST'])
def getMatrizDistancias2():
    puntos = json.loads(request.form['puntos'])
    puntos = convertirPuntos(puntos)
    matriz = calcularMatrizDistancias2(puntos)

    print("MATRIZ: "+ str(matriz))
    return json.dumps({"matriz":matriz})

def convertirPuntos(P):
    coordenadas = []
    print(P)
    for p in P:
        nodo = p.get("nodo")
        coord = p.get("coordenadas")
        coordenadas.append([nodo,coord.get("lat"),coord.get("lng")])
    return coordenadas

def calcularMatrizDistancias(C):
    M = []
    for x in range(len(C)):
        fila = []
        for y in range(len(C)):
            url = f"http://router.project-osrm.org/route/v1/driving/{C[x][2]},{C[x][1]};{C[y][2]},{C[y][1]}?overview=false&hints=;"
            req =requests.get(url)
            jsonReq = req.json()
            dist = jsonReq["routes"][0]["distance"]
            if(dist==0):
                fila.append(float("inf"))
            else:
                fila.append(dist)
        M.append(fila)
    print(M)
    return M

def calcularMatrizDistancias2(C):
    M = []
    for x in range(len(C)):
        fila = []
        for y in range(len(C)):
            url = f"http://router.project-osrm.org/route/v1/driving/{C[x][2]},{C[x][1]};{C[y][2]},{C[y][1]}?overview=false&hints=;"
            req =requests.get(url)
            jsonReq = req.json()
            dist = jsonReq["routes"][0]["distance"]
            if(dist==0):
                fila.append("inf")
            else:
                fila.append(dist)
        M.append(fila)

    M = matrizSimetrica(M)
    return M




def matrizSimetrica(M):
    for x in range(len(M)):
        for y in range(x+1,len(M)):
            if(M[x][y]>M[y][x]):
                M[y][x]=M[x][y]
            elif(M[x][y]<M[y][x]):
                M[x][y]=M[y][x]
    return M

if __name__ == '__main__':
    app.run(debug=True)
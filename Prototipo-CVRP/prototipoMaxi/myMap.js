const tilesProvider = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const coordSalta = [-24.7892, -65.4106]
let direcciones = []

var map = L.map('map').setView(coordSalta, 14)

L.tileLayer(tilesProvider, {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    maxZoom: 18
    //id: 'mapbox/streets-v11',
    //tileSize: 512,
    //zoomOffset: -1,
    //accessToken: 'your.mapbox.access.token'
}).addTo(map);

let iconMarker = L.icon({
    iconUrl: 'iconos/marker.png',
    iconSize: [110, 70],
    iconArchor: [55, 70]
})

let marker = L.marker(coordSalta).addTo(map)
marker.bindPopup("Deposito").openPopup();

map.doubleClickZoom.disable()
map.on('dblclick', e => {
    let latLng = map.mouseEventToLatLng(e.originalEvent)
    //console.log(latLng)
    L.marker([latLng.lat, latLng.lng], {icon: iconMarker}).addTo(map)
})

var searchControl = L.esri.Geocoding.geosearch().addTo(map);
var avdaSanMartin = ["San Martín, Salta, A4400, Salta, ARG"]
var results = L.layerGroup().addTo(map)

searchControl.on('results', function controlBusq(data){ controlBusqueda(data)})

function controlBusqueda(data){
    //results.clearLayers();
    map.setView(coordSalta, 14);
    console.log(data.text);
    console.log(data);
    console.log(results);
    scrollWheelZoom: false
    for(var i = data.results.length -1; i >= 0; i--){
        map.setView(coordSalta, 14);
        var LatLong = data.results[i].latlng
        
        results.addLayer(L.marker(LatLong, {icon: iconMarker}))
        map.setView(coordSalta, 14);
        //L.marker(LatLong, {icon: iconMarker}).addTo(map)
        console.log(LatLong.lat);
        console.log(LatLong.lng);
    }
}

var url = "Direcciones.xlsx";
var oReq = new XMLHttpRequest();
oReq.open("GET", url, true);
oReq.responseType = "arraybuffer";


var valores = null
var latLng
oReq.onload = function(e) {
    var valores = leerDatos();

    function leerDatos(){
        var arraybuffer = oReq.response;
    
        // Convertimos los datos a string
        var datos = new Uint8Array(arraybuffer);
        var arrayAux = new Array();
        for(var i = 0; i != datos.length; ++i) arrayAux[i] = String.fromCharCode(datos[i]);
        var bstr = arrayAux.join("");
    
        // Leemos el archivo .xlsx
        var workbook = XLSX.read(bstr, {type:"binary"});
    
        //Leemos los nombres de los atributos
        var first_sheet_name = workbook.SheetNames[0];
        //La primera hoja de trabajo
        var worksheet = workbook.Sheets[first_sheet_name];
        valores = XLSX.utils.sheet_to_json(worksheet,{raw:true});
        return valores;
    }

    for(var i=0; i<valores.length; i++){
        console.log("Cliente "+i+"- Direccion: "+valores[i].Direccion);
        direcciones.push(buscarDireccion(i+1,valores[i].Direccion, valores[i].Ciudad, valores[i].Provincia))
        //console.log("Length: "+direcciones.length+"     i: "+i)
        // if(direcciones.length-1 == i){
        //     console.log("Length en if: "+direcciones.length+"     i: "+i)
        //     console.log("Direcciones -> ")
        //     console.log(direcciones)
        //     L.marker(direcciones[i]).addTo(map)
        // }
    }
}
oReq.send();

function buscarDireccion(clienteId, Direccion, Ciudad, Provincia){
    salta = L.latLng(coordSalta[0],coordSalta[1])
    //var direccionSeparada = direccion.split(",")
    //console.log(direccionSeparada)
    //resultadoLatLng = null
    var calle = Direccion.split(" ")
    if(calle[0].toLowerCase() == "hernando"){
        calle[0] = "hijo"
    }
    Direccion = calle.join(' ')

    L.esri.Geocoding.geocode().address(Direccion).city(Ciudad).region(Provincia).run(function (err, resultados, response) {
    //resultados = L.esri.Geocoding.geocode().text(Direccion).nearby(salta, 500).run(function (err, resultados, response) {
        if (err) {
          console.log(err);
          return;
        }
        console.log("resultados: "+resultados.results[0].text+"     direccion: "+Direccion)
        console.log(resultados.results[0].latlng)
        console.log(resultados)
        
        coordenadas = [resultados.results[0].latlng.lat, resultados.results[0].latlng.lng]
        var markerCliente = L.marker(coordenadas).addTo(map)
        markerCliente.bindPopup("Cliente "+(clienteId)).openPopup();
    })
    //console.log(resultados)
}

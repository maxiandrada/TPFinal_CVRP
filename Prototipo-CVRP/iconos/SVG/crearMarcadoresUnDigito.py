f = open("pinUnDigito.svg","r")
lineas = f.readlines()
linea = lineas[114]

mitad1 = lineas[114][:26]
mitad2 = lineas[114][27:]
for i in range(10):
    lineas[114] = mitad1 + str(i) + mitad2
    nuevo = open("pin"+str(i)+".svg","w")
    nuevo.writelines(lineas)
    nuevo.close()
f.close()


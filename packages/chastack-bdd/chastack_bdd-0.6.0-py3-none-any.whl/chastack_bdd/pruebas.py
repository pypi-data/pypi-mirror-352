import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chastack_bdd.tipos import *
from chastack_bdd.utiles import *
from chastack_bdd.bdd import ConfigMySQL, BaseDeDatos_MySQL, ProtocoloBaseDeDatos
from chastack_bdd.tabla import Tabla  

from chastack_bdd.registro import Registro
from chastack_bdd.usuario import Usuario
from sobrecargar import sobrecargar
class Administrador(metaclass=Tabla):
    @sobrecargar
    def juan(x: int): ...

    @sobrecargar 
    def juan(x : str): ...

config = ConfigMySQL(
        "localhost", 
        "servidor_local", 
        "Servidor!1234", 
        "fundacionzaffaroni_ar_desarrollo",
    )
bdd = BaseDeDatos_MySQL(config)



dds = Administrador.devolverRegistros(bdd, cantidad = 25, orden ={"id" : TipoOrden.DESC})
for dd in dds:
    print(dd)
    print(dd.nombre_usuario)
    print(dd.__slots__)
    print(dd.tabla)

from datetime import datetime
u = datetime.now().microsecond
admin1 = Administrador(bdd, dict(nombre="Admin",nombre_usuario=f"admin{u}",contrasena="admin1234".encode('utf-8'), sal= "asdadas".encode('utf-8'),correo=f"admin{u}@fundacionzaffaroni.ar"))
#admin1.guardar()
print(Administrador)
print(admin1)


class Administrador(Usuario, metaclass=Tabla):...
    
j = Administrador.registrar(
    bdd,
    correo=f"juan@juan.juan{u}",
    contrasena="JuanJuan!1234",
    atributo_juan=7,
    nombre="juan"
)
print(Juan)
j.guardar()
#print(j)

j2 = Juan.ingresar(bdd,f"juan@juan.juan{u}","JuanJuan!1234")
print(j2)
#admin10 = Administrador(bdd=bdd,id=81)
#print(admin10)

from chastack_bdd.tipos import *
from chastack_bdd.utiles import *
from chastack_bdd.bdd import ProtocoloBaseDeDatos



class Registro: ...
class Registro:
    __slots__ = (
        '__bdd',
        '__tabla',
        '__id',
    )

    __bdd : ProtocoloBaseDeDatos
    __tabla : str
    __id : int

    
    def __new__(cls, bdd : ProtocoloBaseDeDatos, *posicionales,**nominales):
        obj = super(Registro, cls).__new__(cls)
        cls.__tabla = cls.__name__
        obj.__bdd = bdd
        for nombre_campo in ('tabla','id'):
            if not tieneAtributo(cls, nombre_campo):
                setattr(cls, nombre_campo, property(lambda cls, nombre_=nombre_campo: devolverAtributoPrivado(cls,nombre_)))
        return obj        

    @sobrecargar
    def __init__(self, bdd : ProtocoloBaseDeDatos, valores : dict, *, debug : bool =False):
        for atributo in self.__slots__:
            nombre = atributoPublico(atributo)
            valor_SQL : Any = valores.get(nombre,None)
            if valor_SQL is not None:
                valor = valor_SQL
                tipo_esperado : type =get_type_hints(self)[atributo]
                if isinstance(valor_SQL,tipo_esperado):
                    valor = valor_SQL
                elif esSubclaseUnion(tipo_esperado, Decimal):
                    valor : Decimal = Decimal(valor_SQL)
                elif esSubclaseUnion(tipo_esperado, dict):
                    valor : dict = loads(valor_SQL)
                elif esSubclaseUnion(tipo_esperado,bool):
                    valor : bool = bool(valor_SQL)
                elif esSubclaseUnion(tipo_esperado,EnumSQL):
                    valor : tipo_esperado = tipo_esperado.desdeCadena(valor_SQL)
                else:
                    valor = valor_SQL
                setattr(self, atributoPrivado(self,atributo) if '__' in atributo else atributo, valor)
            else:
                setattr(self, atributoPrivado(self,atributo) if '__' in atributo else atributo, devolverAtributo(self,atributo,None))
        self.__bdd = bdd
        self.__id = getattr(self,atributoPrivado(self,'id')) if hasattr(self,atributoPrivado(self,'id')) else valor.get('id',None)  


    @sobrecargar
    def __init__(self, bdd : ProtocoloBaseDeDatos, id : int, *, debug : bool =False):
        resultado : Resultado
        atributos : tuple[str] = (atributoPublico(atr) for atr in self.__slots__ if atr not in ('__bdd','__tabla'))
        
        with bdd as bdd:
            resultado = bdd\
                        .SELECT(self.__tabla,atributos)\
                        .WHERE(id=id)\
                        .ejecutar()\
                        .devolverUnResultado()

        self.__init__(
            bdd,
            resultado
        )
        self.__bdd = bdd
        self.__id = id

    def guardar(self) -> int:
        """Guarda el registro en la tabla correspondiente.
        Si tiene id, se edita un registro existente, 
        de lo contrario se agrega uno nuevo.   

        Devuelve:
        :arg Id int:
            El Id del registro.           

        Levanta:  
        :arg Exception: Propaga errores de la conexión con la BDD  
        :arg Exception: Levanta error si al editar la base con coinciden los id
        """
        match self.__id:
            case None:
                self.__id = self.__crear()
            case _: 
                self.__editar()

        return devolverAtributoPrivado(self,'id')
    

    def __crear(self) -> int: 
        """Crea un nuevo registro en la tabla correspondiente""" 

        atributos : tuple[str] = (atr for atr in self.__slots__ if '__' not in atr)
        ediciones : dict[str,Any] = {
            atributo : getattr(self,atributo)
            for atributo in atributos
        }

        with self.__bdd as bdd:
            id : int = bdd\
                        .INSERT(self.tabla,**ediciones)\
                        .ejecutar()\
                        .devolverIdUltimaInsercion()
            self.__id = id
            self.__fecha_carga = datetime.now()
            self.__fecha_modificacion = datetime.now()

        return devolverAtributoPrivado(self,'id')
    
    def __editar(self) -> None: 
        """
        Edita un registro ya existente, dado por el ID, en la tabla correspondiente.
        """


        atributos : tuple[str] = (atr for atr in self.__slots__ if '__' not in atr)
        ediciones : dict[str,Any] = {
            atributo : getattr(self,atributo)
            for atributo in atributos
        }

        with self.__bdd as bdd:
            bdd\
                .UPDATE(self.tabla,**ediciones)\
                .WHERE(id=devolverAtributoPrivado(self,'id'))\
                .ejecutar()

    @classmethod
    def devolverRegistros(
        cls,
        bdd : ProtocoloBaseDeDatos,
        *,
        cantidad : Optional[int] = 1000,
        indice : Optional[int] = 0,
        orden : Optional[[dict[str, TipoOrden]]] = {"id":TipoOrden.ASC},
        filtrosJoin : dict[str,str] = None,
        **condiciones) -> tuple[Registro]:
        devolverAtributoPrivado(cls,'__inicializar')(bdd) # HACER: (Herni) Generalizar a todos los @classmethods
        resultados : tuple[Resultado]
        atributos : tuple[str] = (atributoPublico(atr) for atr in cls.__slots__ if atr not in ('__bdd','__tabla'))
        
        desplazamiento = indice*cantidad 

        bdd\
        .SELECT(cls.__name__, atributos)\
        .WHERE(TipoCondicion.IGUAL,**condiciones)\
        .ORDER_BY(orden)\
        .LIMIT(desplazamiento,cantidad)

        with bdd as bdd:
            resultados = bdd\
                        .ejecutar()\
                        .devolverResultados()
        registros = []
        if resultados:
            for resultado in resultados:
                registros.append(cls(bdd, resultado))

        return tuple(registros)

    def __cmp__(self, otro : Registro) -> int:  
        if not isinstance(otro, type(self)): raise TypeError(f"Se esperaba {type(self)}, se obtuvo {type(otro)}")
        if self.id == otro.id: return 0;
        if self.fecha_carga > otro.fecha_carga: return 1;
        return -1

    def __add__(self, otro : Registro) -> tuple[Registro]: 
        if not isinstance(otro, type(self)): raise TypeError(f"Se esperaba {type(self)}, se obtuvo {type(otro)}")
        return (self, otro)

    def __repr__(self) -> str:
        return f"<Registro {self.__tabla}> en {id(self)}." 

    def __str__(self) -> str:
        filas = tuple(self.__iter__())      
        if not filas:
            return f"<Registro {self.__tabla}> (vacío)"
        ll_max, v_max = max([len(str(ll)) for ll, _ in filas] + [len("fecha_modificacion"), len(f"{self.__tabla} #{self.__id}" )]), max([len(str(v)) for _, v in filas] + [len("0000-00-00 00:00:00")])
        tabla_str = f"┌{'─' * (ll_max + 2)}┐\n" \
                    + f"│ {self.__tabla:<{ll_max - len(str(self.__id)) - 2}} #{self.__id} │ Registro\n" \
                    + f"├{'─' * (ll_max + 2)}┼{'─' * (v_max + 2)}┐\n" \
                    + f"│ {"fecha_carga":<{ll_max}} │ {str(self.fecha_carga):<{v_max}} │\n"  \
                    + f"│ {"fecha_modificacion":<{ll_max}} │ {str(self.fecha_modificacion):<{v_max}} │\n"  \
                    + f"├{'─' * (ll_max + 2)}┼{'─' * (v_max + 2)}┤\n" \
                    + "\n".join(f"│ {str(ll):<{ll_max}} │ {str(v):<{v_max}} │" for ll, v in filas) \
                    + f"\n└{'─' * (ll_max + 2)}┴{'─' * (v_max + 2)}┘" \
                    + "\n"
        return tabla_str.rstrip()

    def __iter__(self):
        return iter({
            atributo : devolverAtributo(self,atributo)
                for atributo in (
                    atr for atr in self.__slots__ if '__' not in atr
                )
        }.items())
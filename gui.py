import tkinter as tk
import funciones as fun
import pandas as pd
import sqlite3 as sql
from tkinter import ttk
from tkinter import messagebox
import datetime as dt
from datetime import datetime
from random import randint

class RegistroMovimientos:
    
    def __init__(self, tipo, ID_movimiento, fecha, suc_origen, suc_destino):
        self.root = tk.Tk()
        
        self.lbl_movimiento = tk.Label(self.root, text = 'Movimientos', font=('Arial',14, 'bold'))
        self.lbl_movimiento.grid(row = 1, column = 4, columnspan = 3, padx = 7, pady= 7)
        self.lbl_buscarproducto = tk.Label(self.root, text = 'Producto', font=('Arial',9))
        self.lbl_buscarproducto.grid(row = 2, column = 4, padx = 5, pady= 5)
        self.cbb_producto = ttk.Combobox(self.root, text='Teclea aqui para buscar un producto', font=('Arial', 9))
        self.cbb_producto.grid(row = 2, column = 5, columnspan= 2, padx = 5, pady = 5)

        self.lbl_cantidad = tk.Label(self.root, text = 'Cantidad', font=('Arial',9))
        self.lbl_cantidad.grid(row = 3, column = 4, padx = 5, pady= 5)
        self.ent_cantidad = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_cantidad.grid(row = 3, column = 5, columnspan=2, padx = 5, pady= 5)

        self.btn_anadir_registro = tk.Button(self.root, text = 'Añadir Registro', font=('Arial',11), command = lambda: self.anadir_registro(ID_movimiento))
        self.btn_anadir_registro.grid(row = 4, column=5, columnspan = 2, padx=10, pady=10)
        self.btn_anadir_registro.config(bg="#ED7F28", fg = "white")
        self.btn_insertar_registro = tk.Button(self.root, text="Insertar Registro", font=("Arial", 11, 'bold'), command = lambda: self.insertar_registro(tipo, df_movimientos=self.df_movimientos, fecha=fecha, ID_movimiento=ID_movimiento, suc_origen=suc_origen, suc_destino=suc_destino))
        self.btn_insertar_registro.config(bg="#ED7F28", fg = "white")

        df_productos = fun.obtener_productos()

        self.cbb_producto.bind("<ButtonPress-1>", lambda event: fun.buscar_productos(event, df_productos, self.cbb_producto))
        self.btn_anadir_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_anadir_registro))
        self.btn_anadir_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_anadir_registro))
        self.btn_insertar_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_insertar_registro))
        self.btn_insertar_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_insertar_registro))
        
    def inciar(self):
        self.root.mainloop()
        
    def tabla_movimientos(self,df): # Regresa un objeto de Tkinter
        self.tree = tk.ttk.Treeview(self.root, columns=('ID_movimiento', 'ID_producto', 'Nombre', 'Cantidad'))

        # Configurar las columnas del Treeview
        self.tree.column("#0", width = 20)
        self.tree.heading("#1", text="ID_Movimiento")
        self.tree.column('#1', width=120)
        self.tree.heading("#2", text="ID_Producto")
        self.tree.column('#2', width=100)
        self.tree.heading("#3", text="Nombre")
        self.tree.column('#3', width=100)
        self.tree.heading("#4", text="Cantidad")
        self.tree.column('#4', width=100)
        
        for row in df.values:
            self.tree.insert("", tk.END, values=row)
            
        self.tree.grid(row = 6, column=5, padx=5, pady=5)

    def vali_producto(self):
        prod = self.cbb_producto.get().split()
        if prod[0].isnumeric():
            id = int(prod[0])
            prod.insert(0,id)
            prod.pop(1)
            
            productos = [list(elem) for elem in self.cbb_producto['values']]
        
            print(prod)
            print(productos)
        
            if prod in productos:
                return True
            else:
                messagebox.showerror('Producto No Válido', "Selecciona una opción de la lista desplegable")
                return False
        else:
            messagebox.showerror('Producto No Válido', "Selecciona una opción de la lista desplegable")
            return False

    def anadir_registro(self,ID_movimiento = None): # , fecha, suc_origen, suc_destino = None para insertar registro
        
        if hasattr(self, "df_movimientos") == False:
            self.df_movimientos = pd.DataFrame(columns = ['ID_movimiento', 'ID_producto', 'Nombre', 'Cantidad'])
            print('DataFrame creado')
            
        vali_prod = self.vali_producto()
        cantidad = self.ent_cantidad.get().strip()
        
        if cantidad.isnumeric() and vali_prod:
            
            id_producto = int(self.cbb_producto.get().split()[0])
            nombre_producto = str(self.cbb_producto.get().split()[1])
            cantidad = int(cantidad)
            
            row_nuevo = {'ID_movimiento': ID_movimiento,
                        'ID_producto': id_producto, 
                        'Nombre': nombre_producto, 
                        'Cantidad': cantidad}
            
            self.df_movimientos = pd.concat([self.df_movimientos, pd.DataFrame([row_nuevo])], ignore_index= True)
            self.tabla_movimientos(self.df_movimientos)
            self.ent_cantidad.delete(0, tk.END)
            
            self.cbb_producto.set("")
            self.btn_insertar_registro.grid(row = 7, column =6, columnspan = 2, padx = 5, pady = 5)

        elif cantidad.isnumeric() == False:
            messagebox.showerror('Cantidad no es Numérica', "Ingresa un número en cantidad")
        else:
            pass
            
    def insertar_registro(self,tipo,df_movimientos, fecha, ID_movimiento,suc_origen, suc_destino = None): #Agregar tipo a los argumentos de la función
        conn = fun.conectar_db()
        lista = df_movimientos.values.tolist()
        
        if tipo == "Traspaso":
            for rows in lista :
                id_prod = rows[1]
                cantidad = rows[3]
                insert_suc_origen = 'INSERT INTO Movimientos (Fecha, ID_Traspaso, ID_Produccion, ID_Salida, ID_Sucursal, ID_Producto, Cantidad) VALUES (?,?,NULL,NULL,?,?,?)'
                values_origen = (fecha, ID_movimiento, suc_origen, id_prod, -cantidad )
                insert_suc_destino = 'INSERT INTO Movimientos (Fecha, ID_Traspaso, ID_Produccion, ID_Salida, ID_Sucursal, ID_Producto, Cantidad) VALUES (?,?,NULL,NULL,?,?,?)'
                values_destino = (fecha, ID_movimiento, suc_destino, id_prod, cantidad )
                
                conn.execute(insert_suc_destino, values_destino)
                conn.execute(insert_suc_origen, values_origen)
                
            messagebox.showinfo('Consulta Exitosa!', "Los registros han sido insertados a la base de datos correctamente")
            conn.commit()
            conn.close()
        elif tipo=='Produccion':

            for rows in lista :
                id_prod = rows[1]
                cantidad = rows[3]
                insert_suc_origen = 'INSERT INTO Movimientos (Fecha, ID_Traspaso, ID_Produccion, ID_Salida, ID_Sucursal, ID_Producto, Cantidad) VALUES (?,NULL,?,NULL,?,?,?)'
                values_origen = (fecha, ID_movimiento, suc_origen, id_prod, cantidad )
                conn.execute(insert_suc_origen, values_origen)
    
        else:
            for rows in lista :
                id_prod = rows[1]
                cantidad = rows[3]
                insert_suc_origen = 'INSERT INTO Movimientos (Fecha, ID_Traspaso, ID_Produccion, ID_Salida, ID_Sucursal, ID_Producto, Cantidad) VALUES (?,NULL,NULL,?,?,?,?)'
                values_origen = (fecha, ID_movimiento, suc_origen, id_prod, -cantidad )
                conn.execute(insert_suc_origen, values_origen)
                
        messagebox.showinfo('Consulta Exitosa!', "Los registros han sido insertados a la base de datos correctamente")
        conn.commit()
        conn.close()



class RegistroOrdenes:
        
    def __init__(self, tipo):
        self.root = tk.Tk()

        self.titulo = f"Registro de {tipo}"
        self.lbl_titulo = tk.Label(self.root, text= self.titulo, font=("Arial", 16, "bold"))
        self.lbl_titulo.grid(row=0, column=0, columnspan=8, padx=10, pady=10)
        self.lbl_titulo.config(bg="#ED7F28", fg = "white")
        
        self.lbl_fecha1 = tk.Label(self.root, text="Fecha", font=("Arial", 11))
        self.lbl_fecha1.grid(row=1, column=0, columnspan=3, padx=7, pady=7)
        self.lbl_fecha2 = tk.Label(self.root, text="Día", font=("Arial", 9))
        self.lbl_fecha2.grid(row=2, column=0, padx=5, pady=5)
        self.lbl_fecha3 = tk.Label(self.root, text="Mes", font=("Arial", 9))
        self.lbl_fecha3.grid(row=2, column=1, padx=5, pady=5)
        self.lbl_fecha4 = tk.Label(self.root, text="Año", font=("Arial", 9))
        self.lbl_fecha4.grid(row=2, column=2, padx=5, pady=5)

        self.ent_dia = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_dia.grid(row = 3, column=0)
        self.ent_mes = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_mes.grid(row = 3, column=1)
        self.ent_an = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_an.grid(row = 3, column=2)

        if tipo != 'Traspaso':
            
            self.lbl_suc1 = tk.Label(self.root, text="Sucursal", font=("Arial", 11))
            self.lbl_suc1.grid(row = 5, column =0, padx = 7, pady = 7)
            self.cbb_suc_origen = ttk.Combobox(self.root, state="readonly")
            self.cbb_suc_origen.grid(row = 5, column = 1, columnspan = 2, padx = 7, pady = 7)
            self.cbb_suc_origen['values'] = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist()
            
            if tipo == 'Salida':
                self.lbl_cliente = tk.Label(text= 'Cliente', font=('Arial', 11))
                self.lbl_cliente.grid(row = 7, column = 0, padx = 7, pady = 7)
                self.cbb_cliente = ttk.Combobox(self.root, state="readonly", values= fun.obtener_clientes()[['ID_Cliente','Nombre','Localidad']].values.tolist())
                self.cbb_cliente.grid(row = 7, column = 1, columnspan = 2,  padx = 7, pady = 7)
            
        elif tipo == 'Traspaso':
            self.lbl_suc1 = tk.Label(self.root, text="Sucursal", font=("Arial", 11, 'bold'))
            self.lbl_suc1.grid(row = 5, column =0,columnspan=3, padx = 7, pady = 7)
            self.lbl_suc2 = tk.Label(self.root, text = "Origen", font = ("Arial", 11))
            self.lbl_suc2.grid(row = 6, column = 0, padx = 5, pady = 5)
            self.lbl_suc3 = tk.Label(self.root, text = "Destino", font = ("Arial", 11))
            self.lbl_suc3.grid(row = 7, column = 0, padx = 5, pady = 5)

            self.cbb_suc_destino = ttk.Combobox(self.root, state="readonly")
            self.cbb_suc_destino.grid(row = 7, column = 1, columnspan = 2, padx = 7, pady = 7)
            self.cbb_suc_origen = ttk.Combobox(self.root, state="readonly")
            self.cbb_suc_origen.grid(row = 6, column = 1, columnspan = 2, padx = 7, pady = 7)
            
            self.cbb_suc_origen['values'] = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist()
            self.cbb_suc_destino['values'] = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist() 
        
        else:
            pass 
        
        if tipo == 'Traspaso' or tipo == 'Salida':
            self.lbl_atiempo = tk.Label(self.root,text = 'A Tiempo', font=('Arial', 11) )
            self.lbl_atiempo.grid(row=8, column=0, columnspan=2, padx=7, pady=7)
            self.var_cbx_atiempo = tk.BooleanVar(value = False)
            self.cbx_atiempo = ttk.Checkbutton(self.root, variable = self.var_cbx_atiempo)
            self.cbx_atiempo.grid(row = 8, column = 2, padx=7, pady=7)

            self.lbl_completo = tk.Label(self.root,text = 'Completo', font=('Arial', 11) )
            self.lbl_completo.grid(row=9, column=0, columnspan=2, padx=7, pady=7)
            self.var_cbx_completo = tk.BooleanVar(value = False)
            self.cbx_completo = ttk.Checkbutton(self.root, variable = self.var_cbx_completo)
            self.cbx_completo.grid(row = 9, column = 2, padx=7, pady=7)

            if tipo == 'Traspaso':
                self.lbl_chofer = tk.Label(self.root,text = 'Chofer', font=('Arial', 11))
                self.lbl_chofer.grid(row = 10, column = 0, padx = 7, pady = 10)
                self.cbb_chofer = ttk.Combobox(self.root, values = fun.obtener_empleados()[['ID_Chofer','Nombre']].values.tolist(), state="readonly")
                self.cbb_chofer.grid(row = 10, column = 1, columnspan = 2, padx =7, pady =7)
                
        else:
            pass
        
        self.btn_crear_registro = tk.Button(self.root, text = "Crear Registro", command= lambda: self.crear_registro(tipo))
        self.btn_crear_registro.grid(row = 11, column = 1, columnspan= 2, padx = 10, pady = 10)
        self.btn_crear_registro.config(bg="#ED7F28", fg = "white")
        
        self.btn_crear_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_crear_registro))
        self.btn_crear_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_crear_registro))
    
    def vali_cbb(self,tipo):
        if tipo == 'Traspaso':
            if self.cbb_chofer.get() != "" and self.cbb_suc_origen.get() != "" and self.cbb_suc_destino.get() != "":
                return True
            else:
                messagebox.showinfo('Error en Datos',"No has seleccionado un campo para sucursal y/o chofer")
                return False
        elif tipo == 'Salida':
            if self.cbb_suc_origen.get() != "" and self.cbb_cliente.get() !=  "":
                return True
            else:
                messagebox.showinfo('Error en Datos',"No has seleccionado un campo para sucursal y/o chofer")
                return False
        elif tipo == 'Produccion':
            if self.cbb_suc_origen.get() != '':
                return True
            else:
                messagebox.showinfo('Error en Datos',"No has seleccionado un campo para sucursal")
                return False
            
    def crear_registro(self,tipo):
        
        dia = self.ent_dia.get().strip()
        mes = self.ent_mes.get().strip()
        an = self.ent_an.get().strip()
        
        vali_fecha = fun.validar_fecha(dia,mes,an)
        validacion_cbb = self.vali_cbb(tipo)
        
        if validacion_cbb and vali_fecha:
            fecha = an + "-" + mes + "-" + dia
            rand = str(randint(10,99))
            print('Primera Validacion')
            
            if tipo == 'Traspaso':
                ID_movimiento = int('101'+an+mes+dia+(dt.datetime.now().strftime("%H%M%S"))+rand)
                suc_origen = self.cbb_suc_origen.get().split()[0]
                suc_destino = self.cbb_suc_destino.get().split()[0]
                id_empleado = self.cbb_chofer.get().split()[0]
                    
                if self.var_cbx_completo.get():
                    completo = 1
                else:
                    completo = 0
                if self.var_cbx_atiempo.get():
                    atiempo = 1
                else:
                    atiempo = 0
                
                fun.sql_crear_orden(tipo = tipo, ID_movimiento= ID_movimiento, fecha = fecha, suc_origen= suc_origen, suc_destino= suc_destino, ID_chofer= id_empleado, Completo=completo, Atiempo= atiempo)
                RegistroMovimientos(tipo, ID_movimiento=ID_movimiento, fecha=fecha, suc_origen=suc_origen, suc_destino=suc_destino).inciar() 
            
            elif tipo == 'Salida':
                ID_movimiento = int('303'+an+mes+dia+(dt.datetime.now().strftime("%H%M%S"))+rand)
                suc_origen = self.cbb_suc_origen.get().split()[0]
                cliente = self.cbb_cliente.get().split()[0]
                suc_destino = None
                
                if self.var_cbx_completo.get():
                    completo = 1
                else:
                    completo = 0
                if self.var_cbx_atiempo.get():
                    atiempo = 1
                else:
                    atiempo = 0
                    
                fun.sql_crear_orden(tipo = tipo, ID_movimiento= ID_movimiento, fecha = fecha, suc_origen= suc_origen, id_cliente=cliente, Completo=completo, Atiempo= atiempo)
                print('Hola')
                RegistroMovimientos(tipo, ID_movimiento=ID_movimiento, fecha=fecha, suc_origen=suc_origen, suc_destino= suc_destino).inciar() 
            
            elif tipo == 'Produccion':
                ID_movimiento = int('303'+an+mes+dia+(dt.datetime.now().strftime("%H%M%S"))+rand)
                suc_origen = self.cbb_suc_origen.get().split()[0]
                suc_destino = None
                    
                fun.sql_crear_orden(tipo = tipo, ID_movimiento= ID_movimiento, fecha = fecha, suc_origen= suc_origen) 
                RegistroMovimientos(tipo, ID_movimiento=ID_movimiento, fecha=fecha, suc_origen=suc_origen, suc_destino= suc_destino).inciar()    
                
    def iniciar (self):
        self.root.mainloop()



class BuscarRegistroOrden:
    def validar_fecha(self, mes, dia ,an):
        if an == "" and dia == "" and mes == "":
             return True
        elif an != "" and dia != "" and mes != "":
            
            if an.isnumeric() and dia.isnumeric() and mes.isnumeric():
                
                if len(an) == 4 and len(dia) == 2 and len(mes)==2 and int(mes) >= 1 and int(mes)<=12 and int(dia)>=1 and int(dia)<=31:
                    return "'"+an+'-'+mes+'-'+dia+"'"
                else:
                    messagebox.showwarning('Fecha incorrecta',"Asegúrate de ingresar una fecha válida en formato dd/mm/aaaa")
                    return False
            else:
                    messagebox.showwarning('Fecha incorrecta',"Parece que los datos que has ingresado no son numéricos, verifica que la fecha es correcta")
                    return False
        else:
            messagebox.showwarning('Fecha incompleta',"Asegúrate de llenar todos los campos de fechas, o dejarlos vacíos si no quieres considerarlos")
            return False
    
    def val_fechas(self, fecha_inicial, fecha_final):
        if isinstance(fecha_inicial, str) and isinstance(fecha_final, str):
            fecha_in = datetime.strptime(fecha_inicial[1:-1],'%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_final[1:-1],'%Y-%m-%d').date()
            
            if fecha_fin >= fecha_in:
                return True
            else:
                messagebox.showwarning("Fecha final incorrecta", "Asegúrate de que tu fecha final sea mayor o igual a la inicial")
                return False
        else:
            return False
            
    def cmd_fechas(self):
        if self.var_cbx_fecha.get():
            self.ent_an2.config(state = 'normal')
            self.ent_mes2.config(state = 'normal')
            self.ent_dia2.config(state = 'normal')
        else:
            self.ent_an2.config(state = 'disabled')
            self.ent_mes2.config(state = 'disabled')
            self.ent_dia2.config(state = 'disabled')
    
    def buscar_movimientos(self,tipo,movimiento, sucursal_origen= None, fecha_inicial = None, fecha_final = None):
                
        if tipo == 1:
            conn = fun.conectar_db()

            if movimiento == 'Traspaso':
                consulta = f"SELECT Movimientos.ID_Mov, Traspaso.ID_Traspaso, Traspaso.Fecha, Origen.Nombre As Sucursal_Origen, Destino.Nombre As Sucursal_Destino, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Traspaso JOIN Sucursales As Origen ON Origen.ID_Sucursal = Traspaso.Origen JOIN Sucursales As Destino ON Destino.ID_Sucursal = Traspaso.Destino JOIN Movimientos ON Movimientos.ID_Traspaso = Traspaso.ID_Traspaso WHERE Movimientos.Fecha = {fecha_inicial} AND Origen.ID_Sucursal = {sucursal_origen}"
                df = pd.read_sql_query(consulta, conn)
            elif movimiento == 'Salida':
                consulta = f"SELECT Movimientos.ID_Mov, Salidas.ID_Salida, Salidas.Fecha, Salidas.ID_Cliente, Sucursales.Nombre As Sucursal, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Salidas INNER JOIN Sucursales ON Sucursales.ID_Sucursal = Salidas.ID_Sucursal JOIN Movimientos ON Movimientos.ID_Salida = Salidas.ID_Salida WHERE Movimientos.Fecha = {fecha_inicial} AND Salidas.ID_Sucursal = {sucursal_origen}"
                df = pd.read_sql_query(consulta, conn)
            elif movimiento == 'Produccion':
                consulta = f"SELECT Movimientos.ID_Mov, Produccion.ID_Produccion, Produccion.Fecha, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Produccion INNER JOIN Movimientos ON Movimientos.ID_Produccion = Produccion.ID_Produccion WHERE Produccion.Fecha = {fecha_inicial}"
                df = pd.read_sql_query(consulta, conn)

            print(df)
            conn.close()

            return df
        
        # Por sucursal y tipo de movimiento
        elif tipo == 2:
            conn = fun.conectar_db()
            
            if movimiento == 'Traspaso':
                consulta = f"SELECT Movimientos.ID_Mov, Traspaso.ID_Traspaso, Traspaso.Fecha, Origen.Nombre As Sucursal_Origen, Destino.Nombre As Sucursal_Destino, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Traspaso INNER JOIN Sucursales As Origen ON Origen.ID_Sucursal = Traspaso.Origen JOIN Sucursales As Destino ON Destino.ID_Sucursal = Traspaso.Destino JOIN Movimientos ON Movimientos.ID_Traspaso = Traspaso.ID_Traspaso WHERE (date(Traspaso.Fecha) BETWEEN date({fecha_inicial}) AND date({fecha_final})) AND Origen.ID_Sucursal = {sucursal_origen}"
            elif movimiento == 'Salida':
                consulta = f"SELECT Movimientos.ID_Mov, Salidas.ID_Salida, Salidas.Fecha, Sucursales.Nombre As Sucursal, Salidas.ID_Cliente, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Salidas JOIN Sucursales ON Sucursales.ID_Sucursal = Salidas.ID_Sucursal JOIN Movimientos ON Movimientos.ID_Salida = Salidas.ID_Salida WHERE (date(Salidas.Fecha) BETWEEN date({fecha_inicial})AND date({fecha_final})) AND Sucursales.ID_Sucursal = {sucursal_origen}"
            elif movimiento == 'Produccion':
                consulta = f"SELECT Movimientos.ID_Mov, Produccion.ID_Produccion, Produccion.Fecha, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Produccion JOIN Movimientos ON Movimientos.ID_Produccion = Produccion.ID_Produccion WHERE (date(Produccion.Fecha) BETWEEN date({fecha_inicial}) AND date({fecha_final}))"
            
            df = pd.read_sql_query(consulta, conn)
            conn.close()
            return df
        
        elif tipo == 3:
            conn = fun.conectar_db()
            
            if movimiento == 'Traspaso':
                consulta = f"SELECT Movimientos.ID_Mov, Traspaso.ID_Traspaso, Traspaso.Fecha, Origen.Nombre As Sucursal_Origen, Destino.Nombre As Sucursal_Destino, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Traspaso INNER JOIN Sucursales As Origen ON Origen.ID_Sucursal = Traspaso.Origen JOIN Sucursales As Destino ON Destino.ID_Sucursal = Traspaso.Destino JOIN Movimientos ON Movimientos.ID_Traspaso = Traspaso.ID_Traspaso WHERE Movimientos.Fecha = {fecha_inicial}"
            elif movimiento == 'Salida':
                consulta = f"SELECT Movimientos.ID_Mov, Salidas.ID_Salida, Salidas.Fecha, Sucursales.Nombre As Sucursal, Salidas.ID_Cliente,Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Salidas INNER JOIN Sucursales ON Sucursales.ID_Sucursal = Salidas.ID_Sucursal JOIN Movimientos ON Movimientos.ID_Salida = Salidas.ID_Salida WHERE Movimientos.Fecha = {fecha_inicial}"
            elif movimiento == 'Produccion':
                consulta = f"SELECT Movimientos.ID_Mov, Produccion.ID_Produccion, Produccion.Fecha, Produccion.Planta, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Produccion JOIN Movimientos ON Movimientos.ID_Produccion = Produccion.ID_Produccion WHERE Produccion.Fecha = {fecha_inicial}"
            
            df = pd.read_sql_query(consulta, conn)
            conn.close()
            return df
        
        elif tipo == 4:
            conn = fun.conectar_db()
            if movimiento == 'Traspaso':
                consulta = f"SELECT Movimientos.ID_Mov, Traspaso.ID_Traspaso, Traspaso.Fecha, Origen.Nombre As Sucursal_Origen, Destino.Nombre As Sucursal_Destino, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Traspaso INNER JOIN Sucursales As Origen ON Origen.ID_Sucursal = Traspaso.Origen JOIN Sucursales As Destino ON Destino.ID_Sucursal = Traspaso.Destino JOIN Movimientos ON Movimientos.ID_Traspaso = Traspaso.ID_Traspaso WHERE (date(Traspaso.Fecha) BETWEEN date({fecha_inicial}) AND date({fecha_final}))"
            elif movimiento == 'Salida':
                consulta = f"SELECT Movimientos.ID_Mov, Salidas.ID_Salida, Salidas.Fecha, Sucursales.Nombre As Sucursal, Salidas.ID_Cliente, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Salidas JOIN Sucursales ON Sucursales.ID_Sucursal = Salidas.ID_Sucursal JOIN Movimientos ON Movimientos.ID_Salida = Salidas.ID_Salida WHERE (date(Salidas.Fecha) BETWEEN date({fecha_inicial}) AND date({fecha_final}))"
            elif movimiento == 'Produccion':
                consulta = f"SELECT Movimientos.ID_Mov, Produccion.ID_Produccion, Produccion.Fecha, Movimientos.ID_Producto As Producto, Movimientos.Cantidad FROM Produccion JOIN Movimientos ON Movimientos.ID_Produccion = Produccion.ID_Produccion WHERE (date(Produccion.Fecha) BETWEEN date({fecha_inicial}) AND date({fecha_final}))"
        
            df = pd.read_sql_query(consulta, conn)
            conn.close()
            return df
    
    def mostrar_tabla(self, df, tipo):
        conn =  fun.conectar_db()
        if tipo == 'Traspaso':
            id_traspaso = tuple(df["ID_Movimiento"])
            consulta = f"From"
            
        
        tree = tk.ttk.Treeview(self.root, columns=('ID_movimiento', 'Fecha', 'Sucursal'))
        # Configurar las columnas del Treeview
        tree.column("#0", width = 20)
        tree.heading("#1", text="ID_Movimiento")
        tree.column('#1', width=200)
        tree.heading("#2", text="Fecha")
        tree.column('#2', width=100)
        tree.heading("#3", text="Sucursal")
        tree.column('#3', width=100)
        
        for row in df.values:
            tree.insert("", tk.END, values=row)
            
        tree.grid(row = 1, column=4, padx=5, pady=5)
    
    def entre_fechas(self, fecha_in, fecha_fin):
        fecha_in = fecha_in.split("-")
        fecha_fin = fecha_fin.split("-")
        fecha_inicial = pd.Timestamp(int(fecha_in[0]), int(fecha_in[1]), int(fecha_in[2])).date()
        fecha_final = pd.Timestamp(int(fecha_fin[0]), int(fecha_fin[1]), int(fecha_fin[2])).date()
        
        fechas_generadas = pd.date_range(start=fecha_inicial, end=fecha_final, freq='1D')
        fechas = tuple(fechas_generadas.strftime('%Y-%m-%d'))
        
        return fechas
    
    def boton_buscar_movimientos(self):
        global df_movimientos
        global tree_ids
        
        fecha_in = self.validar_fecha(self.ent_mes.get(), self.ent_dia.get(), self.ent_an.get())
        fecha_fin = self.validar_fecha(self.ent_mes2.get(), self.ent_dia2.get(), self.ent_an2.get())
        val_fechas = self.val_fechas(fecha_in, fecha_fin)
        tipo_seleccionado = self.cbb_tipo.get()
        
        if fecha_in == True and fecha_fin == True: # Estas son consultas sin fechas
            # consulta por tipo
            # consulta por sucursal y tipo
            pass
        elif fecha_in != False and (fecha_fin == False or fecha_fin == True):
            
            # consulta por tipo y sucursal
            if self.cbb_sucursal.get() != "" and tipo_seleccionado != "":
                print('Consulta tipo 1')
                sucursal_seleccionada = self.cbb_sucursal.get()[0]
                df_movimientos = self.buscar_movimientos(tipo = 1, sucursal_origen= sucursal_seleccionada, movimiento = tipo_seleccionado, fecha_inicial= fecha_in)
                
                Modificar(tipo_seleccionado, df_movimientos).iniciar()
            
            #consulta por tipo    
            elif self.cbb_sucursal.get() == "" and tipo_seleccionado != "" : 
                
                print('Consulta tipo 3')
                df_movimientos = self.buscar_movimientos(tipo = 3, movimiento = tipo_seleccionado, fecha_inicial= fecha_in)
                
                Modificar(tipo_seleccionado, df_movimientos).iniciar()
        elif isinstance(fecha_in, str) and isinstance(fecha_fin, str):
            # consulta por tipo
            # consulta por sucursal y tipo
            pass
        else:
            messagebox.showerror("No es posible realizar una búsqueda", 'Debe completar, por lo menos, el tipo de movimiento para poder relizar una consulta')

   
    def __init__(self):
        
        self.root = tk.Tk()
        self.lbl_titulo = tk.Label(self.root, text = "Buscar Órdenes", font =('Arial', 16, 'bold'))
        self.lbl_titulo.grid(column = 0, row = 0, columnspan= 3, padx = 7, pady = 7)
        
        self.lbl_fecha1 = tk.Label(self.root, text="Fecha Inicial", font=("Arial", 11))
        self.lbl_fecha1.grid(row=1, column=0, columnspan=3, padx=7, pady=7)
        self.lbl_fecha2 = tk.Label(self.root, text="Día", font=("Arial", 9))
        self.lbl_fecha2.grid(row=2, column=0, padx=5, pady=5)
        self.lbl_fecha3 = tk.Label(self.root, text="Mes", font=("Arial", 9))
        self.lbl_fecha3.grid(row=2, column=1, padx=5, pady=5)
        self.lbl_fecha4 = tk.Label(self.root, text="Año", font=("Arial", 9))
        self.lbl_fecha4.grid(row=2, column=2, padx=5, pady=5)

        self.ent_dia = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_dia.grid(row = 3, column=0)
        self.ent_mes = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_mes.grid(row = 3, column=1)
        self.ent_an = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_an.grid(row = 3, column=2)
        
        # Restablecer lo de las fechas
        self.var_cbx_fecha = tk.BooleanVar()
        self.cbx_fecha = tk.Checkbutton(variable=self.var_cbx_fecha, command= self.cmd_fechas)
        self.cbx_fecha.grid(row = 3, column = 3, padx = 5, pady = 5)
        
        self.lbl_fecha5 = tk.Label(self.root, text="Fecha Final", font=("Arial", 11))
        self.lbl_fecha5.grid(row=4, column=0, columnspan=3, padx=7, pady=7)
        self.lbl_fecha6 = tk.Label(self.root, text="Día", font=("Arial", 9))
        self.lbl_fecha6.grid(row=5, column=0, padx=5, pady=5)
        self.lbl_fecha7 = tk.Label(self.root, text="Mes", font=("Arial", 9))
        self.lbl_fecha7.grid(row=5, column=1, padx=5, pady=5)
        self.lbl_fecha8 = tk.Label(self.root, text="Año", font=("Arial", 9))
        self.lbl_fecha8.grid(row=5, column=2, padx=5, pady=5)

        self.ent_dia2 = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_dia2.grid(row = 6, column=0)
        self.ent_mes2 = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_mes2.grid(row = 6, column=1)
        self.ent_an2 = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_an2.grid(row = 6, column=2)
        
        self.cmd_fechas()
        
        self.lbl_tipo = tk.Label(self.root, text = "Tipo", font = ('Arial',12))
        self.lbl_tipo.grid(row = 7, column=0, padx=5, pady=5)
        self.cbb_tipo = ttk.Combobox(self.root, state = "readonly", values = ['Traspaso','Salida','Produccion'])
        self.cbb_tipo.grid(row = 7, column=1, columnspan=2, padx=5, pady=5)
        
        self.lbl_sucursal = tk.Label(self.root, text = "Sucursal", font = ('Arial',12))
        self.lbl_sucursal.grid(row = 8, column=0, padx=5, pady=5)
        self.cbb_sucursal = ttk.Combobox(self.root, state = "readonly", values = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist())
        self.cbb_sucursal.grid(row = 8, column=1, columnspan=2, padx=5, pady=5)
        
        self.btn_prueba = tk.Button(self.root, text = 'Buscar Movimientos', command = self.boton_buscar_movimientos)
        self.btn_prueba.grid(row = 9, column = 0, columnspan=2, padx= 7, pady=7)
        

    def iniciar(self):
        self.root.mainloop()
 
 
              
class Modificar:
    
    def tree(self, tipo, df):

        if tipo == 'Traspaso':
            tree = ttk.Treeview(self.root, columns = ['ID_Movimiento','ID_Traspaso','Fecha','Origen','Destino','Producto','Cantidad'])
            
            tree.column("#0", width = 20)
            tree.heading("#1", text="ID_Movimiento")
            tree.column('#1', width=80)
            tree.heading("#2", text="ID_Traspaso")
            tree.column('#2', width=200)
            tree.heading("#3", text="Fecha")
            tree.column('#3', width=100)
            tree.heading("#4", text="Origen")
            tree.column('#4', width=100)
            tree.heading("#5", text="Destino")
            tree.column('#5', width=100)
            tree.heading("#6", text="Producto")
            tree.column('#6', width=80)
            tree.heading("#7", text="Cantidad")
            tree.column('#7', width=100)
            
            for index,row in df.iterrows():
                tree.insert('', 'end', values=row.tolist())
        
        if tipo == 'Salida':
            tree = ttk.Treeview(self.root, columns = ['ID_Movimiento','ID_Salida','Fecha','Sucursal','Cliente','Producto','Cantidad'])
            
            tree.column("#0", width = 20)
            tree.heading("#1", text="ID_Movimiento")
            tree.column('#1', width=80)
            tree.heading("#2", text="ID_Salida")
            tree.column('#2', width=200)
            tree.heading("#3", text="Fecha")
            tree.column('#3', width=100)
            tree.heading("#4", text="Sucursal")
            tree.column('#4', width=80)
            tree.heading("#5", text="Cliente")
            tree.column('#5', width=80)
            tree.heading("#6", text="Producto")
            tree.column('#6', width=80)
            tree.heading("#7", text="Cantidad")
            tree.column('#7', width=100)
            
            for index,row in df.iterrows():
                tree.insert('', 'end', values=row.tolist())
        
        if tipo == 'Produccion':
            tree = ttk.Treeview(self.root, columns = ['ID_Movimiento','ID_Produccion','Fecha','Planta','Producto','Cantidad'])
            
            tree.column("#0", width = 20)
            tree.heading("#1", text="ID_Movimiento")
            tree.column('#1', width=80)
            tree.heading("#2", text="ID_Produccion")
            tree.column('#2', width=200)
            tree.heading("#3", text="Fecha")
            tree.column('#3', width=100)
            tree.heading("#4", text="Planta")
            tree.column('#4', width=80)
            tree.heading("#5", text="Producto")
            tree.column('#5', width=80)
            tree.heading("#6", text="Cantidad")
            tree.column('#6', width=100)
            
            for index,row in df.iterrows():
                tree.insert('', 'end', values=row.tolist())
                
        tree.grid(row = 1, column=0, columnspan=4, padx=8, pady=8)
        self.btn_modificar_orden.grid(row = 2, column=0, padx=5, pady=5)
        self.btn_modificar_movimientos.grid(row = 2, column=2, padx=5, pady=5)
        return tree
     
    def obtener_ids(self,indice):
        seleccion = self.tabla.selection()
        ids = []

        if seleccion:
            for i in seleccion:
                id = int(self.tabla.item(i, 'values')[indice])
                ids.append(id)
                
        return ids
     
    def modificar_movimientos(self):
        
        ids = self.obtener_ids(0)
        
        if len(ids) > 1:
            ids = tuple(ids)
        else:
            ids = "("+str(ids[0])+")"
            
        id_mov = self.obtener_ids(1)
        
        if len(list(set(id_mov))) == 1:
            id_mov = id_mov[0]
            instancia = ModificarMovimiento(ids, id_mov, self.tipo)
            instancia.iniciar()
        else:
            messagebox.showwarning('Selección Incorrecta',"Asegúrate de solo seleccionar movimientos con el mismo ID_Movimiento")
        
    def modificar_orden(self):
        
        ids = self.obtener_ids(1)
        
        if len(list(set(ids))) == 1:
            id_movimiento = ids[0]
            ModificarOrden(self.tipo, id_movimiento).iniciar()
        else:
             messagebox.showwarning('Selección Incorrecta',"Asegúrate de solo seleccionar movimientos con el mismo ID_Movimiento")            
    
    def __init__(self, tipo, df):
        self.tipo = tipo
        self.root = tk.Tk()
        messagebox.showinfo("Para Modificar Órdenes o Movimientos","Selecciona las filas de las tablas que quieres modificar y después haz click sobre un botón, si haces delete sobre ellas eliminarás los registros.")
        self.lbl_titulo = tk.Label(self.root, text = "Detalles de los Movimientos", font =('Arial', 16, 'bold'))
        self.lbl_titulo.config(fg = 'green', bg='white')
        self.lbl_titulo.grid(row=0, column=0, columnspan=4, padx=7, pady=7)
        self.btn_modificar_orden = tk.Button(self.root, text = "Modificar Orden", command = self.modificar_orden)
        self.btn_modificar_orden.config(bg="#ED7F28", fg = "white")
        self.btn_modificar_movimientos = tk.Button(self.root, text = "Modificar Movimientos", command = self.modificar_movimientos)
        self.btn_modificar_movimientos.config(bg="#ED7F28", fg = "white")
        
        self.btn_modificar_orden.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_modificar_orden))
        self.btn_modificar_orden.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_modificar_orden))
        self.btn_modificar_movimientos.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_modificar_movimientos))
        self.btn_modificar_movimientos.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_modificar_movimientos))
        
        self.tabla = self.tree(tipo, df)
        
        
    def iniciar(self):
        self.root.mainloop()
        
    def iniciar(self):
        self.root.mainloop()
    
    def cerrar(self):
        self.root.destroy()
 
 
 
class ModificarOrden:
    def obtener_data(self):
        conn = fun.conectar_db()
        id = self.id_movimiento
        
        if self.tipo == 'Salida':
            consulta = f"SELECT * FROM Salidas WHERE ID_Salida = {id}"
        elif self.tipo == 'Traspaso':
            consulta = f"SELECT * FROM Traspaso WHERE ID_Traspaso = {id}"
        elif self.tipo == 'Produccion':
            consulta = f"SELECT * FROM Produccion WHERE ID_Produccion = {id}"
            
        df = pd.read_sql_query(consulta, conn)
        conn.close()
        
        return df    
    
    def definir_cliente(self):
        id = self.data.iloc[0,3]
        clientes = fun.obtener_clientes()
        
        for index, row in clientes.iterrows():
            if id == row['ID_Cliente']:
                return (row['Nombre'],row['Localidad'])
    
    def definir_cbx(self):
        
        if self.tipo == 'Salida':
            completo = self.data.iloc[0,4]
            atiempo = self.data.iloc[0,5]
        elif self.tipo == 'Traspaso':
            completo = self.data.iloc[0,5]
            atiempo = self.data.iloc[0,6]
        else:
            pass
        
        if completo == 0:
            self.var_cbx_completo.set(False)
        elif completo == 1:
            self.var_cbx_completo.set(True)
        else:
            pass
        
        if atiempo == 0:
            self.var_cbx_atiempo.set(False)
        elif atiempo == 1:
            self.var_cbx_atiempo.set(True)
    
    def definir_chofer(self):
        id = self.data.iloc[0,4]
        choferes = fun.obtener_empleados()
        print(id)
        
        for index, row in choferes.iterrows():
            print(row['ID_Chofer'])
            print(row['Nombre'])
            if id == row['ID_Chofer']:
                print('Hola')
                print(row['Nombre'])
                return (row['Nombre'].replace(' ','_'))
    
    def update_orden(self):
        conn = fun.conectar_db()
        if self.tipo == 'Traspaso':
            command = f"UPDATE Traspaso SET Fecha = {self.fecha}, Origen = {self.suc_origen}, Destino = {self.suc_destino}, ID_Chofer = {self.id_empleado}, Completo = {self.completo}, A_Tiempo = {self.atiempo} WHERE ID_Traspaso = {self.id}"
        elif self.tipo == 'Salida':
            command = f"UPDATE Salidas SET Fecha = {self.fecha}, ID_Sucursal = {self.suc_origen}, ID_Cliente = {self.cliente1}, Completo = {self.completo}, A_Tiempo = {self.atiempo} WHERE ID_Salida = {self.id}"
        elif self.tipo == 'Produccion':
            command = f"UPDATE Produccion SET Fecha = {self.fecha}, ID_Sucursal = {self.suc_origen} WHERE ID_Produccion = {self.id}"
        
        conn.execute(command)
        conn.commit()
        conn.close()
        messagebox.showinfo('Orden Modificada Exitosamente!', f"La orden {self.id} se ha modificado exitosamente")
    
    def modificar_registro(self):
        self.dia = self.ent_dia.get().strip()
        self.mes = self.ent_mes.get().strip()
        self.an = self.ent_an.get().strip()
        
        vali_fecha = fun.validar_fecha(self.dia,self.mes,self.an)
        validacion_cbb = RegistroOrdenes.vali_cbb(self,self.tipo)
        
        if validacion_cbb and vali_fecha:
            self.fecha = self.mes + "-" + self.dia + "-" + self.an
                       
            if self.tipo == 'Traspaso':
                self.suc_origen = self.cbb_suc_origen.get()[0]
                self.suc_destino = self.cbb_suc_destino.get()[0]
                self.id_empleado = self.cbb_chofer.get()[0]
                    
                if self.var_cbx_completo.get():
                    self.completo = 1
                else:
                    self.completo = 0
                if self.var_cbx_atiempo.get():
                    self.atiempo = 1
                else:
                    self.atiempo = 0
                
            elif self.tipo == 'Salida':

                self.suc_origen = self.cbb_suc_origen.get()[0]
                self.cliente1 = self.cbb_cliente.get()[0]
                self.suc_destino = None
                
                if self.var_cbx_completo.get():
                    self.completo = 1
                else:
                    self.completo = 0
                if self.var_cbx_atiempo.get():
                    self.atiempo = 1
                else:
                    self.atiempo = 0
            
            elif self.tipo == 'Produccion':
                
                self.suc_origen = self.cbb_suc_origen.get().split()[1]
                self.suc_destino = None
        
            self.update_orden()
    
    def eliminar_registro(self):
        
        respuesta = messagebox.askyesno("Seguro que deseas eliminar?", "Al eliminar esta orden también eliminarás todos sus movimientos asociados")
        
        if respuesta:
            conn = fun.conectar_db()
            ID_movimiento = "ID_" + self.tipo
            
            if self.tipo == 'Salida':
                tipo = self.tipo + 's'
            else:
                tipo = self.tipo
            
            consulta1 = f'DELETE FROM {tipo} WHERE {ID_movimiento} = {self.id_movimiento}' 
            consulta2 = f'DELETE FROM Movimientos WHERE {ID_movimiento} = {self.id_movimiento}'
            
            conn.execute(consulta2)
            conn.execute(consulta1)
            conn.commit()
            conn.close()
    
    def __init__(self,tipo, id_movimiento):
        self.root = tk.Tk()
        self.root.title("Modificar Órdenes")
        self.tipo = tipo
        self.id_movimiento = id_movimiento
        
        self.data = self.obtener_data()
        self.fecha_in = self.data.iloc[0,1].split('-')
        print(self.data)
        
        self.titulo = f"Modificar {tipo}"
        self.lbl_titulo = tk.Label(self.root, text= self.titulo, font=("Arial", 16, "bold"))
        self.lbl_titulo.grid(row=0, column=0, columnspan=8, padx=10, pady=10)
        self.lbl_titulo.config(bg="#ED7F28", fg = "white")
        
        self.lbl_fecha1 = tk.Label(self.root, text="Fecha", font=("Arial", 11))
        self.lbl_fecha1.grid(row=1, column=0, columnspan=3, padx=7, pady=7)
        self.lbl_fecha2 = tk.Label(self.root, text="Día", font=("Arial", 9))
        self.lbl_fecha2.grid(row=2, column=0, padx=5, pady=5)
        self.lbl_fecha3 = tk.Label(self.root, text="Mes", font=("Arial", 9))
        self.lbl_fecha3.grid(row=2, column=1, padx=5, pady=5)
        self.lbl_fecha4 = tk.Label(self.root, text="Año", font=("Arial", 9))
        self.lbl_fecha4.grid(row=2, column=2, padx=5, pady=5)

        self.var_dia = tk.StringVar(value=self.fecha_in[1])
        self.var_mes = tk.StringVar(value=self.fecha_in[0])
        self.var_an = tk.StringVar(value=self.fecha_in[2])
        
        self.ent_dia = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_dia.grid(row = 3, column=0)
        self.ent_dia.insert(0, self.fecha_in[2])
        self.ent_mes = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_mes.grid(row = 3, column=1)
        self.ent_mes.insert(0, self.fecha_in[1])
        self.ent_an = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_an.grid(row = 3, column=2)
        self.ent_an.insert(0, self.fecha_in[0])
        
        if tipo != 'Traspaso':
            
            self.lbl_suc1 = tk.Label(self.root, text="Sucursal", font=("Arial", 11))
            self.lbl_suc1.grid(row = 5, column =0, padx = 7, pady = 7)
            self.cbb_suc_origen = ttk.Combobox(self.root, state="readonly")
            self.cbb_suc_origen.grid(row = 5, column = 1, columnspan = 2, padx = 7, pady = 7)
            self.cbb_suc_origen['values'] = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist()
            
            self.cbb_suc_origen.set(fun.obtener_suc(self.tipo, self.data.iloc[0,2]))
            
            if tipo == 'Salida':
                self.lbl_cliente = tk.Label(text= 'Cliente', font=('Arial', 11))
                self.lbl_cliente.grid(row = 7, column = 0, padx = 7, pady = 7)
                self.cbb_cliente = ttk.Combobox(self.root, state="readonly", values= fun.obtener_clientes()[['ID_Cliente','Nombre','Localidad']].values.tolist())
                self.cbb_cliente.grid(row = 7, column = 1, columnspan = 2,  padx = 7, pady = 7)
                
                self.defcliente = self.definir_cliente()
                self.cliente = str(self.data.iloc[0,3]) +  ' ' + self.defcliente[0] + ' ' + self.defcliente[1]
                self.cbb_cliente.set(self.cliente)
            
        elif tipo == 'Traspaso':
            self.lbl_suc1 = tk.Label(self.root, text="Sucursal", font=("Arial", 11, 'bold'))
            self.lbl_suc1.grid(row = 5, column =0,columnspan=3, padx = 7, pady = 7)
            self.lbl_suc2 = tk.Label(self.root, text = "Origen", font = ("Arial", 11))
            self.lbl_suc2.grid(row = 6, column = 0, padx = 5, pady = 5)
            self.lbl_suc3 = tk.Label(self.root, text = "Destino", font = ("Arial", 11))
            self.lbl_suc3.grid(row = 7, column = 0, padx = 5, pady = 5)

            self.cbb_suc_destino = ttk.Combobox(self.root, state="readonly")
            self.cbb_suc_destino.grid(row = 7, column = 1, columnspan = 2, padx = 7, pady = 7)
            self.cbb_suc_origen = ttk.Combobox(self.root, state="readonly")
            self.cbb_suc_origen.grid(row = 6, column = 1, columnspan = 2, padx = 7, pady = 7)
            
            self.cbb_suc_origen['values'] = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist()
            self.cbb_suc_destino['values'] = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist() 
            self.cbb_suc_destino.set(fun.obtener_suc(self.tipo, self.data.iloc[0,3]))
            self.cbb_suc_origen.set(fun.obtener_suc(self.tipo, self.data.iloc[0,2]))
        
        else:
            pass 
        
        if tipo == 'Traspaso' or tipo == 'Salida':
            self.lbl_atiempo = tk.Label(self.root,text = 'A Tiempo', font=('Arial', 11) )
            self.lbl_atiempo.grid(row=8, column=0, columnspan=2, padx=7, pady=7)
            self.var_cbx_atiempo = tk.BooleanVar(value = False)
            self.cbx_atiempo = ttk.Checkbutton(self.root, variable = self.var_cbx_atiempo)
            self.cbx_atiempo.grid(row = 8, column = 2, padx=7, pady=7)

            self.lbl_completo = tk.Label(self.root,text = 'Completo', font=('Arial', 11) )
            self.lbl_completo.grid(row=9, column=0, columnspan=2, padx=7, pady=7)
            self.var_cbx_completo = tk.BooleanVar(value = False)
            self.cbx_completo = ttk.Checkbutton(self.root, variable = self.var_cbx_completo)
            self.cbx_completo.grid(row = 9, column = 2, padx=7, pady=7)
            self.definir_cbx()

            if tipo == 'Traspaso':
                self.lbl_chofer = tk.Label(self.root,text = 'Chofer', font=('Arial', 11))
                self.lbl_chofer.grid(row = 10, column = 0, padx = 7, pady = 10)
                self.cbb_chofer = ttk.Combobox(self.root, values = fun.obtener_empleados()[['ID_Chofer','Nombre']].values.tolist(), state="readonly")
                self.cbb_chofer.grid(row = 10, column = 1, columnspan = 2, padx =7, pady =7)
                self.nombrechofer = self.definir_chofer()
                print(self.nombrechofer)
                self.chofer = str(self.data.iloc[0,4]) + " " + self.nombrechofer
                
                self.cbb_chofer.set(self.chofer)
                
        else:
            pass
        
        self.btn_crear_registro = tk.Button(self.root, text = "Modificar Registro", command = self.modificar_registro)
        self.btn_crear_registro.grid(row = 11, column = 0, columnspan= 2, padx = 10, pady = 10)
        self.btn_crear_registro.config(bg="#ED7F28", fg = "white")
        
        self.btn_eliminar_registro = tk.Button(self.root, text = "Eliminar Registro", command = self.eliminar_registro)
        self.btn_eliminar_registro.grid(row = 11, column = 1, columnspan= 2, padx = 10, pady = 10)
        self.btn_eliminar_registro.config(bg="#ED7F28", fg = "white")
        
        self.btn_crear_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_crear_registro))
        self.btn_crear_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_crear_registro))
        self.btn_eliminar_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_eliminar_registro))
        self.btn_eliminar_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_eliminar_registro))
        
    def iniciar(self):
        self.root.mainloop()
 
 
 
class ModificarMovimiento:
    
    def obtener_movimientos (self):
        conn = fun.conectar_db()
        consulta = f"SELECT * FROM Movimientos WHERE ID_Mov in {self.ids}"
        
        df = pd.read_sql_query(consulta, conn)
        return df
    
    def vali_producto(self):
        prod = self.cbb_producto.get().split()
        if prod[0].isnumeric():
            id = int(prod[0])
            prod.insert(0,id)
            prod.pop(1)
            
            productos = [list(elem) for elem in self.cbb_producto['values']]
        
            print(prod)
            print(productos)
        
            if prod in productos:
                return True
            else:
                messagebox.showerror('Producto No Válido', "Selecciona una opción de la lista desplegable")
                return False
        else:
            messagebox.showerror('Producto No Válido', "Selecciona una opción de la lista desplegable")
            return False
    
    def actualizar_valores(self):
        self.contador = self.contador + 1
        self.ent_cantidad.delete(0, tk.END)
        self.definir_valores()
    
    def definir_valores(self):
        print(self.data)
        prod = self.data.iloc[self.contador, 6]
        producto = self.df_productos[self.df_productos['ID_Producto'].astype(str).eq(str(prod))]
        producto = producto[['ID_Producto','Nombre','Proveedor']].values.tolist()
        print(producto)
        producto = str(producto[0][0]) + " " + producto[0][1] + " " +producto[0][2]
        self.cbb_producto.set(producto)
        
        cantidad = self.data.iloc[self.contador, 7]
        self.ent_cantidad.insert(0, cantidad)  
    
    def vali_producto(self):
        prod = self.cbb_producto.get().split()
        if prod[0].isnumeric():
            id = int(prod[0])
            prod.insert(0,id)
            prod.pop(1)
            
            productos = [list(elem) for elem in self.cbb_producto['values']]
        
            print(prod)
            print(productos)
        
            if prod in productos:
                return True
            else:
                messagebox.showerror('Producto No Válido', "Selecciona una opción de la lista desplegable")
                return False
        else:
            messagebox.showerror('Producto No Válido', "Selecciona una opción de la lista desplegable")
            return False
    
    def actualizar (self):
        validacion_producto = self.vali_producto()
        cantidad = self.ent_cantidad.get().strip()
        
        try:
            cantidad = int(cantidad)
            
            if validacion_producto:
                id_producto = int(self.cbb_producto.get().split()[0])
                cantidad = int(cantidad)
                
                conn = fun.conectar_db()
                
                if isinstance(self.ids, tuple):
                    valor = self.ids[self.contador]
                    consulta = f"UPDATE Movimientos SET ID_Producto = {id_producto}, Cantidad = {cantidad} WHERE ID_Mov = {valor}"
                else:
                    valor = int(self.ids[1:-1])
                    consulta = f"UPDATE Movimientos SET ID_Producto = {id_producto}, Cantidad = {cantidad} WHERE ID_Mov = {valor}"
                
                conn.execute(consulta)
                conn.commit()
                conn.close()
                messagebox.showinfo('Actualización Exitosa',"Este movimiento ha sido actualizado con éxtio")
                self.actualizar_valores()

        except ValueError:
            messagebox.showerror('Cantidad no es Numérica', "Ingresa un número en la cantidad")
    
    
    def __init__(self, id_movimiento, id_principal, tipo):
        self.contador = 0
        self.ids = id_movimiento
        self.id_movimiento = id_principal
        self.tipo = tipo
        self.data = self.obtener_movimientos()
        self.df_productos = fun.obtener_productos()
        
        self.root = tk.Tk()
        self.root.title('Modificación de Movimientos')
        self.lbl_movimiento = tk.Label(self.root, text = 'Modificar Movimientos', font=('Arial',14, 'bold'))
        self.lbl_movimiento.grid(row = 1, column = 4, columnspan = 3, padx = 7, pady= 7)
        self.lbl_buscarproducto = tk.Label(self.root, text = 'Producto', font=('Arial',9))
        self.lbl_buscarproducto.grid(row = 2, column = 4, padx = 5, pady= 5)
        self.var_cbb_producto = tk.StringVar()
        self.cbb_producto = ttk.Combobox(self.root, text='Teclea aqui para buscar un producto', font=('Arial', 9))
        self.cbb_producto.grid(row = 2, column = 5, columnspan= 2, padx = 5, pady = 5)

        self.lbl_cantidad = tk.Label(self.root, text = 'Cantidad', font=('Arial',9))
        self.lbl_cantidad.grid(row = 3, column = 4, padx = 5, pady= 5)
        self.ent_cantidad = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_cantidad.grid(row = 3, column = 5, columnspan=2, padx = 5, pady= 5)
        
        self.definir_valores()

        self.btn_modificar_registro = tk.Button(self.root, text = 'Modificar Registro', font=('Arial',11), command = self.actualizar)
        self.btn_modificar_registro.grid(row = 4, column=5, columnspan = 2, padx=10, pady=10)
        self.btn_modificar_registro.config(bg="#ED7F28", fg = "white")
        self.btn_eliminar_registro = tk.Button(self.root, text="Insertar Registro", font=("Arial", 11, 'bold'), )
        

        self.cbb_producto.bind("<ButtonPress-1>", lambda event: fun.buscar_productos(event, self.df_productos, self.cbb_producto))
        self.btn_modificar_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_modificar_registro))
        self.btn_modificar_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_modificar_registro))
        #self.btn_eliminar_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_insertar_registro))
        #self.btn_eliminar_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_insertar_registro))
        
    def iniciar(self):
        self.root.mainloop()
                    

          
class AnadirProducto:
    
    def obtener_proveedores(self):
        conn = fun.conectar_db()
        consulta = "SELECT ID_Proveedor, Nombre FROM Proveedores"
    
        df = pd.read_sql_query(consulta, conn)
        df['Nombre'] = df['Nombre'].apply(fun.concatenar)
    
        conn.close()
        
        return df
    
    def validar_campos(self):
        if self.cbb_proveedor.get() != "" and self.ent_animal.get() != "" and self.ent_Codigo.get() != "" and self.ent_nombre.get() != "" and self.ent_peso.get() != "":
            return True
        else:
            messagebox.showerror("Campos no Completos","Asegúrate de seleccionar y llenar todos los campos antes de añadir un producto")
            return False
    
    def validar_id_producto(self):
        
        if self.ent_Codigo.get().strip().isnumeric():
            id_prod = int(self.ent_Codigo.get().strip())
            if id_prod in self.df_productos['ID_Producto'].values:
                messagebox.showerror('ID_Producto en Uso',"Debe usar otro código/id de producto, el que quiere usar ya está en uso")
                return False
            else:
                return id_prod
        else:
            messagebox.showerror('ID_Producto Inválida',"La ID/Código de producto debe ser un número entero")
            return False
    
    def validar_peso(self):
        
        if self.ent_peso.get().strip().isnumeric():
            return int(self.ent_peso.get().strip())
        else:
            messagebox.showwarning('Peso no es Numérico',"El peso debe ser un número entero; ejemplo '35' no '35 kg'")
            return False
    
    def anadir_prod(self):
        
        if self.validar_campos():
            peso = self.validar_peso()
            id = self.validar_id_producto()
            
            if peso != False and id != False:
                proveedor = int(self.cbb_proveedor.get().split()[0])
                nombre = self.ent_nombre.get()
                animal = self.ent_animal.get()
                
                conn = fun.conectar_db()
                comando = f"INSERT INTO Productos (ID_Producto, Nombre, Peso, Animal, ID_Proveedor) VALUES ({id},{nombre},{peso},{animal},{proveedor})"
                
                conn.execute(comando)
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Producto Añadido", f"Listo, se ha añadido el producto {nombre} con id {id} a la base de datos")
            
            else:
                pass
            
        else:
            pass
    
    def __init__(self):
        
        self.root = tk.Tk()
        self.lbl_titulo = tk.Label(self.root, text = "Añadir Productos", font =('Arial', 16, 'bold'))
        self.lbl_titulo.config(fg = 'green', bg='white')
        self.lbl_titulo.grid(column = 1, row = 1, columnspan= 3, padx = 7, pady = 7)
        
        self.df_productos = fun.obtener_productos()
        
        self.lbl_Codigo = tk.Label(self.root, text = "ID_Producto", font =('Arial', 11))
        self.lbl_Codigo.grid(column = 1, row = 2, padx = 7, pady = 7)
        self.ent_Codigo = tk.Entry(self.root, font =('Arial', 11), textvariable=tk.StringVar())
        self.ent_Codigo.grid(column = 2, columnspan = 2, row = 2, padx = 7, pady = 7)
        
        self.lbl_buscarprod = tk.Label(self.root, text = "Buscar Producto", font =('Arial', 9))
        self.lbl_buscarprod.grid(column = 1, row = 3, padx = 7, pady = 7)
        self.cbb_producto = ttk.Combobox(self.root, state=tk.NORMAL)
        self.cbb_producto.grid(column = 2, columnspan = 2, row = 3, padx = 7, pady = 7)
        
        self.lbl_nombre = tk.Label(self.root, text = 'Nombre', font = ('Arial',12) )
        self.lbl_nombre.grid(column = 1, row = 4, padx = 5, pady = 5)
        self.ent_nombre = tk.Entry(self.root, font = ('Arial',12), textvariable=tk.StringVar() )
        self.ent_nombre.grid(column = 2, row = 4, columnspan=2, padx = 5, pady = 5)
        
        self.lbl_peso = tk.Label(self.root, text = 'Peso', font = ('Arial',12) )
        self.lbl_peso.grid(column = 1, row = 5, padx = 5, pady = 5)
        self.ent_peso = tk.Entry(self.root, font = ('Arial',12), textvariable=tk.StringVar() )
        self.ent_peso.grid(column = 2, row = 5, columnspan=2, padx = 5, pady = 5)
        
        self.lbl_animal = tk.Label(self.root, text = 'Animal', font = ('Arial',12) )
        self.lbl_animal.grid(column = 1, row = 6, padx = 5, pady = 5)
        self.ent_animal = tk.Entry(self.root, font = ('Arial',12), textvariable=tk.StringVar() )
        self.ent_animal.grid(column = 2, row = 6, columnspan=2, padx = 5, pady = 5)
        
        self.lbl_proveedor = tk.Label(self.root, text = 'Proveedor', font = ('Arial',12) )
        self.lbl_proveedor.grid(column = 1, row = 7, padx = 5, pady = 5)
        self.cbb_proveedor = ttk.Combobox(self.root, values = self.obtener_proveedores()[['ID_Proveedor','Nombre']].values.tolist(), state="readonly")
        self.cbb_proveedor.grid(column = 2, row = 7, columnspan=2, padx = 5, pady = 5)

        
        self.btn_anadir = tk.Button(self.root, text = 'Añadir Producto', font = ('Arial',11), command = self.anadir_prod)
        self.btn_anadir.config(bg="#ED7F28", fg = "white")
        self.btn_anadir.grid(column=2, row=8, padx=7, pady=7)
        
        self.cbb_producto.bind("<ButtonPress-1>", lambda event: fun.buscar_productos(event, self.df_productos, self.cbb_producto))
        self.btn_anadir.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_anadir))
        self.btn_anadir.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_anadir))
        
    def iniciar(self):
        self.root.mainloop()
        
        
        
class InventarioInicial:
    
    def insertar_registro(self):
        conn = fun.conectar_db()
        lista = self.df_movimientos.values.tolist()
        
        for rows in lista :
            print(rows)
            id_prod = rows[2]
            cantidad = rows[4]
            
            consulta = f'INSERT INTO Inv_Fisico (Fecha, ID_Sucursal, ID_Producto, Cantidad) VALUES ({self.fecha}, {self.sucursal[0]}, {id_prod},{cantidad})'
            print(consulta)
            conn.execute(consulta)
                
        messagebox.showinfo('Consulta Exitosa!', "Los registros han sido insertados a la base de datos correctamente")
        conn.commit()
        conn.close()
    
    def tabla_movimientos(self,df):
        self.tree = tk.ttk.Treeview(self.root, columns=('Fecha','Sucursal','ID_producto', 'Nombre', 'Cantidad'))

        # Configurar las columnas del Treeview
        self.tree.column("#0", width = 20)
        self.tree.heading("#1", text="Fecha")
        self.tree.column('#1', width=120)
        self.tree.heading("#2", text="Sucursal")
        self.tree.column('#2', width=120)
        self.tree.heading("#3", text="ID_Producto")
        self.tree.column('#3', width=100)
        self.tree.heading("#4", text="Nombre")
        self.tree.column('#4', width=100)
        self.tree.heading("#5", text="Cantidad")
        self.tree.column('#5', width=100)
        
        for row in df.values:
            self.tree.insert("", tk.END, values=row)
            
        self.tree.grid(row = 9, column=0, padx=5, pady=5)
    
    def anadir_registro(self):
        
        if hasattr(self, "df_movimientos") == False:
            self.df_movimientos = pd.DataFrame(columns = ['Fecha', 'Sucursal','ID_producto', 'Nombre', 'Cantidad'])
            print('DataFrame creado')
            
        vali_prod = RegistroMovimientos.vali_producto(self)
        sucursal = self.cbb_suc_origen.get()
        cantidad = self.ent_cantidad.get().strip()
        fecha = fun.validar_fecha(self.ent_dia.get().strip(), self.ent_mes.get().strip(), self.ent_an.get().strip() )
        
        if cantidad.isnumeric() and vali_prod and fecha != False and sucursal != "":
            
            self.cbb_suc_origen.config(state = tk.DISABLED)
            self.ent_an.config(state= 'disabled')
            self.ent_mes.config(state= 'disabled')
            self.ent_dia.config(state= 'disabled')
            
    
            fecha = str(self.ent_an.get().strip() + '-' + self.ent_mes.get().strip() + '-' + self.ent_dia.get().strip())
            self.fecha = "'" + fecha + "'"
            self.sucursal = sucursal.split()
            id_producto = int(self.cbb_producto.get().split()[0])
            nombre_producto = str(self.cbb_producto.get().split()[1])
            cantidad = int(cantidad)
            
            row_nuevo = {'Fecha' : fecha,
                        'Sucursal': self.sucursal[1],
                        'ID_producto': id_producto, 
                        'Nombre': nombre_producto, 
                        'Cantidad': cantidad}
            
            self.df_movimientos = pd.concat([self.df_movimientos, pd.DataFrame([row_nuevo])], ignore_index= True)
            self.tabla_movimientos(self.df_movimientos)
            self.ent_cantidad.delete(0, tk.END)
            
            self.cbb_producto.set("")
            self.btn_insertar_registro.grid(row = 10, column =1, columnspan = 2, padx = 5, pady = 5)

        elif cantidad.isnumeric() == False:
            messagebox.showerror('Cantidad no es Numérica', "Ingresa un número en cantidad")
        else:
            messagebox.showerror('Sucursal no Seleccionada', "Asegúrate de seleccionar una sucursal de la lista desplegables")
    
    def __init__(self):
    
        self.root = tk.Tk()
        self.root.title("Inventario Físico")
        self.titulo = f"Inventario Inicial"
        self.lbl_titulo = tk.Label(self.root, text= self.titulo, font=("Arial", 16, "bold"))
        self.lbl_titulo.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        self.lbl_titulo.config(bg="#ED7F28", fg = "white")
        
        self.lbl_fecha1 = tk.Label(self.root, text="Fecha", font=("Arial", 11))
        self.lbl_fecha1.grid(row=1, column=0, columnspan=3, padx=7, pady=7)
        self.lbl_fecha2 = tk.Label(self.root, text="Día", font=("Arial", 9))
        self.lbl_fecha2.grid(row=2, column=0, padx=5, pady=5)
        self.lbl_fecha3 = tk.Label(self.root, text="Mes", font=("Arial", 9))
        self.lbl_fecha3.grid(row=2, column=1, padx=5, pady=5)
        self.lbl_fecha4 = tk.Label(self.root, text="Año", font=("Arial", 9))
        self.lbl_fecha4.grid(row=2, column=2, padx=5, pady=5)

        self.ent_dia = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_dia.grid(row = 3, column=0)
        self.ent_mes = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_mes.grid(row = 3, column=1)
        self.ent_an = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_an.grid(row = 3, column=2)
        
        self.lbl_suc1 = tk.Label(self.root, text="Sucursal", font=("Arial", 11))
        self.lbl_suc1.grid(row = 4, column =0, padx = 7, pady = 7)
        self.cbb_suc_origen = ttk.Combobox(self.root, state="readonly")
        self.cbb_suc_origen.grid(row = 4, column = 1, columnspan = 2, padx = 7, pady = 7)
        self.cbb_suc_origen['values'] = fun.obtener_sucursales()[['ID_Sucursal','Nombre']].values.tolist()
        
        self.lbl_movimiento = tk.Label(self.root, text = 'Movimientos', font=('Arial',14, 'bold'))
        self.lbl_movimiento.grid(row = 5, column = 0, columnspan = 4, padx = 7, pady= 7)
        self.lbl_buscarproducto = tk.Label(self.root, text = 'Producto', font=('Arial',9))
        self.lbl_buscarproducto.grid(row = 6, column = 0, padx = 5, pady= 5)
        self.cbb_producto = ttk.Combobox(self.root, font=('Arial', 9))
        self.cbb_producto.grid(row = 6, column = 1, columnspan= 2, padx = 5, pady = 5)

        self.lbl_cantidad = tk.Label(self.root, text = 'Cantidad', font=('Arial',9))
        self.lbl_cantidad.grid(row = 7, column = 0, padx = 5, pady= 5)
        self.ent_cantidad = tk.Entry(self.root, textvariable=tk.StringVar())
        self.ent_cantidad.grid(row = 7, column = 1, columnspan=2, padx = 5, pady= 5)

        self.btn_anadir_registro = tk.Button(self.root, text = 'Añadir Registro', font=('Arial',11), command = self.anadir_registro)
        self.btn_anadir_registro.grid(row = 8, column=1, columnspan = 2, padx=10, pady=10)
        self.btn_anadir_registro.config(bg="#ED7F28", fg = "white")
        self.btn_insertar_registro = tk.Button(self.root, text="Insertar Registro", font=("Arial", 11, 'bold'), command = self.insertar_registro)
        self.btn_insertar_registro.config(bg="#ED7F28", fg = "white")

        df_productos = fun.obtener_productos()

        self.cbb_producto.bind("<ButtonPress-1>", lambda event: fun.buscar_productos(event, df_productos, self.cbb_producto))
        self.btn_anadir_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_anadir_registro))
        self.btn_anadir_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_anadir_registro))
        self.btn_insertar_registro.bind("<Enter>", lambda event: fun.btn_enter(event, self.btn_insertar_registro))
        self.btn_insertar_registro.bind("<Leave>", lambda event: fun.btn_leave(event, self.btn_insertar_registro))
    
    def iniciar(self):
        self.root.mainloop()
        
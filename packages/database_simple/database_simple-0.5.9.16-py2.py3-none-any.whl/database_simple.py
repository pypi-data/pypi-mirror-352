"""
Made by HQO (https://github.com/MAJHQO) and idea extended from library: database_creatorplus (https://pypi.org/project/database-creatorplus/)
"""

import psycopg2 as psy, sqlite3 as sq,flet as ft,csv, os, time

__version__="0.5.9.16"

class Database:

    def __init_tables(self):
        try:
            if(self.connect_type==True):
                self.__cursor.execute("Select table_name FROM information_schema.tables where table_schema='public'")
            else:
                self.__cursor.execute(f"SELECT name FROM sqlite_master WHERE type = 'table'")
            tables_name=self.__cursor.fetchall()
            if(len(tables_name)!=0 and os.path.exists('.\\tables.csv')==True):
                for name in tables_name:
                    columns_table=[]
                    if(self.connect_type==True):
                        self.__cursor.execute(f"Select column_name from information_schema.columns where table_name='{name[0]}'")
                    else:
                        self.__cursor.execute(f"Select name from Pragma_table_info('{name[0]}')")
                    columns=self.__cursor.fetchall()
                    for column_name in columns:
                        columns_table.append(column_name[0])
                    with open(".\\tables.csv", 'r') as file:
                        csv_reader=csv.DictReader(file)
                        data=[]
                        for row in csv_reader:
                            data.append(row)
                        for rows in data:
                            if(rows['table_name'].lower()==name[0]):
                                self.__tables[name[0]]=self.__Table(columns_table,int(rows['table_width']), name[0].lower())
                                break
                        file.close()
        except Exception as ex:
            raise Exception(f" {ex}")

    def __init__(self, bd_type:bool, **kwargs):
        """
        Используется для создания и взаимодействия с базой данных

        - [bd_type]: определяет тип используемой базы данных
            - False: sqlite3
            - True: psycopg2
        - [kwargs]: принимает именованные аргументы для инициализации объекта базы данных
        """
        try:
            self.__connect= psy.connect(database=kwargs['database'], password=kwargs['password'], user=kwargs['user'], port=kwargs['port']) if bd_type else sq.connect(kwargs['database']+".db", check_same_thread=False)
            self.__cursor=self.__connect.cursor()
            self.connect_type=bd_type
            self.__class__.__Table._conn = self.__connect
            self.__class__.__Table._cursor = self.__cursor
            self.__tables={}
            self.__init_tables()

        except Exception as ex:
            raise Exception(f" {ex}")
        
    def request_execute(self, request:str):
        """
        Используется для выполнения SQL - запросов в базу данных
        """
        try:
            self.__cursor.execute(request)
            self.__connect.commit()
            if(request.lower().find("select")!=-1 or request.lower().find("pragma")!=-1):
                return self.__cursor.fetchall()
        except Exception as ex:
            raise Exception(f" {ex}")
        
    def create_table(self, table_name:str, table_structure:dict[str:str], table_width:int):
        """
        Используется для создания таблицы в базе данных

        [table_structure]: содержит столбцы их типы данных в виде {'cell_name':'cell_type'}
        """
        try:
            if(self.__tables.get(table_name)==None):
                keys=table_structure.keys()
                values_str=""
                columns=[]
                for key in keys:
                    values_str+=f"{key} {table_structure[key]}, "
                    columns.append(key)
                self.__cursor.execute(f"Create table {table_name}({values_str[:-2]})")
                if(os.path.exists(".\\tables.csv")==True):
                    with open('.\\tables.csv', 'a') as file:
                        file.writelines([f'{table_name}, {table_width}\n'])
                else:
                    with open('.\\tables.csv', 'a') as file:
                        file.writelines(['table_name,table_width\n', f'{table_name},{table_width}\n'])

                self.__tables[table_name]=self.__Table(columns,table_width ,table_name)
                self.__connect.commit()
        except Exception as ex:
            raise Exception(f" {ex}")
        
    def drop_all_tables(self):
        """
        Метод для удаления всех таблиц из базы данных
        """
        try:
            self.__cursor.execute("DROP SCHEMA public CASCADE;")
            self.__connect.commit()
            self.__cursor.execute("CREATE SCHEMA public;")
            self.__connect.commit()
        except Exception as ex:
            raise Exception(f" {ex}")
        
    def delete_table(self,table_name:str):
        """
        Метод для удаления определенной таблицы
        """

        try:
            self.__cursor.execute(f"Drop table {table_name}")
            self.__connect.commit()
        except Exception as ex:
            raise Exception(f" {ex}")

    class __Table:
        def __init__(self, column:list[str], table_width:int, table_name:str):
            self.__column=[ft.DataColumn(ft.Text(data, width=200, text_align=ft.TextAlign.CENTER)) for data in column]
            self.__column.append(ft.DataColumn(ft.Text("Delete", width=200,text_align=ft.TextAlign.CENTER)))
            self.table_name=table_name
            self.__table=ft.Row(
                [ft.Column([ft.DataTable(self.__column,[], width=table_width)], height=300,scroll=ft.ScrollMode.ALWAYS)], height=320, width=table_width,scroll=True)
            
        def isfloat(self, value):
            """
            Проверяет полученную строку на то, является ли ее выражение десятичным типом данных
            """
            try:
                float(value)
                return True
            except ValueError:
                return False
            
        def __viewMode(self,obj):
            """
            Осуществляет открытие диалогового окна для детального просмотра данных выбранной ячейки.
            """
            view_dialog=ft.AlertDialog(
                title=ft.Text("Просмотр данных", size=18), 
                content=ft.Text(obj.control.data.split('|')[0], size=15),
                actions=[ft.ElevatedButton("Выйти", color=ft.Colors.RED, on_click=lambda _:obj.page.close(view_dialog))])
            obj.page.open(view_dialog)

        def __changeMode(self,obj):
            """
            Осуществляет открытие диалогового окна для изменения выбранной ячейки

            В случае проявления непредвиденной ошибки - возращает Exception
            В случае не изменения значения, указанное в ячейке - возвращает False
            """
            try:
                change_dialog=ft.AlertDialog(
                    title=ft.Text("Изменение данных", size=18), 
                    actions=[
                        ft.ElevatedButton("Изменить", on_click=self.__updateCellData, data=obj.control.data),
                        ft.ElevatedButton("Выйти", color=ft.Colors.RED, on_click=lambda _: obj.page.close(change_dialog))])
                if (obj.control.data.lower().find("references")!=-1):
                    change_dialog.content=ft.DropdownM2(options=[])
                    self._cursor.execute(f"Select {obj.control.data.split('|')[4].split(' ')[3]} from {obj.control.data.split('|')[4].split(' ')[2]}")
                    result=self._cursor.fetchall()
                    for data in result:
                        change_dialog.content.options.append(ft.dropdownm2.Option(data[0]))
                    change_dialog.content.value=obj.control.data.split("|")[0]
                else:
                    change_dialog.content=ft.TextField(obj.control.data.split('|')[0], text_size=15)

                obj.page.open(change_dialog)
            except Exception as ex:
                raise Exception(f'{ex}')

        def viewMode_handler(self,obj):
            """
            Осуществляет изменения обработчика 'on_click' на открытие диалогового окна 'Детальный просмотр данных', для всех ячеек текущей таблицы.
            """
            try:
                if (type(obj.page.controls[1])==ft.Column and type(obj.page.controls[1].controls[0])==ft.DataTable):
                    for rows in obj.page.controls[1].controls[-1].rows:
                        for i in range(0,len(rows.cells)):
                            if(i!=0):
                                rows.cells[i].content.on_click=self.__viewMode

                    if (type(obj.control) == ft.MenuItemButton):
                        obj.control.content=ft.Text('Изменение')
                    else:
                        if(hasattr(obj.control,'text')):
                            obj.control.text='Изменение'
                        elif(hasattr(obj.control,'value')):
                            obj.control.value='Изменение'
                    obj.control.on_click=self.changeMode_handler
                    obj.page.update()
            except Exception as ex:
                raise Exception(f'{ex}')

        def changeMode_handler(self,obj):
            """
            Осуществляет изменения обработчика 'on_click' на открытие диалогового окна 'Изменение данных', для всех ячеек текущей таблицы.
            """
            try:
                if (type(obj.page.controls[1])==ft.Row and type(obj.page.controls[1].controls[0].controls[0])==ft.DataTable):
                    for rows in obj.page.controls[1].controls[-1].controls[0].rows:
                        for i in range(0,len(rows.cells)):
                            if(i!=0):
                                rows.cells[i].content.on_click=self.__changeMode
                    if (type(obj.control) == ft.MenuItemButton):
                        obj.control.content=ft.Text('Просмотр')
                    else:
                        if(hasattr(obj.control,'text')):
                            obj.control.text='Просмотр'
                        elif(hasattr(obj.control,'value')):
                            obj.control.value='Просмотр'
                    obj.control.on_click=self.viewMode_handler
                obj.page.update()
            except Exception as ex:
                raise Exception(f'{ex}')

        def getTable(self, db_object:object):
            """
            Метод для инициализации и возращении соотвествующей таблицы
            """
            try:
                self._cursor.execute(f"Select * from {self.table_name}")
                result=self._cursor.fetchall()
                columns=db_object.get_table_columns(self.table_name).split(",")
                columns.append("Delete")
                columns_type=db_object.get_table_columns_type(self.table_name)
                columns_type.append("None")
                foreign_key=db_object.request_execute(f"PRAGMA foreign_key_list({self.table_name})")

                if(len(self.__table.controls[-1].controls[-1].rows)):
                    self.__table.controls[-1].controls[-1].rows.clear()
                
                if (len(result)==0):
                    return False

                for row in result:
                    self.__table.controls[-1].controls[-1].rows.append(ft.DataRow([]))
                    for i in range(0,len(row)+1):
                        if(i==0):
                            self.__table.controls[-1].controls[-1].rows[-1].cells.append(ft.DataCell(
                                ft.TextField(
                                    str(row[i]), 
                                    read_only=True, 
                                    border_color=ft.Colors.TRANSPARENT, 
                                    width=200, 
                                    text_align=ft.TextAlign.CENTER)
                            ))
                        elif(i==len(row)):
                            self.__table.controls[-1].controls[-1].rows[-1].cells.append(ft.DataCell(
                                ft.ElevatedButton(
                                    "Удалить",
                                    bgcolor=ft.Colors.RED,
                                    on_click=self.__delete_row,
                                    color=ft.Colors.WHITE,
                                    width=200,
                                    data=f"None|{row[0]}|{columns[i]}|{self.table_name}|{columns_type[i][0]}")
                            ))
                        else:
                            self.__table.controls[-1].controls[-1].rows[-1].cells.append(ft.DataCell(
                                ft.TextField(
                                    str(row[i]), 
                                    read_only=True, 
                                    border_color=ft.Colors.TRANSPARENT, 
                                    width=200, 
                                    text_align=ft.TextAlign.CENTER,
                                    on_click=self.__viewMode,
                                    data=f"{row[i]}|{row[0]}|{columns[i]}|{self.table_name}|{columns_type[i][0]}")
                            ))
                        
                            if (len(foreign_key)!=0):
                                for col in foreign_key:
                                    if (columns[i].strip() in col):
                                        self.__table.controls[-1].controls[-1].rows[-1].cells[-1].content.data+=f" references {col[2]} {col[4]}"
                return self.__table
            except Exception as ex: 
                raise Exception (f'{ex}')

        def select_request(self, columns:str, contidion:str):
            try:
                self._cursor.execute(f"Select {columns} from {self.table_name} where {contidion}")
                return self._cursor.fetchall()
            except Exception as ex: 
                raise Exception(f" {ex}")
            
        def delete_request(self, contidion=""):
            """
            Используеся для удаления данных из таблицы
            
             - [contidion | условие]: если данный параметр не передан в метод - запрос осуществляет удаление все записей из таблицы
            """
            try:
                if (len(contidion)==0):
                    self._cursor.execute(f"Delete from {self.table_name}")
                else:
                    self._cursor.execute(f"Delete from {self.table_name} where {contidion}")
                self._conn.commit()
            except Exception as ex: 
                raise Exception(f" {ex}")
            
        def __delete_row(self, obj):
            try:
                self._cursor.execute(f"Delete from {self.table_name} where ID={obj.control.data.split('|')[1]}")
                self._conn.commit()

                successDialog=ft.AlertDialog(title=ft.Text("Удаление", size=18), content=ft.Text("Удаление прошло успешно", size=15), actions=[
                    ft.ElevatedButton("Выйти", color=ft.Colors.RED,on_click=lambda _:obj.page.close(successDialog))
                ])
                obj.page.open(successDialog)
            except Exception as ex: 
                raise Exception(f" {ex}")
            
        def insert_request(self, values:list[list], db_object:object):
            """
            Используется для записи данных в таблицу
             - (values) [[column_value]]: по порядку нахождения столбцов в таблице
            """
            try:
                columns_str=db_object.get_table_columns(self.table_name)
                for row in values:
                    values_str=""
                    for elem in row:
                        if(type(elem) not in [int, float]):
                            values_str+=f"'{elem}', "
                        else:
                            values_str+=f"{elem}, "
                    self._cursor.execute(f"Insert into {self.table_name}({columns_str}) values ({values_str[:-2]})")
                    self._conn.commit()
            except Exception as ex: 
                raise Exception(f" {ex}")
            
        def update_request(self, set_values:dict, condition: str):
            """
            Используется для обновления данных в таблице
             - (set_values) {column_name: column_value}
            """
            try:
                columns=list(set_values)
                set_expression=""
                for column in columns:
                    if (type(set_values[column]) not in [int, float]):
                        set_expression+=f"Set {column}='{set_values[column]}', "
                    else:
                        set_expression+=f"Set {column}={set_values[column]}, "
                self._cursor.execute(f"Update table {self.table_name} {set_expression[:-2]} where {condition}")
                self._conn.commit()
            except Exception as ex: 
                raise Exception(f" {ex}")
            
        def __updateCellData(self, obj):
            try:
                if (obj.page.overlay[-1].content.value!=obj.control.data.split('|')[0]):
                    if (obj.page.overlay[-1].content.value.isdigit() or self.isfloat(obj.page.overlay[-1].content.value)):
                        self._cursor.execute(f"Update {self.table_name} set {obj.control.data.split('|')[2]}={obj.page.overlay[-1].content.value}")
                    else:
                        self._cursor.execute(f"Update {self.table_name} set {obj.control.data.split('|')[2]}='{obj.page.overlay[-1].content.value}'")
                    self._conn.commit()
                    base_color=obj.page.overlay[-1].content.border_color
                    obj.page.overlay[-1].content.border_color=ft.Colors.GREEN
                    obj.page.update()
                    time.sleep(0.7)
                    obj.page.overlay[-1].content.border_color=base_color
                    obj.page.update()

                else:
                    return False
            except Exception as ex:
                raise Exception(f" {ex}")
        
    # def load_table(self, table_name:str|list, table_width:int) -> __Table | None:
    #     """
    #     Инициализирует Table объекты, для возможности использования [get_table_obj]
    #     """
    #     if(type(table_name)==str):
    #         column=self.get_table_columns(table_name).split(',')
    #         self.__tables[table_name]=self.__Table(column,table_width,table_name,self)
    #         return self.__tables[table_name]
    #     else:
    #         for table in table_name:
    #             column=self.get_table_columns(table).split(',')
    #             self.__tables[table]=self.__Table(column,table_width,table_name,self)
    
    def get_table_obj(self, table_name:str)->__Table:
        """
        Возвращает объект Table, позволяющие взаимодействовать с конкреткной таблицей в базе данных
        """
        try:
            if (self.__tables.get(table_name)!=None):
                return self.__tables[table_name] 
        except Exception as ex:
            raise Exception(f" {ex}")
        
    def get_table_columns(self, table_name:str):
        """
        Возвращает столбцы заданной таблицы 
        """
        try:
            if(self.__tables[table_name]!=None):
                if (self.connect_type):
                    self.__cursor.execute(f"Select column_name from information_schema.columns where table_name='{table_name}'")
                else:
                    self.__cursor.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{table_name}')")
                result=self.__cursor.fetchall()
                column_str=""
                for column in result:
                    column_str+=column[0]+", "
                return column_str[:-2]
            else:
                return False
        except Exception as ex:
            raise Exception(f" {ex}")
        
    def get_table_columns_type(self, table_name:str):
        """
        Возращает типы столбцов заданной таблицы в порядке возрастания (от 1 к последнему)
        """
        try:
            if(table_name in self.__tables.keys()):
                if(self.connect_type):
                    self.__cursor.execute(f"Select data_type from information_schema.columns where table_name='{table_name}'")
                else:
                    self.__cursor.execute(f"SELECT type FROM PRAGMA_TABLE_INFO('{table_name}')")
                result=self.__cursor.fetchall()
                return result
            else:
                return False
        except Exception as ex:
            raise Exception(f" {ex}")
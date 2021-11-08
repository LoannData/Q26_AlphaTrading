import sqlite3

class SQL: 

    def __init__(self): 
        self.path      = None 
        self.connexion = None 
        self.cursor    = None 
        self.verbose   = False 
    
    def to_SQL_type(self, type_, mode = "format"): 
        """ 
        Function allowing to convert element type expressed in Python syntax into type 
        expressed into SQL syntax. 

        Parameter: 
            - type_ [str]: Types have to be committed as a string format 
        
        Returns: 
            - [str]: The parameter type converted in the SQL format if the type is considered in the method. 
                     The input variable otherwise. 
        """
        if type(type_) == list and mode == "list": 
            sql_list = "("
            for element in type_: 
                sql_list += "'"+str(element)+"'"+","
            sql_list = sql_list[:-1]
            sql_list += ")"
            return sql_list

        if mode == "format": 
            if type_ == "str": 
                return "text"
            elif type_ == "int": 
                return "integer"
            elif type_ == "float": 
                return "real"
            else: 
                return type_

        elif mode == "logic": 
            if type_ == "all": 
                return "ALL"
            elif type_ == "any": 
                return "ANY"
            elif type_ == "and": 
                return "AND"
            elif type_ == "or": 
                return "OR"
            elif type_ == "not": 
                return "NOT"
            elif type_ == "in": 
                return "IN"
            elif type_ == "is" or type_ == "==":
                return "IS" 
            else: 
                return type_

        elif mode == "operator": 
            if type_ == "==": 
                return "="
            elif type_ == "!=": 
                return "<>"
            else: 
                return type_

        else: 
            return type_ 

    def create_database(self, path): 
        """  
        Function allowing to create a database. 

        Parameter: 
            - path [str]: Path and name of the database. Note: The folder should exist. 

        Returns: 
            None 
        """

        if not path[-3:] == ".db": 
            path += ".db"
        
        self.path      = path 
        self.connexion = sqlite3.connect(path)
        self.cursor    = self.connexion.cursor() 

        return 
    
    def connect_database(self, path): 
        """ 
        Function allowing to connect to an existing database

        Parameter: 
            - path [str]: Path and name of the database. Note: The folder should exist.

        Returns: 
            None 
        """
        self.create_database(path) 
    
    def execute(self, 
                action = None, 
                object = None, 
                argument = None): 
        """ 
        Function that execute every command following the SQL query 
        structure. 
        """
        
        command = action+" "+object+" "+argument
        if self.verbose: 
            print (command)
        iterator = self.cursor.execute(command) 
        return iterator 

    #=====================================================================================#
    # LISTING FUNCTIONS
    #=====================================================================================# 

    def get_table_list(self): 
        """ 
        Function returning the list of tables in the database 

        Parameters: 
            None 

        Returns: 
            - [list(str)]: ["table_name1", "table_name2", ...]
        """

        action = "SELECT" 
        object = "name FROM sqlite_master"
        argument = "WHERE type='table'"

        iterator = self.execute(action = action, 
                                object = object, 
                                argument = argument)
        
        table_list = [x[0] for x in iterator.fetchall()]

        return table_list
    
    def get_id_list(self, table): 
        """ 
        Function that retrieves the list of ids of the elements within 
        a table. If the tabe doesn't contain any elements, it return 
        the following list: [0]

        Parameters: 
            - table [str]: Table name 

        Returns: 
            - [int]: List of ids of the elements in the table 
                     in the order they have been added 
        """

        action = "SELECT"
        object = "id"
        argument = "FROM "+table

        iterator = self.execute(action = action, 
                                object = object, 
                                argument = argument)
        
        id_list = [x[0] for x in iterator.fetchall()]

        if len(id_list) == 0 : 
            return [0]

        return id_list 



    #=====================================================================================#
    # CREATION & INSERTION FUNCTIONS
    #=====================================================================================# 
    
    def create_table(self, 
                     name, 
                     structure): 
        """ 
        Function allowing to create a table in the already existing database 

        Parameters: 
            - name [str]: Name of the table 
            - structure [dict]: Structure of the table. Keys corresponds to the name of the columns while 
                                associated values corresponds to the anounced type of the data.
        
        Returns: 
            None 
        """
        
        action = "CREATE" 
        object = "TABLE"+" "+name 
        argument = "("
        argument += "id"+" "+"integer"+", "
        for key in structure.keys(): 
            argument += key+" "+self.to_SQL_type(structure[key], mode = "format")+", "
        argument = argument[:-2]
        argument += ")" 

        self.execute(action = action, 
                     object = object, 
                     argument = argument)

        return 
    
    def insert(self, 
               table, 
               value): 
        """ 
        Function allowing to insert an element in an existing table 
        of the connected database 

        Parameters: 
            - table [str]  : Name of the table 
            - value [list] : List of the attributes of the element to be 
                             inserted 

        Returns: 
            None  
        """

        last_id = self.get_id_list(table)[-1]
        value = [last_id+1]+value 
        
        action = "INSERT INTO" 
        object = table 
        argument = "VALUES ("
        for element in value: 
            if type(element) == str: 
                element = element.replace("'", '"') 
                element = "'"+element+"'"
            else: 
                element = str(element)
            argument += element+","
        argument = argument[:-1]
        argument += ")"

        self.execute(action   = action, 
                     object   = object, 
                     argument = argument)
        
        self.connexion.commit() 

        return 

    def delete(self, 
               table, 
               where_ = None): 
        """ 
        Function allowing to delete an element from a table in the database. 
        
        Parameters: 
            - table              [str]: Name of the table 
            - where_ [list(dict, str, list)]: List of conditions defining elements to be deleted. The structure of this
                                        variable follows the scheme below: 
                                        [{
                                            "object"  : #Define the attribute name of an element, 
                                            "operator": #Define an operator defined in python syntax but provided inside a string 
                                            "value"   : #A value which close the conditional statement 
                                        }, 
                                        logic_operator [str] (it may be : "and", "or", "not"...)
                                        ...
                                        The sequence of conditions has to follow logical rules otherwise it will probably raise an error.  
                                        ]
        """
        
        action = "DELETE FROM"+" "
        object = table 
        argument = "" 
        if where_ is not None: 
            argument += "WHERE"+" "
            for condition in where_: 
                if type(condition) == dict: 
                    sub_object = condition["object"]
                    operator   = self.to_SQL_type(condition["operator"], mode = "operator")
                    sub_value  = condition["value"]
                    if type(sub_value) == str: 
                        sub_value = "'"+sub_value+"'"
                    else: 
                        sub_value = str(sub_value)
                    argument += sub_object+operator+sub_value+" "
                if type(condition) == str: 
                    argument += self.to_SQL_type(condition, mode = "logic")+" "
                if type(condition) == list: 
                    argument += self.to_SQL_type(condition, mode="list")+" " 
        
        self.execute(action   = action, 
                     object   = object, 
                     argument = argument)
        self.connexion.commit() 
        return 
    
    def drop_table(self, 
                   table): 
        """ 
        Function allowing to drop a table from the database 

        Parameters: 
            - table [str]: Table name 
        
        Returns: 
            None 
        """

        action   = "DROP"
        object   = "TABLE"
        argument = table

        self.execute(action   = action, 
                     object   = object, 
                     argument = argument)
        self.connexion.commit()
        return 

    #=====================================================================================#
    # QUERY FUNCTIONS
    #=====================================================================================# 

    def select(self,               #https://www.w3schools.com/sql/sql_select.asp
               distinct   = False, #https://www.w3schools.com/sql/sql_distinct.asp
               columns    = ["*"], #column1, column2 ...
               table      = None, 
               where_     = None,  #https://www.w3schools.com/sql/sql_where.asp
               orderby_   = None,  #https://www.w3schools.com/sql/sql_orderby.asp
               ordering   = "ASC" # "DESC"
              ): 

        action = "SELECT"
        if distinct: 
            action += " "+"DISTINCT"
        
        object = ""
        for col in columns: 
            object += col+", "
        object = object[:-2]
        if "*" in columns: 
            object = "*"+" "
        object += "FROM"+" "+table

        argument = "" 
        if where_ is not None: 
            argument += "WHERE"+" "
            for condition in where_: 
                if type(condition) == dict: 
                    sub_object = condition["object"]
                    operator   = self.to_SQL_type(condition["operator"], mode = "operator")
                    sub_value  = condition["value"]
                    if type(sub_value) == str: 
                        sub_value = "'"+sub_value+"'"
                    else: 
                        sub_value = str(sub_value)
                    argument += sub_object+operator+sub_value+" "
                if type(condition) == str: 
                    argument += self.to_SQL_type(condition, mode = "logic")+" "
                if type(condition) == list: 
                    argument += self.to_SQL_type(condition, mode="list")+" " 
        if orderby_ is not None: 
            argument += "ORDER BY"+" "
            for col in orderby_: 
                argument += col+", "
            argument = argument[:-2]
            argument += " "+ordering

        iterator = self.execute(action = action, 
                                object = object, 
                                argument = argument)
        
        result_list = [x for x in iterator.fetchall()]
        return result_list



    



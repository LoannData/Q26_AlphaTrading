

class DATABASE: 

    def __init__(self): 

        self.db_model = "sqlite3"
        self.db_name  = "unamed"
        self.db_path  = "./"
        self.db = None 

        self.tables = list()

    
    def activate(self): 

        if self.db_model == "sqlite3": 
            from .db_methods.method_sqlite3 import SQL

        self.db = SQL()
    
    def connect(self): 

        self.db.connect_database(self.db_path+self.db_name)

    
    def create_table(self, 
                     name, 
                     structure): 
        
        self.db.create_table(name, structure) 
    
    def insert_element(self, 
                       table, 
                       value): 
        
        self.db.insert(table, value) 


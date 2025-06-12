import psycopg2 as pg_interface
import time
import jwt_tokens as jwt

POSTGRES_DATABASE_NAME = "rts_database"
HOST = "127.0.0.1"
PORT = 5432
USERNAME = "postgres"
PASSWORD = "password"
DB = "rts_database"
DSN_STRING = f'user={USERNAME} password={PASSWORD} dbname={DB} host={HOST} port={PORT}'

jwt_expiration_offset = "15778800" #in seconds

def run_query(q,params=(), has_results=False, commit=True,local_conn=None):
    if local_conn is None:
        local_conn = conn

    with local_conn.cursor() as cursor:
        if params == ():
            cursor.execute(q)
        else:
            cursor.execute(q,vars=params)
        if has_results == True:
            try:
                results = cursor.fetchall()
                return results
            except psycopg2.NoResults:
                return []
    if commit:
        conn.commit()

def init(return_conn=False):
    connected = False
    while connected == False:
        try: local_conn = pg_interface.connect(dsn=DSN_STRING)
        except: time.sleep(0.01)
        else: connected = True

    if return_conn == False:
        global conn 
        conn = local_conn 
    else: return local_conn

    global private_key
    global public_key
    private_pem,public_pem = communication_layer.get_jwt_keys()
    private_key,public_key = jwt.convert_pems_to_objects(private_pem,public_pem)

def init_db():
    import hashlib

    local_conn = init_db_conn(return_conn=True)

    query = '''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        id_salt INTEGER NOT NULL,
        name TEXT NOT NULL,
        hashed_password TEXT NOT NULL,
        password_salt INTEGER NOT NULL
    );
    '''
    run_query(query,((hashlib.sha512(('global').encode("utf-8"))).hexdigest(),),local_conn=local_conn)

    local_conn.close()

    f = open("/dedicated_server/jwt_keys","x")
    f.close()
    f = open("/dedicated_server/jwt_keys","r")
    text = f.read()
    f.close()
    text.split(",,,")
    if float(text[0]) >= time.time():
        f = open("/dedicated_server/jwt_keys","w")
        f.write('')
        f.close()
        private_key,public_key,private_pem,public_pem = jwt.generate_rsa_keys()
        add_jwt_keys(private_pem,public_pem,jwt_expiration_offset)

def get_entries(table,columns,search_keywords,boolean="AND"):
    #create the query
    query = f"SELECT * FROM {table} WHERE {columns[0]} = \'{search_keywords[0]}\'"

    if len(columns) != 1:
        for i in range(len(columns)):
            if i == 0: 
                continue
            query += " " + boolean + f" {columns[i]} = {search_keywords[i]}"
    return run_query(query,has_results=True)


def get_all_entries(table):
    query = f"select * from {table}"
    return run_query(query,has_results=True)

def add_jwt_keys(new_private_key,new_public_key,jwt_expiration_offset):
    f = open("/dedicated_server/jwt_keys",'a')
    f.write(str(time.time() + jwt_expiration_offset) + ",,," + new_private_key + ",,," + new_public_key)
    f.close()


def add_entry(table,column_values : tuple):
    query = f"INSERT INTO {table} \n VALUES ("
    for i in range(len(column_values)):
        query += "%s"
        if i != (len(column_values)-1):
            query += ", "
    query += ")"
    run_query(q=query,params=column_values)

def get_jwt_keys():
    f = open("/dedicated_server/jwt_keys","r")
    text = f.read()
    f.close()
    text.split(",,,")
    return text[1],text[2]
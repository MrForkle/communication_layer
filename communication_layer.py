import psycopg2 as pg_interface
from psycopg2 import sql
import time
import jwt_tokens
import jwt

POSTGRES_DATABASE_NAME = "rts_database"
HOST = "db"
PORT = 5432
USERNAME = "postgres"
PASSWORD = "password"
DB = "rts_database"
DSN_STRING = f'user={USERNAME} password={PASSWORD} dbname={DB} host={HOST} port={PORT}'

jwt_key_expiration_offset = 15778800.0 #in seconds
jwt_token_expiration_offset = 604800 #in seconds

jwt_keys_path = "/dedicated_server/jwt_keys/jwt_keys.txt"

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
        local_conn.commit()

def init(return_conn=False,call_get_jwt_keys=True):
    connected = False
    while connected == False:
        try: local_conn = pg_interface.connect(dsn=DSN_STRING)
        except:
            print("Could not connect to DB. Sleeping.",flush=True)
            time.sleep(1)
        else: connected = True

    if return_conn == False:
        global conn 
        conn = local_conn 
    else: return local_conn

    if call_get_jwt_keys:
        global private_key
        global public_key
        private_pem,public_pem = get_jwt_keys()
        private_key,public_key = jwt_tokens.convert_pems_to_objects(private_pem,public_pem)

def init_db():
    import hashlib

    local_conn = init(return_conn=True,call_get_jwt_keys=False)

    query = '''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        id_salt INTEGER NOT NULL,
        name TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        password_salt INTEGER NOT NULL
    );
    '''
    run_query(query,((hashlib.sha512(('global').encode("utf-8"))).hexdigest(),),local_conn=local_conn)

    local_conn.close()

    try:
        f = open(jwt_keys_path,"x")
        f.close()
    except:
        pass
    f = open(jwt_keys_path,"r")
    text = f.read()
    f.close()
    text = text.split(",,,")
    if text == [] or len(text) != 2:
        set_jwt_key_file()
    elif float(text[0]) >= time.time():
        set_jwt_key_file()

def set_jwt_key_file():
    f = open(jwt_keys_path,"w")
    f.write('')
    f.close()
    private_key,public_key,private_pem,public_pem = jwt_tokens.generate_rsa_keys()
    add_jwt_keys(private_pem,public_pem,jwt_key_expiration_offset)

def get_entries(table,columns,search_keywords,boolean="AND"):
    #create the query
    query = ""
    if len(columns) != 1:
        for i in range(len(columns)):
            if i == 0: 
                continue
            query += " " + boolean + f" {columns[i]} = {search_keywords[i]}"
    query = sql.SQL("select from {table} WHERE {column} = %s \n" + query).format(
        table=sql.Identifier(table),
        column=sql.Identifier(columns)
        )
    return run_query(query,params=(columns[0],search_keywords[0]),has_results=True)


def get_all_entries(table):
    query = "select * from %s"
    return run_query(query,params=(table,),has_results=True)

def add_jwt_keys(new_private_key,new_public_key,jwt_key_expiration_offset):
    f = open(jwt_keys_path,'a')
    f.write(str(time.time() + jwt_key_expiration_offset) + ",,," + new_private_key + ",,," + new_public_key)
    f.close()


def add_entry(table,column_values : tuple):
    query = ""
    for i in range(len(column_values)):
        query += "%s"
        if i != (len(column_values)-1):
            query += ", "
    query += ")"
    query = sql.SQL("insert into {table} \n VALUES (" + query).format(table=sql.Identifier(table))
    run_query(q=query,params=column_values)

def get_jwt_keys():
    f = open(jwt_keys_path,"r")
    text = f.read()
    f.close()
    text = text.split(",,,")
    return text[1],text[2]

def create_jwt_token(payload,expiration= time.time() + jwt_token_expiration_offset):
    expiration = str(expiration)
    payload["expiration"] = expiration
    encoded = jwt_tokens.encode(payload,private_key)
    return encoded

def verify_jwt_token(token,return_decoded=False):
    try:
        decoded = jwt_tokens.decode()
    except jwt.InvalidSignatureError:
        return jwt.InvalidSignatureError
    else:
        if return_decoded:
            return decoded
        else:
            return 0
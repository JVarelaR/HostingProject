import os, psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "mi_db"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password")
        )
    return conn

def insert_user(username, email):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insertamos el nuevo usuario
        cur.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (username, email)
        )
        
        conn.commit() #commit para guardar los cambios
        cur.close()
    except Exception as e:
        print(f"Error al insertar en la DB: {e}")
        if conn:
            conn.rollback() # Revierte cambios si hubo error
    finally:
        if conn:
            conn.close()
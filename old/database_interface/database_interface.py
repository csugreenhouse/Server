import psycopg2

"""
DATABASE HELPERS 
- functions to interact with the database   
"""
def generate_query(plant_height_m, plant_id):
    query = f"INSERT INTO HEIGHT_LOG (specimen_id, HEIGHT_CM) VALUES ({plant_id}, {plant_height_m});"
    return query

def execute_query(query):
    conn = psycopg2.connect(
        host="localhost",
        dbname="greenhouse",
        user="agmin",
        password="Grow-Big"
    )
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()    

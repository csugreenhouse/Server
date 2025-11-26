import psycopg2

"""
DATABASE HELPERS 
- functions to interact with the database   
"""
def generate_query(plant_height_m, plant_id):
    query = f"INSERT INTO HEIGHT_LOG (specimen_id, HEIGHT_CM) VALUES (plant_id, height_cm) VALUES ({plant_id}, {plant_height_m/100});"
    return query

def execute_query(query):
    conn = psycopg2.connect(
        host="localhost",
        dbname="greenhouse",
        user="agmin",
        password="Grow-Big"
    )
    cur = conn.cursor()
    cur.execute("Select * from height_log;")
    print(cur.fetchone)
    cur.close()
    conn.close()

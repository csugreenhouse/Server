import cv2
import os
import importlib
from pathlib import Path
import pytest
import psycopg2

ROOT = Path(__file__).resolve().parents[2]  # repo root (/srv/samba/Server)
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent



def test_species_seed_data_exists():
    """
    Verifies that the test database is reachable
    and that seed species data was loaded.
    """
    conn = psycopg2.connect(
    dbname="test_greenhouse",
        user="greenhouse_test_user",
        password="greenhouse_test_pass",
        host="localhost",
        port=5432,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT scientific_name, common_name
                FROM species
                ORDER BY species_id;
                """
            )
            rows = cur.fetchall()

        # Basic sanity checks
        assert len(rows) == 3

        scientific_names = [row[0] for row in rows]

        assert "Lactuca sativa (Truchas)" in scientific_names
        assert "Lactuca sativa (Little Gem)" in scientific_names
        assert "Ocimum basilicum" in scientific_names

    finally:
        conn.close()
        
def test_plant_data_exists():
    """
    Verifies that the test database is reachable
    and that seed plant data was loaded.
    """
    conn = psycopg2.connect(
    dbname="test_greenhouse",
        user="greenhouse_test_user",
        password="greenhouse_test_pass",
        host="localhost",
        port=5432,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT plant_id, species_id
                FROM plant
                ORDER BY plant_id;
                """
            )
            rows = cur.fetchall()

        # Basic sanity checks
        assert len(rows) == 6

        plant_ids = [row[0] for row in rows]

        assert 1 in plant_ids
        assert 2 in plant_ids
        assert 3 in plant_ids
        assert 4 in plant_ids
        assert 5 in plant_ids
        assert 6 in plant_ids

    finally:
        conn.close()
        
def test_get_tag_information_from_database():
    """
    Verifies that get_tag_information_from_database
    returns correct data for a known tag_id.
    """
    
    conn = psycopg2.connect(
    dbname="test_greenhouse",
        user="greenhouse_test_user",
        password="greenhouse_test_pass",
        host="localhost",
        port=5432,
    )
    
    database_util = importlib.import_module("database.database_util")
    
    tag_id = 4  # Known tag_id in the test database

    result = database_util.get_tag_information_from_database(conn, tag_id)
    
    assert result is not None
    assert len(result) == 1  # Expecting one record for tag_id 4

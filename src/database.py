import pymysql

def get_table_structure(db_config, table_name='leads'):
    try:
        connection = pymysql.connect(**db_config, charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
        connection.close()
        return columns
    except Exception as e:
        print(f"Error fetching table structure: {str(e)}")
        return []


def verify_database_connection(db_config):
    try:
        connection = pymysql.connect(**db_config, charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        connection.close()
        return True
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False

def fetch_leads(db_config):
    try:
        connection = pymysql.connect(**db_config, charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM leads")
            leads = cursor.fetchall()
        connection.close()
        return leads
    except Exception as e:
        print(f"Error fetching leads: {str(e)}")
        return []

def update_lead(db_config, lead):
    try:
        connection = pymysql.connect(**db_config, charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s = %%s' % key for key in lead.keys()])
            query = f"UPDATE leads SET {placeholders} WHERE id = %s"
            cursor.execute(query, list(lead.values()) + [lead['id']])
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating lead: {str(e)}")
        return False

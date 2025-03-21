from datetime import datetime, timedelta
import psycopg2
import os

# Database connection parameters
db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def create_table():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # Create the app_details table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_details (
        id SERIAL PRIMARY KEY,
        application_name VARCHAR(255) NOT NULL,
        app_key VARCHAR(255) NOT NULL,
        app_id VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) NOT NULL,
        expiryDate TIMESTAMP,
        updateDate TIMESTAMP
    )
    """)
    
    # Commit the transaction
    conn.commit()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    print("Table created successfully.")

def insert_app_details(application_name, app_key, app_id, status):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Insert the app details into the table
        insert_query = """
        INSERT INTO app_details (application_name, app_key, app_id, status)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(insert_query, (application_name, app_key, app_id, status))
        
        # Commit the transaction
        conn.commit()
        print("App details inserted successfully.")
        
    except (Exception, psycopg2.Error) as error:
        print("Error while inserting app details:", error)
        
    finally:
        # Close the database connection
        if conn:
            cur.close()
            conn.close()

def fetch_app_details():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Fetch the first 5 rows of data from the app_details table
        # Calculate the date 5 days ago
        five_days_ago = datetime.now() - timedelta(days=5)
        
        # Fetch the application_name, app_key, and app_id where status is 'active' and created_at is more than 5 days ago
        cur.execute("""
        SELECT application_name, app_key, app_id 
        FROM app_details 
        WHERE status = 'active' AND created_at < %s
        LIMIT 1
        """, (five_days_ago,))
        
        rows = cur.fetchall()
        
        # Print the first 5 rows of data
        for row in rows:
            print(row)

        return rows    
        
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching app details:", error)
        return None
    
    finally:
        # Close the database connection
        if conn:
            cur.close()
            conn.close()

def deactivate_app_details(app_key, app_id):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        current_date = datetime.now()
        expiry_date = current_date + timedelta(days=180)
        # Update the status to 'deactive' based on app_key and app_id
        update_query = """
        UPDATE app_details
        SET status = 'deactive',
        updateDate = %s, expiryDate = %s
        WHERE app_key = %s AND app_id = %s
        """
        cur.execute(update_query, (current_date,expiry_date,app_key, app_id))
        
        # Commit the transaction
        conn.commit()
        print("App details deactivated successfully.")
        
    except (Exception, psycopg2.Error) as error:
        print("Error while deactivating app details:", error)
        
    finally:
        # Close the database connection
        if conn:
            cur.close()
            conn.close()

def main():
    # Example usage
    create_table()
    # Insert provided data into the table
    # insert_app_details("WIG - PTE - Maersk DT 028", "a15df103-2f36-4932-80ec-1bcea1023072", "2739", "active")
    # deactivate_app_details("a15df103-2f36-4932-80ec-1bcea1023072", "2739")
    fetch_app_details()

if __name__ == "__main__":
    main()
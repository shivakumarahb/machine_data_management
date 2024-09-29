import asyncpg
import asyncio
import logging

# Database connection details
DB_HOST = "localhost"
DB_NAME = "machine_info"  
DB_USER = "shiva"        
DB_PASS = "password"    
DB_PORT = 5432  

logging.basicConfig(level=logging.INFO)

async def create_tables():
    # Connect to the database
    conn = await asyncpg.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    
    # SQL commands to create tables
    create_machine_table = """
    CREATE TABLE IF NOT EXISTS machine (
        machine_id INT PRIMARY KEY,  
        machine_name VARCHAR(255) NOT NULL, 
        tool_capacity INT NOT NULL  
    );
    """
    
    create_tool_table = """
    CREATE TABLE IF NOT EXISTS tool (
        tool_id SERIAL PRIMARY KEY,  
        machine_id INT REFERENCES machine(machine_id) ON DELETE CASCADE,  
        tool_offset FLOAT NOT NULL,  
        feedrate FLOAT NOT NULL,  
        update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
    );
    """
    
    create_tool_usage_table = """
    CREATE TABLE IF NOT EXISTS tool_usage (
        usage_id SERIAL PRIMARY KEY,
        machine_id INT REFERENCES machine(machine_id) ON DELETE CASCADE,
        tool_in_use INT NOT NULL,
        update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_axis_table = """
    CREATE TABLE IF NOT EXISTS axis (
        axis_id SERIAL PRIMARY KEY, 
        machine_id INT REFERENCES machine(machine_id) ON DELETE CASCADE,  
        axis_name VARCHAR(255) NOT NULL CHECK (axis_name IN ('X', 'Y', 'Z', 'A', 'C')),
        max_acceleration DECIMAL(10, 3) NOT NULL,
        max_velocity DECIMAL(10, 3) NOT NULL,
        UNIQUE (machine_id, axis_name) 
    );
    """
    
    create_axis_data_table = """
    CREATE TABLE IF NOT EXISTS axis_data (
        axis_data_id SERIAL PRIMARY KEY,  
        axis_id INT REFERENCES axis(axis_id) ON DELETE CASCADE,  
        actual_position DECIMAL(10, 3) NOT NULL, 
        target_position DECIMAL(10, 3) NOT NULL,  
        distance_to_go DECIMAL(10, 3) GENERATED ALWAYS AS (target_position - actual_position) STORED,
        homed BOOLEAN NOT NULL,  
        acceleration DECIMAL(10, 3) NOT NULL, 
        velocity DECIMAL(10, 3) NOT NULL, 
        update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
    );
    """
    
    create_index_axis_machine_id = """
    CREATE INDEX IF NOT EXISTS idx_axis_machine_id ON axis (machine_id);
    """
    
    create_index_axis_data_axis_id = """
    CREATE INDEX IF NOT EXISTS idx_axis_data_axis_id ON axis_data (axis_id);
    """

    # Execute the SQL commands
    await conn.execute(create_machine_table)
    await conn.execute(create_tool_table)
    await conn.execute(create_tool_usage_table)
    await conn.execute(create_axis_table)
    await conn.execute(create_axis_data_table)
    await conn.execute(create_index_axis_machine_id)
    await conn.execute(create_index_axis_data_axis_id)

    logging.info("Tables created successfully.")
    
    # Close the connection
    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_tables())

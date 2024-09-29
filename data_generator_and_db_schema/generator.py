import asyncpg
import random
import sys
import time
from datetime import datetime, timedelta
import logging
import asyncio
logging.basicConfig(level=logging.INFO)


DB_HOST = "localhost"
DB_NAME = "machine_info"  
DB_USER = "shiva"        
DB_PASS = "password"    
DB_PORT = 5432  



class Data_generator:
    def __init__(self):
    # Declaring these values here as they are constant & also can be taken by input when required    
        self._max_acceleration = 200
        self._max_velocity     = 60
        self._axes_names  = ['X', 'Y', 'Z', 'A', 'C']
        self._tool_capacity = 24   

    async def generate_tool_data(self, machine_id):
        tool_offset = random.uniform(5, 40) 
        feedrate = random.uniform(0, 20000)   
        return (machine_id, tool_offset, feedrate)
    
    async def generate_tool_in_use(self, machine_id): 
        tool_in_use = random.randint(1, 24)    
        return (machine_id, tool_in_use)

    async def generate_axis_data(self, axis_name):
        actual_position = random.uniform(-190, 190)
        target_position = random.uniform(-190, 191)
        homed = random.choice([True, False])
        acceleration = random.uniform(0, 150)
        velocity = random.uniform(0, 80)

        #return (axis_name, actual_position, target_position, homed, acceleration, velocity)
        return [
        axis_name,
        float(actual_position),
        float(target_position),
        bool(homed),
        float(acceleration),
        float(velocity)
    ]


class Database_Writer:
    def __init__(self):
        self._pool = None
    
    async def connect_db(self):
        try:
            self._pool = await asyncpg.create_pool(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
            logging.info('connected to database')
        except Exception as e:
            logging.warning(f'error connecting to database :  {e}')
            
    
    async def insert_machine_data(self, machine_id, machine_name, tool_capacity):
        async with self._pool.acquire() as connection:
            await connection.execute("""
            INSERT INTO machine (machine_id, machine_name, tool_capacity)
            VALUES ($1, $2, $3)
            ON CONFLICT (machine_id) DO NOTHING
        """, machine_id, machine_name, tool_capacity)

    async def insert_tool_data(self, tool_data):
        async with self._pool.acquire() as connection:
            await connection.execute("""
            INSERT INTO tool (machine_id, tool_offset, feedrate)
            VALUES ($1, $2, $3)
        """, tool_data[0], tool_data[1], tool_data[2] )
        
    async def insert_tool_in_use(self, data):
        async with self._pool.acquire() as connection:
            await connection.execute("""
            INSERT INTO tool_usage (machine_id, tool_in_use)
        VALUES ($1, $2)
        """, data[0], data[1])
    
    async def insert_axis(self, machine_id, axis_name, max_acceleration, max_velocity):
        async with self._pool.acquire() as connection:
            await connection.execute("""
            INSERT INTO axis (machine_id, axis_name, max_acceleration, max_velocity)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (machine_id, axis_name) DO NOTHING
        """, machine_id, axis_name, max_acceleration, max_velocity) 

    async def insert_axis_data(self, machine_id, axis_name, axis_data):
        async with self._pool.acquire() as connection:
            axis_id_row = await connection.fetchrow("""
                SELECT axis_id FROM axis WHERE machine_id = $1 AND axis_name = $2
            """, machine_id, axis_name)

            # Check if we retrieved an axis_id
            if axis_id_row is None:
                logging.error(f"Axis with machine_id {machine_id} and axis_name {axis_name} not found.")
                return  # Exit if the axis_id doesn't exist

            axis_id = axis_id_row['axis_id']

            await connection.execute("""
            INSERT INTO axis_data (axis_id, actual_position, target_position, homed, acceleration, velocity)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, axis_id, axis_data[1], axis_data[2], axis_data[3], axis_data[4], axis_data[5] )
            


async def machine_data(no_of_machines, generator, data_base_writer):
    # writing to machine table at start and once cause they dont update frequently
    
    for machine_id in range(81258856, 81258856 + no_of_machines):
        await data_base_writer.insert_machine_data(machine_id=machine_id, machine_name=str(machine_id), tool_capacity=generator._tool_capacity)
    logging.info(f"inserted machine info for {no_of_machines} machines")

    
async def axis(no_of_machines, generator, data_base_writer):
    # writing to machine table at start and once cause they dont update frequently
    for machine_id in range(81258856, 81258856 + no_of_machines):
        for axis_name in generator._axes_names:
            await data_base_writer.insert_axis(machine_id, axis_name, generator._max_acceleration, generator._max_velocity)
    logging.info(f"inserted axis info for {no_of_machines} machines")
        

async def tool_data(interval, no_of_machines, generator, data_base_writer):
    try:
        while True:
            for machine_id in range(81258856, 81258856 + no_of_machines):
                data = await generator.generate_tool_data(machine_id)
                await data_base_writer.insert_tool_data(data)
            logging.info("inserterd to tool_data")
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
            pass
    
async def tool_in_use(interval, no_of_machines, generator, data_base_writer):
    try:
        while True:
            for machine_id in range(81258856, 81258856 + no_of_machines):
                data = await generator.generate_tool_in_use(machine_id)
                await data_base_writer.insert_tool_in_use(data)
            logging.info("inserterd to tool_in_use")
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
            pass
        

async def insert_to_axis(interval, no_of_machines, generator, data_base_writer):
    count = 0
    start_time = time.time()
    try:
        while True:
            for machine_id in range(81258856, 81258856 + no_of_machines):
                for axis_name in generator._axes_names:
                    data = await generator.generate_axis_data(axis_name)
                    await data_base_writer.insert_axis_data(machine_id, axis_name, data)
            logging.info("inserterd to axis")
            count+=1
            if time.time() - start_time >1 :
                logging.info(f'no of insert for second {count}')
                count = 0
                start_time = time.time()
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
            logging.error(f'ctrl-c : stopped inserting')
        
        

async def main():
    no_of_machines = 20
    generator = Data_generator()
    data_base_writer = Database_Writer()
    await data_base_writer.connect_db()
    
    await asyncio.gather(
        machine_data(no_of_machines, generator, data_base_writer),
        axis(no_of_machines, generator, data_base_writer),
        tool_data(10, no_of_machines, generator, data_base_writer), # pushes for every 15 minutes interval
        tool_in_use(5, no_of_machines, generator, data_base_writer), # pushes for every 5 minutes interval
        insert_to_axis(0.01, no_of_machines, generator, data_base_writer) # pushes for every 0.1 seconds interval
    )
    
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error('ctrl-c called exiting')
        sys.exit()

        

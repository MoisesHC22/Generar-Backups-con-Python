import os.path
import pymongo
import json
from datetime import datetime
import bson
import win32net

# Conexión con la base de datos
client = pymongo.MongoClient("mongodb://192.168.4.16:6001/")

# La base de datos que se usará
db_name = "Company"
db = client[db_name]

# Directorio en donde se guardará los archivos de copia de seguridad
backup_dir = r"\\192.168.4.14\Respaldos\Python"

username = "Administrator"
password = "Pqssw0rd"

net_use_name = "Respaldos"
try:
    win32net.NetUseAdd(None, 2, {'local': None, 'remote': backup_dir, 'password': password, 'username': username, 'use': net_use_name})

    #Crear la carpeta de la fecha del backup
    fecha = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    backup_fecha_dir = os.path.join(backup_dir, fecha)
    os.makedirs(backup_fecha_dir, exist_ok=True)

    #Iterar sobre las colecciones de la base de datos
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        backup_db_dir = os.path.join(backup_fecha_dir, db_name)
        os.makedirs(backup_db_dir, exist_ok=True)

    # Realizar copia de seguridad de los registros
    backup_records_file = os.path.join(backup_db_dir, f"{collection_name}.bson")
    with open(backup_records_file, "wb") as file:
        for document in collection.find():
            file.write(bson.BSON.encode(document))

    print("Copia de seguridad realizada con éxito")


    # Realizar copia de seguridad de las configuraciones de la colleccion
    config_data = {
        'indexes': collection.index_information(),
        'uuid': str(collection.uuid),
        'collectionName': collection_name,
        'type': 'collection'
    }
    backup_metadata_file = os.path.join(backup_db_dir, f"{collection_name}.metadata.json")
    with open(backup_metadata_file, "w") as config_file:
        json.dump(config_data, config_file)

    print("Copia de seguridad de configuraciones realizadas con éxito")

except Exception as e:
    print(f"Error: {e}")



finally:
    client.close()

    win32net.NetUseDel(backup_dir, 0, 0)

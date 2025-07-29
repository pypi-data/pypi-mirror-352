from datetime import datetime
from pymongo.database import Database


class MongoParameters:
    def __init__(self, mongo_db: Database, collection_name):
        self.database = mongo_db
        self.collection_name = collection_name
        self.temp_col = None

    @property
    def current_collection(self):
        return self.database[self.collection_name]

    def create_temp_col(self):
        # create a new collection in case of error
        temp_collection_name = f'{self.collection_name}_temp'
        self.database.drop_collection(temp_collection_name)
        self.temp_col = self.database.create_collection(temp_collection_name)
        return self.temp_col

    def backup_existing_col_and_swap_temp_to_production(self):
        current_col = self.database.get_collection(self.collection_name)
        if current_col.count_documents({}) > 0:
            current_col.rename(f'{self.collection_name}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}')
        self.temp_col.rename(self.collection_name)

    def remove_redundant_parameter_backup(self, collections_to_keep):
        parameters_list = self.database.list_collection_names()
        for parameter_name in list(parameters_list):
            if not parameter_name.startswith(self.collection_name) or not parameter_name.split('_')[-1].isdigit():
                parameters_list.remove(parameter_name)
        parameters_list.sort()
        if len(parameters_list) >= collections_to_keep:
            for i in range(0, len(parameters_list) - collections_to_keep):
                self.database[parameters_list[i]].drop()

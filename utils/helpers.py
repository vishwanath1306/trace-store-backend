import glob
import json
import random
import uuid


def generate_id():
    return str(uuid.uuid4())


def extract_sqlalchemy_errors(error: str) -> str:
    mes = error.split(')')[1]
    mes = mes.split('(')[1]
    mes = mes.split(',')
    mes = bytes(mes[1], "utf-8").decode("unicode_escape")
    return mes

def generate_random_float_array():
    return [random.uniform(10,15) for _ in range(10)]

def store_file(file, file_path):
    file.save(file_path)

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def return_index_name_from_filename(filename: str) -> str:
    last_file = filename.split('/')[-1]
    index_name = last_file.split('.')[0]
    return f"index-{index_name}"


def construct_app_to_embedding(app_name: str, embedding: str) -> str:
    return f"{app_name}_{embedding}"

def get_all_json(folder_path: str):
    return glob.glob(f"{folder_path}/*.json")

def read_json_file(file_path: str):
    with open(file_path, 'r') as file:
        return json.load(file)
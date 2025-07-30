from pydomo import Domo
from io import StringIO
import pandas as pd
import os

CLIENT_ID = os.environ["DOMO_CLIENT_ID"]
CLIENT_SECRET = os.environ["DOMO_CLIENT_SECRET"]

# Conecta as credenciais do Domo
domo = Domo(CLIENT_ID, CLIENT_SECRET, api_host='api.domo.com')
datasets = domo.datasets
streams = domo.streams


''' Funções para interação com DOMO '''


# Importa do domo e salva em um csv
def import_from_domo_to_csv(dataset_id, csv_file_path):
    csv_file_path = csv_file_path
    include_csv_header = True
    csv_file = datasets.data_export_to_file(dataset_id, csv_file_path, include_csv_header)
    csv_file.close()

    return print(f'Downloaded data from DataSet {dataset_id}.')


# Importa do Domo e salva em Pandas DataFrame
def import_from_domo_to_df(dataset_id):
    include_csv_header = True
    csv_download = datasets.data_export(dataset_id, include_csv_header)
    domo.logger.info(f'Downloaded data as a file from DataSet {dataset_id}')

    return pd.read_csv(StringIO(csv_download))


# Cria Dataset no Domo de um Pandas Dataframe
def create_dataset_in_domo(dataset, domo_name):
    dataset_id = domo.ds_create(dataset, domo_name)
    return dataset_id, print(f'{domo_name} dataframe created  in Domo!')


# Replace/Append .csv para um Dataset no domo (update_method = REPLACE ou APPEND)
def update_file_in_domo(dataset_id, csv_file_path,  update_method='APPEND'):
    datasets.data_import_from_file(dataset_id, csv_file_path, update_method=update_method)

    return f'File updated with {update_method} method!'


# Replace/Append .csv para um Dataset no domo
def update_dataset_in_domo(dataset_id, dataset_to_update):
    domo.ds_update(dataset_id, dataset_to_update)

    return f'Dataset updated!'

def get_stream_list(stream_list_limit=200000):
    stream_list = streams.list(stream_list_limit, 0)
    return stream_list


def get_stream_by_dataset_id(dataset_id):
    stream_list = get_stream_list()
    dataset_streams = [stream for stream in stream_list if stream['dataSet']['id'] == dataset_id]
    if len(dataset_streams) == 1:
        return dataset_streams[0]
    else:
        no_stream_found_string = 'No stream found for dataset {}'.format(dataset_id)
        return no_stream_found_string


def get_stream_info_by_id(dataset_id):
    dataset_stream = get_stream_by_dataset_id(dataset_id)
    retrieved_stream = streams.get(dataset_stream['id'])
    # retrieved_stream = streams.get(dataset_stream['id'])
    return retrieved_stream


def run_dataset(dataset_id):
    try:
        print(f'Searching ID from Dataset ID: {dataset_id}...')
        dataset_stream = get_stream_by_dataset_id(dataset_id)
        print(f'ID: {dataset_id} found...')
        dataset_stream_id = dataset_stream['id']
        print('Initializing update, please wait!...')
        retrieved_stream = get_stream_info_by_id(dataset_id)
        dataset_name = retrieved_stream['dataSet']['name']
        streams.create_execution(dataset_stream_id)
        print(f'Dataset {dataset_name}, ID={dataset_stream_id}....')
        print(f'Please check ind Domo')
        print(f'https://iron-fit.domo.com/datasources/{dataset_id}/details/overview')
    except Exception as e:
        logging.error(e)
        raise Exception(e)
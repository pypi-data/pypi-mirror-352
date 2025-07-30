import datetime
import pandas as pd
from datetime import datetime, timedelta
import boto3
import awswrangler as wr
import time
import os


import warnings
warnings.simplefilter("ignore")
# aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
# aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

session = boto3.Session(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name="us-east-1")

athena_cache_settings = {'max_cache_seconds': 900,
                         'max_cache_query_inspections': 500}


def get_timestamp():
    timestamp = datetime.utcnow() - timedelta(hours=3)
    return timestamp


def send_file_to_s3(local_file, s3_path, file_name):
    wr.s3.upload(local_file, f's3://{s3_path}/{file_name}')
    print('Arquivo enviado para S3 com sucesso!')


def send_dataset_to_s3(dataset, file_name, bucket_folder, folder_name, sep=';'):
    if 'csv' in file_name:
        dataset.to_csv(f"s3://{bucket_folder}/{folder_name}/{file_name}", sep=sep, encoding='utf-8',
                       storage_options={'key': os.environ['AWS_ACCESS_KEY_ID'],
                                        'secret': os.environ['AWS_SECRET_ACCESS_KEY']})
    else:
        dataset.to_excel(f"s3://{bucket_folder}/{folder_name}/{file_name}", index=False,
                         storage_options={'key': os.environ['AWS_ACCESS_KEY_ID'],
                                          'secret': os.environ['AWS_SECRET_ACCESS_KEY']})

    print(f'{file_name} adicionado ao S3\n')
    return


def download_file_from_s3_to_dataset(arquivo, bucket_name, folder_name, sep=';', sheet_name=0):
    s3 = session.resource('s3')
    my_bucket = s3.Bucket(bucket_name)

    files = []
    df_final = pd.DataFrame()
    for object_summary in my_bucket.objects.filter(Prefix=folder_name):
        if arquivo in object_summary.key:
            print(object_summary.key)
            if 'homologacao' in object_summary.key:
                continue
                files.pop(-1)
                files.append(object_summary.key)
            else:
                files.append(object_summary.key)
            if 'xlsx' in object_summary.key:
                df = wr.s3.read_excel(f's3://{bucket_name}/{object_summary.key}', dtype={'CPF': str, 'cpf': str},
                                      boto3_session=session, use_threads=True, engine='openpyxl', sheet_name=sheet_name)
            elif 'json' in object_summary.key:
                df = wr.s3.read_json(f's3://{bucket_name}/{object_summary.key}', dtype={'CPF': str, 'cpf': str},
                                      boto3_session=session, use_threads=True)
            else:
                df = wr.s3.read_csv(f's3://{bucket_name}/{object_summary.key}', dtype={'CPF': str, 'cpf': str},
                                    boto3_session=session, use_threads=True, sep=sep, encoding='latin')
                # df = pd.read_csv(f's3://{bucket_name}/{object_summary.key}', sep=',', encoding='latin',
                #                  dtype={'cpf': str},
                #                  storage_options={'key': os.environ['AWS_ACCESS_KEY_ID'],
                #                                   'secret': os.environ['AWS_SECRET_ACCESS_KEY']})
            df['origem'] = object_summary.key.removeprefix(f'{folder_name}/')
            df_final = pd.concat([df_final, df], ignore_index=True, sort=True)
            time.sleep(2)
    print(f'Finalizado! {df_final["origem"].nunique()} arquivo (s) foi/foram carregados!\n')
    return df_final


def send_json_to_s3(df, bucket_name, foler_name, file_name=None):

    df['DT_ENVIO'] = get_timestamp()

    wr.s3.to_json(
        df=df,
        path=f's3://{bucket_name}/{foler_name}/{file_name}.json',
        dataset=False,
        concurrent_partitioning=True,
        use_threads=True,
        boto3_session=session,
        orient='records',
        date_format='iso')

    print(f'Tabela {foler_name} adicionada ao S3\n')
    return


def get_last_last_modified_file(bucket_name, folder_name, sep=';', sheet_name=0):
    s3_client = boto3.client('s3')
    all_files = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)['Contents']
    latest_file = max(all_files, key=lambda x: x['LastModified'])
    file_path = latest_file['Key']
    file_name = latest_file['Key'].removeprefix(f'{folder_name}/')
    print(f'\nBaixando arquivo {file_name}!')

    if 'xlsx' in file_name:
        df = wr.s3.read_excel(f's3://{bucket_name}/{file_path}', dtype={'CPF': str, 'cpf': str},
                              boto3_session=session, use_threads=True, engine='openpyxl', sheet_name=sheet_name)
    elif 'json' in file_name:
        df = wr.s3.read_json(f's3://{bucket_name}/{file_path}', dtype={'CPF': str, 'cpf': str},
                             boto3_session=session, use_threads=True)
    elif 'csv' in file_name:
        df = wr.s3.read_csv(f's3://{bucket_name}/{file_path}', dtype={'CPF': str, 'cpf': str},
                            boto3_session=session, use_threads=True, sep=sep, encoding='latin')

    print(f'Arquivo {file_name} carregado com sucesso!')
    return df


''' Funções para enviar arquivo parquet e criar tabela no Glue Catalogue '''


def send_parquet_partioned_to_s3(dataset, bucket_name, folder_name=None, database=None, mode="append",
                                 table_name=None, partition_cols=None):

    dataset['envio_s3'] = get_timestamp()

    if folder_name is None:
        s3_uri = f's3://{bucket_name}'
    else:
        if table_name is None:
            s3_uri = f's3://{bucket_name}/{folder_name}'
        else:
            s3_uri = f's3://{bucket_name}/{folder_name}/{table_name}'

    wr.s3.to_parquet(
        df=dataset,
        path=s3_uri,
        index=False,
        dataset=True,
        # max_rows_by_file=10000,
        database=database,
        table=table_name,
        # compression='zstd',
        compression='snappy',
        # dtype=dict
        mode=mode,
        catalog_versioning=True,
        partition_cols=partition_cols,
        concurrent_partitioning=True,
        use_threads=True,
        boto3_session=session)

    return print(f'{table_name} adicionado ao S3\n')


def send_parquet_to_s3(dataset, bucket_name, folder_name, mode="append", database=None, table_name=None,
                       partition_cols=None):

    dataset['envio_s3'] = get_timestamp()

    if folder_name is None:
        s3_uri = f's3://{bucket_name}'
    else:
        if table_name is None:
            s3_uri = f's3://{bucket_name}/{folder_name}'
        else:
            s3_uri = f's3://{bucket_name}/{folder_name}/{table_name}'

    wr.s3.to_parquet(
        df=dataset,
        path=s3_uri,
        index=False,
        dataset=True,
        # max_rows_by_file=10000,
        database=database,
        table=table_name,
        # dtype=dict
        mode=mode,
        # compression='zstd',
        compression='snappy',
        catalog_versioning=True,
        partition_cols=partition_cols,
        concurrent_partitioning=True,
        use_threads=True,
        boto3_session=session)

    return print(f'{table_name} adicionado ao S3\n')

# wr.s3.to_parquet(
#         df=dataset,
#         path=f's3://{bucket_name}/{folder_name}/{table_name}',
#         index=False,
#         dataset=True,
#         # max_rows_by_file=10000,
#         database=database,
#         table=table_name,
#         compression='zstd',
#         mode=mode,
#         catalog_versioning=True,
#         partition_cols=partition_cols,
#         concurrent_partitioning=True,
#         use_threads=True,
#         boto3_session=session)



def send_csv_to_s3(dataset, bucket_name, folder_name, mode=None, database=None, table_name=None,
                   partition_cols=None, sep=';'):

    if database is not None:
        dataset['envio_s3'] = get_timestamp()
        wr.s3.to_csv(
            df=dataset,
            path=f's3://{bucket_name}/{folder_name}/{table_name}',
            index=False,
            sep=sep,
            dataset=True,
            database=database,
            table=table_name,
            mode=mode,
            catalog_versioning=True,
            partition_cols=partition_cols,
            concurrent_partitioning=True,
            use_threads=True,
            boto3_session=session)
    else:
        wr.s3.to_csv(
            df=dataset,
            path=f's3://{bucket_name}/{folder_name}/{table_name}',
            index=False,
            index_label=False,
            use_threads=True,
            sep=sep,
            boto3_session=session)

    print(f'{table_name} adicionado ao S3\n')
    return


def download_csv_from_s3(path, filename):
    dataset = wr.s3.read_csv(f'{path}/{filename}', sep=';')
    print(f'Arquivo {filename} carregado com sucesso!')
    return dataset


def read_parquet_from_s3(bucket_folder, folder_name, file_name, columns=None):
    dataset = wr.s3.read_parquet(path=f's3://{bucket_folder}/{folder_name}/{file_name}',
                                 path_suffix='.parquet',
                                 use_threads=True,
                                 boto3_session=session,
                                 columns=columns)
    return dataset


def read_parquet_from_s3_with_filter(bucket_folder, folder_name, file_name, filters, columns=None):
    dataset = wr.s3.read_parquet(path=f's3://{bucket_folder}/{folder_name}/{file_name}',
                                 path_suffix='.parquet',
                                 # chunked=True,
                                 dataset=True,
                                 use_threads=True,
                                 boto3_session=session,
                                 columns=columns,
                                 pyarrow_additional_kwargs={"filters": filters})  # ('corporacao', '=', 'corporacao')
    return dataset


def get_max_updated_date_from_table(database, table, column):
    print(f"SELECT MAX({column}) FROM {table} AS max_date")
    max_updates_date = wr.athena.read_sql_query(boto3_session=session,
                                                database=database,
                                                athena_cache_settings=athena_cache_settings,
                                                use_threads=True,
                                                sql=f"SELECT MAX({column}) AS max_date FROM {table}")
    return max_updates_date


def remove_duplicates_from_table(database, table, table_view, column, order_by):
    sql = f'''CREATE OR REPLACE VIEW {table_view} AS
                WITH agendamentos_duplicados AS
                    (SELECT
                        *,
                        ROW_NUMBER() OVER(PARTITION BY {column} ORDER BY {order_by} DESC) AS contagem_registro 
                    FROM {table})
                SELECT
                    *
                FROM
                    agendamentos_duplicados
                WHERE
                    contagem_registro = 1'''
    retorno = wr.athena.start_query_execution(sql=sql,
                                              boto3_session=session,
                                              database=database,
                                              athena_cache_settings=athena_cache_settings,)
    print(f'Duplicados Removidos e Tabela {table_view} criada')
    return retorno


def run_query_in_athena(sql, database):
    query = wr.athena.read_sql_query(boto3_session=session,
                                     database=database,
                                     sql=sql,
                                     use_threads=True,
                                     athena_cache_settings=athena_cache_settings,)
    return query


def create_view_athena(sql, database):
    query = wr.athena.start_query_execution(boto3_session=session,
                                            database=database,
                                            sql=sql,
                                            athena_cache_settings=athena_cache_settings,)
    return query


def check_table_length(database, table):
    table_length = wr.athena.read_sql_query(boto3_session=session,
                                            database=database,
                                            use_threads=True,
                                            athena_cache_settings=athena_cache_settings,
                                            sql=f"SELECT count(*) AS table_legnth FROM {table}")
    return table_length.iloc[0, 0]


# def create_table_to_updadate(database, table, new_table, column, order_by):
def create_table_to_update(database, bucket, folder_name, table, update_table, col_update, col_drop,
                           partition_cols=None):

    try:
        dt_ultimo_registro = str(get_max_updated_date_from_table(database, update_table, col_update))[0:23]
        table_to_update = run_query_in_athena(f'SELECT * FROM {table}_update', database)
        data_to_update = wr.athena.read_sql_query(boto3_session=session,
                                                  database=database,
                                                  athena_cache_settings=athena_cache_settings,
                                                  use_threads=True,
                                                  sql=f''' SELECT
                                                                *
                                                             FROM
                                                                {table}
                                                             where 
                                                                {table}.{col_update} > timestamp '{dt_ultimo_registro}' 
                                                                ''')
    except Exception as e:
        dt_ultimo_registro = datetime.datetime(2015, 1, 1)
        table_to_update = pd.DataFrame()
        data_to_update = wr.athena.read_sql_query(boto3_session=session,
                                                  database=database,
                                                  athena_cache_settings=athena_cache_settings,
                                                  use_threads=True,
                                                  sql=f'''SELECT
                                                              *
                                                          FROM
                                                              {table}''')
        print(f'Tabela para update vazia, error: {e}')

    table_to_update = pd.concat([table_to_update, data_to_update], ignore_index=True)
    table_to_update.sort_values(by=[col_drop], ascending=False, inplace=True)
    table_to_update.drop_duplicates([col_drop], keep='last', inplace=True)
    table_to_update.drop(columns=['envio_s3'], inplace=True)

    send_parquet_to_s3(table_to_update, bucket,
                       folder_name=folder_name,
                       database=database,
                       table_name=update_table,
                       mode='overwrite',
                       partition_cols=partition_cols)

    return dt_ultimo_registro, table_to_update, data_to_update


def return_query_log_results(query_id):
    query_results = wr.athena.get_query_results(query_execution_id=query_id, boto3_session=session)
    return query_results


def remove_duplicates_and_add_emae(database, table, table_view, column, order_by, table_emae, column_emae):

    sql = f'''CREATE OR REPLACE VIEW {table_view} AS
                WITH atendimentos_duplicados AS
                    (SELECT
                        *,
                        ROW_NUMBER() OVER(PARTITION BY {table}.{column} ORDER BY {order_by} DESC) AS contagem_registro 
                    FROM 
                        {table})
                SELECT
                    *
                FROM
                    atendimentos_duplicados
                LEFT JOIN
                    {database}.{table_emae}
                ON
                    atendimentos_duplicados.{column} = {table_emae}.{column_emae} 
                WHERE 
                    atendimentos_duplicados.contagem_registro = 1'''

    wr.catalog.delete_column(database=database,
                             table=table_emae,
                             column_name='envio_s3',
                             boto3_session=session)

    retorno = wr.athena.start_query_execution(sql=sql,
                                              boto3_session=session,
                                              database=database,
                                              athena_cache_settings={'max_cache_seconds': 900,
                                                                     'max_cache_query_inspections': 500})
    print(f'Duplicados Removidos e resumos de EMAE adicionados Tabela {table_view}')

    # wr.catalog.delete_column(database=database,
    #                          table=table_view,
    #                          column_name='contagem_registro',
    #                          boto3_session=session)
    #
    # wr.catalog.delete_column(database=database,
    #                          table=table_view,
    #                          column_name='resumoemae_pa_cod',
    #                          boto3_session=session)

    return retorno


def delete_column_from_table(database, table, column):
    wr.catalog.delete_column(database=database,
                             table=table,
                             column_name=column,
                             boto3_session=session)


def drop_table(table, database):

    sql = f'DROP TABLE IF EXISTS {table};'

    retorno = wr.athena.start_query_execution(sql,
                                              boto3_session=session,
                                              database=database,
                                              athena_cache_settings={'max_cache_seconds': 900,
                                                                     'max_cache_query_inspections': 500})
    return retorno


def wait_for_query_to_complete(query_execution_id):
    athena_client = boto3.client('athena', region_name='us-east-1')
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            return status
        time.sleep(5)


def delete_s3_folder(bucket_name, folder_name):
    s3_client = boto3.client('s3')

    # Listar todos os objetos no prefixo especificado
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    if 'Contents' in response:
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]

        # Deletar os objetos listados
        delete_response = s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': objects_to_delete}
        )

        # Verificar se houve algum erro durante a exclusão
        if 'Errors' in delete_response:
            for error in delete_response['Errors']:
                print(f"Error deleting {error['Key']}: {error['Message']}")
        else:
            print(f"Folder '{folder_name}' and all its contents have been deleted successfully.")
    else:
        print(f"No objects found in the folder '{folder_name}'.")


def remove_duplicates_from_table_and_create_table(bucket, database, table, new_table, column, order_by):

    sql = f'''CREATE TABLE {new_table} WITH (
        format = 'parquet',
        external_location = 's3://{bucket}/{new_table}/',
        write_compression = 'SNAPPY')
        AS WITH nova_tabela AS (
            SELECT
                *,
                ROW_NUMBER() OVER(PARTITION BY {column} ORDER BY {order_by} DESC) AS contagem_registro
            FROM {table})
        SELECT * FROM nova_tabela WITH DATA '''

    retorno = wr.athena.start_query_execution(sql=sql,
                                              boto3_session=session,
                                              database=database,
                                              athena_cache_settings=athena_cache_settings,)

    retorno_ = wait_for_query_to_complete(retorno)
    print(f'{retorno_}...Duplicados Removidos e Tabela {new_table} criada!')
    return

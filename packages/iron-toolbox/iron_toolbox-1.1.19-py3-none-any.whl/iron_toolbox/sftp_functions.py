import io
import pandas as pd
import paramiko

''' Funções para conexão e download/upload de arquivos para SFTP '''


def connect_sftp(hostname, username, password):
    """
        Args:
            hostname: the remote host to read the file from
            username: the username to login to the remote host with
            password: the user password to login into the remote host
        """

    # open an SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    # read the file using SFTP
    sftp = client.open_sftp()
    print(f'{hostname} Conectado!')
    return sftp


def disconnect_sftp(client):
    client.close()
    print(f'SFTP Desconectado!')


def from_sftp_to_df(client_sftp, remote_path):
    with io.BytesIO() as fl:
        client_sftp.getfo(remote_path, fl)
        fl.seek(0)
    return fl


def read_csv_sftp(hostname: str, username: str, password: str, remotepath: str, *args, **kwargs) -> pd.DataFrame:
    """
    Read a file from a remote host using SFTP over SSH.
    Args:
        hostname: the remote host to read the file from
        username: the username to login into the remote host with
        password: the user password to login into the remote host
        remotepath: the path of the remote file to read
        *args: positional arguments to pass to pd.read_csv
        **kwargs: keyword arguments to pass to pd.read_csv
    Returns:
        a pandas DataFrame with data loaded from the remote host
    """
    # open an SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    # read the file using SFTP
    sftp = client.open_sftp()
    remote_file = sftp.open(remotepath)
    dataframe = pd.read_csv(remote_file, *args, **kwargs)
    remote_file.close()
    # close the connections
    sftp.close()
    client.close()
    return dataframe
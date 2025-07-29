from pathlib import Path
from stat import S_ISDIR
import paramiko
import logging

logger = logging.getLogger(__name__)


def sftp_download_dir(sftp, remote_dir: str, local_dir: Path):
    local_dir.mkdir(parents=True, exist_ok=True)

    for entry in sftp.listdir_attr(remote_dir):
        remote_path = f"{remote_dir}/{entry.filename}"
        local_path = local_dir / entry.filename

        if S_ISDIR(entry.st_mode):
            sftp_download_dir(sftp, remote_path, local_path)
        else:
            try:
                sftp.get(remote_path, str(local_path))
                logger.info(f"İndirildi: {remote_path} -> {local_path}")
            except Exception as e:
                logger.error(f"Hata: {remote_path} indirilemedi. {e}")


def download_recursive_from_server(
    hostname: str,
    port: int,
    username: str,
    key_path: Path,
    remote_path: str,
    local_path: Path,
    passphrase: str = None
):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        private_key = paramiko.RSAKey.from_private_key_file(
            str(key_path), password=passphrase)
        ssh.connect(hostname, port=port, username=username, pkey=private_key)
        logger.info(f"{hostname} adresine bağlantı başarılı.")

        sftp = ssh.open_sftp()
        sftp_download_dir(sftp, remote_path, local_path)

        sftp.close()
        ssh.close()
        logger.info("Tüm dosyalar başarıyla indirildi.")

    except Exception as e:
        logger.exception(f"Sunucuya bağlanırken hata oluştu: {e}")

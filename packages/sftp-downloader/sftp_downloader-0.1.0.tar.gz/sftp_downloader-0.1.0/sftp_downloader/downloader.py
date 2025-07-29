from pathlib import Path
from stat import S_ISDIR
import paramiko
import logging
from tqdm import tqdm

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


def sftp_download_dir(sftp, remote_dir: str, local_dir: Path):
    local_dir.mkdir(parents=True, exist_ok=True)

    for entry in sftp.listdir_attr(remote_dir):
        remote_path = f"{remote_dir}/{entry.filename}"
        local_path = local_dir / entry.filename

        if S_ISDIR(entry.st_mode):
            sftp_download_dir(sftp, remote_path, local_path)
        else:
            try:
                download_file_with_progress(
                    sftp, remote_path, local_path, entry.st_size)
                logger.info(f"İndirildi: {remote_path} -> {local_path}")
            except Exception as e:
                logger.error(f"Hata: {remote_path} indirilemedi. {e}")


def download_file_with_progress(sftp, remote_path: str, local_path: Path, file_size: int):
    """
    Dosyayı indirme sırasında tqdm ile ilerleme çubuğu gösterir.
    """
    with sftp.file(remote_path, 'rb') as remote_file, local_path.open('wb') as local_file:
        with tqdm(
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            desc=local_path.name,
            leave=True
        ) as progress:
            while True:
                data = remote_file.read(32768)  # 32 KB
                if not data:
                    break
                local_file.write(data)
                progress.update(len(data))

    logger.info(f"İndirildi: {remote_path} -> {local_path}")
    
    
def get_total_size_and_files(sftp, remote_dir: str):
    files = []
    total_size = 0

    for entry in sftp.listdir_attr(remote_dir):
        remote_path = f"{remote_dir}/{entry.filename}"
        if S_ISDIR(entry.st_mode):
            sub_files, sub_total = get_total_size_and_files(sftp, remote_path)
            files.extend(sub_files)
            total_size += sub_total
        else:
            files.append((remote_path, entry.st_size))
            total_size += entry.st_size

    return files, total_size


def download_files_with_overall_progress(sftp, files, local_base: Path, remote_base: str):
    with tqdm(
        total=sum(f[1] for f in files),
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        desc='Toplam',
        leave=True
    ) as progress:
        for remote_path, file_size in files:
            relative_path = Path(remote_path.replace(
                remote_base, "").lstrip("/"))
            local_path = local_base / relative_path
            local_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                with sftp.file(remote_path, 'rb') as remote_file, local_path.open('wb') as local_file:
                    while True:
                        data = remote_file.read(32768)
                        if not data:
                            break
                        local_file.write(data)
                        progress.update(len(data))
                logger.info(f"İndirildi: {remote_path} -> {local_path}")
            except Exception as e:
                logger.error(f"İndirilemedi: {remote_path} -> {e}")


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

        logger.info(f"{remote_path} taranıyor...")
        files, total_size = get_total_size_and_files(sftp, remote_path)
        logger.info(
            f"{len(files)} dosya, toplam {total_size / (1024*1024):.2f} MB indirilecek.")

        download_files_with_overall_progress(
            sftp, files, local_path, remote_path)

        sftp.close()
        ssh.close()
        logger.info("Tüm dosyalar başarıyla indirildi.")

    except Exception as e:
        logger.exception(f"Sunucuya bağlanırken hata oluştu: {e}")

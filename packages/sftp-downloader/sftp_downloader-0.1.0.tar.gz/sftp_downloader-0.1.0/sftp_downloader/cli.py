import argparse
from pathlib import Path
from sftp_downloader.downloader import download_recursive_from_server
from sftp_downloader.logger import setup_logger


def main():

    parser = argparse.ArgumentParser(description="SFTP klasör indirme aracı")
    parser.add_argument("--host", required=True,
                        help="Uzak sunucu IP veya domain")
    parser.add_argument("--port", type=int, default=22,
                        help="SSH port (varsayılan: 22)")
    parser.add_argument("--user", required=True, help="SSH kullanıcı adı")
    parser.add_argument("--key", required=True, help="Private key dosyası")
    parser.add_argument("--remote", required=True, help="Uzak klasör yolu")
    parser.add_argument("--local", required=True,
                        help="İndirilecek yerel klasör")
    parser.add_argument("--passphrase", help="Anahtar dosyası şifresi (varsa)")

    parser.add_argument("--logfile", help="Log dosyası yolu")

    args = parser.parse_args()

    setup_logger(log_file=Path(args.logfile) if args.logfile else None)

    download_recursive_from_server(
        hostname=args.host,
        port=args.port,
        username=args.user,
        key_path=Path(args.key),
        remote_path=args.remote,
        local_path=Path(args.local),
        passphrase=args.passphrase
    )


if __name__ == "__main__":
    main()

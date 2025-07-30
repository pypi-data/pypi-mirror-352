import base64
import math
import secrets
import socket
import uuid

import betterproto2
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519

from xray_cfo.message_pool import default_message_pool
from xray_cfo.xray.common.serial import TypedMessage


def to_typed_message(message: betterproto2.Message):
    return TypedMessage(
        type=message.__class__.__name__, value=message.SerializeToString()
    )


def to_typed_message_v2(message: betterproto2.Message):
    message_type = message.__class__
    type_url = default_message_pool.type_to_url.get(message_type)
    if "/" in type_url:
        type_url = type_url.split("/")[-1]
    return TypedMessage(
        type=type_url,
        value=message.SerializeToString(),
    )


def get_message_type(message: betterproto2.Message):
    message_type = message.__class__
    type_url = default_message_pool.type_to_url.get(message_type)
    if "/" in type_url:
        type_url = type_url.split("/")[-1]
    return type_url


def ip2bytes(ip: str):
    return bytes([int(i) for i in ip.split(".")])


def generate_random_tag():
    return secrets.token_urlsafe()


def generate_random_name(hex_count=8):
    return f"{secrets.token_hex(hex_count)}"


def generate_random_user_id():
    return uuid.uuid4().hex


def generate_random_email(tld="vump.com", hex_count=8):
    return f"{generate_random_name(hex_count)}@{tld}"


def generate_short_id() -> bytes:
    return secrets.token_bytes(8)


def generate_short_ids(count_ids: int = 10) -> list[bytes]:
    return [generate_short_id() for _ in range(count_ids)]


def generate_random_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
        tcp.bind(("", 0))
        addr, port = tcp.getsockname()
    return port


def human_readable_bytes(size_bytes):
    if not size_bytes:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def generate_x25519_keys() -> tuple[bytes, bytes]:
    private_key = x25519.X25519PrivateKey.generate()

    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )

    return private_bytes, public_bytes


def generate_x25519_keys():
    priv = x25519.X25519PrivateKey.generate()
    pub = priv.public_key()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    import base64

    # pub_str = base64.urlsafe_b64encode(pub_bytes).decode()[:-1]
    # priv_str = base64.urlsafe_b64encode(priv_bytes).decode()[:-1]

    return priv_bytes, pub_bytes


def generate_wireguard_keys(use_hex: bool = False) -> tuple[str, str]:
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    if use_hex:
        private_key_str = private_bytes.hex()
        public_key_str = public_bytes.hex()
    else:
        private_key_str = base64.b64encode(private_bytes).decode("utf-8")
        public_key_str = base64.b64encode(public_bytes).decode("utf-8")

    return private_key_str, public_key_str


def generate_vless_reality_link(
    user_id: str,
    domain_or_ip: str,
    public_key: bytes,
    short_id: bytes,
    port: int = 443,
    email: str = "user",
    sni: str = "amazon.com",
    spider_x: str = "/",
    flow: str = "xtls-rprx-vision",
    fingerprint: str = "chrome",
    header_type: str = "none",
) -> str:
    """
    Генерирует VLESS ссылку для Reality + Vision + TCP.

    :param user_id: UUID пользователя (str)
    :param domain_or_ip: Хост или IP сервера
    :param public_key: Публичный ключ Reality
    :param short_id: Short ID (обычно один из сгенерированных)
    :param email: Комментарий (опционально)
    :param sni: SNI/DEST, по умолчанию amazon.com
    :param spider_x: SPX путь, по умолчанию '/'
    :param flow: Потоковая схема, по умолчанию xtls-rprx-vision
    :param fingerprint: Браузерный отпечаток (chrome, firefox и т.д.)
    :param port: Порт, обычно 443
    :param header_type: Тип заголовка TCP (обычно none)
    :return: Готовая VLESS-ссылка
    """
    # public_key = base64.urlsafe_b64encode(public_key).rstrip(b"=").decode()
    # public_key = base64.urlsafe_b64encode(public_key).decode()[:-1]
    # short_id = base64.urlsafe_b64encode(short_id).rstrip(b"=").decode()
    return (
        f"vless://{user_id}@{domain_or_ip}:{port}"
        f"?encryption=none"
        f"&flow={flow}"
        f"&security=reality"
        f"&sni={sni}"
        f"&fp={fingerprint}"
        f"&pbk={public_key}"
        f"&sid={short_id}"
        f"&type=tcp"
        f"&headerType={header_type}"
        f"&spx={spider_x}"
        f"#{email}"
    )


def hex_to_base64(s: str) -> str:
    return base64.b64encode(bytes.fromhex(s)).decode()


def generate_wireguard_client_config(
    client_private_key: str,
    client_ip: str,
    server_public_key: str,
    server_endpoint: str,
    mtu: int = 1420,
    allowed_ips: str = "0.0.0.0/0",
    dns: str = "1.1.1.1",
    keep_alive: int = 25,
) -> str:
    """
    Сгенерировать конфигурацию клиента WireGuard.

    :param client_private_key: Приватный ключ клиента (Base64)
    :param client_ip: IP клиента в сети VPN (например, "10.0.0.2")
    :param server_public_key: Публичный ключ сервера (Base64)
    :param server_endpoint: Адрес сервера и порт (например, "vpn.example.com:443")
    :param mtu: MTU интерфейса
    :param allowed_ips: Разрешённые маршруты (по умолчанию весь трафик)
    :param dns: DNS-сервер
    :param keep_alive: Интервал keep-alive сообщений (в секундах)
    :return: Строка WireGuard-конфига
    """
    return f"""[Interface]
PrivateKey = {hex_to_base64(client_private_key)}
Address = {client_ip}/32
DNS = {dns}
MTU = {mtu}

[Peer]
PublicKey = {hex_to_base64(server_public_key)}
Endpoint = {server_endpoint}
AllowedIPs = {allowed_ips}
"""

from enum import StrEnum


class Network(StrEnum):
    tcp = "tcp"
    udp = "udp"
    tcp_upd = "tcp,udp"

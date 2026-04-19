from typing import Optional, Tuple, Dict, Any
import socks


def parse_proxy(proxy_line: str, proxy_format: str) -> Optional[Dict[str, str]]:
    if '@' in proxy_line or proxy_format == 'at_format':
        parts = proxy_line.split('@')
        if len(parts) == 2:
            auth = parts[0].split(':')
            addr = parts[1].split(':')
            if len(auth) == 2 and len(addr) == 2:
                return {
                    'host': addr[0],
                    'port': addr[1],
                    'login': auth[0],
                    'password': auth[1]
                }

    parts = proxy_line.split(':')
    if len(parts) != 4:
        return None

    if proxy_format == 'host_port_login_password':
        return {
            'host': parts[0],
            'port': parts[1],
            'login': parts[2],
            'password': parts[3]
        }
    elif proxy_format == 'login_password_host_port':
        return {
            'host': parts[2],
            'port': parts[3],
            'login': parts[0],
            'password': parts[1]
        }
    return None


def to_pyrogram(proxy_data: Dict[str, str], proxy_type: str) -> Optional[Dict[str, Any]]:
    if not proxy_data:
        return None
    return {
        'scheme': proxy_type,
        'hostname': proxy_data['host'],
        'port': int(proxy_data['port']),
        'username': proxy_data['login'],
        'password': proxy_data['password']
    }


def to_telethon(proxy_data: Dict[str, str], proxy_type: str) -> Optional[Tuple]:
    if not proxy_data:
        return None

    proxy_type_map = {
        'socks5': socks.SOCKS5,
        'socks4': socks.SOCKS4,
        'http': socks.HTTP,
        'https': socks.HTTP
    }

    return (
        proxy_type_map.get(proxy_type, socks.SOCKS5),
        proxy_data['host'],
        int(proxy_data['port']),
        True,
        proxy_data['login'],
        proxy_data['password']
    )


def to_url(proxy_data: Dict[str, str], proxy_type: str) -> str:
    return f"{proxy_type}://{proxy_data['login']}:{proxy_data['password']}@{proxy_data['host']}:{proxy_data['port']}"

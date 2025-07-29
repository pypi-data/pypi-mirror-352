from pathlib import Path
from typing import Dict, NamedTuple
import functools


class Address(NamedTuple):
    email: str
    name: str
    short_name: str


def create_address(addr: str, short_name: str = '') -> Address:
    """Create Address object from string.

    >>> create_address('sl@mail.org')
    Address(email='sl@mail.org', name='', short_name='sl')
    >>> create_address('Sloof Lirpa <sl@mail.org>')
    Address(email='sl@mail.org', name='Sloof Lirpa', short_name='Sloof Lirpa')
    >>> create_address('Sloof Lirpa <sl@mail.org>', 'sloof')
    Address(email='sl@mail.org', name='Sloof Lirpa', short_name='sloof')
    """
    name, _, email = addr.rstrip('>').rpartition(' <')
    if not short_name:
        short_name = name or email.split('@', 1)[0]
    return Address(email, name, short_name)


class Addresses:
    def __init__(self):
        self.addresses: Dict[str, Address] = {}

    def read(self, path: Path) -> None:
        if not path.is_file():
            return
        for line in path.read_text().splitlines():
            address, short = (word.strip() for word in line.split(','))
            self.add(address, short)

    def add(self, addr: str, short_name: str = '') -> None:
        self.addresses[addr] = create_address(addr, short_name)

    def short_name(self, addr: str) -> str:
        """Get a short name.

        >>> addresses = Addresses()
        >>> addresses.add('slirpa@mail.org')
        >>> addresses.short_name('slirpa@mail.org')
        'slirpa'
        """
        address = self.addresses.get(addr)
        if address is None:
            address = create_address(addr)
        return address.short_name


@functools.lru_cache(maxsize=10)
def create_addresses(path: Path) -> Addresses:
    """Create Addresses object (once for each path).
    """
    addresses = Addresses()
    addresses.read(path)
    return addresses

# ipchecker

Package Python sederhana untuk memeriksa IP address.

## Fitur

- Cek apakah IP valid
- Cek apakah IP private
- Cek apakah IP termasuk dalam subnet
- Ambil IP publik dari internet

## Instalasi

- pip install ipchecker

## Contoh Penggunaan

```python
from ipchecker import is_valid_ip, is_private_ip, is_in_subnet, get_public_ip

print(is_valid_ip("192.168.1.1"))
print(is_private_ip("8.8.8.8"))
print(is_in_subnet("192.168.1.10", "192.168.1.0/24"))
print(get_public_ip())
```

---

### ✅ `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name='ipchecker',
    version='0.1.0',
    description='Simple IP address checker utility',
    author='Nama Kamu',
    author_email='email@kamu.com',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
```

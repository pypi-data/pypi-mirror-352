from ipcuy import is_valid_ip, is_private_ip, is_in_subnet

def test_is_valid_ip():
    assert is_valid_ip("8.8.8.8")
    assert not is_valid_ip("999.999.999.999")

def test_is_private_ip():
    assert is_private_ip("192.168.1.1")
    assert not is_private_ip("8.8.8.8")

def test_is_in_subnet():
    assert is_in_subnet("192.168.1.5", "192.168.1.0/24")
    assert not is_in_subnet("10.0.0.1", "192.168.0.0/16")

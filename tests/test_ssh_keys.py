from chimera_app.ssh_keys import SSHKeys, forbidden_strings


def test_looks_like_ssh_key():
    for s in forbidden_strings:
        test_string = "ssh-rsa {} test".format(s)
        assert not SSHKeys.looks_like_ssh_key(test_string)

    assert not SSHKeys.looks_like_ssh_key("ssh-rsa test")
    assert not SSHKeys.looks_like_ssh_key("ssh-rsa test test test")
    assert not SSHKeys.looks_like_ssh_key("test test test")
    assert SSHKeys.looks_like_ssh_key("ssh-rsa test test")

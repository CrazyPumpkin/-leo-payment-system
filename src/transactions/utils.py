import base64

import rsa


def get_hash_base(d: dict):
    hash_base = [d[key] for key in sorted(d.keys())]
    return "|".join(map(str, hash_base))


def sign_dict(d: dict, priv_key, hash_alg="SHA-256"):
    """
    Add signature attr to copy of dict `d` and return this copy

    :param d:
    :param priv_key:
    :param hash_alg:
    :return:
    """
    hash = rsa.sign(get_hash_base(d).encode(), priv_key, hash_alg)
    res = d.copy()
    res["signature"] = base64.b64encode(hash).decode()
    return res

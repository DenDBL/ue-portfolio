# -*- coding: utf-8 -*-

"""Хеш тесты файлов. """

import hashlib


def md5(file_name):
    """
    Возвращает md5 хеш файла.

    :parm file_name: file path
    :type file_name: str
    :return: str
    """
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

#!/usr/bin/env python

"""
Конфигурация сборки для kybercffi с поддержкой CFFI.
"""

from setuptools import setup

# Указываем требования для сборки
setup_requires = [
    "cffi>=1.15.0"
]

setup(
    # Зависимости для сборки
    setup_requires=setup_requires,
    # CFFI модули для автоматической сборки при установке
    cffi_modules=[
        "kybercffi/_build_cffi.py:ffibuilder_kyber512",
        "kybercffi/_build_cffi.py:ffibuilder_kyber768", 
        "kybercffi/_build_cffi.py:ffibuilder_kyber1024"
    ],
    # Остальная конфигурация берётся из pyproject.toml
) 
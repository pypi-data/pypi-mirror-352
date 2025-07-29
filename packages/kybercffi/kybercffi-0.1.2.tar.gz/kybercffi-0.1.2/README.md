# KyberCFFI

**Python CFFI привязки для пост-квантовой криптографии Kyber**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/kybercffi.svg)](https://pypi.org/project/kybercffi/)

## Описание

KyberCFFI предоставляет Python привязки для эталонной реализации криптографического алгоритма Kyber - победителя конкурса NIST по пост-квантовой криптографии. Библиотека использует CFFI для эффективного взаимодействия с оригинальным C кодом Kyber.

### Поддерживаемые варианты

- **Kyber512** - Уровень безопасности 1 (эквивалент AES-128)
- **Kyber768** - Уровень безопасности 3 (эквивалент AES-192)  
- **Kyber1024** - Уровень безопасности 5 (эквивалент AES-256)

## Установка

```bash
pip install kybercffi
```

### Требования

- Python >= 3.8
- CFFI >= 1.15.0
- C компилятор (автоматически используется при установке)

## Быстрый старт

```python
import kybercffi

# Создание экземпляра Kyber768
kyber = kybercffi.Kyber768()

# Генерация пары ключей
public_key, secret_key = kyber.generate_keypair()

# Инкапсуляция (создание общего секрета)
ciphertext, shared_secret = kyber.encapsulate(public_key)

# Декапсуляция (восстановление общего секрета)
recovered_secret = kyber.decapsulate(ciphertext, secret_key)

# Проверка
assert shared_secret == recovered_secret
print("Kyber работает корректно!")
```

## Удобные функции

```python
from kybercffi import generate_keypair, encapsulate, decapsulate

# Генерация ключей с указанием уровня безопасности
pk, sk = generate_keypair(security_level=3)  # Kyber768

# Инкапсуляция
ct, ss = encapsulate(pk, security_level=3)

# Декапсуляция
ss2 = decapsulate(ct, sk, security_level=3)
```

## Фабричный метод

```python
# Создание экземпляра через фабрику
kyber512 = kybercffi.KyberKEM.create(security_level=1)   # Kyber512
kyber768 = kybercffi.KyberKEM.create(security_level=3)   # Kyber768
kyber1024 = kybercffi.KyberKEM.create(security_level=5)  # Kyber1024
```

## Информация о вариантах

```python
# Получение информации о всех вариантах
info = kybercffi.get_kyber_info()
print(info)

# Получение информации о версии
version_info = kybercffi.get_version_info()
print(version_info)
```

## Размеры ключей и зашифрованного текста

| Вариант   | Открытый ключ | Секретный ключ | Зашифрованный текст | Общий секрет |
|-----------|---------------|----------------|---------------------|--------------|
| Kyber512  | 800 байт      | 1632 байта     | 768 байт            | 32 байта     |
| Kyber768  | 1184 байта    | 2400 байт      | 1088 байт           | 32 байта     |
| Kyber1024 | 1568 байт     | 3168 байт      | 1568 байт           | 32 байта     |

## Особенности

- ⚡ **Высокая производительность** - использует оптимизированную C реализацию
- 🛡️ **Пост-квантовая безопасность** - устойчив к атакам квантовых компьютеров
- 🌐 **Кроссплатформенность** - работает на Windows, Linux, macOS
- 📦 **Простая установка** - автоматическая сборка при установке
- 🔒 **Криптографически безопасен** - основан на эталонной реализации NIST

## Лицензия

Проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## Автор

**Denis Magnitov**
- Email: pm13.magnitov@gmail.com
- GitHub: [Denis872](https://github.com/Denis872)

## Ссылки

- [Репозиторий](https://github.com/Denis872/KyberCFFI)
- [PyPI](https://pypi.org/project/kybercffi/)
- [Официальная спецификация Kyber](https://pq-crystals.org/kyber/)
- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)

## Поддержка

Если у вас возникли проблемы или вопросы, пожалуйста:
1. Проверьте [существующие Issues](https://github.com/Denis872/KyberCFFI/issues)
2. Создайте новый Issue с подробным описанием проблемы
3. Укажите версию Python, ОС и версию kybercffi 
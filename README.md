# Backup database file to google drive

## Operating Environment

Python 3.4 and above is required

The following libraries are required:

- cryptography
- hashlib

## Feature

* Encrypt with AES_GCM
* Use gzip to compress large database export files
* Once upload, the previous file will be deleted automatically
* Auto upload backup file to google drive

## WARNING

**You should always remember your key, or your data will be lost forever**

## Install

* Copy `config.ini.default` to `config.ini`
* Configure database name which you want to backup in `config.ini`
* Configure log level and encrypt key in `config.ini`
* Download [GDrive](https://github.com/prasmussen/gdrive) to your `/usr/bin` directory and login
* Use `cron` to run this program programmatically

## Decrypt

Simply run `python3 main.py <aes_filename>`

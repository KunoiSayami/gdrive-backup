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

## LICENSE

[![](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.txt)

Copyright (C) 2018 KunoiSayami

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

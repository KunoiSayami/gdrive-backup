# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2018 Too-Naive
#
# This module is part of gdrive-backup and is released under
# the AGPL v3 License: https://www.gnu.org/licenses/agpl-3.0.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import subprocess, time, gzip, shutil, os
from libpy3 import Log
from libpy3.Encrypt import encrypt_by_AES_GCM as AES_GCM
from configparser import ConfigParser

class timestamp:
	timestamp_ = ''
	@staticmethod
	def gen():
		timestamp.timestamp_ = time.strftime('%Y-%m-%d %H:%M:%S')
		return timestamp.get()
	@staticmethod
	def get():
		return timestamp.timestamp_

def gensql(db_names: tuple or list, db_passwd: str, *, db_user: str = 'root'):
	sub = subprocess.Popen(['mysqldump', '-u', db_user,'-p{}'.format(db_passwd), '--databases'] + [ db_name for db_name in db_names], stdout=subprocess.PIPE)
	#sub.wait()
	return sub.communicate()[0].decode('utf8')

def bkup(db_names: tuple or list, db_passwd: str, *, db_user: str = 'root'):
	with open('bakupsql{}.sql'.format(timestamp.gen()), 'w') as fout:
		fout.write(gensql(db_names, db_passwd, db_user=db_user))
	with open('backupsql{}.sql'.format(timestamp.get()), 'rb') as fin, open('backupsql{}.sql.gz'.format(timestamp.get()), 'wb') as fout:
		shutil.copyfileobj(fin, fout)
	with open('backupsql{}.sql.gz'.format(timestamp.get()), 'rb') as fin, open('backupsql{}.sql'.format(timestamp.get()), 'w') as fout:
		fout.write(AES_GCM().b64encrypt(fin.read()))
	os.remove('backupsql{}.sql.gz'.format(timestamp.get()))
	sub = subprocess.Popen(['gdrive', 'upload', 'bakupsql{}.sql'.format(timestamp.get())], stdout=subprocess.PIPE)
	#sub.wait()
	return sub.communicate()[0].decode('utf8').split()[3]

def del_file(file_id: str):
	sub = subprocess.Popen(['gdrive', 'delete', file_id])
	#sub.wait()
	r = sub.communicate()[0].decode('utf8')
	return 'Deleted' in r

def main():
	config = ConfigParser()
	config.read('config.ini')
	if config.has_option('sql', 'fileid'):
		fileid_ = config['sql']['fileid']
	else:
		config['sql']['fileid'] = ''
		fileid_ = ''
	Log.info('Backup process started')
	current_fileid = bkup(eval(config['sql']['databases']), config['sql']['passwd'])
	#print(repr(current_fileid))
	if fileid_ != '':
		del_file(fileid_)
	config['sql']['fileid'] = current_fileid
	Log.info('Success backup {}', current_fileid)
	with open('config.ini', 'w') as fout:
		config.write(fout)

if __name__ == '__main__':
	main()


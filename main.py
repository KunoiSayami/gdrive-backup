#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2018 KunoiSayami
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
import subprocess, time, gzip, shutil, os, sys
from libpy3 import Log
from libpy3.Encrypt import encrypt_by_AES_GCM as AES_GCM
from configparser import ConfigParser

global prefix

class timestamp:
	timestamp_ = ''
	@staticmethod
	def gen():
		timestamp.timestamp_ = time.strftime('_%Y%m%d_%H%M%S')
		return timestamp.get()
	@staticmethod
	def get():
		return timestamp.timestamp_

def gensql(db_names: tuple or list, db_passwd: str, *, db_user: str = 'root'):
	subprocess.Popen(
		['mysqldump', '-u', db_user,'-p{}'.format(db_passwd), '--databases'] + [ db_name for db_name in db_names],
		stdout = open('{}{}.sql'.format(prefix, timestamp.gen()), 'w'),
		stderr = subprocess.DEVNULL,
		close_fds = True
	).wait()

def bkup(db_names: tuple or list, db_passwd: str, *, db_user: str = 'root'):
	gensql(db_names, db_passwd, db_user = db_user)
	encrypt_sql('{}{}'.format(prefix, timestamp.get()))
	sub = subprocess.Popen(['gdrive', 'upload', '{}{}.sql.aes'.format(prefix, timestamp.get())], stdout = subprocess.PIPE)
	r = sub.communicate()[0].decode('utf8')
	if r.split()[3] == 'to':
		Log.warn('File id is `to\': origin output:\n{}', repr(r))
	return r.split()[3]

def del_file(file_id: str):
	sub = subprocess.Popen(['gdrive', 'delete', file_id], stdout = subprocess.PIPE)
	r = sub.communicate()[0].decode('utf8')
	return 'Deleted' in r

def encrypt_sql(filename_with_timestamp: str):
	with open('{}.sql'.format(filename_with_timestamp), 'rb') as fin, gzip.open('{}.sql.gz'.format(filename_with_timestamp), 'wb') as fout:
		shutil.copyfileobj(fin, fout)
	with open('{}.sql.gz'.format(filename_with_timestamp), 'rb') as fin, open('{}.sql.aes'.format(filename_with_timestamp), 'w') as fout:
		fout.write(AES_GCM().b64encrypt(fin.read()))
	os.remove('{}.sql.gz'.format(filename_with_timestamp))

def decrypt_sql(file_name: str):
	with open(file_name, 'r') as fin, open('{}.gz'.format(file_name), 'wb') as fout:
		fout.write(AES_GCM().b64decrypt(fin.read()))
	with gzip.open('{}.gz'.format(file_name), 'rb') as gfin, open('{}.orign'.format(file_name), 'wb') as fout:
		shutil.copyfileobj(gfin, fout)
	os.remove('{}.gz'.format(file_name))
	Log.info('decrypt sql file successful ({}.orign)'.format(file_name))

def main():
	global prefix
	config = ConfigParser()
	config.read('config.ini')
	if config.has_option('sql', 'fileid'):
		fileid_ = config['sql']['fileid']
	else:
		config['sql']['fileid'], fileid_ = '', ''
	prefix = config['sql']['prefix'] if config.has_option('sql', 'prefix') and config['sql']['prefix'] != '' else 'backupsql'
	#Log.info('Backup process started')
	if isinstance(eval(config['sql']['databases']), str): config['sql']['databases'] = repr((eval(config['sql']['databases']), ))
	current_fileid = bkup(eval(config['sql']['databases']), config['sql']['passwd'])
	os.remove('{}{}.sql'.format(prefix, timestamp.get()))
	os.remove('{}{}.sql.aes'.format(prefix, timestamp.get()))
	#print(repr(current_fileid))
	if fileid_ != '':
		try: del_file(fileid_)
		except: Log.exc()
	config['sql']['fileid'] = current_fileid
	Log.info('Success backup {}', current_fileid)
	with open('config.ini', 'w') as fout: config.write(fout)

if __name__ == '__main__':
	if len(sys.argv) == 2: decrypt_sql(sys.argv[1])
	else: main()


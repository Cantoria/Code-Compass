#!~/anaconda3/bin/ python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Zimeng Qiu <CNPG-qzm@hotmail.com>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

"""
Crawler for Github repository issues using Github API
"""

import os
import json
import requests
import logging
import pymysql.cursors

JSON_DIR = 'data/'
JSON_FILE = 'issues_api.json'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_issues(owner, repo, page):
    """
    Using Github API.
    Allow request 10 times per minute.
    """
    url = 'https://api.github.com/repos/%s/%s/issues?page=%i？client_id=bfb2f68f744e4018554d' % (owner, repo, page)
    results = requests.get(url)
    """HTTP status code, 200 means OK"""
    if results.status_code == 200:
        logger.info('Fetched page #%i success!' % page)
    return results.json()


def iter_over_pages(owner, repo, pages):
    data_list = []
    for page in range(1, pages):
        data = get_issues(owner, repo, page)
        if not len(data):
            break
        data_list.extend(data)
    return data_list


def insert_to_db(data):
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='root',
                                     db='test',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = 'insert into project_info(issue_url, open_time, issue_author, issues_by_this_author) ' \
                      'VALUES (%s, %s, %s, %s, %s)'
                cursor.executemany(sql, data)
                connection.commit()
        except TimeoutError:
            connection.close()


def insert_to_json(data):
        if not os.path.exists(JSON_DIR):
            try:
                os.makedirs(JSON_DIR)
            except OSError as exception:
                raise SystemExit("Error: {}".format(exception))
        with open(JSON_DIR + JSON_FILE, 'w') as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    issues = iter_over_pages('tensorflow', 'tensorflow', pages=100)
    insert_to_json(issues)
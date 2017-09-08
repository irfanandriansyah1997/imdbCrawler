import os
import traceback

import pymongo

from pymongo import errors
from pymongo.mongo_client import MongoClient
from imdbCrawler.library.logger import Logger
from imdbCrawler.consumer.film import FilmConsumer
from imdbCrawler.consumer.actress import ActressConsumer

class MongoPipeline(object):
    def __init__(self, host, port, db, logger = 'log'):
        """Pemanggilan fungsi MongoClient dan membuat cursor koneksi pada database

        :param host : (String) host database
        :param port : (Integer) port database
        :param db : (String) name database
        """

        try:
            self.connection = MongoClient('mongodb://{}:{}'.format(host, port))
            self.db = self.connection[db]
            self.actress = ActressConsumer()
            self.film = FilmConsumer()

            directory = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                logger
            )

            self.logger = Logger(directory, 'crawler.imdb')
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
            raise ValueError(e)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host = crawler.settings.get('MONGODB_HOST'),
            port=crawler.settings.get('MONGODB_PORT'),
            db=crawler.settings.get('MONGODB_DB'),
            logger=crawler.settings.get('LOGGER_PATH')
        )

    def reprocess_item(self, type, id):
        result = self.get("reprocess_item", where={"id": id, "type": type})

        if result.get("count") == 0:
            data = dict()
            data.update({"id": id})
            data.update({"type": type})
            query = self.insertOne("reprocess_item", data, id)

            if query.get('code') == 200:
                self.logger.print_log_to_file(
                    'Success insert data into collection reprocess {}: {}'.format(type, id), type='INFO'
                )

    def process_item(self, item, spider):
        data = dict()
        primary_key = spider.mongo_requirement.get('primary')
        collection = spider.mongo_requirement.get('collection')

        if 'actress' in spider.name:
            data = ActressConsumer(item).get_dict()
            data = {k: v for k, v in data.items() if v is not None and v != "" and v != {} and v != []}

        elif 'film' in spider.name:
            data = FilmConsumer(item).get_dict()
            data = {k: v for k, v in data.items() if v is not None and v != "" and v != {} and v != []}


        check_data = self.get(collection, where={primary_key: item.get(primary_key)})

        if check_data.get('count') > 0:
            query = self.updateOne(collection, data, {'key': primary_key, 'value': str(item.get(primary_key))})

            if query.get('code') == 200:
                self.logger.print_log_to_file(
                    'Success update data into collection {} : {}'.format(collection, item.get(primary_key)), type='INFO'
                )

                self.remove("reprocess_item", {"id": item.get(primary_key)})

        else:

            query = self.insertOne(collection, data, item.get(primary_key))

            if query.get('code') == 200:
                self.logger.print_log_to_file(
                    'Success insert data into collection {} : {}'.format(collection, item.get(primary_key)), type='INFO'
                )

                self.remove("reprocess_item", {"id" : item.get(primary_key)})


        return item

    def close_spider(self, spider):
        self.connection.close()

    def get(self, table, field = None, where = None, limit = None, sort = None):
        """Mengambil semua data dengan kriteria tertentu sesuai parameter

        Usage

        self.get('product', {Object}, {Object}, 5)

        :param table : (String) nama tabel
        :param field : (Dictionary) field yang akan ditampilkan
        :param where : (Dictionary) criteria yang akan dipakai untuk mengambil data
        :param limit : (Integer) port database
        :return data : (Dictionary) berisi dari data hasil pencarian dan jumlah data yang ditemukan
        """

        try:
            where = {} if where is None else dict(where)
            field = None if field is None else dict(field)
            if limit is None:
                if sort is None:
                    query = self.db[table].find(where, field)
                    return {'data' : query, 'count' : query.count()}
                else:
                    query = self.db[table].find(where, field)\
                        .sort(sort['key'], pymongo.DESCENDING if sort['status'] else pymongo.ASCENDING)
                    return {'data': query, 'count': query.count()}
            else:
                if sort is None:
                    query = self.db[table].find(where, field).limit(limit)
                    return {'data': query, 'count': query.count()}
                else:
                    query = self.db[table].find(where, field).limit(limit)\
                        .sort(sort['key'], pymongo.DESCENDING if sort['status'] else pymongo.ASCENDING)
                    return {'data': query, 'count': query.count()}

        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
            raise ValueError(e)

    def getOne(self, table, field=None, where=None):
        """Mengambil satu data dengan kriteria tertentu sesuai parameter

        Usage

        self.getOne('product', {Object}, {Object})

        :param table : (String) nama tabel
        :param field : (Dictionary) field yang akan ditampilkan
        :param where : (Dictionary) criteria yang akan dipakai untuk mengambil data
        :return data : (Dictionary) berisi dari data hasil pencarian
        """
        try:
            where = {} if where is None else dict(where)
            field = None if field is None else dict(field)

            query = self.db[table].find_one(where, field)
            return {'data': query}
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
            raise ValueError(e)

    def updateOne(self, table, data, index):
        """Mengubah satu data sesuai dengan parameter

        Usage

        self.updateOne('product', {Object}, {Object})

        :param table : (String) nama tabel
        :param data : (Dictionary) data yang akan diubah
        :param index : (Dictionary) criteria yang akan dipakai untuk mengubah data
        :return data : (Dictionary) berisi dari data code dan pesan proses update data
        """

        try:
            if data is not None:
                self.db[table].update_one({index['key']: index['value']}, {"$set": dict(data)})
                return {'code': 200, 'message': 'Update Success'}
            else:
                raise ValueError({'code': 500, 'message': 'Attribut data is not found'})
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
            raise ValueError(e.message)

    def updateAll(self, table, data, index):
        """Mengubah semua data sesuai dengan parameter

        Usage

        self.updateOne('product', {Object}, {Object})

        :param table : (String) nama tabel
        :param data : (Dictionary) data yang akan diubah
        :param index : (Dictionary) criteria yang akan dipakai untuk mengubah data
        :return data : (Dictionary) berisi dari data code dan pesan proses update data
        """

        try:
            if data is not None:
                self.db[table].update_one({index['key']: index['value']}, data)
                return {'code': 200, 'message': 'Update Success'}
            else:
                raise ValueError({'code': 500, 'message': 'Attribut data is not found'})
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
            raise ValueError(e)

    def updateOneFlex(self, table, data, key):
        """Mengubah satu data sesuai dengan parameter

        Usage

        self.updateOne('product', {Object}, {Object})

        :param table : (String) nama tabel
        :param data : (Dictionary) data yang akan diubah
        :param index : (Dictionary) criteria yang akan dipakai untuk mengubah data
        :return data : (Dictionary) berisi dari data code dan pesan proses update data
        """

        try:
            if data is not None:
                self.db[table].update_one(dict(key), {"$set": dict(data)})
                return {'code': 200, 'message': 'Update Success'}
            else:
                raise ValueError({'code': 500, 'message': 'Attribut data is not found'})
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
            raise ValueError(e.message)

    def insertOne(self, table, data, custom_id):
        """Menambahkan semua data sesuai dengan parameter

        Usage

        self.insertOne('product', {Object})

        :param table : (String) nama tabel
        :param data : (Dictionary) data yang akan diubah
        :param custom : (Any) _id value yang akan diubah
        :return data : (Dictionary) berisi dari data code dan pesan proses insert data
        """
        if custom_id:
            data['_id'] = custom_id

        try:
            self.db[table].insert_one(dict(data))
            return {'code': 200, 'message': 'Insert Success'}
        except errors.PyMongoError, e:
            print traceback.print_exc()
            raise ValueError(e)
        except Exception, e:
            print traceback.print_exc()
            raise ValueError(e)

    def findAndModify(self, table, filter, update, sort):
        try:
            if update is not None:
                result = self.db[table].find_and_modify(filter, sort=sort, update=update)
                if result.matched_count:
                    return {'code': 200, 'message': 'Update Success'}
                else:
                    raise ValueError({'code': 404, 'message': 'No matched Data'})
            else:
                raise ValueError({'code': 500, 'message': 'Attribut data is not found'})
        except Exception, e:
            raise ValueError(e)

    def remove(self, table, filter):
        try:
            if filter is not None:
                result = self.db[table].delete_many(filter)
                if result.deleted_count:
                    return {'code': 200, 'message': 'Delete Success'}
                else:
                    return {'code': 200, 'message': 'No Matched Data'}
            else:
                raise ValueError({'code': 500, 'message': 'Attribut filter is not found'})
        except Exception, e:
            raise ValueError(e)

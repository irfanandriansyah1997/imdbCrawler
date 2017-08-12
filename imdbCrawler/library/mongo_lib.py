from pymongo.mongo_client import MongoClient
from pymongo import errors
import pymongo
import traceback


class mongoLib:
    def __init__(self, host, port, db):
        """Pemanggilan fungsi MongoClient dan membuat cursor koneksi pada database

        :param host : (String) host database
        :param port : (Integer) port database
        :param db : (String) name database
        """

        try:
            self.connection = MongoClient('mongodb://{}:{}'.format(host, port))
            self.db = self.connection[db]
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
            raise ValueError(e)

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


    def insertOne(self, table, data):
        """Menambahkan semua data sesuai dengan parameter

        Usage

        self.insertOne('product', {Object})

        :param table : (String) nama tabel
        :param data : (Dictionary) data yang akan diubah
        :return data : (Dictionary) berisi dari data code dan pesan proses insert data
        """

        try:
            self.db[table].insert_one(dict(data))
            return {'code': 200, 'message': 'Insert Success'}
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, e:
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

    def getDatabase(self, database, mode, address, dev = False, reprocess = False):
        db_list = {}
        kota = database.get('topic', None, {})

        for data in kota['data']:
            nameCity = data['t_kode_kota']
            if dev:
                nameDatabase = 'dev_smartcity_{}'.format(data['t_kode_kota'])
            else:
                nameDatabase = 'smartcity_{}'.format(data['t_kode_kota'])

            db_list.update({nameCity: mongoLib(address, 27017, nameDatabase)})

        db_list.update({'temporary' : mongoLib(address, 27017, 'smartcity_temporary')})


        try:
            if mode not in db_list:
                raise ValueError('Database is not found {} in main server'.format(mode))
            else:
                return db_list if reprocess == True else db_list[mode]
        except errors.PyMongoError, e:
            raise ValueError(e)
        except Exception, arg:
            raise ValueError('Error : {}'.format(arg))

    def CursorIntoObject(self, data):
        try:
            result = dict()
            result.update({'items' : []})
            result.update({'count': 0})

            for k in data:
                del k['_id']
                result['items'].append(k)
                result['count'] = len(result['items'])

            return result
        except Exception, e:
            raise ValueError(e)
        except errors.CursorNotFound, e:
            raise ValueError(e)
        except errors.PyMongoError, e:
            raise ValueError(e)

    def multiDictToColumnar(self, data, prefix, type = 'string'):
        try:
            if type == 'string':
                column = {'{}.{}'.format(prefix, k): v for k, v in data.items()}
                return column
            elif type == 'column':
                var = dict()
                var.update({prefix :  {k : v for k, v in data.items()}})
                return var
        except Exception, e:
            raise ValueError(e)
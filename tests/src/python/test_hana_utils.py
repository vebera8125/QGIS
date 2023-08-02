"""Helper utilities for HANA provider.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

"""

__author__ = 'Maxim Rylov'
__date__ = '2019-11-21'
__copyright__ = 'Copyright 2019, The QGIS Project'

from hdbcli import dbapi
from qgis.core import QgsDataSourceUri, QgsVectorLayer


class QgsHanaProviderUtils:

    @staticmethod
    def createConnection(uri):
        ds_uri = QgsDataSourceUri(uri)
        conn = dbapi.connect(address=ds_uri.host(), port=ds_uri.port(), user=ds_uri.username(),
                             password=ds_uri.password(), ENCRYPT=True, sslValidateCertificate=False, CHAR_AS_UTF8=1)
        conn.setautocommit(False)
        return conn

    @staticmethod
    def createVectorLayer(conn_parameters, layer_name):
        layer = QgsVectorLayer(conn_parameters, layer_name, 'hana')
        assert layer.isValid()
        return layer

    @staticmethod
    def executeSQL(conn, statement, parameters=None, return_result=False):
        assert conn
        cursor = conn.cursor()
        assert cursor
        res = None
        if parameters is not None:
            cursor.executemany(statement, parameters)
        else:
            cursor.execute(statement)
        if return_result:
            res = cursor.fetchone()
        cursor.close()
        conn.commit()
        if return_result:
            return res[0]

    @staticmethod
    def executeSQLMany(conn, statement, parameters):
        QgsHanaProviderUtils.executeSQL(conn, statement, parameters)

    @staticmethod
    def executeSQLFetchOne(conn, statement):
        return QgsHanaProviderUtils.executeSQL(conn, statement, return_result=True)

    @staticmethod
    def createAndFillTable(conn, create_statement, insert_statement, insert_args):
        QgsHanaProviderUtils.executeSQL(conn, create_statement)
        QgsHanaProviderUtils.executeSQLMany(conn, insert_statement, insert_args)

    @staticmethod
    def dropTableIfExists(conn, schema_name, table_name):
        res = QgsHanaProviderUtils.executeSQLFetchOne(conn,
                                                      f"SELECT COUNT(*) FROM SYS.TABLES WHERE "
                                                      f"SCHEMA_NAME='{schema_name}' AND TABLE_NAME='{table_name}'")
        if res != 0:
            QgsHanaProviderUtils.executeSQL(conn, f'DROP TABLE "{schema_name}"."{table_name}" CASCADE')

    @staticmethod
    def dropSchemaIfExists(conn, schema_name):
        res = QgsHanaProviderUtils.executeSQLFetchOne(conn,
                                                      f"SELECT COUNT(*) FROM SYS.SCHEMAS WHERE SCHEMA_NAME='{schema_name}'")
        if res != 0:
            QgsHanaProviderUtils.executeSQL(conn, f'DROP SCHEMA "{schema_name}" CASCADE')

    @staticmethod
    def createAndFillDefaultTables(conn, schema_name):
        QgsHanaProviderUtils.dropSchemaIfExists(conn, schema_name)

        QgsHanaProviderUtils.executeSQL(conn, f'CREATE SCHEMA "{schema_name}"')

        create_sql = f'CREATE TABLE "{schema_name}"."some_data" ( ' \
            '"pk" INTEGER GENERATED BY DEFAULT AS IDENTITY NOT NULL PRIMARY KEY,' \
            '"cnt" INTEGER,' \
            '"name" NVARCHAR(32) DEFAULT \'qgis\',' \
            '"name2" NVARCHAR(32) DEFAULT \'qgis\',' \
            '"num_char" NVARCHAR(1),' \
            '"dt" TIMESTAMP,' \
            '"date" DATE,' \
            '"time" TIME,' \
            '"geom" ST_GEOMETRY(4326))'
        insert_sql = f'INSERT INTO "{schema_name}"."some_data" ("pk", "cnt", "name", "name2", "num_char", "dt",' \
            '"date", "time", "geom") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ST_GeomFromEWKB(?)) '
        insert_args = [
            [5, -200, None, 'NuLl', '5', '2020-05-04 12:13:14', '2020-05-02', '12:13:01',
             bytes.fromhex('0101000020E61000001D5A643BDFC751C01F85EB51B88E5340')],
            [3, 300, 'Pear', 'PEaR', '3', None, None, None, None],
            [1, 100, 'Orange', 'oranGe', '1', '2020-05-03 12:13:14', '2020-05-03', '12:13:14',
             bytes.fromhex('0101000020E61000006891ED7C3F9551C085EB51B81E955040')],
            [2, 200, 'Apple', 'Apple', '2', '2020-05-04 12:14:14', '2020-05-04', '12:14:14',
             bytes.fromhex('0101000020E6100000CDCCCCCCCC0C51C03333333333B35140')],
            [4, 400, 'Honey', 'Honey', '4', '2021-05-04 13:13:14', '2021-05-04', '13:13:14',
             bytes.fromhex('0101000020E610000014AE47E17A5450C03333333333935340')]]
        QgsHanaProviderUtils.createAndFillTable(conn, create_sql, insert_sql, insert_args)
        QgsHanaProviderUtils.executeSQL(conn, f'COMMENT ON TABLE "{schema_name}"."some_data" IS \'QGIS Test Table\'')
        QgsHanaProviderUtils.executeSQL(conn, f'CREATE VIEW "{schema_name}"."some_data_view" AS SELECT * FROM '
                                        f'"{schema_name}"."some_data"')

        create_sql = f'CREATE TABLE "{schema_name}"."some_poly_data" ( ' \
            '"pk" INTEGER NOT NULL GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,' \
            '"geom" ST_GEOMETRY(4326))'
        insert_sql = f'INSERT INTO "{schema_name}"."some_poly_data" ("pk", "geom") VALUES (?, ST_GeomFromText(?, 4326))'
        insert_args = [
            [1, 'Polygon ((-69.0 81.4, -69.0 80.2, -73.7 80.2, -73.7 76.3, -74.9 76.3, -74.9 81.4, -69.0 81.4))'],
            [2, 'Polygon ((-67.6 81.2, -66.3 81.2, -66.3 76.9, -67.6 76.9, -67.6 81.2))'],
            [3, 'Polygon ((-68.4 75.8, -67.5 72.6, -68.6 73.7, -70.2 72.9, -68.4 75.8))'],
            [4, None]]
        QgsHanaProviderUtils.createAndFillTable(conn, create_sql, insert_sql, insert_args)

    @staticmethod
    def cleanUp(conn, schema_name):
        QgsHanaProviderUtils.dropSchemaIfExists(conn, schema_name)

    @staticmethod
    def generateSchemaName(conn, prefix):
        sql = "SELECT REPLACE(CURRENT_UTCDATE, '-', '') || '_' || BINTOHEX(SYSUUID) FROM DUMMY;"
        uid = QgsHanaProviderUtils.executeSQL(conn, sql, return_result=True)
        return f'{prefix}_{uid}'

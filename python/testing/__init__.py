# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : January 2016
    Copyright            : (C) 2016 by Matthias Kuhn
    Email                : matthias@opengis.ch
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Matthias Kuhn'
__date__ = 'January 2016'
__copyright__ = '(C) 2016, Matthias Kuhn'

import os
import sys
import difflib
import functools
import filecmp
import tempfile
from pathlib import Path
from typing import Optional

from qgis.PyQt.QtCore import (
    QVariant,
    QDateTime,
    QDate,
    QDir,
    QUrl,
    QSize
)
from qgis.PyQt.QtGui import (
    QImage,
    QDesktopServices
)
from qgis.core import (
    QgsApplication,
    QgsFeatureRequest,
    QgsCoordinateReferenceSystem,
    NULL,
    QgsVectorLayer,
    QgsRenderChecker,
    QgsMultiRenderChecker,
    QgsMapSettings,
    QgsLayout,
    QgsLayoutChecker,
)

import unittest

# Get a backup, we will patch this one later
_TestCase = unittest.TestCase
unittest.util._MAX_LENGTH = 2000


class TestCase(_TestCase):

    @staticmethod
    def is_ci_run() -> bool:
        """
        Returns True if the test is being run on the CI environment
        """
        return os.environ.get("QGIS_CONTINUOUS_INTEGRATION_RUN") == 'true'

    @classmethod
    def setUpClass(cls):
        cls.report = ''

    @classmethod
    def tearDownClass(cls):
        if cls.report:
            cls.write_local_html_report(cls.report)

    @classmethod
    def control_path_prefix(cls) -> Optional[str]:
        """
        Returns the prefix for test control images used by the class
        """
        return None

    @classmethod
    def write_local_html_report(cls, report: str):
        report_dir = QgsRenderChecker.testReportDir()
        if not report_dir.exists():
            QDir().mkpath(report_dir.path())

        report_file = report_dir.filePath('index.html')

        # only append to existing reports if running under CI
        if cls.is_ci_run() or \
                os.environ.get("QGIS_APPEND_TO_TEST_REPORT") == 'true':
            file_mode = 'ta'
        else:
            file_mode = 'wt'

        with open(report_file, file_mode, encoding='utf-8') as f:
            f.write(f"<h1>Python {cls.__name__} Tests</h1>\n")
            f.write(report)

        if not TestCase.is_ci_run():
            QDesktopServices.openUrl(QUrl.fromLocalFile(report_file))

    @classmethod
    def image_check(cls,
                    name: str,
                    reference_image: str,
                    image: QImage,
                    control_name=None,
                    color_tolerance: int = 2,
                    allowed_mismatch: int = 20) -> bool:
        temp_dir = QDir.tempPath() + '/'
        file_name = temp_dir + name + ".png"
        image.save(file_name, "PNG")
        checker = QgsMultiRenderChecker()
        if cls.control_path_prefix():
            checker.setControlPathPrefix(cls.control_path_prefix())
        checker.setControlName(control_name or "expected_" + reference_image)
        checker.setRenderedImage(file_name)
        checker.setColorTolerance(color_tolerance)
        result = checker.runTest(name, allowed_mismatch)
        if not result:
            cls.report += f"<h2>Render {name}</h2>\n"
            cls.report += checker.report()

        return result

    @classmethod
    def render_map_settings_check(cls,
                                  name: str,
                                  reference_image: str,
                                  map_settings: QgsMapSettings,
                                  color_tolerance: Optional[int] = None,
                                  allowed_mismatch: Optional[int] = None) -> bool:
        checker = QgsMultiRenderChecker()
        checker.setMapSettings(map_settings)

        if cls.control_path_prefix():
            checker.setControlPathPrefix(cls.control_path_prefix())
        checker.setControlName("expected_" + reference_image)
        if color_tolerance:
            checker.setColorTolerance(color_tolerance)
        result = checker.runTest(name, allowed_mismatch or 0)
        if not result:
            cls.report += f"<h2>Render {name}</h2>\n"
            cls.report += checker.report()

        return result

    @classmethod
    def render_layout_check(cls, name: str,
                            layout: QgsLayout,
                            size: Optional[QSize] = None):
        checker = QgsLayoutChecker(name, layout)
        if size is not None:
            checker.setSize(size)
        if cls.control_path_prefix():
            checker.setControlPathPrefix(cls.control_path_prefix())
        result, message = checker.testLayout()
        if not result:
            cls.report += f"<h2>Render {name}</h2>\n"
            cls.report += checker.report()
        return result

    def assertLayersEqual(self, layer_expected, layer_result, **kwargs):
        """
        :param layer_expected: The first layer to compare
        :param layer_result: The second layer to compare
        :param request: Optional, A feature request. This can be used to specify
                        an order by clause to make sure features are compared in
                        a given sequence if they don't match by default.
        :keyword compare: A map of comparison options. e.g.
                         { fields: { a: skip, b: { precision: 2 }, geometry: { precision: 5 } }
                         { fields: { __all__: cast( str ) } }
        :keyword pk: "Primary key" type field - used to match features
        from the expected table to their corresponding features in the result table. If not specified
        features are compared by their order in the layer (e.g. first feature compared with first feature,
        etc)
        """
        self.checkLayersEqual(layer_expected, layer_result, True, **kwargs)

    def checkLayersEqual(self, layer_expected, layer_result, use_asserts=False, **kwargs):
        """
        :param layer_expected: The first layer to compare
        :param layer_result: The second layer to compare
        :param use_asserts: If true, asserts are used to test conditions, if false, asserts
        are not used and the function will only return False if the test fails
        :param request: Optional, A feature request. This can be used to specify
                        an order by clause to make sure features are compared in
                        a given sequence if they don't match by default.
        :keyword compare: A map of comparison options. e.g.
                         { fields: { a: skip, b: { precision: 2 }, geometry: { precision: 5 } }
                         { fields: { __all__: cast( str ) } }
        :keyword pk: "Primary key" type field - used to match features
        from the expected table to their corresponding features in the result table. If not specified
        features are compared by their order in the layer (e.g. first feature compared with first feature,
        etc)
        """

        try:
            request = kwargs['request']
        except KeyError:
            request = QgsFeatureRequest()

        try:
            compare = kwargs['compare']
        except KeyError:
            compare = {}

        # Compare CRS
        if 'ignore_crs_check' not in compare or not compare['ignore_crs_check']:
            expected_wkt = layer_expected.dataProvider().crs().toWkt(QgsCoordinateReferenceSystem.WKT_PREFERRED)
            result_wkt = layer_result.dataProvider().crs().toWkt(QgsCoordinateReferenceSystem.WKT_PREFERRED)

            if use_asserts:
                _TestCase.assertEqual(self, layer_expected.dataProvider().crs(), layer_result.dataProvider().crs())
            elif layer_expected.dataProvider().crs() != layer_result.dataProvider().crs():
                return False

        # Compare features
        if use_asserts:
            _TestCase.assertEqual(self, layer_expected.featureCount(), layer_result.featureCount())
        elif layer_expected.featureCount() != layer_result.featureCount():
            return False

        try:
            precision = compare['geometry']['precision']
        except KeyError:
            precision = 14

        try:
            topo_equal_check = compare['geometry']['topo_equal_check']
        except KeyError:
            topo_equal_check = False

        try:
            ignore_part_order = compare['geometry']['ignore_part_order']
        except KeyError:
            ignore_part_order = False

        try:
            normalize = compare['geometry']['normalize']
        except KeyError:
            normalize = False

        try:
            explode_collections = compare['geometry']['explode_collections']
        except KeyError:
            explode_collections = False

        try:
            snap_to_grid = compare['geometry']['snap_to_grid']
        except KeyError:
            snap_to_grid = None

        try:
            unordered = compare['unordered']
        except KeyError:
            unordered = False

        try:
            equate_null_and_empty = compare['geometry']['equate_null_and_empty']
        except KeyError:
            equate_null_and_empty = False

        if unordered:
            features_expected = [f for f in layer_expected.getFeatures(request)]
            for feat in layer_result.getFeatures(request):
                feat_expected_equal = None
                for feat_expected in features_expected:
                    if self.checkGeometriesEqual(feat.geometry(), feat_expected.geometry(),
                                                 feat.id(), feat_expected.id(),
                                                 False, precision, topo_equal_check, ignore_part_order, normalize=normalize,
                                                 explode_collections=explode_collections,
                                                 snap_to_grid=snap_to_grid,
                                                 equate_null_and_empty=equate_null_and_empty) and \
                       self.checkAttributesEqual(feat, feat_expected, layer_expected.fields(), False, compare):
                        feat_expected_equal = feat_expected
                        break

                if feat_expected_equal is not None:
                    features_expected.remove(feat_expected_equal)
                else:
                    if use_asserts:
                        _TestCase.assertTrue(
                            self, False,
                            'Unexpected result feature: fid {}, geometry: {}, attributes: {}'.format(
                                feat.id(),
                                feat.geometry().constGet().asWkt(precision) if feat.geometry() else 'NULL',
                                feat.attributes())
                        )
                    else:
                        return False

            if len(features_expected) != 0:
                if use_asserts:
                    lst_missing = []
                    for feat in features_expected:
                        lst_missing.append('fid {}, geometry: {}, attributes: {}'.format(
                            feat.id(),
                            feat.geometry().constGet().asWkt(precision) if feat.geometry() else 'NULL',
                            feat.attributes())
                        )
                    _TestCase.assertTrue(self, False, 'Some expected features not found in results:\n' + '\n'.join(lst_missing))
                else:
                    return False

            return True

        def sort_by_pk_or_fid(f):
            if 'pk' in kwargs and kwargs['pk'] is not None:
                key = kwargs['pk']
                if isinstance(key, list) or isinstance(key, tuple):
                    return [f[k] for k in key]
                else:
                    return f[kwargs['pk']]
            else:
                return f.id()

        expected_features = sorted(layer_expected.getFeatures(request), key=sort_by_pk_or_fid)
        result_features = sorted(layer_result.getFeatures(request), key=sort_by_pk_or_fid)

        for feats in zip(expected_features, result_features):

            eq = self.checkGeometriesEqual(feats[0].geometry(),
                                           feats[1].geometry(),
                                           feats[0].id(),
                                           feats[1].id(),
                                           use_asserts, precision, topo_equal_check, ignore_part_order, normalize=normalize, explode_collections=explode_collections,
                                           snap_to_grid=snap_to_grid, equate_null_and_empty=equate_null_and_empty)
            if not eq and not use_asserts:
                return False

            eq = self.checkAttributesEqual(feats[0], feats[1], layer_expected.fields(), use_asserts, compare)
            if not eq and not use_asserts:
                return False

        return True

    def checkFilesEqual(self, filepath_expected, filepath_result, use_asserts=False):
        with open(filepath_expected, 'r') as file_expected:
            with open(filepath_result, 'r') as file_result:
                diff = difflib.unified_diff(
                    file_expected.readlines(),
                    file_result.readlines(),
                    fromfile='expected',
                    tofile='result',
                )
                diff = list(diff)
                eq = not len(diff)
                if use_asserts:
                    self.assertEqual(0, len(diff), ''.join(diff))
                else:
                    return eq

    def assertFilesEqual(self, filepath_expected, filepath_result):
        self.checkFilesEqual(filepath_expected, filepath_result, use_asserts=True)

    def assertDirectoryEqual(self, dirpath_expected: str, dirpath_result: str):
        """
        Checks whether both directories have the same content (non-recursively) and raises an assertion error if not.
        """
        path_expected = Path(dirpath_expected)
        path_result = Path(dirpath_result)

        contents_result = list(path_result.iterdir())
        contents_expected = list(path_expected.iterdir())
        contents_expected = [p for p in contents_expected if p.suffix != '.png' or not p.stem.endswith('_mask')]
        self.assertCountEqual([p.name if p.is_file() else p.stem for p in contents_expected], [p.name if p.is_file() else p.stem for p in contents_result], f'Directory contents mismatch in {dirpath_expected} vs {dirpath_result}')

        # compare file contents
        for expected_file_path in contents_expected:
            if expected_file_path.is_dir():
                continue

            result_file_path = path_result / expected_file_path.name

            if expected_file_path.suffix == '.pbf':
                # vector layer, use assertLayersEqual
                layer_expected = QgsVectorLayer(str(expected_file_path), 'Expected')
                self.assertTrue(layer_expected.isValid())
                layer_result = QgsVectorLayer(str(result_file_path), 'Result')
                self.assertTrue(layer_result.isValid())
                self.assertLayersEqual(layer_expected, layer_result)
            elif expected_file_path.suffix == '.png':
                # image file, use QgsRenderChecker
                checker = QgsRenderChecker()
                res = checker.compareImages(expected_file_path.stem, expected_file_path.as_posix(), result_file_path.as_posix())
                self.assertTrue(res)
            else:
                assert False, f"Don't know how to compare {expected_file_path.suffix} files"

    def assertDirectoriesEqual(self, dirpath_expected: str, dirpath_result: str):
        """ Checks whether both directories have the same content (recursively) and raises an assertion error if not. """
        self.assertDirectoryEqual(dirpath_expected, dirpath_result)

        # recurse through subfolders
        path_expected = Path(dirpath_expected)
        path_result = Path(dirpath_result)
        for p in path_expected.iterdir():
            if p.is_dir():
                self.assertDirectoriesEqual(str(p), path_result / p.stem)

    def assertGeometriesEqual(self, geom0, geom1, geom0_id='geometry 1', geom1_id='geometry 2', precision=14, topo_equal_check=False, ignore_part_order=False, normalize=False, explode_collections=False, snap_to_grid=None, equate_null_and_empty=False):
        self.checkGeometriesEqual(geom0, geom1, geom0_id, geom1_id, use_asserts=True, precision=precision, topo_equal_check=topo_equal_check, ignore_part_order=ignore_part_order, normalize=normalize, explode_collections=explode_collections, snap_to_grid=snap_to_grid, equate_null_and_empty=equate_null_and_empty)

    def checkGeometriesEqual(self, geom0, geom1, geom0_id, geom1_id, use_asserts=False, precision=14, topo_equal_check=False, ignore_part_order=False, normalize=False, explode_collections=False, snap_to_grid=None, equate_null_and_empty=False):
        """ Checks whether two geometries are the same - using either a strict check of coordinates (up to given precision)
        or by using topological equality (where e.g. a polygon with clockwise is equal to a polygon with counter-clockwise
        order of vertices)
        .. versionadded:: 3.2
        """
        geom0_wkt = ''
        geom0_wkt_full = ''
        geom1_wkt = ''
        geom1_wkt_full = ''

        geom0_is_null = geom0.isNull() or (equate_null_and_empty and geom0.isEmpty())
        geom1_is_null = geom1.isNull() or (equate_null_and_empty and geom1.isEmpty())
        if not geom0_is_null and not geom1_is_null:
            if snap_to_grid is not None:
                geom0 = geom0.snappedToGrid(snap_to_grid, snap_to_grid, snap_to_grid, snap_to_grid)
                geom1 = geom1.snappedToGrid(snap_to_grid, snap_to_grid, snap_to_grid, snap_to_grid)
            if normalize:
                geom0.normalize()
                geom1.normalize()

            raw_geom0 = geom0.constGet()
            raw_geom1 = geom1.constGet()
            if explode_collections:
                raw_geom0 = raw_geom0.simplifiedTypeRef()
                raw_geom1 = raw_geom1.simplifiedTypeRef()
            geom0_wkt = raw_geom0.asWkt(precision)
            geom0_wkt_full = raw_geom0.asWkt()
            geom1_wkt = raw_geom1.asWkt(precision)
            geom1_wkt_full = raw_geom1.asWkt()
            equal = geom0_wkt == geom1_wkt
            if not equal and topo_equal_check:
                equal = geom0.isGeosEqual(geom1)
            if not equal and ignore_part_order and geom0.isMultipart():
                equal = sorted([p.asWkt(precision) for p in geom0.constParts()]) == sorted([p.asWkt(precision) for p in geom1.constParts()])
        elif geom0_is_null and geom1_is_null:
            equal = True
        else:
            geom0_wkt = geom0.asWkt(precision)
            geom1_wkt = geom1.asWkt(precision)
            geom0_wkt_full = geom0.asWkt()
            geom1_wkt_full = geom1.asWkt()
            equal = False

        if use_asserts:
            _TestCase.assertTrue(
                self,
                equal, ''
                ' Features (Expected fid: {}, Result fid: {}) differ in geometry with method {}: \n\n'
                '  At given precision ({}):\n'
                '   Expected geometry: {}\n'
                '   Result geometry:   {}\n\n'
                '  Full precision:\n'
                '   Expected geometry : {}\n'
                '   Result geometry:   {}\n\n'.format(
                    geom0_id,
                    geom1_id,
                    'geos' if topo_equal_check else 'wkt',
                    precision,
                    geom0_wkt if not geom0_is_null else 'NULL',
                    geom1_wkt if not geom1_is_null else 'NULL',
                    geom0_wkt_full if not geom0_is_null else 'NULL',
                    geom1_wkt_full if not geom1_is_null else 'NULL'
                )
            )
        else:
            return equal

    def checkAttributesEqual(self, feat0, feat1, fields_expected, use_asserts, compare):
        """ Checks whether attributes of two features are the same
        .. versionadded:: 3.2
        """

        for attr_expected, field_expected in zip(feat0.attributes(), fields_expected.toList()):
            try:
                cmp = compare['fields'][field_expected.name()]
            except KeyError:
                try:
                    cmp = compare['fields']['__all__']
                except KeyError:
                    cmp = {}

            # Skip field
            if 'skip' in cmp:
                continue

            if use_asserts:
                _TestCase.assertIn(
                    self,
                    field_expected.name().lower(),
                    [name.lower() for name in feat1.fields().names()])

            attr_result = feat1[field_expected.name()]
            field_result = [fld for fld in fields_expected.toList() if fld.name() == field_expected.name()][0]

            # Cast field to a given type
            isNumber = False
            if 'cast' in cmp:
                if cmp['cast'] == 'int':
                    attr_expected = int(attr_expected) if attr_expected else None
                    attr_result = int(attr_result) if attr_result else None
                    isNumber = True
                if cmp['cast'] == 'float':
                    attr_expected = float(attr_expected) if attr_expected else None
                    attr_result = float(attr_result) if attr_result else None
                    isNumber = True
                if cmp['cast'] == 'str':
                    if isinstance(attr_expected, QDateTime):
                        attr_expected = attr_expected.toString('yyyy/MM/dd hh:mm:ss')
                    elif isinstance(attr_expected, QDate):
                        attr_expected = attr_expected.toString('yyyy/MM/dd')
                    else:
                        attr_expected = str(attr_expected) if attr_expected else None
                    if isinstance(attr_result, QDateTime):
                        attr_result = attr_result.toString('yyyy/MM/dd hh:mm:ss')
                    elif isinstance(attr_result, QDate):
                        attr_result = attr_result.toString('yyyy/MM/dd')
                    else:
                        attr_result = str(attr_result) if attr_result else None

            # Round field (only numeric so it works with __all__)
            if 'precision' in cmp and (field_expected.type() in [QVariant.Int, QVariant.Double, QVariant.LongLong] or isNumber):
                if not attr_expected == NULL:
                    attr_expected = round(attr_expected, cmp['precision'])
                if not attr_result == NULL:
                    attr_result = round(attr_result, cmp['precision'])

            if use_asserts:
                _TestCase.assertEqual(
                    self,
                    attr_expected,
                    attr_result,
                    'Features {}/{} differ in attributes\n\n * Field expected: {} ({})\n * result  : {} ({})\n\n * Expected: {} != Result  : {}'.format(
                        feat0.id(),
                        feat1.id(),
                        field_expected.name(),
                        field_expected.typeName(),
                        field_result.name(),
                        field_result.typeName(),
                        repr(attr_expected),
                        repr(attr_result)
                    )
                )
            elif attr_expected != attr_result:
                return False

        return True


class _UnexpectedSuccess(Exception):

    """
    The test was supposed to fail, but it didn't!
    """
    pass


def expectedFailure(*args):
    """
    Will decorate a unittest function as an expectedFailure. A function
    flagged as expectedFailure will be succeed if it raises an exception.
    If it does not raise an exception, this will throw an
    `_UnexpectedSuccess` exception.

        @expectedFailure
        def my_test(self):
            self.assertTrue(False)

    The decorator also accepts a parameter to only expect a failure under
    certain conditions.

        @expectedFailure(time.localtime().tm_year < 2002)
        def my_test(self):
            self.assertTrue(qgisIsInvented())
    """
    if hasattr(args[0], '__call__'):
        # We got a function as parameter: assume usage like
        #   @expectedFailure
        #   def testfunction():
        func = args[0]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                pass
            else:
                raise _UnexpectedSuccess
        return wrapper
    else:
        # We got a function as parameter: assume usage like
        #   @expectedFailure(failsOnThisPlatform)
        #   def testfunction():
        condition = args[0]

        def realExpectedFailure(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if condition:
                    try:
                        func(*args, **kwargs)
                    except Exception:
                        pass
                    else:
                        raise _UnexpectedSuccess
                else:
                    func(*args, **kwargs)
            return wrapper

        return realExpectedFailure


# Patch unittest
unittest.TestCase = TestCase
unittest.expectedFailure = expectedFailure


def start_app(cleanup=True):
    """
    Will start a QgsApplication and call all initialization code like
    registering the providers and other infrastructure. It will not load
    any plugins.

    You can always get the reference to a running app by calling `QgsApplication.instance()`.

    The initialization will only happen once, so it is safe to call this method repeatedly.

        Parameters
        ----------

        cleanup: Do cleanup on exit. Defaults to true.

        Returns
        -------
        QgsApplication

        A QgsApplication singleton
    """
    global QGISAPP

    try:
        QGISAPP
    except NameError:
        myGuiFlag = True  # All test will run qgis in gui mode

        try:
            sys.argv
        except AttributeError:
            sys.argv = ['']

        # In python3 we need to convert to a bytes object (or should
        # QgsApplication accept a QString instead of const char* ?)
        try:
            argvb = list(map(os.fsencode, sys.argv))
        except AttributeError:
            argvb = sys.argv

        # Note: QGIS_PREFIX_PATH is evaluated in QgsApplication -
        # no need to mess with it here.
        QGISAPP = QgsApplication(argvb, myGuiFlag)

        tmpdir = tempfile.mkdtemp('', 'QGIS-PythonTestConfigPath-')
        os.environ['QGIS_CUSTOM_CONFIG_PATH'] = tmpdir

        QGISAPP.initQgis()
        print(QGISAPP.showSettings())

        def debug_log_message(message, tag, level):
            print('{}({}): {}'.format(tag, level, message))

        QgsApplication.instance().messageLog().messageReceived.connect(debug_log_message)

        if cleanup:
            import atexit
            import shutil

            @atexit.register
            def exitQgis():
                QGISAPP.exitQgis()
                shutil.rmtree(tmpdir)

    return QGISAPP


def stop_app():
    """
    Cleans up and exits QGIS
    """
    global QGISAPP

    QGISAPP.exitQgis()
    del QGISAPP

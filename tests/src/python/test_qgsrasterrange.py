"""QGIS Unit tests for QgsRasterRange.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
__author__ = 'Nyall Dawson'
__date__ = '07/06/2018'
__copyright__ = 'Copyright 2018, The QGIS Project'

import qgis  # NOQA switch sip api

from qgis.core import QgsRasterRange
from qgis.testing import unittest


class TestQgsRasterRange(unittest.TestCase):

    def testBasic(self):
        range = QgsRasterRange(1, 5)
        self.assertEqual(range.min(), 1)
        self.assertEqual(range.max(), 5)
        range.setMin(2.2)
        range.setMax(10.4)
        self.assertEqual(range.min(), 2.2)
        self.assertEqual(range.max(), 10.4)
        self.assertEqual(range.bounds(), QgsRasterRange.IncludeMinAndMax)
        range.setBounds(QgsRasterRange.IncludeMin)
        self.assertEqual(range.bounds(), QgsRasterRange.IncludeMin)

    def testEquality(self):
        range = QgsRasterRange(1, 5)
        range2 = QgsRasterRange(1, 5)
        self.assertEqual(range, range2)
        range2.setMin(2)
        self.assertNotEqual(range, range2)
        range2.setMin(1)
        range2.setMax(4)
        self.assertNotEqual(range, range2)
        range2.setMax(5)
        self.assertEqual(range, range2)
        range.setBounds(QgsRasterRange.IncludeMax)
        self.assertNotEqual(range, range2)
        range2.setBounds(QgsRasterRange.IncludeMax)
        self.assertEqual(range, range2)
        range = QgsRasterRange()
        range2 = QgsRasterRange()
        self.assertEqual(range, range2)
        range.setMin(1)
        self.assertNotEqual(range, range2)
        range2.setMin(1)
        self.assertEqual(range, range2)
        range = QgsRasterRange()
        range2 = QgsRasterRange()
        range.setMax(5)
        self.assertNotEqual(range, range2)
        range2.setMax(5)
        self.assertEqual(range, range2)

    def testContains(self):
        range = QgsRasterRange(1, 5)
        self.assertTrue(range.contains(1))
        self.assertTrue(range.contains(5))
        self.assertTrue(range.contains(4))
        self.assertTrue(range.contains(1.00001))
        self.assertTrue(range.contains(4.99999))
        self.assertFalse(range.contains(0.99999))
        self.assertFalse(range.contains(5.00001))

        # with nan min/maxs
        range = QgsRasterRange()
        self.assertTrue(range.contains(1))
        self.assertTrue(range.contains(-909999999))
        self.assertTrue(range.contains(999999999))
        range.setMin(5)
        self.assertFalse(range.contains(0))
        self.assertTrue(range.contains(5))
        self.assertTrue(range.contains(10000000))

        range = QgsRasterRange()
        range.setMax(5)
        self.assertFalse(range.contains(6))
        self.assertTrue(range.contains(5))
        self.assertTrue(range.contains(-99999))

        range = QgsRasterRange(1, 5, QgsRasterRange.IncludeMax)
        self.assertFalse(range.contains(0))
        self.assertFalse(range.contains(1))
        self.assertTrue(range.contains(2))
        self.assertTrue(range.contains(5))
        self.assertFalse(range.contains(6))

        range = QgsRasterRange(1, 5, QgsRasterRange.IncludeMin)
        self.assertFalse(range.contains(0))
        self.assertTrue(range.contains(1))
        self.assertTrue(range.contains(2))
        self.assertFalse(range.contains(5))
        self.assertFalse(range.contains(6))

        range = QgsRasterRange(1, 5, QgsRasterRange.Exclusive)
        self.assertFalse(range.contains(0))
        self.assertFalse(range.contains(1))
        self.assertTrue(range.contains(2))
        self.assertFalse(range.contains(5))
        self.assertFalse(range.contains(6))

    def testContainsList(self):
        self.assertFalse(QgsRasterRange.contains(1, []))
        ranges = [QgsRasterRange(1, 5)]
        self.assertTrue(QgsRasterRange.contains(3, ranges))
        self.assertFalse(QgsRasterRange.contains(13, ranges))
        ranges.append(QgsRasterRange(11, 15))
        self.assertTrue(QgsRasterRange.contains(3, ranges))
        self.assertTrue(QgsRasterRange.contains(13, ranges))
        self.assertFalse(QgsRasterRange.contains(16, ranges))

    def testOverlaps(self):
        # includes both ends
        range = QgsRasterRange(0, 10, QgsRasterRange.IncludeMinAndMax)
        self.assertTrue(range.overlaps(QgsRasterRange(1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0)))
        self.assertFalse(range.overlaps(QgsRasterRange(-10, -1)))
        self.assertFalse(range.overlaps(QgsRasterRange(11, 12)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(0, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(10, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(11, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(float('NaN'), -1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 0)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.Exclusive)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMin)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMax)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.Exclusive)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMin)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMax)))

        range = QgsRasterRange(float('NaN'), 10, QgsRasterRange.IncludeMinAndMax)
        self.assertTrue(range.overlaps(QgsRasterRange(1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0)))
        self.assertTrue(range.overlaps(QgsRasterRange(-10, -1)))
        self.assertFalse(range.overlaps(QgsRasterRange(11, 12)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(0, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(10, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(11, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), -1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 0)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.Exclusive)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMin)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMax)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.Exclusive)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMin)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMax)))

        range = QgsRasterRange(0, float('NaN'), QgsRasterRange.IncludeMinAndMax)
        self.assertTrue(range.overlaps(QgsRasterRange(1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0)))
        self.assertFalse(range.overlaps(QgsRasterRange(-10, -1)))
        self.assertTrue(range.overlaps(QgsRasterRange(11, 12)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(0, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(10, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(11, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(float('NaN'), -1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 0)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.Exclusive)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMin)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMax)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.Exclusive)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMin)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMax)))

        # includes left end
        range = QgsRasterRange(0, 10, QgsRasterRange.IncludeMin)
        self.assertTrue(range.overlaps(QgsRasterRange(1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 11)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0)))
        self.assertFalse(range.overlaps(QgsRasterRange(-10, -1)))
        self.assertFalse(range.overlaps(QgsRasterRange(11, 12)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(0, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(1, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(10, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(11, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(float('NaN'), -1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 0)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.Exclusive)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMin)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMax)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.Exclusive)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMin)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMax)))

        # includes right end
        range = QgsRasterRange(0, 10, QgsRasterRange.IncludeMax)
        self.assertTrue(range.overlaps(QgsRasterRange(1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0)))
        self.assertFalse(range.overlaps(QgsRasterRange(-10, -1)))
        self.assertFalse(range.overlaps(QgsRasterRange(11, 12)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 50)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(10, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(11, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(float('NaN'), -1)))
        self.assertFalse(range.overlaps(QgsRasterRange(float('NaN'), 0)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.Exclusive)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMin)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMax)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.Exclusive)))
        self.assertTrue(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMin)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMax)))

        # includes neither end
        range = QgsRasterRange(0, 10, QgsRasterRange.Exclusive)
        self.assertTrue(range.overlaps(QgsRasterRange(1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(0, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 9)))
        self.assertTrue(range.overlaps(QgsRasterRange(1, 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, 11)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0)))
        self.assertFalse(range.overlaps(QgsRasterRange(-10, -1)))
        self.assertFalse(range.overlaps(QgsRasterRange(11, 12)))
        self.assertTrue(range.overlaps(QgsRasterRange(-1, float('NaN'))))
        self.assertTrue(range.overlaps(QgsRasterRange(1, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(10, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(11, float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(float('NaN'), -1)))
        self.assertFalse(range.overlaps(QgsRasterRange(float('NaN'), 0)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 1)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 10)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), 11)))
        self.assertTrue(range.overlaps(QgsRasterRange(float('NaN'), float('NaN'))))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.Exclusive)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMin)))
        self.assertFalse(range.overlaps(QgsRasterRange(-1, 0, QgsRasterRange.IncludeMax)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.Exclusive)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMin)))
        self.assertFalse(range.overlaps(QgsRasterRange(10, 11, QgsRasterRange.IncludeMax)))

    def testAsText(self):
        self.assertEqual(QgsRasterRange(0, 10, QgsRasterRange.IncludeMinAndMax).asText(), '0 ≤ x ≤ 10')
        self.assertEqual(QgsRasterRange(-1, float('NaN')).asText(), '-1 ≤ x ≤ ∞')
        self.assertEqual(QgsRasterRange(float('NaN'), 5).asText(), '-∞ ≤ x ≤ 5')
        self.assertEqual(QgsRasterRange(float('NaN'), float('NaN')).asText(), '-∞ ≤ x ≤ ∞')
        self.assertEqual(QgsRasterRange(0, 10, QgsRasterRange.IncludeMin).asText(), '0 ≤ x < 10')
        self.assertEqual(QgsRasterRange(-1, float('NaN'), QgsRasterRange.IncludeMin).asText(), '-1 ≤ x < ∞')
        self.assertEqual(QgsRasterRange(float('NaN'), 5, QgsRasterRange.IncludeMin).asText(), '-∞ ≤ x < 5')
        self.assertEqual(QgsRasterRange(float('NaN'), float('NaN'), QgsRasterRange.IncludeMin).asText(), '-∞ ≤ x < ∞')
        self.assertEqual(QgsRasterRange(0, 10, QgsRasterRange.IncludeMax).asText(), '0 < x ≤ 10')
        self.assertEqual(QgsRasterRange(-1, float('NaN'), QgsRasterRange.IncludeMax).asText(), '-1 < x ≤ ∞')
        self.assertEqual(QgsRasterRange(float('NaN'), 5, QgsRasterRange.IncludeMax).asText(), '-∞ < x ≤ 5')
        self.assertEqual(QgsRasterRange(float('NaN'), float('NaN'), QgsRasterRange.IncludeMax).asText(), '-∞ < x ≤ ∞')
        self.assertEqual(QgsRasterRange(0, 10, QgsRasterRange.Exclusive).asText(), '0 < x < 10')
        self.assertEqual(QgsRasterRange(-1, float('NaN'), QgsRasterRange.Exclusive).asText(), '-1 < x < ∞')
        self.assertEqual(QgsRasterRange(float('NaN'), 5, QgsRasterRange.Exclusive).asText(), '-∞ < x < 5')
        self.assertEqual(QgsRasterRange(float('NaN'), float('NaN'), QgsRasterRange.Exclusive).asText(), '-∞ < x < ∞')


if __name__ == '__main__':
    unittest.main()
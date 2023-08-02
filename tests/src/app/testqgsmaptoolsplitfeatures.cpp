/***************************************************************************
     testqgsmaptoolsplitfeatures.cpp
     ------------------------
    Date                 : August 2020
    Copyright            : (C) 2020 by Stefanos Natsis
    Email                : uclaros@gmail.com
 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include "qgstest.h"

#include "qgisapp.h"
#include "qgsgeometry.h"
#include "qgsmapcanvas.h"
#include "qgssettings.h"
#include "qgsvectorlayer.h"
#include "qgsmaptoolsplitfeatures.h"
#include "qgsgeometryutils.h"

#include "testqgsmaptoolutils.h"

class TestQgsMapToolSplitFeatures : public QObject
{
    Q_OBJECT

  public:
    TestQgsMapToolSplitFeatures();

  private slots:
    void initTestCase();
    void cleanupTestCase();

    void testNoFeaturesSplit();
    void testSplitPolygon();
    void testSplitPolygonTopologicalEditing();
    void testSplitSelectedLines();
    void testSplitSomeOfSelectedLines();

  private:
    QPoint mapToPoint( double x, double y );
    QgisApp *mQgisApp = nullptr;
    QgsMapCanvas *mCanvas = nullptr;
    QgsVectorLayer *mMultiLineStringLayer = nullptr;
    QgsVectorLayer *mPolygonLayer = nullptr;
    QgsVectorLayer *mMultiPolygonLayer = nullptr;
    QgsFeature lineF1, lineF2, polygonF1, polygonF2, multipolygonF1;
};

TestQgsMapToolSplitFeatures::TestQgsMapToolSplitFeatures() = default;


//runs before all tests
void TestQgsMapToolSplitFeatures::initTestCase()
{
  QgsApplication::init();
  QgsApplication::initQgis();

  mQgisApp = new QgisApp();

  mCanvas = new QgsMapCanvas();
  mCanvas->setDestinationCrs( QgsCoordinateReferenceSystem( QStringLiteral( "EPSG:3946" ) ) );

  // make testing layers
  mMultiLineStringLayer = new QgsVectorLayer( QStringLiteral( "MultiLineString?crs=EPSG:3946" ), QStringLiteral( "layer multiline" ), QStringLiteral( "memory" ) );
  QVERIFY( mMultiLineStringLayer->isValid() );
  mMultiLineStringLayer->startEditing();
  lineF1.setGeometry( QgsGeometry::fromWkt( QStringLiteral( "MultiLineString ((0 0, 10 0))" ) ) );
  lineF2.setGeometry( QgsGeometry::fromWkt( QStringLiteral( "MultiLineString ((0 5, 10 5),(10 5, 15 5))" ) ) );
  mMultiLineStringLayer->addFeature( lineF1 );
  mMultiLineStringLayer->addFeature( lineF2 );

  mPolygonLayer = new QgsVectorLayer( QStringLiteral( "PolygonZ?crs=EPSG:3946" ), QStringLiteral( "layer polygon" ), QStringLiteral( "memory" ) );
  QVERIFY( mPolygonLayer->isValid() );
  mPolygonLayer->startEditing();
  polygonF1.setGeometry( QgsGeometry::fromWkt( QStringLiteral( "PolygonZ ((0 5 10, 0 10 20, 10 10 30, 10 5 20, 0 5 10))" ) ) );
  polygonF2.setGeometry( QgsGeometry::fromWkt( QStringLiteral( "PolygonZ ((0 0 10, 0 5 20, 10 5 30, 10 0 20, 0 0 10))" ) ) );
  mPolygonLayer->addFeature( polygonF1 );
  mPolygonLayer->addFeature( polygonF2 );

  mMultiPolygonLayer = new QgsVectorLayer( QStringLiteral( "MultiPolygon?crs=EPSG:3946" ), QStringLiteral( "layer multipolygon" ), QStringLiteral( "memory" ) );
  QVERIFY( mMultiPolygonLayer->isValid() );
  mMultiPolygonLayer->startEditing();
  multipolygonF1.setGeometry( QgsGeometry::fromWkt( QStringLiteral( "MultiPolygon (((0 5, 0 10, 10 10, 10 5, 0 5)),((0 0, 0 4, 10 4, 10 0, 0 0)))" ) ) );
  mMultiPolygonLayer->addFeature( multipolygonF1 );

  mCanvas->setFrameStyle( QFrame::NoFrame );
  mCanvas->resize( 50, 50 );
  mCanvas->setExtent( QgsRectangle( 0, 0, 10, 10 ) );
  mCanvas->show(); // to make the canvas resize
  mCanvas->hide();
  // Disable flaky tests on windows...
  // QCOMPARE( mCanvas->mapSettings().outputSize(), QSize( 50, 50 ) );
  // QCOMPARE( mCanvas->mapSettings().visibleExtent(), QgsRectangle( 0, 0, 10, 10 ) );

  QgsProject::instance()->addMapLayers( QList<QgsMapLayer *>() << mMultiLineStringLayer
                                        << mPolygonLayer
                                        << mMultiPolygonLayer );

  // set layers in canvas
  mCanvas->setLayers( QList<QgsMapLayer *>() << mMultiLineStringLayer
                      << mPolygonLayer
                      << mMultiPolygonLayer );

}

void TestQgsMapToolSplitFeatures::cleanupTestCase()
{
  QgsApplication::exitQgis();
}

QPoint TestQgsMapToolSplitFeatures::mapToPoint( double x, double y )
{

  const QgsPointXY mapPoint = mCanvas->mapSettings().mapToPixel().transform( x, y );

  return QPoint( std::round( mapPoint.x() ), std::round( mapPoint.y() ) );
}

void TestQgsMapToolSplitFeatures::testNoFeaturesSplit()
{
  mCanvas->setCurrentLayer( mMultiLineStringLayer );
  QgsMapToolSplitFeatures *mapTool = new QgsMapToolSplitFeatures( mCanvas ) ;
  mCanvas->setMapTool( mapTool );

  std::unique_ptr< QgsMapMouseEvent > event( new QgsMapMouseEvent(
        mCanvas,
        QEvent::MouseButtonRelease,
        mapToPoint( 4, 7 ),
        Qt::LeftButton
      ) );
  mapTool->cadCanvasReleaseEvent( event.get() );
  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 4, 8 ),
                 Qt::LeftButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 4, 8 ),
                 Qt::RightButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );


  QVERIFY( mMultiLineStringLayer->featureCount() == 2 );
  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 2 );
}

void TestQgsMapToolSplitFeatures::testSplitPolygon()
{
  QgsProject::instance()->setTopologicalEditing( false );
  mCanvas->setCurrentLayer( mPolygonLayer );
  QgsMapToolSplitFeatures *mapTool = new QgsMapToolSplitFeatures( mCanvas ) ;
  mCanvas->setMapTool( mapTool );

  std::unique_ptr< QgsMapMouseEvent > event( new QgsMapMouseEvent(
        mCanvas,
        QEvent::MouseButtonRelease,
        mapToPoint( 4, 11 ),
        Qt::LeftButton
      ) );
  mapTool->cadCanvasReleaseEvent( event.get() );
  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 4, 3 ),
                 Qt::LeftButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 4, 3 ),
                 Qt::RightButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  QVERIFY( mPolygonLayer->undoStack()->index() == 3 );
  QVERIFY( mPolygonLayer->featureCount() == 3 );
  QCOMPARE( mPolygonLayer->getFeature( polygonF1.id() ).geometry().asWkt(), QStringLiteral( "PolygonZ ((4 10 24, 4 5 14, 0 5 10, 0 10 20, 4 10 24))" ) );
  QCOMPARE( mPolygonLayer->getFeature( polygonF2.id() ).geometry().asWkt(), QStringLiteral( "PolygonZ ((0 0 10, 0 5 20, 10 5 30, 10 0 20, 0 0 10))" ) );

  // no change to other layers
  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 2 );
  QVERIFY( mMultiPolygonLayer->undoStack()->index() == 1 );

  // undo changes
  mPolygonLayer->undoStack()->undo();
  QVERIFY( mPolygonLayer->undoStack()->index() == 2 );
}

void TestQgsMapToolSplitFeatures::testSplitPolygonTopologicalEditing()
{
  QgsProject::instance()->setTopologicalEditing( true );
  mCanvas->setCurrentLayer( mPolygonLayer );
  QgsMapToolSplitFeatures *mapTool = new QgsMapToolSplitFeatures( mCanvas ) ;
  mCanvas->setMapTool( mapTool );

  std::unique_ptr< QgsMapMouseEvent > event( new QgsMapMouseEvent(
        mCanvas,
        QEvent::MouseButtonRelease,
        mapToPoint( 4, 11 ),
        Qt::LeftButton
      ) );
  mapTool->cadCanvasReleaseEvent( event.get() );
  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 4, 3 ),
                 Qt::LeftButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 4, 3 ),
                 Qt::RightButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  QVERIFY( mPolygonLayer->undoStack()->index() == 3 );
  QVERIFY( mPolygonLayer->featureCount() == 3 );
  QCOMPARE( mPolygonLayer->getFeature( polygonF1.id() ).geometry().asWkt(), QStringLiteral( "PolygonZ ((4 10 24, 4 5 14, 0 5 10, 0 10 20, 4 10 24))" ) );
  QCOMPARE( mPolygonLayer->getFeature( polygonF2.id() ).geometry().asWkt(), QStringLiteral( "PolygonZ ((0 0 10, 0 5 20, 4 5 14, 10 5 30, 10 0 20, 0 0 10))" ) );

  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 3 );
  QCOMPARE( mMultiLineStringLayer->getFeature( lineF2.id() ).geometry().asWkt(), QStringLiteral( "MultiLineString ((0 5, 4 5, 10 5),(10 5, 15 5))" ) );
  QVERIFY( mMultiPolygonLayer->undoStack()->index() == 2 );
  QCOMPARE( mMultiPolygonLayer->getFeature( multipolygonF1.id() ).geometry().asWkt(), QStringLiteral( "MultiPolygon (((0 5, 0 10, 4 10, 10 10, 10 5, 4 5, 0 5)),((0 0, 0 4, 10 4, 10 0, 0 0)))" ) );

  // undo changes
  mPolygonLayer->undoStack()->undo();
  QVERIFY( mPolygonLayer->undoStack()->index() == 2 );
  mMultiLineStringLayer->undoStack()->undo();
  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 2 );
  mMultiPolygonLayer->undoStack()->undo();
  QVERIFY( mMultiPolygonLayer->undoStack()->index() == 1 );
}

void TestQgsMapToolSplitFeatures::testSplitSelectedLines()
{
  mMultiLineStringLayer->select( lineF1.id() );
  mCanvas->setCurrentLayer( mMultiLineStringLayer );
  QgsMapToolSplitFeatures *mapTool = new QgsMapToolSplitFeatures( mCanvas ) ;
  mCanvas->setMapTool( mapTool );

  std::unique_ptr< QgsMapMouseEvent > event( new QgsMapMouseEvent(
        mCanvas,
        QEvent::MouseButtonRelease,
        mapToPoint( 5, 6 ),
        Qt::LeftButton
      ) );
  mapTool->cadCanvasReleaseEvent( event.get() );
  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 5, -1 ),
                 Qt::LeftButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 5, -1 ),
                 Qt::RightButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );


  // only the selected feature should be split
  QVERIFY( mMultiLineStringLayer->featureCount() == 3 );
  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 3 );

  // undo changes
  mMultiLineStringLayer->undoStack()->undo();
  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 2 );
  mMultiLineStringLayer->removeSelection();
}

void TestQgsMapToolSplitFeatures::testSplitSomeOfSelectedLines()
{
  mMultiLineStringLayer->selectAll();
  mCanvas->setCurrentLayer( mMultiLineStringLayer );
  QgsMapToolSplitFeatures *mapTool = new QgsMapToolSplitFeatures( mCanvas ) ;
  mCanvas->setMapTool( mapTool );

  std::unique_ptr< QgsMapMouseEvent > event( new QgsMapMouseEvent(
        mCanvas,
        QEvent::MouseButtonRelease,
        mapToPoint( 5, 1 ),
        Qt::LeftButton
      ) );
  mapTool->cadCanvasReleaseEvent( event.get() );
  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 5, -1 ),
                 Qt::LeftButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  event.reset( new QgsMapMouseEvent(
                 mCanvas,
                 QEvent::MouseButtonRelease,
                 mapToPoint( 5, -1 ),
                 Qt::RightButton
               ) );
  mapTool->cadCanvasReleaseEvent( event.get() );

  // intersecting selected feature should be split
  QVERIFY( mMultiLineStringLayer->featureCount() == 3 );
  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 3 );

  // undo changes
  mMultiLineStringLayer->undoStack()->undo();
  QVERIFY( mMultiLineStringLayer->undoStack()->index() == 2 );
  mMultiLineStringLayer->removeSelection();
}

QGSTEST_MAIN( TestQgsMapToolSplitFeatures )
#include "testqgsmaptoolsplitfeatures.moc"

/***************************************************************************
  qgsvectortiledataprovider.cpp
  --------------------------------------
  Date                 : March 2020
  Copyright            : (C) 2020 by Martin Dobias
  Email                : wonder dot sk at gmail dot com
 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include "qgsvectortiledataprovider.h"
#include "qgsthreadingutils.h"
#include "qgsreadwritelocker.h"
#include "qgsvectortileloader.h"

#include <QNetworkRequest>
#include <QImage>

QgsVectorTileDataProvider::QgsVectorTileDataProvider(
  const QString &uri,
  const ProviderOptions &options,
  QgsDataProvider::ReadFlags flags )
  : QgsDataProvider( uri, options, flags )
  , mShared( new QgsVectorTileDataProviderSharedData )
{}

QgsVectorTileDataProvider::QgsVectorTileDataProvider( const QgsVectorTileDataProvider &other )
  : QgsDataProvider( other.dataSourceUri( false ), ProviderOptions(), other.mReadFlags )
  , mShared( other.mShared )
{
  setTransformContext( other.transformContext() );
}

Qgis::VectorTileProviderFlags QgsVectorTileDataProvider::providerFlags() const
{
  return Qgis::VectorTileProviderFlags();
}

Qgis::VectorTileProviderCapabilities QgsVectorTileDataProvider::providerCapabilities() const
{
  return Qgis::VectorTileProviderCapabilities();
}

QgsRectangle QgsVectorTileDataProvider::extent() const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return QgsRectangle();
}

bool QgsVectorTileDataProvider::renderInPreview( const PreviewContext &context )
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  // Vector tiles by design are very CPU light to render, so we are much more permissive here compared
  // with other layer types. (Generally if a vector tile layer has taken more than a few milliseconds to render it's
  // a result of network requests, and the tile manager class handles these gracefully for us)
  return context.lastRenderingTimeMs <= 1000;
}

bool QgsVectorTileDataProvider::supportsAsync() const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return false;
}

QNetworkRequest QgsVectorTileDataProvider::tileRequest( const QgsTileMatrixSet &, const QgsTileXYZ &, Qgis::RendererUsage ) const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return QNetworkRequest();
}

QVariantMap QgsVectorTileDataProvider::styleDefinition() const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return QVariantMap();
}

QString QgsVectorTileDataProvider::styleUrl() const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return QString();
}

QVariantMap QgsVectorTileDataProvider::spriteDefinition() const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return QVariantMap();
}

QImage QgsVectorTileDataProvider::spriteImage() const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return QImage();
}

QString QgsVectorTileDataProvider::htmlMetadata() const
{
  QGIS_PROTECT_QOBJECT_THREAD_ACCESS

  return QString();
}




QgsVectorTileDataProviderSharedData::QgsVectorTileDataProviderSharedData()
{
  mTileCache.setMaxCost( 200 );
}

bool QgsVectorTileDataProviderSharedData::getCachedTileData( QgsVectorTileRawData &data, QgsTileXYZ tile )
{
  QgsReadWriteLocker locker( mMutex, QgsReadWriteLocker::Read );
  if ( QgsVectorTileRawData *cachedData = mTileCache.object( tile ) )
  {
    data = *cachedData;
    return true;
  }

  return false;
}

void QgsVectorTileDataProviderSharedData::storeCachedTileData( const QgsVectorTileRawData &data )
{
  QgsReadWriteLocker locker( mMutex, QgsReadWriteLocker::Write );
  mTileCache.insert( data.id, new QgsVectorTileRawData( data ) );
}

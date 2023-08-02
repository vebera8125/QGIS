/***************************************************************************
      qgsogrguiprovider.cpp  - GUI for QGIS Data provider for GDAL rasters
                             -------------------
    begin                : June, 2019
    copyright            : (C) 2019 by Peter Petrik
    email                : zilolv at gmail dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include <QList>

#include "qgsogrguiprovider.h"
///@cond PRIVATE

#include "qgssourceselectprovider.h"
#include "qgsogrsourceselect.h"
#include "qgsogrdbsourceselect.h"
#include "qgsapplication.h"
#include "qgsprovidermetadata.h"
#include "qgsdataitemguiprovider.h"
#include "qgsgeopackageitemguiprovider.h"
#include "qgsogritemguiprovider.h"
#include "qgsgeopackageprojectstorageguiprovider.h"
#include "qgsprojectstorageguiprovider.h"

static const QString TEXT_PROVIDER_KEY = QStringLiteral( "ogr" );

//! Provider for OGR vector source select
class QgsOgrVectorSourceSelectProvider : public QgsSourceSelectProvider
{
  public:

    QString providerKey() const override { return QStringLiteral( "ogr" ); }
    QString text() const override { return QObject::tr( "Vector" ); }
    int ordering() const override { return QgsSourceSelectProvider::OrderLocalProvider + 10; }
    QIcon icon() const override { return QgsApplication::getThemeIcon( QStringLiteral( "/mActionAddOgrLayer.svg" ) ); }
    QgsAbstractDataSourceWidget *createDataSourceWidget( QWidget *parent = nullptr, Qt::WindowFlags fl = Qt::Widget, QgsProviderRegistry::WidgetMode widgetMode = QgsProviderRegistry::WidgetMode::Embedded ) const override;
};


//! Provider for GPKG vector source select
class QgsGeoPackageSourceSelectProvider : public QgsSourceSelectProvider
{
  public:

    virtual QString name() const override;
    QString providerKey() const override { return QStringLiteral( "ogr" ); }
    QString text() const override { return QObject::tr( "GeoPackage" ); }
    int ordering() const override { return QgsSourceSelectProvider::OrderLocalProvider + 45; }
    QIcon icon() const override { return QgsApplication::getThemeIcon( QStringLiteral( "/mActionAddGeoPackageLayer.svg" ) ); }
    QgsAbstractDataSourceWidget *createDataSourceWidget( QWidget *parent = nullptr, Qt::WindowFlags fl = Qt::Widget, QgsProviderRegistry::WidgetMode widgetMode = QgsProviderRegistry::WidgetMode::Embedded ) const override;
};


/* This has been tested and works just fine:
//! Provider for SQLite vector source select
class QgsSpatiaLiteSourceSelectProvider : public QgsSourceSelectProvider
{
  public:

    QString providerKey() const override { return QStringLiteral( "ogr" ); }
    QString text() const override { return QObject::tr( "SQLite" ); }
    int ordering() const override { return QgsSourceSelectProvider::OrderLocalProvider + 46; }
    QIcon icon() const override { return QgsApplication::getThemeIcon( QStringLiteral( "/mIconSpatialite.svg" ) ); }
    QgsAbstractDataSourceWidget *createDataSourceWidget( QWidget *parent = nullptr, Qt::WindowFlags fl = Qt::Widget, QgsProviderRegistry::WidgetMode widgetMode = QgsProviderRegistry::WidgetMode::Embedded ) const override
    {
      return new QgsOgrDbSourceSelect( QStringLiteral( "SQLite" ), QObject::tr( "SQLite" ),  QObject::tr( "SpatiaLite Database (*.db *.sqlite)" ), parent, fl, widgetMode );
    }
};
//*/

QString QgsGeoPackageSourceSelectProvider::name() const { return QStringLiteral( "GeoPackage" ); }

QgsAbstractDataSourceWidget *QgsGeoPackageSourceSelectProvider::createDataSourceWidget( QWidget *parent, Qt::WindowFlags fl, QgsProviderRegistry::WidgetMode widgetMode ) const
{
  return new QgsOgrDbSourceSelect( QStringLiteral( "GPKG" ), QObject::tr( "GeoPackage" ), QObject::tr( "GeoPackage Database (*.gpkg)" ), parent, fl, widgetMode );
}

QgsAbstractDataSourceWidget *QgsOgrVectorSourceSelectProvider::createDataSourceWidget( QWidget *parent, Qt::WindowFlags fl, QgsProviderRegistry::WidgetMode widgetMode ) const
{
  return new QgsOgrSourceSelect( parent, fl, widgetMode );
}

QgsOgrGuiProviderMetadata::QgsOgrGuiProviderMetadata()
  : QgsProviderGuiMetadata( TEXT_PROVIDER_KEY )
{
}

QList<QgsSourceSelectProvider *> QgsOgrGuiProviderMetadata::sourceSelectProviders()
{
  QList<QgsSourceSelectProvider *> providers;

  providers
      << new QgsOgrVectorSourceSelectProvider
      << new QgsGeoPackageSourceSelectProvider;
  // << new QgsSpatiaLiteSourceSelectProvider;

  return providers;
}

QList<QgsDataItemGuiProvider *> QgsOgrGuiProviderMetadata::dataItemGuiProviders()
{
  QList<QgsDataItemGuiProvider *> providers;
  providers << new QgsGeoPackageItemGuiProvider();
  providers << new QgsOgrItemGuiProvider();
  return providers;
}

QList<QgsProjectStorageGuiProvider *> QgsOgrGuiProviderMetadata::projectStorageGuiProviders()
{
  QList<QgsProjectStorageGuiProvider *> providers;
  providers << new QgsGeoPackageProjectStorageGuiProvider();
  return providers;

}

///@endcond

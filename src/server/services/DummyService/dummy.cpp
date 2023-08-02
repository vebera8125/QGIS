/***************************************************************************
                           dummy.cpp

  Sample service implementation
  -----------------------------
  begin                : 2016-12-13
  copyright            : (C) 2016 by David Marteau
  email                : david dot marteau at 3liz dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include "qgsmodule.h"

// Service
class SampleService: public QgsService
{
  public:
    QString name()    const override { return "SampleService"; }
    QString version() const override { return "1.0"; }

    void executeRequest( const QgsServerRequest &request, QgsServerResponse &response,
                         const QgsProject *project ) override
    {
      Q_UNUSED( project )
      Q_UNUSED( request )
      QgsDebugMsgLevel( QStringLiteral( "SampleService::executeRequest called" ), 2 );
      response.write( QString( "Hello world from myService" ) );
    }
};

// Module
class QgsSampleModule: public QgsServiceModule
{
  public:
    void registerSelf( QgsServiceRegistry &registry, QgsServerInterface *serverIface ) override
    {
      Q_UNUSED( serverIface )
      QgsDebugMsgLevel( QStringLiteral( "SampleModule::registerSelf called" ), 2 );
      registry.registerService( new  SampleService() );
    }
};

// Entry points
QGISEXTERN QgsServiceModule *QGS_ServiceModule_Init()
{
  static QgsSampleModule sModule;
  return &sModule;
}
QGISEXTERN void QGS_ServiceModule_Exit( QgsServiceModule * )
{
  // Nothing to do
}






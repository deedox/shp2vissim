# -*- coding: utf-8 -*-
"""
"""
import ftools_utils
import VissimData
import MoveFeaturesFastTool

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class ZlyTools:

  def __init__( self, iface ):
    # Save reference to the QGIS interface
    self.iface = iface
 
  def initGui( self ):
 
    # create action that will start plugin
    self.shp2vissim = QAction( "SHP2Vissim", self.iface.mainWindow() )
    self.shp2vissim2 = QAction( "SHP2Vissim2", self.iface.mainWindow() )
    QObject.connect( self.shp2vissim, SIGNAL("triggered()"), self.run )
    
    self.moveFeaturesAction = QAction( "moveFeatures", self.iface.mainWindow() )
    QObject.connect( self.moveFeaturesAction, SIGNAL("triggered()"), self.moveFeatures )
    
    self.iface.addPluginToMenu( "zlyTools", self.shp2vissim )
    self.iface.addPluginToMenu( "zlyTools", self.moveFeaturesAction )
    
  def moveFeatures( self ):
    canvas = self.iface.mapCanvas()
    self.moveTool = MoveFeaturesFastTool.MoveFeaturesFastTool( canvas )
    QObject.connect( self.moveTool.object, SIGNAL("finished()"), self.doneMoveFeatures)
    self.saveTool = canvas.mapTool()
    canvas.setMapTool( self.moveTool )

  def doneMoveFeatures( self ):
    self.iface.mapCanvas().setMapTool( self.saveTool )
    
  def unload(self):
    # remove the plugin menu item and icon
    self.iface.removePluginMenu( "zlyTools", self.shp2vissim )
    self.iface.removePluginMenu( "zlyTools", self.moveFeaturesAction )
 
  def run( self ):
    #from tools.doAbout import GdalToolsAboutDialog as About
    #d = About( self.iface )
    #d.exec_()
    
    layer = ftools_utils.getVectorLayerByName( 'heighway' )
    provider = layer.dataProvider()
    
    feat = QgsFeature()
    allAttrs = provider.attributeIndexes()
    provider.select( allAttrs )
    
    vfile = VissimData.VissimFile( 'd:/kuku_vissim.inp' )
    wgs84 = QgsCoordinateReferenceSystem( 4326, QgsCoordinateReferenceSystem.EpsgCrsId )
    beijing = QgsCoordinateReferenceSystem( 2404, QgsCoordinateReferenceSystem.EpsgCrsId )
    i = 1
    while provider.nextFeature( feat ):  #iterate all features
        geom = feat.geometry()
        if geom == None:
            QMessageBox.information( None, '', 'no geometry exist' )
            break
        
        pline = geom.asPolyline()
        QMessageBox.information( None, '', ' pline points number: %d' % len(pline)  )
        
        xform = QgsCoordinateTransform( wgs84, beijing )   
        points = []
        for p in pline:
            points.append( xform.transform( p ) )        
        link = VissimData.Link( i )
        link.setGeometry( points )
        link.lanes = 2
        vfile.appendLink( link )
        i += 1
        
        #add reverse link
        points.reverse()
        pointsReverse = []
        for pt in points:
            pointsReverse.append( QgsPoint( pt.x(), pt.y()+15 ) )
        link = VissimData.Link( i )
        link.lanes = 2
        link.setGeometry( pointsReverse )
        vfile.appendLink( link )
        i += 1

    vfile.save()
    
    QMessageBox.information(None, '', 'finished' ) 

        
        
        





# -*- coding: utf-8 -*-
""" File: MoveFeaturesFastTool.py
    Description: 
    Author: Li-Ye Zhang
    Created Date: 2012-7-15 / 下午3:16:17
"""
import ftools_utils

from qgis.core import *
from qgis.gui import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

cursor = QCursor(QPixmap(["16 16 3 1","# c None","a c #000000",". c #ffffff",".###############","...#############",".aa..###########","#.aaa..a.a.a.a.#","#.aaaaa..#####a#","#a.aaaaaa..###.#","#..aaaaaa...##a#","#a.aaaaa.#####.#","#.#.aaaaa.####a#","#a#.aa.aaa.###.#","#.##..#..aa.##a#","#a##.####.aa.#.#","#.########.aa.a#","#a#########.aa..","#.a.a.a.a.a..a.#","#############.##"]))

class MoveFeaturesFastTool( QgsMapTool ):
    def __init__( self, canvas ):
        QgsMapTool.__init__( self,canvas )
        self.canvas = canvas
        QMessageBox.information( None, '', 'hello the world')
        self.object = QObject()   #for signal emition
        self.origionPoint = None
        self.currentPoint = None
        self.prepared = True
        self.layer = None
        
    def canvasPressEvent( self, event ):
        self.layers = []        
        #self.layers.append( ftools_utils.getVectorLayerByName( 'area' ) )
        #self.layers.append( ftools_utils.getVectorLayerByName( 'Road_S' ) )
        #self.layers.append( ftools_utils.getVectorLayerByName( 'Road_G' ) )
        self.layers.append( ftools_utils.getVectorLayerByName( 'city' ) )
        for layer in self.layers:
            if ( (layer == None) or ( layer.isEditable() is True ) ):
                QMessageBox.information( None, '', 'please make the layer editable')
                self.prepared = False
                return        
        
        transform = self.canvas.getCoordinateTransform()
        self.origionPoint = transform.toMapCoordinates( event.pos().x(), event.pos().y())        
        
    def canvasMoveEvent(self,event):
        pass
        
    def canvasReleaseEvent( self, event ):    
        if self.prepared is False:
            return
        for layer in self.layers:
            provider = layer.dataProvider()
            caps = layer.dataProvider().capabilities()
            if not (caps & QgsVectorDataProvider.ChangeGeometries):
                QMessageBox.information( None, '', 'vector geometry cannot be modified' )
                return        
        
        transform = self.canvas.getCoordinateTransform() 
        self.currentPoint = transform.toMapCoordinates( event.pos().x(), event.pos().y())        
        
        #move vertex of all features
        #    
        self.canvas.freeze()
        QMessageBox.information( None, '', 'start ')
        for layer in self.layers:            
            ##calculate delta X and Y
            self.currentPointLayer = self.toLayerCoordinates( layer, self.currentPoint )
            self.origionPointLayer = self.toLayerCoordinates( layer, self.origionPoint )
            deltX = self.currentPointLayer.x()-self.origionPointLayer.x()
            deltY = self.currentPointLayer.y()-self.origionPointLayer.y()
            #QMessageBox.information( None, 'delta', '%f,%f' % (deltX, deltY))
            
            provider = layer.dataProvider()
            feat = QgsFeature()
            allAttrs = provider.attributeIndexes()
            provider.select( allAttrs )
            featuresMap = {}                
            while provider.nextFeature( feat ):  #iterate all features
                #QMessageBox.information( None, '', '%d' % feat.id()) 
                geomOld = feat.geometry()
                if geomOld.type() == QGis.Point:
                    pointOld = geomOld.asPoint()
                    pointNew = QgsPoint( pointOld.x()+deltX, pointOld.y()+deltY )
                    geomNew = QgsGeometry.fromPoint( pointNew )
                    featuresMap[ feat.id() ] = geomNew                        
                elif geomOld.type() == QGis.Line:              
                    polylineOld = geomOld.asPolyline()
                    polylineNew = []
                    for pt in polylineOld:
                        #QMessageBox.information( None, '', '%f,%f' % (pt.x(), pt.y())) 
                        polylineNew.append( QgsPoint( pt.x()+deltX, pt.y()+deltY ) )
                    geomNew = QgsGeometry.fromPolyline( polylineNew )
                    featuresMap[ feat.id() ] = geomNew    
                    #layer.dataProvider().changeGeometryValues({ feat.id() : geomNew })
                    #QMessageBox.information( None, '', 'Line')
                elif geomOld.type() == QGis.Polygon:                             
                    geomOld = feat.geometry()
                    polygonOld = geomOld.asPolygon()
                    polygonNew = []
                    for pline in polygonOld:
                        newPline = []
                        for pt in pline:
                            newPline.append( QgsPoint( pt.x()+deltX, pt.y()+deltY ) )
                            #geomNew = QgsGeometry.fromPolyline( polylineNew )
                        polygonNew.append( newPline )
                    geomNew = QgsGeometry.fromPolygon( polygonNew )
                    featuresMap[ feat.id() ] = geomNew
                    #layer.dataProvider().changeGeometryValues({ feat.id() : geomNew })
                    #QMessageBox.information( None, '', 'Polygon')
                else:
                    QMessageBox.information( None, 'layer: %s' % layer.name(), '%d, Unknown' % geomOld.wkbType() )
            #end while provider.nextFeature( feat ):
            layer.dataProvider().changeGeometryValues( featuresMap )
            QMessageBox.information( None, '', 'finished %s' % layer.name() )
        #end for layer in self.layers:                
        
        #redraw map
        self.canvas.freeze( False )
        self.canvas.refresh()
        QMessageBox.information( None, '', 'successful canvasReleaseEvent')
        self.object.emit( SIGNAL("finished()") )
    

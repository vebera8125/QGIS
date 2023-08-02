/***************************************************************************
    qgslabelfeature.h
    ---------------------
    begin                : December 2015
    copyright            : (C) 2015 by Martin Dobias
    email                : wonder dot sk at gmail dot com
 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
#ifndef QGSLABELFEATURE_H
#define QGSLABELFEATURE_H

#define SIP_NO_FILE

#include "qgis_core.h"
#include "geos_c.h"
#include "qgsgeos.h"
#include "qgsmargins.h"
#include "qgslabelobstaclesettings.h"
#include "qgslabellinesettings.h"
#include "qgsfeature.h"
#include "qgscoordinatereferencesystem.h"

namespace pal
{
  class Layer;
}

class QgsAbstractLabelProvider;
class QgsRenderContext;
class QgsGeometry;


/**
 * \ingroup core
 * \brief The QgsLabelFeature class describes a feature that
 * should be used within the labeling engine. Those may be the usual textual labels,
 * diagrams, or any other custom type of map annotations (generated by custom
 * label providers).
 *
 * Instances only contain data relevant to the labeling engine (geometry, label size etc.)
 * necessary for the layout. Rendering of labels is done by label providers.
 *
 * Individual label providers may create subclasses of QgsLabelFeature in order to add
 * more data to the instances that will be later used for drawing of labels.
 *
 * \note this class is not a part of public API yet. See notes in QgsLabelingEngine
 * \note not available in Python bindings
 * \since QGIS 2.12
 */
class CORE_EXPORT QgsLabelFeature
{
  public:

    /**
     * Constructor for QgsLabelFeature.
     *
     * The feature \a id argument links the label feature back to the original layer feature.
     *
     * The \a geometry argument specifies the geometry associated with the feature, which is
     * used by the labeling engine to generate candidate placements for the label. For
     * a vector layer feature this will generally be the feature's geometry.
     *
     * The \a size argument dicates the size of the label's content (e.g. text width and height).
     */
    QgsLabelFeature( QgsFeatureId id, geos::unique_ptr geometry, QSizeF size );

    virtual ~QgsLabelFeature();

    //! Identifier of the label (unique within the parent label provider)
    QgsFeatureId id() const { return mId; }

    //! Gets access to the associated geometry
    GEOSGeometry *geometry() const { return mGeometry.get(); }

    /**
     * Sets the label's permissible zone geometry. If set, the feature's label MUST be fully contained
     * within this zone, and the feature will not be labeled if no candidates can be generated which
     * are not contained within the zone.
     * \param geometry permissible zone geometry. If an invalid QgsGeometry is passed then no zone limit
     * will be applied to the label candidates (this is the default behavior).
     * \see permissibleZone()
     * \since QGIS 3.0
     */
    void setPermissibleZone( const QgsGeometry &geometry );

    /**
     * Returns the label's permissible zone geometry. If a valid geometry is returned, the feature's label
     * MUST be fully contained within this zone, and the feature will not be labeled if no candidates can be
     * generated which are not contained within the zone.
     * \see setPermissibleZone()
     * \see permissibleZonePrepared()
     * \since QGIS 3.0
     */
    QgsGeometry permissibleZone() const { return mPermissibleZone; }

    /**
     * Returns a GEOS prepared geometry representing the label's permissibleZone().
     * \see permissibleZone()
     * \since QGIS 3.0
     */
    //TODO - remove when QgsGeometry caches GEOS preparedness
    const GEOSPreparedGeometry *permissibleZonePrepared() const { return mPermissibleZoneGeosPrepared.get(); }

    //! Size of the label (in map units)
    QSizeF size( double angle = 0.0 ) const;

    /**
     * Returns the extreme outer bounds of the label feature, including any surrounding content like
     * borders or background shapes.
     *
     * \see setOuterBounds()
     * \since QGIS 3.30
     */
    QRectF outerBounds() const { return mOuterBounds; }

    /**
     * Sets the extreme outer \a bounds of the label feature, including any surrounding content like
     * borders or background shapes.
     *
     * \see outerBounds()
     * \since QGIS 3.30
     */
    void setOuterBounds( const QRectF &bounds ) { mOuterBounds = bounds; }

    /**
     * Sets the visual margin for the label feature. The visual margin represents a margin
     * within the label which should not be considered when calculating the positions of candidates
     * for the label feature. It is used in certain label placement modes to adjust the position
     * of candidates so that they all appear to be at visually equal distances from a point feature.
     * For instance, this can be used to place labels which sit above a point so that their baseline
     * rather then the descender of the label is at a preset distance from the point.
     * \param margin visual margins for label
     * \see visualMargin()
     */
    void setVisualMargin( const QgsMargins &margin ) { mVisualMargin = margin; }

    /**
     * Returns the visual margin for the label feature.
     * \see setVisualMargin() for details
     */
    const QgsMargins &visualMargin() const { return mVisualMargin; }

    /**
     * Sets the size of the rendered symbol associated with this feature. This size is taken into
     * account in certain label placement modes to avoid placing labels over the rendered
     * symbol for this feature.
     * \see symbolSize()
     */
    void setSymbolSize( QSizeF size ) { mSymbolSize = size; }

    /**
     * Returns the size of the rendered symbol associated with this feature, if applicable.
     * This size is taken into account in certain label placement modes to avoid placing labels over
     * the rendered symbol for this feature. The size will only be set for labels associated
     * with a point feature.
     * \see symbolSize()
     */
    const QSizeF &symbolSize() const { return mSymbolSize; }

    /**
     * Returns the feature's labeling priority.
     * \returns feature's priority, as a value between 0 (highest priority)
     * and 1 (lowest priority). Returns -1.0 if feature will use the layer's default priority.
     * \see setPriority
     */
    double priority() const { return mPriority; }

    /**
     * Sets the priority for labeling the feature.
     * \param priority feature's priority, as a value between 0 (highest priority)
     * and 1 (lowest priority). Set to -1.0 to use the layer's default priority
     * for this feature.
     * \see priority
     */
    void setPriority( double priority ) { mPriority = priority; }

    /**
     * Returns the label's z-index. Higher z-index labels are rendered on top of lower
     * z-index labels.
     * \see setZIndex()
     * \since QGIS 2.14
     */
    double zIndex() const { return mZIndex; }

    /**
     * Sets the label's z-index. Higher z-index labels are rendered on top of lower
     * z-index labels.
     * \param zIndex z-index for label
     * \see zIndex()
     * \since QGIS 2.14
     */
    void setZIndex( double zIndex ) { mZIndex = zIndex; }

    //! Whether the label should use a fixed position instead of being automatically placed
    bool hasFixedPosition() const { return mHasFixedPosition; }
    //! Sets whether the label should use a fixed position instead of being automatically placed
    void setHasFixedPosition( bool enabled ) { mHasFixedPosition = enabled; }
    //! Coordinates of the fixed position (relevant only if hasFixedPosition() returns TRUE)
    QgsPointXY fixedPosition() const { return mFixedPosition; }

    //! Sets coordinates of the fixed position (relevant only if hasFixedPosition() returns TRUE)
    void setFixedPosition( const QgsPointXY &point ) { mFixedPosition = point; }

    /**
     * In case of quadrand or aligned positioning, this is set to the anchor point.
     * This can be used for proper vector based output like DXF.
     *
     * \since QGIS 3.12
     */
    QgsPointXY anchorPosition() const;

    /**
     * In case of quadrand or aligned positioning, this is set to the anchor point.
     * This can be used for proper vector based output like DXF.
     *
     * \since QGIS 3.12
     */
    void setAnchorPosition( const QgsPointXY &anchorPosition );

    //! Whether the label should use a fixed angle instead of using angle from automatic placement
    bool hasFixedAngle() const { return mHasFixedAngle; }
    //! Sets whether the label should use a fixed angle instead of using angle from automatic placement
    void setHasFixedAngle( bool enabled ) { mHasFixedAngle = enabled; }
    //! Angle in degrees of the fixed angle (relevant only if hasFixedAngle() returns TRUE)
    double fixedAngle() const { return mFixedAngle; }
    //! Sets angle in degrees of the fixed angle (relevant only if hasFixedAngle() returns TRUE)
    void setFixedAngle( double angle ) { mFixedAngle = angle; }

    /**
     * Returns whether the quadrant for the label is fixed.
     * Applies to "around point" placement strategy.
     * \see setHasFixedQuadrant
     * \see quadOffset
     */
    bool hasFixedQuadrant() const { return mHasFixedQuadrant; }

    /**
     * Sets whether the quadrant for the label must be respected. This can be used
     * to fix the quadrant for specific features when using an "around point" placement.
     * \see hasFixedQuadrant
     * \see quadOffset
     */
    void setHasFixedQuadrant( bool enabled ) { mHasFixedQuadrant = enabled; }

    /**
     * Applies to "offset from point" placement strategy and "around point" (in case hasFixedQuadrant() returns TRUE).
     * Determines which side of the point to use.
     * For X coordinate, values -1, 0, 1 mean left, center, right.
     * For Y coordinate, values -1, 0, 1 mean above, center, below.
     */
    QPointF quadOffset() const { return mQuadOffset; }

    /**
     * Set which side of the point to use
     * \see quadOffset
     */
    void setQuadOffset( QPointF quadOffset ) { mQuadOffset = quadOffset; }

    /**
     * Applies only to "offset from point" placement strategy.
     * What offset (in map units) to use from the point
     */
    QgsPointXY positionOffset() const { return mPositionOffset; }

    /**
     * Applies only to "offset from point" placement strategy.
     * Set what offset (in map units) to use from the point
     */
    void setPositionOffset( const QgsPointXY &offset ) { mPositionOffset = offset; }

    /**
     * Returns the offset type, which determines how offsets and distance to label
     * behaves. Support depends on which placement mode is used for generating
     * label candidates.
     * \see setOffsetType()
     */
    Qgis::LabelOffsetType offsetType() const { return mOffsetType; }

    /**
     * Sets the offset type, which determines how offsets and distance to label
     * behaves. Support depends on which placement mode is used for generating
     * label candidates.
     * \see offsetType()
     */
    void setOffsetType( Qgis::LabelOffsetType type ) { mOffsetType = type; }

    /**
     * Applies to "around point" placement strategy or linestring features.
     * Distance of the label from the feature (in map units)
     */
    double distLabel() const { return mDistLabel; }

    /**
     * Applies to "around point" placement strategy or linestring features.
     * Set distance of the label from the feature (in map units)
     */
    void setDistLabel( double dist ) { mDistLabel = dist; }

    /**
     * Returns the priority ordered list of predefined positions for label candidates. This property
     * is only used for OrderedPositionsAroundPoint placements.
     * \see setPredefinedPositionOrder()
     */
    QVector< Qgis::LabelPredefinedPointPosition > predefinedPositionOrder() const { return mPredefinedPositionOrder; }

    /**
     * Sets the priority ordered list of predefined positions for label candidates. This property
     * is only used for OrderedPositionsAroundPoint placements.
     * \see predefinedPositionOrder()
     */
    void setPredefinedPositionOrder( const QVector< Qgis::LabelPredefinedPointPosition > &order ) { mPredefinedPositionOrder = order; }

    /**
     * Applies only to linestring features - after what distance (in map units)
     * the labels should be repeated (0 = no repetitions)
     */
    double repeatDistance() const { return mRepeatDistance; }

    /**
     * Applies only to linestring features - set after what distance (in map units)
     * the labels should be repeated (0 = no repetitions)
     */
    void setRepeatDistance( double dist ) { mRepeatDistance = dist; }

    //! Whether label should be always shown (sets very high label priority)
    bool alwaysShow() const { return mAlwaysShow; }
    //! Sets whether label should be always shown (sets very high label priority)
    void setAlwaysShow( bool enabled ) { mAlwaysShow = enabled; }

    /**
     * Returns the feature's arrangement flags.
     * \see setArrangementFlags
     */
    Qgis::LabelLinePlacementFlags arrangementFlags() const { return mArrangementFlags; }

    /**
     * Sets the feature's arrangement flags.
     * \param flags arrangement flags
     * \see arrangementFlags
     */
    void setArrangementFlags( Qgis::LabelLinePlacementFlags flags ) { mArrangementFlags = flags; }

    /**
     * Returns the polygon placement flags, which dictate how polygon labels can be placed.
     *
     * \see setPolygonPlacementFlags()
     * \since QGIS 3.14
     */
    Qgis::LabelPolygonPlacementFlags polygonPlacementFlags() const { return mPolygonPlacementFlags; }

    /**
     * Sets the polygon placement \a flags, which dictate how polygon labels can be placed.
     *
     * \see polygonPlacementFlags()
     * \since QGIS 3.14
     */
    void setPolygonPlacementFlags( Qgis::LabelPolygonPlacementFlags flags ) { mPolygonPlacementFlags = flags; }

    /**
     * Text of the label
     *
     * Used also if "merge connected lines to avoid duplicate labels" is enabled
     * to identify which features may be merged.
     */
    QString labelText() const { return mLabelText; }
    //! Sets text of the label
    void setLabelText( const QString &text ) { mLabelText = text; }

    //! Gets PAL layer of the label feature. Should be only used internally in PAL
    pal::Layer *layer() const { return mLayer; }
    //! Assign PAL layer to the label feature. Should be only used internally in PAL
    void setLayer( pal::Layer *layer ) { mLayer = layer; }

    //! Returns provider of this instance
    QgsAbstractLabelProvider *provider() const;

    /**
     * Returns the original feature associated with this label.
     * \see setFeature()
     *
     * \since QGIS 3.10
     */
    QgsFeature feature() const;

    /**
     * Sets the original \a feature associated with this label.
     * \see feature()
     *
     * \since QGIS 3.10
     */
    void setFeature( const QgsFeature &feature );

    /**
     * Returns the feature symbol associated with this label.
     * \see setSymbol()
     *
     * \since QGIS 3.10
     */
    const QgsSymbol *symbol() const { return mSymbol; }

    /**
     * Sets the feature \a symbol associated with this label.
     * Ownership of \a symbol is not transferred to the label feature, .
     * \see symbol()
     *
     * \since QGIS 3.10
     */
    void setSymbol( const QgsSymbol *symbol ) { mSymbol = symbol; }

    /**
     * Returns the permissible distance (in map units) which labels are allowed to overrun the start
     * or end of linear features.
     *
     * \see setOverrunDistance()
     * \see overrunSmoothDistance()
     * \since QGIS 3.10
     */
    double overrunDistance() const;

    /**
     * Sets the permissible \a distance (in map units) which labels are allowed to overrun the start
     * or end of linear features.
     *
     * \see overrunDistance()
     * \see setOverrunSmoothDistance()
     * \since QGIS 3.10
     */
    void setOverrunDistance( double distance );

    /**
     * Returns the distance (in map units) with which the ends of linear features are averaged over when
     * calculating the direction at which to overrun labels.
     *
     * \see setOverrunSmoothDistance()
     * \see overrunDistance()
     * \since QGIS 3.10
     */
    double overrunSmoothDistance() const;

    /**
     * Sets the \a distance (in map units) with which the ends of linear features are averaged over when
     * calculating the direction at which to overrun labels.
     *
     * \see overrunSmoothDistance()
     * \see setOverrunDistance()
     * \since QGIS 3.10
     */
    void setOverrunSmoothDistance( double distance );

    /**
     * Returns the percent along the line at which labels should be placed, for line labels only.
     *
     * By default, this is 0.5 which indicates that labels should be placed as close to the
     * center of the line as possible. A value of 0.0 indicates that the labels should be placed
     * as close to the start of the line as possible, while a value of 1.0 pushes labels towards
     * the end of the line.
     *
     * \see setLineAnchorPercent()
     * \see lineAnchorType()
     * \since QGIS 3.16
     */
    double lineAnchorPercent() const { return mLineAnchorPercent; }

    /**
     * Sets the \a percent along the line at which labels should be placed, for line labels only.
     *
     * By default, this is 0.5 which indicates that labels should be placed as close to the
     * center of the line as possible. A value of 0.0 indicates that the labels should be placed
     * as close to the start of the line as possible, while a value of 1.0 pushes labels towards
     * the end of the line.
     *
     * \see lineAnchorPercent()
     * \see setLineAnchorType()
     * \since QGIS 3.16
     */
    void setLineAnchorPercent( double percent ) { mLineAnchorPercent = percent; }

    /**
     * Returns the line anchor type, which dictates how the lineAnchorPercent() setting is
     * handled.
     *
     * \see setLineAnchorType()
     * \see lineAnchorPercent()
     */
    QgsLabelLineSettings::AnchorType lineAnchorType() const { return mLineAnchorType; }

    /**
     * Sets the line anchor \a type, which dictates how the lineAnchorPercent() setting is
     * handled.
     *
     * \see lineAnchorType()
     * \see setLineAnchorPercent()
     */
    void setLineAnchorType( QgsLabelLineSettings::AnchorType type ) { mLineAnchorType = type; }

    /**
     * Returns the line anchor text point, which dictates which part of the label text
     * should be placed at the lineAnchorPercent().
     *
     * \see setLineAnchorTextPoint()
     *
     * \since QGIS 3.26
     */
    QgsLabelLineSettings::AnchorTextPoint lineAnchorTextPoint() const;

    /**
     * Sets the line anchor text \a point, which dictates which part of the label text
     * should be placed at the lineAnchorPercent().
     *
     * \see lineAnchorTextPoint()
     *
     * \since QGIS 3.26
     */
    void setLineAnchorTextPoint( QgsLabelLineSettings::AnchorTextPoint point ) { mAnchorTextPoint = point; }

    /**
     * Returns TRUE if all parts of the feature should be labeled.
     * \see setLabelAllParts()
     * \since QGIS 3.10
     */
    bool labelAllParts() const { return mLabelAllParts; }

    /**
     * Sets whether all parts of the feature should be labeled.
     * \see labelAllParts()
     * \since QGIS 3.10
     */
    void setLabelAllParts( bool labelAllParts ) { mLabelAllParts = labelAllParts; }

    /**
     * Sets an alternate label \a size to be used when a label rotation angle is between 45 to 135
     * and 235 to 313 degrees and the text rotation mode is set to rotation-based.
     * \since QGIS 3.10
     */
    void setRotatedSize( QSizeF size ) { mRotatedSize = size; }

    /**
     * Returns the label's obstacle settings.
     *
     * \see setObstacleSettings()
     * \since QGIS 3.12
     */
    const QgsLabelObstacleSettings &obstacleSettings() const;

    /**
     * Sets the label's obstacle \a settings.
     *
     * \see obstacleSettings()
     * \since QGIS 3.12
     */
    void setObstacleSettings( const QgsLabelObstacleSettings &settings );

    /**
     * Returns the original layer CRS of the feature associated with the label.
     *
     * \see setOriginalFeatureCrs()
     * \since QGIS 3.20
     */
    QgsCoordinateReferenceSystem originalFeatureCrs() const;

    /**
     * Sets the original layer \a crs of the feature associated with the label.
     *
     * \see originalFeatureCrs()
     * \since QGIS 3.20
     */
    void setOriginalFeatureCrs( const QgsCoordinateReferenceSystem &crs );

    /**
     * Returns the minimum size (in map unit) for a feature to be labelled.
     *
     * \note At the moment this is only used when labeling merged lines
     * \see minimumSize()
     * \since QGIS 3.20
     */
    double minimumSize() const { return mMinimumSize; }

    /**
     * Sets the minimum \a size (in map unit) for a feature to be labelled.
     *
     * \note At the moment this is only used when labeling merged lines
     * \see setMinimumSize()
     * \since QGIS 3.20
     */
    void setMinimumSize( double size ) { mMinimumSize = size; }

    /**
     * Returns the technique to use for handling overlapping labels for the feature.
     *
     * \see setOverlapHandling()
     * \since QGIS 3.26
     */
    Qgis::LabelOverlapHandling overlapHandling() const { return mOverlapHandling; }

    /**
     * Sets the technique to use for handling overlapping labels for the feature.
     *
     * \see overlapHandling()
     * \since QGIS 3.26
     */
    void setOverlapHandling( Qgis::LabelOverlapHandling handling ) { mOverlapHandling = handling; }

    /**
     * Returns TRUE if the label can be placed in inferior fallback positions if it cannot otherwise
     * be placed.
     *
     * For instance, this will permit a curved line label to fallback to a horizontal label at the end of the line
     * if the label cannot otherwise be placed on the line in a curved manner.
     *
     * \see setAllowDegradedPlacement()
     * \since QGIS 3.26
     */
    bool allowDegradedPlacement() const { return mAllowDegradedPlacement; }

    /**
     * Sets whether the label can be placed in inferior fallback positions if it cannot otherwise
     * be placed.
     *
     * For instance, this will permit a curved line label to fallback to a horizontal label at the end of the line
     * if the label cannot otherwise be placed on the line in a curved manner.
     *
     * \see allowDegradedPlacement()
     * \since QGIS 3.26
     */
    void setAllowDegradedPlacement( bool allow ) { mAllowDegradedPlacement = allow; }

  protected:
    //! Pointer to PAL layer (assigned when registered to PAL)
    pal::Layer *mLayer = nullptr;

    //! Associated ID unique within the parent label provider
    QgsFeatureId mId;
    //! Geometry of the feature to be labelled
    geos::unique_ptr mGeometry;
    //! Optional geometry to use for label's permissible zone
    QgsGeometry mPermissibleZone;
    //! Width and height of the label
    QSizeF mSize;
    //! Width and height of the label when rotated between 45 to 135 and 235 to 315 degrees;
    QSizeF mRotatedSize;
    //! Extreme outer bounds of the label feature, including any surrounding content like borders or background shapes.
    QRectF mOuterBounds;
    //! Visual margin of label contents
    QgsMargins mVisualMargin;
    //! Size of associated rendered symbol, if applicable
    QSizeF mSymbolSize;
    //! Priority of the label
    double mPriority = -1;
    //! Z-index of label (higher z-index labels are rendered on top of lower z-index labels)
    double mZIndex = 0;
    //! whether mFixedPosition should be respected
    bool mHasFixedPosition = false;
    //! fixed position for the label (instead of automatic placement)
    QgsPointXY mFixedPosition;
    //! whether mFixedAngle should be respected
    bool mHasFixedAngle = false;
    //! fixed rotation for the label (instead of automatic choice)
    double mFixedAngle = 0;
    //! whether mQuadOffset should be respected (only for "around point" placement)
    bool mHasFixedQuadrant = false;
    //! whether the side of the label is fixed (only for "around point" placement)
    QPointF mQuadOffset;
    //! offset of label from the feature (only for "offset from point" placement)
    QgsPointXY mPositionOffset;
    //! distance of label from the feature (only for "around point" placement or linestrings)
    double mDistLabel = 0;
    //! Offset type for certain placement modes
    Qgis::LabelOffsetType mOffsetType = Qgis::LabelOffsetType::FromPoint;
    //! Ordered list of predefined positions for label (only for OrderedPositionsAroundPoint placement)
    QVector< Qgis::LabelPredefinedPointPosition > mPredefinedPositionOrder;
    //! distance after which label should be repeated (only for linestrings)
    double mRepeatDistance = 0;
    //! whether to always show label - even in case of collisions
    bool mAlwaysShow = false;
    //! text of the label
    QString mLabelText;

    //! Distance to allow label to overrun linear features
    double mOverrunDistance = 0;
    //! Distance to smooth angle of line start and end when calculating overruns
    double mOverrunSmoothDistance = 0;

    Qgis::LabelLinePlacementFlags mArrangementFlags = Qgis::LabelLinePlacementFlags();
    Qgis::LabelPolygonPlacementFlags mPolygonPlacementFlags = Qgis::LabelPolygonPlacementFlag::AllowPlacementInsideOfPolygon;

  private:

    //! GEOS geometry on which mPermissibleZoneGeosPrepared is based on
    geos::unique_ptr mPermissibleZoneGeos;

    // TODO - not required when QgsGeometry caches geos preparedness
    geos::prepared_unique_ptr mPermissibleZoneGeosPrepared;

    QgsFeature mFeature;

    const QgsSymbol *mSymbol = nullptr;

    bool mLabelAllParts = false;

    QgsLabelObstacleSettings mObstacleSettings{};

    QgsPointXY mAnchorPosition;

    double mLineAnchorPercent = 0.5;
    QgsLabelLineSettings::AnchorType mLineAnchorType = QgsLabelLineSettings::AnchorType::HintOnly;
    QgsLabelLineSettings::AnchorTextPoint mAnchorTextPoint = QgsLabelLineSettings::AnchorTextPoint::CenterOfText;

    Qgis::LabelOverlapHandling mOverlapHandling = Qgis::LabelOverlapHandling::PreventOverlap;
    bool mAllowDegradedPlacement = false;

    QgsCoordinateReferenceSystem mOriginalFeatureCrs;

    double mMinimumSize = 0.0;

};

#endif // QGSLABELFEATURE_H

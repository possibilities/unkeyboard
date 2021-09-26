use <util.scad>

bleedMm = 0.1;
halfBleedMm = bleedMm / 2;

module topLayerSwitchCutout(topLayerHeightMm) {
  switchGrooveHeight = 3.5;
  union() {
    getPartFromLayers("top-layer-switch-cutout", topLayerHeightMm);
    getPartFromLayers("top-layer-switch-grooves", switchGrooveHeight);
  }
}

module middleLayerSocketCutout(middleLayerHeightMm, row, column, numberOfRows,
                               numberOfColumns) {
  socketAndWiringHeight = 1.75;

  isLastRow = row == 0;
  isLastColumn = column == 0;
  isFirstColumn = column == numberOfColumns - 1;

  union() {
    getPartFromLayers("center-layer-socket", socketAndWiringHeight);
    if (!isLastRow) {
      getPartFromLayers("center-layer-wiring-upper-rows",
                        socketAndWiringHeight);
    }
    if (!isFirstColumn) {
      getPartFromLayers("center-layer-wiring-horizontal-connector",
                        socketAndWiringHeight);
    }
    if (!isLastRow || !isLastColumn) {
      getPartFromLayers("center-layer-wiring-non-diode-connector",
                        socketAndWiringHeight);
    }
  }
}

module middleLayerSocketCutouts(middleLayerHeightMm, numberOfRows,
                                numberOfColumns, keyDistanceMm) {
  for (row = [0:numberOfRows - 1]) {
    for (column = [0:numberOfColumns - 1]) {
      translate([ column * keyDistanceMm, row * keyDistanceMm ]) {
        middleLayerSocketCutout(middleLayerHeightMm, row, column, numberOfRows,
                                numberOfColumns);
      }
    }
  }
}

module middleLayerSocketHoles(middleLayerHeightMm, numberOfRows,
                              numberOfColumns, keyDistanceMm) {
  for (row = [0:numberOfRows - 1]) {
    for (column = [0:numberOfColumns - 1]) {
      translate([ column * keyDistanceMm, row * keyDistanceMm, -halfBleedMm ]) {
        switchHoleSmallRadiusMm = 1.5;
        switchHoleLargeRadiusMm = 2;
        translate([ keyDistanceMm / 2, keyDistanceMm / 2 ]) {
          // Small lower hole
          translate([ -3.81, 2.54 ]) {
            cylinder(middleLayerHeightMm + bleedMm, switchHoleSmallRadiusMm,
                     switchHoleSmallRadiusMm);
          }
          // Small upper hole
          translate([ 2.54, 5.08 ]) {
            cylinder(middleLayerHeightMm + bleedMm, switchHoleSmallRadiusMm,
                     switchHoleSmallRadiusMm);
          }
          // Large center hole
          cylinder(middleLayerHeightMm + bleedMm, switchHoleLargeRadiusMm,
                   switchHoleLargeRadiusMm);
        }
      }
    }
  }
}

module topLayerSwitchCutouts(topLayerHeightMm, numberOfRows, numberOfColumns,
                             keyDistanceMm) {
  for (row = [0:numberOfRows - 1]) {
    for (column = [0:numberOfColumns - 1]) {
      translate([ column * keyDistanceMm, row * keyDistanceMm ]) {
        topLayerSwitchCutout(topLayerHeightMm);
      }
    }
  }
}

module topLayerSwitches(topLayerHeightMm, switchBezelMm, numberOfRows,
                        numberOfColumns, keyDistanceMm) {
  layerLengthMm = numberOfColumns * keyDistanceMm;
  layerWidthMm = numberOfRows * keyDistanceMm;

  layerLengthWithBezelMm = layerLengthMm + switchBezelMm;
  layerWidthWithBezelMm = layerWidthMm + switchBezelMm;

  difference() {
    center(layerLengthWithBezelMm, layerWidthWithBezelMm) {
      cube([ layerLengthWithBezelMm, layerWidthWithBezelMm, topLayerHeightMm ]);
    }
    center(layerLengthMm, layerWidthMm) {
      topLayerSwitchCutouts(topLayerHeightMm, numberOfRows, numberOfColumns,
                            keyDistanceMm);
    }
  }
}

module middleLayerSwitches(middleLayerHeightMm, switchBezelMm, numberOfRows,
                           numberOfColumns, keyDistanceMm) {
  layerLengthMm = numberOfColumns * keyDistanceMm;
  layerWidthMm = numberOfRows * keyDistanceMm;

  layerLengthWithBezelMm = layerLengthMm + switchBezelMm;
  layerWidthWithBezelMm = layerWidthMm + switchBezelMm;

  difference() {
    center(layerLengthWithBezelMm, layerWidthWithBezelMm) {
      cube([
        layerLengthWithBezelMm, layerWidthWithBezelMm,
        middleLayerHeightMm
      ]);
    }
    center(layerLengthMm, layerWidthMm) {
      middleLayerSocketCutouts(middleLayerHeightMm, numberOfRows,
                               numberOfColumns, keyDistanceMm);
      middleLayerSocketHoles(middleLayerHeightMm, numberOfRows, numberOfColumns,
                             keyDistanceMm);
    }
  }
}

module bottomLayerSwitches(bottomLayerHeightMm, switchBezelMm, numberOfRows,
                           numberOfColumns, keyDistanceMm) {
  layerLengthMm = (numberOfColumns * keyDistanceMm) + switchBezelMm;
  layerWidthMm = (numberOfRows * keyDistanceMm) + switchBezelMm;

  center(layerLengthMm, layerWidthMm) {
    cube([ layerLengthMm, layerWidthMm, bottomLayerHeightMm ]);
  }
}

use <util.scad>

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
    getPartFromLayers("center-layer-switch-holes", middleLayerHeightMm);
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

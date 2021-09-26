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

module topLayerSwitchCutouts(topLayerHeightMm, numberOfRows, numberOfColumns,
                             keyDistanceMm) {
  socketAndWiringHeight = 1.75;
  for (row = [0:numberOfRows - 1]) {
    for (column = [0:numberOfColumns - 1]) {
      translate([ column * keyDistanceMm, row * keyDistanceMm ]) {
        topLayerSwitchCutout(topLayerHeightMm);
      }
    }
  }
}

module middleLayerSocketCutouts(numberOfRows, numberOfColumns, keyDistanceMm) {
  socketAndWiringHeight = 1.75;
  for (row = [0:numberOfRows - 1]) {
    for (column = [0:numberOfColumns - 1]) {
      translate([ column * keyDistanceMm, row * keyDistanceMm ]) {
        getPartFromLayers("center-layer-socket", socketAndWiringHeight);
      }
    }
  }
}

module middleLayerSocketHoles(middleLayerHeightMm, numberOfRows,
                              numberOfColumns, keyDistanceMm) {
  socketAndWiringHeight = 1.75;
  for (row = [0:numberOfRows - 1]) {
    for (column = [0:numberOfColumns - 1]) {
      translate([ column * keyDistanceMm, row * keyDistanceMm ]) {
        getPartFromLayers("center-layer-switch-holes", middleLayerHeightMm);
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
      middleLayerSocketCutouts(numberOfRows, numberOfColumns, keyDistanceMm);
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

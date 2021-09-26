use <switches.scad>

module main(view) {
  $fs = 0.1;

  numberOfRows = 2;
  numberOfColumns = 3;

  keyDistanceMm = 19.05;

  topLayerHeightMm = 5;
  middleLayerHeightMm = 3;
  bottomLayerHeightMm = 5;

  // Needs to be 3 or more to ensure wiring doesn't fall off edge. Additional
  // bezel should be added to case.
  switchesBezelMm = 3;

  if (view == "exploded") {
    demoExplodeMm = 20;
    translate([ 0, 0, 2 * demoExplodeMm ]) {
      topLayerSwitches(topLayerHeightMm, switchesBezelMm, numberOfRows,
                       numberOfColumns, keyDistanceMm);
    }
    !translate([ 0, 0, 1 * demoExplodeMm ]) {
      middleLayerSwitches(middleLayerHeightMm, switchesBezelMm, numberOfRows,
                          numberOfColumns, keyDistanceMm);
    }
    translate([ 0, 0, 0 * demoExplodeMm ]) {
      bottomLayerSwitches(bottomLayerHeightMm, switchesBezelMm, numberOfRows,
                          numberOfColumns, keyDistanceMm);
    }
  } else if (view == "assembled") {
    translate([ 0, 0, bottomLayerHeightMm + middleLayerHeightMm ]) {
      topLayerSwitches(topLayerHeightMm, switchesBezelMm, numberOfRows,
                       numberOfColumns, keyDistanceMm);
    }
    !translate([ 0, 0, bottomLayerHeightMm ]) {
      middleLayerSwitches(middleLayerHeightMm, switchesBezelMm, numberOfRows,
                          numberOfColumns, keyDistanceMm);
    }
    translate([ 0, 0, 0 ]) {
      bottomLayerSwitches(bottomLayerHeightMm, switchesBezelMm, numberOfRows,
                          numberOfColumns, keyDistanceMm);
    }
  } else if (view == "top-layer") {
    topLayerSwitches(topLayerHeightMm, switchesBezelMm, numberOfRows,
                     numberOfColumns, keyDistanceMm);
  } else if (view == "middle-layer") {
    middleLayerSwitches(middleLayerHeightMm, switchesBezelMm, numberOfRows,
                        numberOfColumns, keyDistanceMm);
  } else if (view == "bottom-layer") {
    bottomLayerSwitches(bottomLayerHeightMm, switchesBezelMm, numberOfRows,
                        numberOfColumns, keyDistanceMm);
  }
}

view = "assembled";

main(view);

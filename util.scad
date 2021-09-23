bleedMm = 0.1;
halfBleedMm = bleedMm / 2;

module getPartFromLayers(layer, height) {
  translate([ 0, 0, -halfBleedMm ]) {
    linear_extrude(height + bleedMm, convexity = 3)
        import("parts.dxf", layer = layer);
  }
}

module center(lengthMm, widthMm) {
  translate([ -(lengthMm / 2), -(widthMm / 2), 0 ]) { children(); }
}

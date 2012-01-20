void setup() {
  canvasWidth = 800;
  canvasHeight = 200;
  size(canvasWidth, canvasHeight);
  background(0, 0);
  rectMode(CORNERS);
  noStroke();
  fill(255);

  rectangleWidth = 20;
  xPadding = 10;
  yPadding = 15;
  versionWidth = 100;

  for (int i = 0; i < revisionCount; i++) {
    randomlyCreateRevision(i, rectangleWidth, xPadding, yPadding, versionWidth,
        canvasHeight);
  }
}

void randomlyCreateRevision(int versionNumber, int rectangleWidth,
    int xPadding, int yPadding, int versionWidth) {
  fill(0);
  text("version " + (versionNumber + 1), 
      getXPositionFromVersion(versionNumber, versionWidth, xPadding,
      rectangleWidth, true), 10);
  totalPercentage = (int)random(100);
  numberOfSectionsChanged = (int)random(1, 6);
  previousPercentage = 0
  for (int i = 0; i < numberOfSectionsChanged; i++) {
    fill(getUserColor((int)random(3)));
    currentPercentage = (int)random(totalPercentage);
    rect(
        getXPositionFromVersion(versionNumber, versionWidth, xPadding,
            rectangleWidth, true),
        getYPositionFromPercentage(previousPercentage, yPadding, canvasHeight),
        getXPositionFromVersion(versionNumber, versionWidth, xPadding,
            rectangleWidth, false),
        getYPositionFromPercentage(currentPercentage, yPadding, canvasHeight)
    );
    previousPercentage = currentPercentage;
  }
}

int getUserColor(int userId) {
  if (userId == 0) {
    return 255;
  } else if (userId == 1) {
    return 150;
  } else {
    return 50;
  }
}

// Assuming reading from left to right
int getXPositionFromVersion(int versionNumber, int versionWidth,
    int xPadding, int rectangleWidth, boolean isLeft) {
  if (isLeft) {
    return xPadding + versionNumber * versionWidth;
  } else {
    return xPadding + versionNumber * versionWidth + rectangleWidth;
  }
}

int getYPositionFromPercentage(int percent, int yPadding, int totalHeight) {
  return yPadding + (int)((percent / 100) * (totalHeight - (2 * yPadding)));
}

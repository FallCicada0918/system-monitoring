// ==========================================================================
// CYBER_PULSE // CANVAS ANIMATION ENGINE: MATRIX RAIN & 3D CYBER GRID
// ==========================================================================

(function () {
  // 1. Matrix Digital Rain
  const matrixCanvas = document.getElementById('canvas-matrix');
  if (!matrixCanvas) return;
  const mCtx = matrixCanvas.getContext('2d');

  let mWidth, mHeight;
  let columns = [];
  const chars = '0123456789ABCDEF??????????????????????????????????//><{}[]*~=+';
  const fontSize = 14;
  let isMatrixActive = true;

  function resizeMatrix() {
    mWidth = matrixCanvas.width = window.innerWidth;
    mHeight = matrixCanvas.height = window.innerHeight;
    const colCount = Math.floor(mWidth / fontSize);
    columns = [];
    for (let i = 0; i < colCount; i++) {
      columns[i] = Math.floor(Math.random() * -50);
    }
  }

  function drawMatrix() {
    if (!isMatrixActive) {
      mCtx.clearRect(0, 0, mWidth, mHeight);
      return;
    }

    mCtx.fillStyle = 'rgba(5, 7, 15, 0.12)';
    mCtx.fillRect(0, 0, mWidth, mHeight);

    const activeColor = getComputedStyle(document.body).getPropertyValue('--neon-cyan').trim() || '#00f0ff';
    mCtx.font = fontSize + 'px Consolas, monospace';

    for (let i = 0; i < columns.length; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)];
      const x = i * fontSize;
      const y = columns[i] * fontSize;

      // Glowing head of the stream
      mCtx.fillStyle = '#ffffff';
      mCtx.fillText(char, x, y);

      // Tail with cyber theme color
      mCtx.fillStyle = activeColor;
      mCtx.fillText(char, x, y - fontSize);

      if (y > mHeight && Math.random() > 0.975) {
        columns[i] = 0;
      }
      columns[i]++;
    }
  }

  // 2. 3D Cyber Floor Grid
  const gridCanvas = document.getElementById('canvas-grid');
  const gCtx = gridCanvas.getContext('2d');
  let gWidth, gHeight;
  let gridOffset = 0;

  function resizeGrid() {
    gWidth = gridCanvas.width = window.innerWidth;
    gHeight = gridCanvas.height = window.innerHeight;
  }

  function drawGrid() {
    gCtx.clearRect(0, 0, gWidth, gHeight);

    const horizonY = gHeight * 0.45;
    const gridColor = getComputedStyle(document.body).getPropertyValue('--grid-color').trim() || 'rgba(0, 240, 255, 0.08)';

    gCtx.strokeStyle = gridColor;
    gCtx.lineWidth = 1;

    // Moving horizontal perspective lines
    gridOffset = (gridOffset + 0.8) % 36;
    for (let y = horizonY; y <= gHeight; y += 4) {
      const depth = (y - horizonY) / (gHeight - horizonY);
      const scaledY = horizonY + Math.pow(depth, 2.5) * (gHeight - horizonY);
      if (scaledY > horizonY) {
        gCtx.beginPath();
        gCtx.moveTo(0, scaledY);
        gCtx.lineTo(gWidth, scaledY);
        gCtx.stroke();
      }
    }

    // Perspective vanishing lines
    const centerX = gWidth / 2;
    const lineCount = 28;
    for (let i = -lineCount; i <= lineCount; i++) {
      const bottomX = centerX + i * 85;
      gCtx.beginPath();
      gCtx.moveTo(centerX, horizonY);
      gCtx.lineTo(bottomX, gHeight);
      gCtx.stroke();
    }
  }

  window.addEventListener('resize', () => {
    resizeMatrix();
    resizeGrid();
  });

  resizeMatrix();
  resizeGrid();

  let lastTime = 0;
  function loop(timestamp) {
    if (timestamp - lastTime > 40) {
      drawMatrix();
      drawGrid();
      lastTime = timestamp;
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  window.toggleMatrixRain = function () {
    isMatrixActive = !isMatrixActive;
    return isMatrixActive;
  };
})();

/**
 * Table Proof using canvas.
 *
 * Draws all the pieces onto a scaled to fit canvas to show the initial
 * distribution of pieces.  Pieces are not interactive and all load from inlined
 * img tags that data urls.
 * This is my first time working with the canvas API, so I may have made some
 * rookie mistakes.
 */
window.addEventListener('load', (event) => {

  const $canvas = document.getElementById('piecemaker-table');
  const $container = $canvas.parentElement;
  const ctx = $canvas.getContext('2d', {"alpha": false});
  let raf;

  // Scaling down larger puzzles doesn't work well.
  // window.addEventListener('resize', resizePiecemakerTable);
  // resizePiecemakerTable();


  const allPieces = fetch("index.json")
    .then(response => response.json())
    .then(piecemaker_index => {
      clear();
      const lineWidth = Math.ceil(Math.min(piecemaker_index.image_width * 0.01, piecemaker_index.image_height * 0.01));
      drawPuzzleOutline(lineWidth, [
        Math.floor((piecemaker_index.table_width - piecemaker_index.image_width) * 0.5),
        Math.floor((piecemaker_index.table_height - piecemaker_index.image_height) * 0.5),
        Math.floor((piecemaker_index.table_width - piecemaker_index.image_width) * 0.5) + piecemaker_index.image_width,
        Math.floor((piecemaker_index.table_height - piecemaker_index.image_height) * 0.5) + piecemaker_index.image_height
      ])
      ctx.save();
      return piecemaker_index.piece_properties.map((piece_prop) => {
        const pieceId = piece_prop.id
        const pc = {
          id: pieceId,
          x: piece_prop.x,
          y: piece_prop.y,
          draw: drawPieceFactory(ctx, pieceId)
        };
        return pc;
      });
      function clear() {
        ctx.clearRect(0,0, $canvas.width, $canvas.height);
      }
    })
    .then((allPieces) => {
      return {
        render: drawAllPieces
      };
      function drawAllPieces() {
        ctx.restore();
        ctx.save();
        allPieces.forEach((pc) => {
          pc.draw();
        })
      }
    })
    .then((obj) => {
      obj.render();
    });

  function drawPuzzleOutline(lineWidth, bbox) {
    ctx.save();
    ctx.fillStyle = 'rgba(255,255,255,0.2)';
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth = lineWidth;
    ctx.beginPath();
    ctx.moveTo(bbox[0], bbox[1])
    ctx.fillRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
    ctx.strokeRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]);
    ctx.restore();
  }

  function resizePiecemakerTable() {
    const rect = $container.getBoundingClientRect();
    const scaleX = rect.width / $canvas.width;
    const scaleY = rect.height / $canvas.height;

    const scaleToFit = Math.min(scaleX, scaleY);

    $canvas.style.transformOrigin = '0 0';
    $canvas.style.transform = `scale(${scaleToFit})`;
  }


  function drawPieceFactory(ctx, pieceId) {
    // TODO: Instead of having all the images inlined; pull them from the
    // size-100/sprite_with_padding.jpg and cut them out based on the inlined
    // svg clip paths.
    const img = document.getElementById(`p-img-${pieceId}`);
    if (!img) {
      return () => {};
    }

    return drawPiece;

    function drawPiece() {
      ctx.drawImage(img, this.x, this.y);
    }
  }

});

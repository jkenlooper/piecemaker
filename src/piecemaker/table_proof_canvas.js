/**
 * Table Proof using canvas.
 *
 * Draws all the pieces onto a scaled to fit canvas to show the initial
 * distribution of pieces.  Pieces are not interactive and all load from inlined
 * img tags that data urls.
 * This is my first time working with the canvas API, so I may have made some
 * rookie mistakes.
 */

class TableProofCanvas {
  constructor(piecemakerIndex, spriteLayout, $container, $canvas, $sprites) {
    this.piecemakerIndex = piecemakerIndex;
    this.spriteLayout = spriteLayout;
    this.$container = $container;
    this.$canvas = $canvas;
    this.$sprites = $sprites;
    this._assembled = false;
    this._side = 0;
    this._factor = 1.0;
    this._zoom = 0;
    this._scale = 1.0;
    this._offset = [0, 0];
    this.setCanvasDimensions();
    this.ctx = this.$canvas.getContext('2d', {"alpha": false});
    this.ctx.imageSmoothingEnabled = false;
    this.pieces = this.piecemakerIndex.piece_properties.map((pieceProperty) => {
      const pc = new Piece(this.ctx, this._factor, this._offset, this.$sprites,
        this.spriteLayout[String(pieceProperty.id)],
        {
          id: pieceProperty.id,
          x: pieceProperty.x,
          y: pieceProperty.y,
          ox: pieceProperty.ox,
          oy: pieceProperty.oy,
          s: pieceProperty.s,
          sides: pieceProperty.sides,
          width: pieceProperty.w,
          height: pieceProperty.h,
        });
      return pc;
    });
    this._setScale(this._zoom);
    this.render();
  }

  get imageWidth() {
    return this.piecemakerIndex.image_width;
  }
  get imageHeight() {
    return this.piecemakerIndex.image_height;
  }
  get tableWidth() {
    return this.piecemakerIndex.table_width;
  }
  get tableHeight() {
    return this.piecemakerIndex.table_height;
  }

  get zoom() {
    return this._zoom;
  }
  set zoom(zoomLevel) {
    this._setScale(zoomLevel);
    // TODO: improve zooming by maintaining the center.
    this.offset = this.offset;
    this.render();
  }
  _setScale(zoomLevel) {
    this._zoom = Math.max(0, Math.min(zoomLevel, this._zoomRanges.length - 1));
    this._factor = Math.min(1.0, this._zoomRanges[this._zoom]);
    this._scale = Math.max(1.0, this._zoomRanges[this._zoom]);
    this.$canvas.style.transformOrigin = "left top";
    this.$canvas.style.transform = `scale(${this._scale})`;
  }
  get factor() {
    return this._factor;
  }
  get offset() {
    return [
      this._offset[0],
      this._offset[1],
    ];
  }
  set offset(value) {
    const minX = Math.round(((this._factor * Math.min(1.0, this._scale)) - this.minimumScale) * (Math.max(this.tableWidth, this.$canvas.width) * -1));
    const maxX = 0;
    const minY = Math.round(((this._factor * Math.min(1.0, this._scale)) - this.minimumScale) * (Math.max(this.tableHeight, this.$canvas.height) * -1));
    const maxY = 0;
    this._offset[0] = Math.max(minX, Math.min(maxX, value[0]));
    this._offset[1] = Math.max(minY, Math.min(maxY, value[1]));
    this.render();
  }
  get assembled() {
    return this._assembled;
  }
  set assembled(value) {
    this._assembled = value;
    this.render();
  }
  get side() {
    return this._side;
  }
  set side(value) {
    this._side = value;
    this.render();
  }

  setCanvasDimensions() {
    const rect = this.$container.getBoundingClientRect();
    const scaleX = rect.width / this.tableWidth;
    const scaleY = rect.height / this.tableHeight;
    const scaleToFit = Math.min(scaleX, scaleY);
    this.minimumScale = Math.min(1.0, scaleToFit);
    const zoomLevelCount = Math.ceil(1.0 / scaleToFit)
    const zoomLinearIncrementAmount = (1.0 - Math.min(scaleToFit, 1.0)) / zoomLevelCount
    this._zoomRanges = [...Array(zoomLevelCount).keys()].reduce((acc, count) => {
      const z = acc[acc.length - 1] + zoomLinearIncrementAmount;
      if (z < 1.0) {
        acc.push(z);
      }
      return acc;
    }, [scaleToFit]).concat([1.0]);
    this._zoomRanges.sort();
    this.$canvas.width = Math.min(rect.width, this.tableWidth);
    this.$canvas.height = Math.min(rect.height, this.tableHeight);
  }

  render() {
    this.clear();
    const lineWidth = 2;
    this.drawPuzzleOutline(lineWidth, [
      this._offset[0] + (1.0 * (this.factor * Math.floor((this.tableWidth - this.imageWidth) * 0.5))),
      this._offset[1] + (1.0 * (this.factor * Math.floor((this.tableHeight - this.imageHeight) * 0.5))),
      this._offset[0] + (1.0 * (this.factor * (Math.floor((this.tableWidth - this.imageWidth) * 0.5) + this.imageWidth))),
      this._offset[1] + (1.0 * (this.factor * (Math.floor((this.tableHeight - this.imageHeight) * 0.5) + this.imageHeight)))
    ])
    this.drawTableBoundary(lineWidth, [
      this._offset[0] + (1.0 * this.factor),
      this._offset[1] + (1.0 * this.factor),
      this._offset[0] + (1.0 * (this.factor * this.tableWidth)),
      this._offset[1] + (1.0 * (this.factor * this.tableHeight))
    ])
    this.ctx.save();
    this.pieces.forEach((pc) => {
      pc.factor = this.factor;
      pc.offset = this._offset;
      pc.render(this._assembled, this._side);
    });
  }

  drawPuzzleOutline(lineWidth, bbox) {
    this.ctx.save();
    this.ctx.fillStyle = 'rgba(255,255,255,0.2)';
    this.ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    this.ctx.lineWidth = lineWidth;
    this.ctx.beginPath();
    this.ctx.moveTo(bbox[0], bbox[1])
    this.ctx.fillRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
    this.ctx.strokeRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]);
    this.ctx.restore();
  }
  drawTableBoundary(lineWidth, bbox) {
    this.ctx.save();
    this.ctx.fillStyle = 'transparent';
    this.ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    this.ctx.lineWidth = lineWidth;
    this.ctx.beginPath();
    this.ctx.moveTo(bbox[0], bbox[1])
    this.ctx.fillRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
    this.ctx.strokeRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]);
    this.ctx.restore();
  }

  clear() {
    this.ctx.clearRect(0,0, this.$canvas.width, this.$canvas.height);
  }
}

class Piece {
  constructor(ctx, factor, offset, $sprites, bbox, props) {
    this.ctx = ctx;
    this.factor = factor;
    this.offset = offset;
    this.$sprites = $sprites;
    this.id = props.id;
    this.bbox = bbox;
    this.x = props.x;
    this.y = props.y;
    this.ox = props.ox;
    this.oy = props.oy;
    this.s = props.s;
    this.sides = props.sides;
    this.width = props.width;
    this.height = props.height;

    // TODO: Use size-100/sprite_with_padding.jpg and cut them out based on the inlined
    // svg clip paths.
    //this.clipPath = document.getElementById(`p-clip_path-${this.id}`);
  }

  render(assembled, side_index) {
    //if (!this.clipPath) {
    //  throw "clipPath for piece not found";
    //}
    const x = assembled ? this.ox : this.x;
    const y = assembled ? this.oy : this.y;
    const s = assembled ? this.sides[side_index] : side_index;
    this.ctx.drawImage(
      this.$sprites[s],
      this.bbox[0],
      this.bbox[1],
      this.bbox[2],
      this.bbox[3],
      this.offset[0] + (x * this.factor),
      this.offset[1] + (y * this.factor),
      this.width * this.factor,
      this.height * this.factor
    );
  }
}

window.addEventListener('load', (event) => {
  const $canvas = document.getElementById('piecemaker-table');
  const $container = $canvas.parentElement;
  const $sprites = $canvas.querySelectorAll("img[data-side-index]").values().toArray();
  const $zoomInButton = document.getElementById("zoom-in");
  const $zoomOutButton = document.getElementById("zoom-out");
  const $toggleAssemble = document.getElementById("assembled");
  const $sideInputs = document.querySelectorAll("input[name=side]");

  if (!$canvas || !$container || !$sprites.length) {
    throw "Couldn't load elements"
  }
  const scale = $canvas.dataset.size;
  let tableProofCanvas;

  const piecemaker_index_req = fetch("index.json").then(response => response.json());
  const sprite_layout_req = fetch(`size-${scale}/sprite_without_padding_layout.json`).then(response => response.json());
  Promise.all([
    piecemaker_index_req,
    sprite_layout_req
  ]).then((values) => {
    const [piecemaker_index, sprite_layout] = values;
    tableProofCanvas = new TableProofCanvas(piecemaker_index, sprite_layout, $container, $canvas, $sprites);
    tableProofCanvas.assembled = $toggleAssemble.checked;
    $toggleAssemble.addEventListener('change', (event) => {
      tableProofCanvas.assembled = $toggleAssemble.checked;
      tableProofCanvas.render();
    });
    tableProofCanvas.side = 0;
    $sideInputs.forEach(($sideInput) => {
      $sideInput.addEventListener('change', (event) => {
        if ($sideInput.checked) {
          tableProofCanvas.side = Number($sideInput.value);
          tableProofCanvas.render();
        }
      });
    });
    window.addEventListener('resize', () => {
      tableProofCanvas.setCanvasDimensions();
      tableProofCanvas.zoom = tableProofCanvas.zoom;
    });
    let zooming = false;
    let panning = false;
    const zoomAmount = 0.05;
    $canvas.addEventListener('wheel', (event) => {
      event.preventDefault();
      event.stopPropagation();
      if (event.ctrlKey) {
        if (!zooming) {
          window.requestAnimationFrame(() => {
            //tableProofCanvas.zoom = tableProofCanvas.zoom + (event.deltaY * zoomAmount);
            tableProofCanvas.zoom = tableProofCanvas.zoom + Math.max(-1, Math.max(1, event.deltaY));
            zooming = false;
          });
          zooming = true;
        }
      } else {
        if (!panning) {
          window.requestAnimationFrame(() => {
            const offset = tableProofCanvas.offset;
            offset[0] = offset[0] + event.deltaX * 5;
            offset[1] = offset[1] + event.deltaY * 5;
            tableProofCanvas.offset = offset;
            panning = false;
          });
          panning = true;
        }
      }
    });
    $zoomInButton.addEventListener('click', (event) => {
      tableProofCanvas.zoom = tableProofCanvas.zoom + 1;
    });
    $zoomOutButton.addEventListener('click', (event) => {
      tableProofCanvas.zoom = tableProofCanvas.zoom - 1;
    });
    $canvas.addEventListener('mousedown', (event) => {
      const originOffset = tableProofCanvas.offset;
      const mouseOriginX = event.clientX - originOffset[0];
      const mouseOriginY = event.clientY - originOffset[1];
      function mousemoveHandler(event) {
        if (!panning) {
          const mouseDragX = event.clientX - mouseOriginX;
          const mouseDragY = event.clientY - mouseOriginY;
          window.requestAnimationFrame(() => {
            tableProofCanvas.offset = [mouseDragX, mouseDragY];
            panning = false;
          });
          panning = true;
        }
      }
      function mouseupHandler(event) {
        document.removeEventListener('mousemove', mousemoveHandler);
        document.removeEventListener('mouseup', mouseupHandler);
      }
      document.addEventListener('mousemove', mousemoveHandler);
      document.addEventListener('mouseup', mouseupHandler);
    });

  });
});

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
  constructor(piecemakerIndex, spriteLayout, $container, $canvas, $sprite) {
    this.piecemakerIndex = piecemakerIndex;
    this.spriteLayout = spriteLayout;
    this.$container = $container;
    this.$canvas = $canvas;
    this.$sprite = $sprite;
    this.factor;
    this.setCanvasDimensions();
    this.ctx = this.$canvas.getContext('2d', {"alpha": false});
    this.raf;

    this.pieces = this.piecemakerIndex.piece_properties.map((pieceProperty) => {
        const pc = new Piece(this.ctx, this.factor, this.$sprite,
          this.spriteLayout[String(pieceProperty.id)],
          {
          id: pieceProperty.id,
          x: pieceProperty.x,
          y: pieceProperty.y,
          width: pieceProperty.w,
          height: pieceProperty.h,
        })
        return pc;
      });
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

  setCanvasDimensions() {
    const rect = this.$container.getBoundingClientRect();
    const scaleX = rect.width / this.tableWidth;
    const scaleY = rect.height / this.tableHeight;
    const scaleToFit = Math.min(scaleX, scaleY);
    this.factor = scaleToFit;
    this.$canvas.width = Math.ceil(this.factor * this.tableWidth);
    this.$canvas.height = Math.ceil(this.factor * this.tableHeight);
  }

  render() {
    this.clear();
    this.setCanvasDimensions();
    const lineWidth = 2;
    this.drawPuzzleOutline(lineWidth, [
      this.factor * Math.floor((this.tableWidth - this.imageWidth) * 0.5),
      this.factor * Math.floor((this.tableHeight - this.imageHeight) * 0.5),
      this.factor * (Math.floor((this.tableWidth - this.imageWidth) * 0.5) + this.imageWidth),
      this.factor * (Math.floor((this.tableHeight - this.imageHeight) * 0.5) + this.imageHeight)
    ])
    this.ctx.save();
    this.pieces.forEach((pc) => {
      pc.factor = this.factor;
      pc.render();
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

  clear() {
    this.ctx.clearRect(0,0, this.$canvas.width, this.$canvas.height);
  }
}

class Piece {
  constructor(ctx, factor, $sprite, bbox, props) {
    this.ctx = ctx;
    this.factor = factor;
    this.$sprite = $sprite;
    this.id = props.id;
    this.bbox = bbox;
    this.x = props.x;
    this.y = props.y;
    this.width = props.width;
    this.height = props.height;

    // TODO: Use size-100/sprite_with_padding.jpg and cut them out based on the inlined
    // svg clip paths.
    //this.clipPath = document.getElementById(`p-clip_path-${this.id}`);
  }

  render() {
    //if (!this.clipPath) {
    //  throw "clipPath for piece not found";
    //}
    this.ctx.drawImage(
      this.$sprite,
      this.bbox[0],
      this.bbox[1],
      this.bbox[2],
      this.bbox[3],
      this.x * this.factor,
      this.y * this.factor,
      this.width * this.factor,
      this.height * this.factor
    );
  }
}

window.addEventListener('load', (event) => {
  const $canvas = document.getElementById('piecemaker-table');
  const $container = $canvas.parentElement;
  const $sprite = document.getElementById("piecemaker-sprite_without_padding");
  if (!$canvas || !$container || !$sprite) {
    throw "Couldn't load elements"
  }
  const scale = $canvas.dataset.size;
  const ctx = $canvas.getContext('2d', {"alpha": false});
  let tableProofCanvas;

  const piecemaker_index_req = fetch("index.json").then(response => response.json());
  const sprite_layout_req = fetch(`size-${scale}/sprite_without_padding_layout.json`).then(response => response.json());
  Promise.all([
    piecemaker_index_req,
    sprite_layout_req
  ]).then((values) => {
    const [piecemaker_index, sprite_layout] = values;
    tableProofCanvas = new TableProofCanvas(piecemaker_index, sprite_layout, $container, $canvas, $sprite);
    tableProofCanvas.render();
    window.addEventListener('resize', () => {
      tableProofCanvas.render();
    });
  });
});

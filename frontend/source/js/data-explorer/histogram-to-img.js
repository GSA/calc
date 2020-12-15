/* global XMLSerializer, canvg, vex, Image, saveAs */

// canvg is from canvg.js
// vex is from vex.combined.min.js
// saveAs is from FileSaver.js

export default function histogramToImg(originalSvg, canvas) {
  const serializer = new XMLSerializer();
  let img;
  let modalImg;

  const svg = serializer.serializeToString(originalSvg);

  // convert svg into canvas
  canvg(canvas, svg, { ignoreMouse: true, scaleWidth: 720, scaleHeight: 300 });

  if (typeof Blob !== 'undefined') {
    canvas.toBlob((blob) => {
      saveAs(blob, 'histogram.png');
    });
  } else {
    img = canvas.toDataURL('image/png');
    modalImg = new Image();
    modalImg.src = img;

    vex.open({
      content: 'Please right click the image and select "save as" to download the graph.',
      afterOpen(content) {
        return content.append(modalImg);
      },
      showCloseButton: true,
      contentCSS: {
        width: '800px',
      },
    });
  }
}

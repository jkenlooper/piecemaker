import subprocess
import os
import os.path
import cairosvg

def rasterize_svgfiles(svgfiles):
    """
    Converts multiple svg files to png files with same basename.
    """

    for svgfile in svgfiles:
        output_dir = os.path.dirname(svgfile)
        name = os.path.basename(svgfile)
        (root, ext) = os.path.splitext(name)
        subprocess.call(['svgo', '-i', svgfile, '-o', svgfile], shell=False)
        cairosvg.svg2png(url=svgfile, write_to=os.path.join(output_dir, '{0}.png'.format(root)))

def potrace(trimmedpng, output_dir):
    """
    Convert the mask into a svg file.
    """
    #TODO: convert the trimmedpng to a bmp, but not use imagemagick.
    # convert trimmed.png -alpha Extract trimmed.bmp
    #(bmp, ext) = os.path.splitext(trimmedpng)
    #trimmedbmp = "%s.bmp" % bmp
    mask_dir = os.path.dirname(trimmedpng)
    mask_png = os.path.basename(trimmedpng)
    (mask_name, ext) = os.path.splitext(mask_png)

    trimmedbmp = os.path.join(mask_dir, "%s.bmp" % mask_name)
    subprocess.call(['convert', trimmedpng, '-alpha', 'Extract', '-negate',
        trimmedbmp], shell=False)

    masksvg = os.path.join(output_dir, "%s.svg" % mask_name)
    potrace = ['potrace', trimmedbmp, '-s', '-o', masksvg]
    subprocess.call(potrace, shell=False)

    os.unlink(trimmedbmp)

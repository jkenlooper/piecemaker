import subprocess
import os
import os.path

def rasterize_svgfiles(svgfiles):
    """
    Converts multiple svg files to png files with same basename.
    Relies on batik being installed.
    """
    raster = ['/usr/bin/java', '-Xint', '-jar']

    #TODO: better way of getting the path to the rasterizer?
    raster.append('batik-1.7/batik-rasterizer.jar')

    for svgfile in svgfiles:
        output_dir = os.path.dirname(svgfile)
        name = os.path.basename(svgfile)
        (root, ext) = os.path.splitext(name)
        raster.append(os.path.join(output_dir, '%s.svg' % root))

    subprocess.call(raster, shell=False)

def potrace(trimmedpng, output_dir):
    """
    Convert the mask into a svg file.
    """
    #TODO: use pypotrace on each mask to convert to vector

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

#!/usr/bin/python

from gimpfu import *

from base64 import b64encode
from os.path import splitext



svg_preamble = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
svg_doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'

def img_reference(filename):
    return filename

def img_embedded(filename):
    with open(filename, "rb") as f:
        text = b64encode(f.read())
        return 'data:image/{};base64,{}'.format(splitext(filename)[1][1:], text.decode('ascii'))

def write_mask(io, file_name_mask, im_size, img_write_method):
     io.write("""  <mask id="Mask">  
     <image x="0" y="0" width="{}" height="{}" xlink:href="{}"/>
   </mask>\n""".format(im_size[0], im_size[1], img_write_method(file_name_mask)))

def write_img(io, file_name_im, im_size, img_write_method):
    io.write('  <image x="0" y="0" width="{}" height="{}" mask="url(#Mask)" xlink:href="{}"/>\n'.format(im_size[0], im_size[1], img_write_method(file_name_im)))


def svg_mask_image(output_name, img_name, mask_name, size, img_write_method):
    """ Creates an svg image with a mask
    """
    with open(output_name, "w") as f:
        f.write(svg_preamble)
        f.write(svg_doctype)
        f.write('<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'.format(size[0], size[1]))
        write_mask(f, mask_name, size, img_write_method)
        write_img(f, img_name, size, img_write_method)
        f.write('</svg>\n')


def plugin_main(img, drawable, jpeg_output, mask_output, svg_output, embed):

    img_write_method = img_reference
    if embed:
        img_write_method = img_embedded

    #create mask
    mask = pdb.gimp_layer_create_mask(img.active_layer, ADD_MASK_ALPHA)
    
    # save files with default jpg/png settings
    pdb.gimp_file_save(img, drawable, jpeg_output, jpeg_output)
    pdb.gimp_file_save(img, mask, mask_output, mask_output)
    svg_mask_image(svg_output, jpeg_output, mask_output, (drawable.width, drawable.height), img_write_method)

register(
        "svg_mask_exporter",
        "Exports an jpg image with a png-image mask as alpha channel in a svg file",
        """Exports an jpg image with a png-image mask as alpha channel in a svg file.
        Therefore, you can use the compression of a jpg file but also use the transperency, which is
        usually not supported by jpg.
        There are two modes, embed and non-embed. embed writes the jpeg image and the mask into the svg files while
        non-embed mode just reference to the image files. embed files consumes ~30% more space, but you dont need the
        intermediate jpeg/png image.""",
        "Matthias Moeller",
        "Matthias Moeller",
        "2018",
        "<Image>/Image/Export with alpha mask ...",
        "RGBA, GRAYA",
        [
            (PF_FILENAME, "jpeg_output" ,"jpeg out file", "image.jpg"),
            (PF_FILENAME, "mask_output", "mask out file", "mask.png"),
            (PF_FILENAME, "svg_output", "svg out file", "output.svg"),
            (PF_TOGGLE, "embed", "Embed images into svg file", True)
        ],
        [],
        plugin_main)

main()
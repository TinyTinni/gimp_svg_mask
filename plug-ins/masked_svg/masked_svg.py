#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# if this doesn't work under linux, try
# chmod +x masked_svg.py 

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')

from gi.repository import Gimp
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib
from base64 import b64encode
from os.path import splitext
import gzip
import sys

plug_in_proc   = "tinni-svg-mask-export"
plug_in_binary = "svg-mask-export"

svg_preamble = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
svg_doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'

def img_reference(filename):
    return filename

def get_writer(filename, use_gzip):
    if use_gzip:
        if not filename.endswith(".svgz"):
           if filename.endswith(".svg"):
              filename += "z"
           else:
              filename += ".svgz"
        return gzip.open(filename, "wt")
    
    if not filename.endswith(".svg"):
           filename += ".svg"
    return open(filename, "w")

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


def svg_mask_image(output_name, img_name, mask_name, size, img_write_method, use_gzip):
    """ Creates an svg image with a mask
    """
    with get_writer(output_name, use_gzip) as f:
        f.write(svg_preamble)
        f.write(svg_doctype)
        f.write('<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'.format(size[0], size[1]))
        write_mask(f, mask_name, size, img_write_method)
        write_img(f, img_name, size, img_write_method)
        f.write('</svg>\n')




def svg_export_run(procedure, run_mode, image, drawables, config, data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
      GimpUi.init(plug_in_binary)
      dialog = GimpUi.ProcedureDialog.new(procedure, config, "Export masked SVG")
      dialog.fill(None)
      if not dialog.run():
        dialog.destroy()
        return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
      else:
        dialog.destroy()

    jpeg_out          = config.get_property("jpeg_output")
    mask_out          = config.get_property("mask_output")
    svg_out           = config.get_property("svg_output")

    embed             = config.get_property("embed")
    use_gzip          = config.get_property("svgz")

    image_width = image.get_width()
    image_height = image.get_height()

    if len(image.get_selected_layers()) != 1:
      return procedure.new_return_values (Gimp.PDBStatusType.CALLING_ERROR,
                                          GLib.Error(f"Procedure '{plug_in_proc}' works only with 1 selected layer."))
    layer = image.get_selected_layers()[0]

    # save jpeg
    save_file = Gimp.get_pdb().lookup_procedure('gimp-file-save')
    save_file_config = save_file.create_config()
    save_file_config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    save_file_config.set_property("image", image)
    save_file_config.set_property("file", jpeg_out)
    result = save_file.run(save_file_config)
    if result.index(0) is not Gimp.PDBStatusType.SUCCESS:
      return procedure.new_return_values (result.index(0),
                                          GLib.Error(f"Procedure '{plug_in_proc}' could not save the color image."))

    # save mask
    mask = layer.create_mask(Gimp.AddMaskType.ALPHA)
    mask_image = Gimp.Image.new(image_width, image_height, Gimp.ImageBaseType.GRAY)
    test = Gimp.Layer.new_from_drawable(mask, mask_image)
    mask_image.insert_layer(test, None, -1)
    save_file_config.set_property("image", mask_image)
    save_file_config.set_property("file", mask_out)
    result = save_file.run(save_file_config)
    mask_image.delete()
    mask.delete()
    if result.index(0) is not Gimp.PDBStatusType.SUCCESS:
      return procedure.new_return_values (result.index(0),
                                          GLib.Error(f"Procedure '{plug_in_proc}' could not save the mask."))

    img_write_method = img_reference
    embed = embed or use_gzip
    if embed:
        img_write_method = img_embedded

    svg_mask_image(svg_out.get_path(), jpeg_out.get_path(), mask_out.get_path(), (image.get_width(), image.get_height()), img_write_method, use_gzip)

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class SvgMaskExport (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc ]
  
  def do_set_i18n (self, name):
    return False

  def do_create_procedure(self, name):
    procedure = None

    if name == plug_in_proc:
      procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          svg_export_run, None)
      procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE)
      procedure.set_image_types("RGBA,GRAYA")

      procedure.set_menu_label("_Export with alpha mask ...")
      procedure.set_attribution("Matthias Möller", "Matthias Möller", "2018")
      procedure.add_menu_path ("<Image>/Image/")
      procedure.set_documentation ("""Exports a jpg image with a png-image mask as alpha channel in a svg file.
        Therefore, you can use the compression of a jpg file but also use the transperency, which is
        usually not supported by jpg.
        There are two modes, embed and non-embed. embed writes the jpeg image and the mask into the svg files while
        non-embed mode just reference to the image files. embed files consumes ~30% more space, but you dont need the
        intermediate jpeg/png image.""",
                                   None)

      procedure.add_file_argument("jpeg_output", "jpeg out file", "Path to the color image output file. You can also change the image extension if you don't want jpg.", Gimp.FileChooserAction.SAVE, False, Gio.File.new_for_path("image.jpg"), GObject.ParamFlags.READWRITE)
      procedure.add_file_argument("mask_output", "mask out file", "Path to the color mask output file. You can also change the image extension if you don't want png.", Gimp.FileChooserAction.SAVE, False, Gio.File.new_for_path("mask.png"), GObject.ParamFlags.READWRITE)
      procedure.add_file_argument("svg_output", "svg out file", "Path to the color svg output file.", Gimp.FileChooserAction.SAVE, False, Gio.File.new_for_path("output.svg"), GObject.ParamFlags.READWRITE)

      procedure.add_boolean_argument("embed", "Embed images into svg file", "If checked, the color image (jpeg) and mask image (png) will be encoded in the svg. In this case, the jpeg/png are not required to be carried around.", True, GObject.ParamFlags.READWRITE)
      procedure.add_boolean_argument("svgz", "Save embedding as svgz (enables embed option implicit)", "Will compress the resulting svg.", False, GObject.ParamFlags.READWRITE)

    return procedure

Gimp.main(SvgMaskExport.__gtype__, sys.argv)

# Gimp Plugin for SVG Masks

![Example](https://cdn.rawgit.com/TinyTinni/gimp_svg_mask/master/images/example_banner.svg)
![Valid SVG 1.1](http://www.w3.org/Icons/valid-svg11)

As you may know, the _jpeg_ file format cannot save an alpha-channel, which is often used for transparency, of any image.
Another popular format, _png_, is able to save the alpha channel, but it is
a lossless compression and the same image can occupy much more space.

A lot of image process program, i.e. modern Browsers (prior IE8), also support _svg_ files.
With this file format, it is possible to decompose an image to two images, one defining the color and one defining the alpha channel.
This allows you to use a higher compressions from i.e. jpeg but also having transparency in your image.

This Gimp Plugin helps you, creating such a svg file from an image with alpha channel.

The top image is such a svg file (see [Image Source](./images/example_banner.svg) for more details).

## Modes

There are two modes, one mode, which creates an output color image, the mask containing
the alpha channel and the svg file which stiches everything together.

The other mode, _embed_, saves everything in the svg file.

- The first mode **not embed** requires ~30% less space than the second mode, but you have to keep all the files. The produces svg just links to the images.

- The second mode **embed** requires more space, but everything is encoded in the svg file.

## Space Consumption Comparison

Some results from the website [clipartpng.com](https://clipartpng.com/) (first found using a search engine):

format      | [Cat](https://clipartpng.com/?2690,cat-png-clip-art) | [White Bear](https://clipartpng.com/?1044,angry-white-bear-png-clipart)|[Baby Fox](https://clipartpng.com/?2277,baby-fox-png-clip-art)|[Brown Bear](https://clipartpng.com/?2279,bear-brown-png-clip-art)|[Earth](https://clipartpng.com/?2279,bear-brown-png-clip-art)|[Trash Bin](https://clipartpng.com/?2129,garbage-trash-bin-with-recycle-symbol-png-clip-art)|
|---|---|---|---|---|---|---|
**png**         | 11.172kb      | 4.151kb       | 4.030kb       | 824kb         | 3.602kb       | 2.152kb       |
**svg+jpeg+png**| 2.001kb (~18%) | 573kb (~14%) | 833kb (~21%)   | 251kb (~30%)  | 1.342kb (~37%)| 1.428kb (~66%) |
**embed svg**   | 2.813kb (~25%) | 762kb (~18%) | 1.109kb (~28%) | 332kb (~40%)  | 1.787kb (~50%)| 1.903kb (~88%) |
**svgz**        | 1.961kb (~18%)  | 524kb (~13%) |  820kb (~20%)| 235kb (~29%)| 926kb (~26%) | 864kb (~40%) |

The _svgz_ file format is a compressed embed svg file (using gzip method).
The plugin does not support creating _svgz_ out of the box, but you can use Inkscape, 7-zip or any other compression program which has gzip support.

All images where exported as jpeg for the color image and png for the mask image (jpeg can also be used as a mask image).
All jepg/gzip compressions where done with GIMP 2.10 default setting (quality 90/0.9) and 7-zip gzip method default settings.

## How to Install/Use

Place the [python script file](./plug-ins/masked_svg.py) under plug-ins in the GIMP plugin folder.
The directory is usually located somewhere:
- Windows: %AppData%\Roaming\GIMP\<Version>\plug-ins
- Linux (GIMP 2.10): ~/.config/GIMP/2.10/plug-ins

You can find a new option now under the menu: _Image->Export with mask..._

## License

[MIT-License](./LICENSE)

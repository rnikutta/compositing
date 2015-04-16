compositing
===========

**Author:** Robert Nikutta
**Version:** 2014-12-12
**License:** BSD 3-clause, please see [LICENSE](./LICENSE) file

alpha-blending (image compositing) of arbitrary number of
monochromatic 2d images. Implements algorithms developed in [Porter &
Duff (1984)](http://dl.acm.org/citation.cfm?id=808606) and [Smith
(1995)](http://www.cs.princeton.edu/courses/archive/fall00/cs426/papers/smith95a.pdf). Image
cubes can be loaded from arrays, or FITS files, etc. Any valid `pylab`
color specification can be assigned to each image slice. The
individual alphas (values of opaqueness) for all slices will be
computed automatically such that each slice contributes 1/N to the
total image. The alphas can also be assigned manually (per-slice).

See also the extensive docstrings of classes `Compositing`, `Image`,
`Cube`, `ClumpyImage` for documentation.

####Contents####

An *Ipython Notebook* file is provided to see the classes in
action. If you have Ipython notebook installed, launch

```ipython notebook```

A window in your browser should pop up. There, load the file
`compositing.ipynb` and play the cells. Alternatively, you can use the
online [Ipython notebook viewer](http://nbviewer.ipython.org/) to play
the file.

`compositing.md` is a static *Markdown* view of the evaluated Ipython
notebook.

`IMG-AA00-TORUSG-sig15-i60-Y010-N01-q0.0-tv005.0.fits.gz` is an
example FITS file used in the notebook. It's a
[CLUMPY](https://www.clumpy.org) model, with nine 2d brightness maps
of torus emission at different wavelengths.

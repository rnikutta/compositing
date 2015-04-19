"""alpha-Compositing of images.

Implements algorithms developed in

  Porter, Thomas & Duff, Tom (1984), "Compositing Digital Images",
      SIGGRAPH Comput. Graph.,
      doi:10.1145/964965.808606

  Smith, Alvy Ray (1995), "Image Compositing Fundamentals",
      Microsoft Tech Memo 4,
      http://www.cs.princeton.edu/courses/archive/fall00/cs426/papers/smith95a.pdf

For an example, open the Ipython notebook compositing.ipynb. Either
run locally by launching

    ipython notebook

and then opening the compositing.ipynb file in the browser window that
just popped up, or open compositing.ipynb in the on-line Ipython
notebook viewer (nbviewer):

    http://nbviewer.ipython.org/

More instructions on Ipython Notebook are in:

    http://ipython.org/ipython-doc/1/interactive/notebook.html

For usage of the classes provided in this module, see docstrings of
classes Cube, FitsFile, Image, and Compositing.

This module composits RGBA images from an arbitrary number of
monochromatic (MC) 2d-intensity/brightness maps. For each MC image
'slice', any color can be specified separately, using standard
pylab/matplotlib notation, e.g. 'r' (red) or 'blue' or '0.5' (middle
gray) or (0.,1.,0.) (green in RGB notation), or #ff0000 (red in
hex). It is recommended to use "pure" RGB colors, i.e. r,g, or b, but
any valid color specification is accepted. Be aware though that using
"mixed" colors can result in unexpected final rendition of the
composite image. Experiment a bit!

For each slice, a separate value of alpha (opaqueness) can be
specified. However, in many cases it is advisable to leave the
assignment of alpha values to the code. In that case, the alpha of the
k-th layer (counted from the bottom layer) will be 1/k. This
dependence ensures that for the observer looking down through all the
N layers, each layer contributes 1/N-th of the total visibility.

    1st 2nd ... n-th  <-- k-th layer
     |   |   |   |    
     |   |   |   |    
     |---|---|---|---->  Observer
     |   |   |   |    
     |   |   |   |    
    a1  a2  ...  an   <-- alpha of k-th layer (opaqueness)

Visible of k-th layer by the observer:

layer       total transmitted part at observer's site
  1         a1 * (1-a2) * ... * (1-n)
  2              (1-a2) * ... * (1-n)
  ...
  n                             (1-n)

If all layers are to contribute with equal strength to the total
signal (i.e. single-layer strength is 1/N), then it follows from the
above equations that a1 = 1, a2 = 1/2, a3 = 1/3, ..., an = 1/N. Thus,
the total transmitted contribution tr(k) from the k-th layer is a
harmonic series with

    tr(k) = \sum_{n=k}^{n=N} 1/n.

However, if you want to bring out the features in a layer more, you
can specify the alphas for the individual layers in a list (see
docstring of Compositing.__call__).

"""

__author__ = "Robert Nikutta <robert.nikutta@gmail.com"
__version__ = "2015-04-19"

import numpy as N
import pyfits as pf
import os
import matplotlib


class Cube():

    def __init__(self,data,slices=(0,1,2)):

        """3d representation of image slices to blend.

        Parameters
        ----------

        data : 3d array
            data.shape = (nx,ny,nz), with nx, ny the x,y number of
            pixels, and nz a number of image 'slices'. This is the
            original data set, and need not be identical to the one to
            be used for blending / compositing (see 'slices').

        slices : tuple of integers or None
            Tuple of integers, all from range(nz), representing the
            image slices from data to select for compositing. The
            order of the indices will be the order in which the images
            will be blended: first slice at the bottom, last slice on
            top. Example: slices=(0,1,2) (default), or slices=(5,0,8),
            etc. If None, all frames from 'data' will be used.

        """

        self.data = data
        self.update_slices(slices)


    def update_slices(self,slices):

        if slices is None:
            slices = range(self.data.shape[0])

        else:
            if isinstance(slices,int):
                slices = list(slices)
        
        if not isinstance(slices,(list,tuple,N.ndarray)):
            raise Exception, "slices is neither None, nor an integer, nor a sequence of integers."

        self.slices = slices
        self.__update_cube()


    def __update_cube(self):
        self.cube = self.data[self.slices,:,:]


class FitsFile():

    def __init__(self,path):

        if os.path.isfile(path):
            try:
                self.hdr = pf.getheader(path)
            except IOError:
                raise Exception, "Opening FITS file %s failed." % path
    
            self.nw = self.hdr['NAXIS3']
            self.ny = self.hdr['NAXIS2']
            self.nx = self.hdr['NAXIS1']

            self.data = pf.getdata(path)

        else:
            raise Exception, "'path' is not a regular file or is missing."


class Image():

    def __init__(self,data,color,alpha=1.,normalize=True):

        """Represent a 2d monochromatic image as RGBA cube, with
           pre-multiplied color channels.

        Parameters
        ----------
        
        data : 2d array
            A monochromatic image / brightness map. Will be
            alpha-blended with others

        color : str or 3-tuple
            Any valid pylab designation of a color to be used for this
            2d image. E.g. 'r', 'blue', '0.5', '#ffb500', or (0.,1.,0)
            (the latter is an RGB 3-tuple).

        alpha : float
            The alpha values (opaqueness) of this image. Between
            0. (fully transparent) and 1.0 (fully opaque).

        normalize : bool
            If True, 'data' will be normalized to it's peak value
            first.

        """

        self.color = color

        self.alpha = alpha
        self.alpha_premultiplied = False

        self.data = data
        self.ny, self.nx = self.data.shape

        if normalize == True:
            self.data /= self.data.max()

        self.construct_rgba()


    def construct_rgb(self):
        
        self.rgb_tuple = matplotlib.colors.colorConverter.to_rgb(self.color)  # e.g. color='r'

        # construct image as RGBA
        self.rgb = N.ones((self.ny,self.nx,3),dtype=N.float64)
        for channel in xrange(3):
            self.rgb[:,:,channel] = self.data[...] * self.rgb_tuple[channel]  # set red channel


    def construct_rgba(self):

        self.construct_rgb()
        self.alpha_map = N.ones((self.nx,self.ny),dtype=N.float64) * self.alpha   # same shape as a single RGB channel
        self.rgba = N.dstack((self.rgb,self.alpha_map))
        self.alpha_premultiply()


    def alpha_premultiply(self):

        """alpha-premultiply the color channels."""

        for channel in xrange(3):
            self.rgba[:,:,channel] *= self.alpha_map

        self.alpha_premultiplied = True   # to be used in future versions


    def __call__(self):
        """Nothing yet."""

        pass


class Compositing():

    def __init__(self,obj):

        """Initialize class with 'obj'.

        obj has at least a Cube() instance in obj.cube. See class
        ClumpyFile() or simply class Cube() for an example.

        """

        self.obj = obj


    def __setup(self):

        """Reset some init parameters, to allow for composite image
           re-computation without having to re-compute the Cube()
           instance.
        """

        self.cube = self.obj.cube.copy()
        self.nz, self.ny, self.nx = self.obj.cube.shape  # important: retain the shape of the original cube
        self.images = []

        
    def __call__(self,colors,alphas=None,bgcolor='black',pre_multiply=True,normalize_cube=True,normalize_slices=True):

        """Compute the correctly alpha-blended composite image of N
           monochromatic 2d image slices.

        Parameters
        ----------

        colors : list
            Sequence of color specifications for all 2d images to be
            alpha-blended. Any color specification valid in pylab is
            permitted, e.g. 'r', 'green, '0.5', '#ffb500', etc., but
            the use of "pure" RGB colors is recommended for more
            predictable compositing. If self.obj.cube has N image
            slices to blend, len(colors) must be N. Example:
            colors=['r','g','b'].

        alphas : list or None (default)
            If None (default), the alphas (values of opaqueness) of
            each layer will be computed automatically such that each
            layer contributes 1/N to the final image. This is
            recommended in most cases (see docstring of this
            module). However, if you want to bring the features of
            some layers out more, you can specify arbitrary alpha
            values per layer in a list. All alpha values must be
            between 0. (fully transparent) and 1. (fully opaque).

        bgcolor : str
            Allows to specify a custom background color for the final
            image. Black is default and looks good, other colors may
            look a bit washed-out, because the monochromatic
            background image is also properly blended with the final
            background-free composite.

        pre_multiply : bool
            If True (default), the images are pre-multiplied with
            their alphas. This allows for easier/cleaner and more
            intuitive computation of the compsite images. See the two
            literature references for details.

        normalize_cube : bool
            If True (default), the cube of 2d images to be blended is
            first normalized to the global peak. Recommended.

        normalize_slices : bool
            If True (dafault), every single 2d images slice is
            normalized individually first. This is recommended to
            bring out the features in each slice more, but if the
            individual images in .cube are in some physical relation
            to each other (e.g. the brightness maps of a sky object in
            several wavebands), you may want to preserve the images'
            relative strengths in the final image. In that case set
            normalize_slices=False. Note that if the difference
            between individual images is too large (e.g. logarithmic),
            the faint slices may be invisible in the final image
            (unless you tweak their individual alpha values).


        Returns
        -------

        Nothing. The final composite image is in self.image, and is an
        RGBA array. It can be displayed via:

            pylab.imshow(self.image)


        Examples
        --------
        
        Load and run the compositing.ipynb Ipython Notebook file.

        """

        self.__setup()

        self.colors = colors
        if len(self.colors) != self.nz:
            raise Exception, "Number of provided colors must match number of images."

        if normalize_cube:
            self.cube /= self.cube.max()  # normalize to cube's maximum

        # background frame
        self.img_bg = Image(N.ones((self.nx,self.ny)),bgcolor,1.)
        self.images = [self.img_bg]

        # set alphas of all layers
        if alphas == None:
            alphas = [1/float(j+2) for j in range(self.nz)]  # +2 because a background 'image' is added

        # generate RGBA representations of all slices to be blended
        for j in xrange(self.nz):
            Image_ = Image(self.cube[j,:,:],self.colors[j],alpha=alphas[j],normalize=normalize_slices)
            self.images.append(Image_)

        # alpha-compositing
        self.compose()

        # output adjustment
        self.stretch_contrast()


    def over_premultiplied(self,A,B):

        """Composite image of 'B over A', if both A and B have
        alpha-premultiplied colors.

        The formula for the resulting composite image is (see
        docstring of this module for literature references):

            C = B + A - beta*A

        where beta is the alpha-channel of the above image B
        (i.e. beta = B[...,-1]). This formula is valid for both the 3
        color channels and the alpha channel.

        Parameters
        ----------

        A : RGBA array, i.e. (nx,ny,4)
            image below (with alpha-premultiplied colors)

        B : RGBA array, i.e. (nx,ny,4)
            image above (with alpha-premultiplied colors)

        """

        # Currently the alpha is a single value per image, but in
        # future we may want to compute images with variable
        # alphas. Thus: array ops.
        beta = B[...,-1]

        aux = A.copy()
        for j in xrange(4):
            aux[:,:,j] *= beta[:,:]

        C = B + A - aux

        return C


    def compose(self):

        """alpha-compositing of all images, using over_premultiplied().

        Starts with the "bottom" image (first image), and
        progressively blends the next higher image, until list of
        images is empty.
        """

        self.image = self.images[0].rgba
        for j in xrange(1,len(self.images)):
            self.image = self.over_premultiplied(self.image,self.images[j].rgba)


    def stretch_contrast(self):

        """Stretch contrast of the final image.

        Normalize all 3 color channels to the global intensity
        maximum.

        """

        norm = self.image[...,:-1].max()
        self.image[...,:-1] /= norm

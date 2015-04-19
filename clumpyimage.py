"""ClumpyImage class represents a CLUMPY model image cube. Can be used
with compositing.py. See compositing.ipynb for an exampele."""

__author__ = "Robert Nikutta <robert.nikutta@gmail.com"
__version__ = "2015-04-19"

from compositing import FitsFile, Cube
import numpy as N

class ClumpyImage(FitsFile,Cube):

    """Load data from a Clumpy FITS image file.

    Description
    -----------
    Loads the slices of the data cube from the primary HDU of a Clumpy
    FITS image file. The primary HDU holds brightness distrubutions at
    given wavelengths (the z-axis of the cube).

    Parameters
    ----------
    path : str
        Path to a Clumpy FITS file

    slices : None, or list or 1D array of integers, or single integer
        (Pythonic) index of FITS slice to fetch from fitsfile. If
        none, the entire data cube from the FITS file will be
        returned. If single integer, one slice will be returned.

    return_fullsize : bool
        If true, and the data cube in the FITS file was half-sized (nx
        != ny), then the cube will be mirrored to the left, and a
        full-sized cube will be returned.

    flip_y : bool
        If true, the cube will be flipped in the y-direction (In FITS
        images, the rows are counted from to bottom, but Numpy arrays
        count the opposite way.

    """

    def __init__(self,path,return_fullsize=True,flip_y=True,slices=(0,1,2)):

        FitsFile.__init__(self,path)

        self.slices = slices
 
        # mirror columns, giving full-sized CLUMPY image instead of half-sized
        if return_fullsize:
            if self.nx != self.ny:
                self.data = self.fullsize_img(self.data)
                # print "fullsize: data.shape: " , data.shape
            else:
                pass  # in this case the image was already square. Silently ignore the request to mirror.

        # flip rows of cube (up-down flip)
        if flip_y:
            self.data = self.yflip(self.data)

        Cube.__init__(self,self.data,self.slices)


    def yflip(self,img):
        """Flip a 3D datacube (nz,ny,nx) along its y-dimension."""

        if img.ndim == 3:
            return img[:,::-1,:]
        else:
            raise Exception, "Supplied data cube must have 3 axes, but has %d" % img.ndim


    def fullsize_img(self,hsimg):
        """Turn half-size Clumpy image cube into a full-sized one.

        The full-size output cube will have the half-sized data (hsimg)
        mirrored along the x-axis to the left. The very first y-column of
        hsimg will be re-used, i.e. in the full-sized image it will occur
        only once.

        hsimg has shape (nz,ny,nx), where ny and nx are odd. The return
        array will be of shape (nz,ny,2*nx-1), i.e. ny and nx still odd.

        hsimg must have 3 axes.
        """

        print "in fullsize_img: hsimg.shape = ", hsimg.shape

        if hsimg.ndim == 3:
            return N.dstack((hsimg[:,:,:0:-1],hsimg))
        else:
            raise Exception, "Supplied data cube must have 3 axes, but has %d" % hsimg.ndim

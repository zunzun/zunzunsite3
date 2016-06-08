



# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 09:24:01 2014

@author: Sukhbinder Singh

Fig to data
http://www.icare.univ-lille1.fr/wiki/index.php/How_to_convert_a_matplotlib_figure_to_a_numpy_array_or_a_PIL_image
"""


import numpy
import PIL

 
def fig2data ( fig ):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw ( )
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = numpy.fromstring ( fig.canvas.tostring_argb(), dtype=numpy.uint8 )
    buf.shape = ( w, h,4 )
 
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll ( buf, 3, axis = 2 )
    return buf
    

 
def fig2img ( fig ):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data ( fig )
    w, h, d = buf.shape
    im=PIL.Image.frombytes( "RGBA", ( w ,h ), buf.tostring())
    return im.convert(mode="RGB")



if __name__ == '__main__':
# Demo Generate a figure with matplotlib and make it as gif
    from images2gif import writeGif
    import matplotlib.pyplot as plt
    
    figure = plt.figure()
    plot   = figure.add_subplot (111)
    
    plot.hold(False)
    # draw a cardinal sine plot
    images=[]
    y = numpy.random.randn(100,10)
    for i in range(y.shape[1]):
        plot.plot (y[:,i])  
        plot.set_ylim(-3.0,3)
        plot.text(90,-2.5,str(i))
        im = fig2img(figure)
        images.append(im)

    writeGif("images.gif",images,duration=0.5,dither=0)

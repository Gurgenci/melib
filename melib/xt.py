"""
    **xt.py**

    Routines to create markdown documents for Jupyter notebooks, PDF files, and some other useful stuff
"""

import pylatex
import matplotlib
#from pylatex.utils import italic, bold
from datetime import date
from pylatex import Document, PageStyle, Head, LineBreak, simple_page_number,\
Foot, MiniPage, LargeText, MediumText, Section, Subsection, Math, Alignat
#, , , Tabular, , TikZ, Axis, \
#     Plot, Figure, Matrix, , Quantity, , , \
#     
# import matplotlib.image as mpimg
import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import glob
from zipfile import ZipFile
from shutil import copyfile
#
WINDOWS = True  # If you are not using WINDOWS, make this False
#
EXAMPLE=False

def iswindows(q):
    global WINDOWS
    WINDOWS = q  # True or False; will be set at the notebook entry

# Combine the folder and the file names into a single path string
# This will be differently for MAC and WINDOWS
# The foldername is from the root folder for the zip file pack I distribute
# There are no back or forward slashes in the folder name, e.g. "pics"


def ff2p(foldername, filename):
    if WINDOWS:
        return foldername+"\\"+filename
    else:
        return foldername+"/"+filename
# ZIP functions will only run on my computer


def mdzip(zipfile, listfile):
    """ Creates a zip archive of all components used in the notebook

    Args:
        zipfile  : The name of the zip file to be created
        listfile : The text file containing the file names to be archived (optional)

    For example,
        mdzip("L10") -- Will archive the list in "L10_zip.txt" into "L10.zip" 
        mdzip("xxxx", "zzzz.txt") -- Will archive the list in "zzzz.txt" into "xxxx.zip"
    """

    def my_makezip(ziplist, zipfile=None):
        libfolder = r"H:\My Documents\python"
        libraryfiles = ["xt.py", "excel.py", "library.py"]
        zipobj = ZipFile(zipfile+".zip", 'w')
        for f in ziplist:
            if f != "":
                if f in libraryfiles:
                    copyfile(libfolder+r"\%s" % f, f)
                    zipobj.write(f)
                    os.remove(f)
                else:
                    zipobj.write(f)
        zipobj.close()
#
    if listfile==None:
        listfile=zipfile+"_zip.txt"
    fdx = open(listfile)
    ziplist = fdx.read().split("\n")
    my_makezip(ziplist, zipfile)


FZIP = None
NOTEBOOK = ""
ZIPFILES = []
EQNUMS={}  # Equation References


def mdxziplist(files):
    """ It adds `files` to the zip listfile (see mdzip())

    Args:
        files (string array): Names of files to archive, e.g. `["xt.py", "dat\\mats.xlsx"]`

    """
    if FZIP != None:
        for f in files:
            if not f in ZIPFILES:
                ZIPFILES.append(f)
                if os.path.exists(f) or True:
                    FZIP.write(f)
                    FZIP.write("\n")


def mdxzipopen(notebook, libfiles):
    """ Creates the zip file list and insert the 'libfiles' into it

    Args:
        notebook : Usually the name of the notebook but could be any string, e.g. "L20"
        libfiles : File names as an array of strings, e.g. ["xt.py", "excel.py"]

    The name of the list file will be `notebook+"_zip.txt"`
    """

    global FZIP, ZIPFILES
    FZIP = open(NOTEBOOK+"_zip.txt", "w")
    ZIPFILES = []
    filelist = libfiles+[notebook+".ipynb", notebook+".html"]
    if os.path.exists("common.py"):
        filelist += ["common.py"]
    popfile = notebook+"_pop.txt"
    if os.path.exists(popfile):
        filelist += [popfile]
    for f in filelist:
        FZIP.write(f)
        FZIP.write("\n")


def mdxzipclose():
    """ Do not use this function.
        It adds double back slash to the zip list file and it confuses zip file creation
    """

    if FZIP != None:
        FZIP.close()

# Do not use this function because it adds double back slash to the zip list file,
#  which confuses zip file creation


def img2zip(img):
    top = "../"
    if top in img:
        s = img.split(top)[1]
        mdxziplist([s])
    else:
        mdxziplist([img])


def imgshow(imgfile, s=""):
    img2zip(imgfile)
    if s == "":
        s = imgfile
    return '<img src="%s" alt="%s">' % (imgfile, s)


def urlref(url, title, hover=""):
    if hover == "":
        hover = title
    return '<a href="%s" target="_blank" title="%s">%s</a>' % (url, title, hover)


def imgref(imgfile, imgtext):
    #    img2zip(imgfile)
    return '<a href="%s" onclick="javascript:void window.open(\'%s\',\'1556185057675\',\
\'width=600,height=300,toolbar=0,menubar=0,location=0,status=1,scrollbars=0,resizable=1,left=300,top=300,fullscreen=0\');\
return false;">%s</a>' % (imgfile, imgfile, imgtext)
#    return '<a href="%s" onclick="javascript:void window.open(\'%s\',\'1556185057675\',\
# \'toolbar=0,menubar=0,location=0,status=1,scrollbars=0,resizable=1,left=300,top=300,fullscreen=0\');\
# return false;">%s</a>'%(imgfile, imgfile, imgtext)

# Example 's'
#  When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
#  $$x = {-b \pm \sqrt{b^2-4ac} \over 2a}.$$


def sjax(stext):
    if stext == "":
        return '\
<!DOCTYPE html>\
<html>\
<head>\
  <meta charset="utf-8">\
  <meta name="viewport" content="width=device-width">\
  <title>MathJax</title>\
  <script type="text/javascript" async\
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML" async>\
</script>\
</head>\
<body>'
#
    s = '\
<!DOCTYPE html>\
<html>\
<head>\
  <meta charset="utf-8">\
  <meta name="viewport" content="width=device-width">\
  <title>MathJax</title>\
  <script type="text/javascript" async\
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML" async>\
</script>\
</head>\
<body>\
<p>%s\
</p>\
</body>\
</html>' % stext
    return s


def openplot(figno, aspect=[]):
    """
    Arguments
        `figno` : Figure numbers

        `aspect` : Aspect ratio, e.g. 0.5 for a rectangle width=2*height
        
        
    Returns (f1, ax)
    
        f1 = Pointer to the figure (can be used to save the figure, e.g. f1.savefig("myfigure.png") 
        
        ax = Pointer to the plot axes (use this to plot, e.g. ax.plot((x, y, "r", label="Y")))

    **Example**
        
        >>> x=np.arange(0,10,0.01)
        >>> y=np.sin(x)
        >>> (f1,ax)=openplot(1,0.5)
        >>> ax.plot(x,y,"m",label="sine")
        >>> plotanno(ax,xlabel="X variable", ylabel="sin(x)", xlim=[1,9], ylim=[0, 1.0], grid="on", legendloc="upper right", title="Example - y=sin(x)")
        
    """
    
    
    plt.close(1)
#    f1=plt.figure()
    if aspect != []:
        w, h = plt.figaspect(aspect)
        f1 = plt.figure(figsize=(w, h))
    else:
        f1 = plt.figure()
    ax = f1.add_subplot(111)
    return (f1, ax)
# For example
#    (fig,ax)=openplot(1)
#    ax.plot(x, y, "r", label="Y")
#    ax.plot(x, z, "b", label="Z")
#    plotanno(ax,xlabel="Length, m", ylabel="Temperatures", legendloc="upper right")
#    fig.savefig(filename)
#


def plotanno(ax, xlabel="", ylabel="", xlim=[], ylim=[], grid="on",
             legendloc="", title=""):
    """ 
        For the matplotlib figure axis pointer ``ax``:
            Add axis labels (``xlabel`` and ``ylabel`` )
            Axis limits, e.g. ``xlim`` (=``[xmin, xmax]`` )
            Location for the legend , eg "upper right"
            Turn the grid lines on and off
            and a figure title
            
        **Example**
        
        >>> x=np.arange(0,10,0.01)
        >>> y=np.sin(x)
        >>> (f1,ax)=openplot(1,0.5)
        >>> ax.plot(x,y,"m",label="sine")
        >>> plotanno(ax,xlabel="X variable", ylabel="sin(x)", xlim=[1,9], ylim=[0, 1.0], grid="on", legendloc="upper right", title="Example - y=sin(x)")

            
    """
    if ylim != []:
        ax.set_ylim(ylim)
    if xlim != []:
        ax.set_xlim(xlim)
    if xlabel != "":
        ax.set_xlabel(xlabel)
    if ylabel != "":
        ax.set_ylabel(ylabel)
    if grid != "":
        if grid == "on" or grid == "off":
            ax.grid(grid)
        else:
            ax.grid(True, grid)
    if legendloc != "":
        ax.legend(loc=legendloc)
    if title != "":
        ax.set_title(title)
# EXAMPLE="openplot"
if EXAMPLE=="openplot":
    x=np.arange(0,10,0.01)
    y=np.sin(x)
    (f1,ax)=openplot(1,0.5)
    ax.plot(x,y,"m",label="sine")
    plotanno(ax,xlabel="X variable", ylabel="sin(x)", xlim=[1,9], ylim=[0, 1.0], grid="on", legendloc="upper right", title="Example - y=sin(x)")


def saveplot(fig, folder, filename):
    plotfilename=ff2p(folder, filename)
    fig.savefig(plotfilename)
    return plotfilename



def imgplot(X, Y, XXYY, cs='b-', imgfile="", ax=[], xticks=[], yticks=[]):
    """ 
        This function is used to superimpose my curve on a chart image from
        a reference.  The image should be the box only.

        ``X`` , ``Y``   The data to be plotted (the same units as on the chart image)
        
        ``XXYY``        The axis limits [[xmin, xmax], [ymin, ymax]] (from the reference image)
        
        ``cs``          Plot line descriptor, e.g. ``"b--"``
        
        ``imgfile``     The name of the output, e.g. ``r"pics\Meshram_Fig6b.png"``
        
        ``ax``          This should not be included at first call.  It is used to add curves later.
        
        ``xticks``      x-axis tick positions you want to see, e.g. ["4000", "midpoint", "26000"]
        
        ``yticks``      y-axis tick positions, e.g. ["ten", "forty", "seventy", "hundred"]
        

        The function returns ``(figno, ax)``. 
        The ``ax`` can be used to add more y(x) curves:

            e.g. imgplot(X2, Y2, XXYY, "r--", ax=ax)
            
            The ``XXYY`` in the second call should be the same as in the first
            
            The ``ax`` in the second call is the same 'ax' returned by the first call

        The ``figno`` can be used by the calling figure to save or to clear the figure

    **Example**

        >>> x = np.log10(np.arange(10, 10000, 100))
        >>> y = x-np.log10(1.0)
        >>> XXYY = [[1, np.log10(50000.0)], [-2, 4]]
        >>> (f, ax) = imgplot(x, y, XXYY, cs='r-',imgfile=r"ashby_strength_density_chart_no_axes.png",xticks=[10, "mid", 100], yticks=[0.01, 10000])
        >>> imgplot(x, x-np.log10(2.0), XXYY, 'b', ax=ax)
        >>> imgplot(x, x-np.log10(10.0), XXYY, 'k', ax=ax)
        >>> plt.show()

    This example draws lines on the following reference chart:
        
        .. image::  ../../assets/ashby_strength_density_chart.png
        
    To create the following plot:
        
        .. image:: ../../assets/imgplot.png
    
    """
    def ptransform(XY, XXYY, xxyy):
        X1 = XXYY[0][0]
        X2 = XXYY[0][1]
        Y1 = XXYY[1][0]
        Y2 = XXYY[1][1]
        x1 = xxyy[0][0]
        x2 = xxyy[0][1]
        y1 = xxyy[1][0]
        y2 = xxyy[1][1]
        X = XY[0]
        Y = XY[1]
        x = (X-X1)/(X2-X1)*(x2-x1)+x1
        y = y2-(Y2-Y)/(Y2-Y1)*(y2-y1)
        return (x, y)
    if ax == []:
        img = matplotlib.image.mpimg.imread(imgfile)
        f1 = plt.figure()
        ax = f1.add_subplot(111)
        ax.imshow(img)
    else:
        f1 = plt.gcf()
    (y1, y2) = ax.get_ylim()
    (x1, x2) = ax.get_xlim()
    xxyy = [(x1, x2), (y1, y2)]
    (x, y) = ptransform((X, Y), XXYY, xxyy)
    ax.plot(x, y, cs)
    if xticks != []:
        n = len(xticks)
        xtickpos = np.zeros(n)
        dx = (x2-x1)/(n-1)
        for k in range(0, n):
            xtickpos[k] = k*dx
#        ax.set_xticks([x1, x2])
        ax.set_xticks(xtickpos)
        ax.set_xticklabels(xticks)
    if yticks != []:
        n = len(yticks)
        ytickpos = np.zeros(n)
        dy = abs(y2-y1)/(n-1)
        for k in range(0, n):
            ytickpos[k] = y1-k*dy
        ax.set_yticks(ytickpos)
        ax.set_yticklabels(yticks)
    return (f1, ax)


if False:  # Test
    x = np.log10(np.arange(10, 10000, 100))
    y = x-np.log10(1.0)
    XXYY = [[1, np.log10(50000.0)], [-2, 4]]
    (f, ax) = imgplot(x, y, XXYY, cs='r-',
                      imgfile=r"H:\My Documents\_Acad\courses\mech2100\2020\web" +
                      "\\pics\\ashby_strength_density_chart_no_axes.png",
                      xticks=[10, "mid", 100], yticks=[0.01, 10000])
    imgplot(x, x-np.log10(2.0), XXYY, 'b', ax=ax)
    imgplot(x, x-np.log10(10.0), XXYY, 'k', ax=ax)
    plt.show()


def poptext(s):  # Process pop text, e.g. equations etc
    sa = s.split('"')
    if len(sa) < 2:
        return s
    sout = sjax("")
    for i in range(1, len(sa), 2):
        sout += sa[i-1]+sa[i]
    sout += sa[len(sa)-1]
    return sout


def eqnumber(s):
    return EQNUMS[s]

class mdx:
    """ 
        ``mdx`` is a pointer to a markdown file.  I use it in creating lecture
        notes.  A typical notebook have an iniialisation cell and then several
        chapter cells.  
        
        The structures for these cells are given below.  Create a notebook 
        named "XXXX.ipynb" and copy and paste the following code segments 
        into that notebook as separate cells to create an example notebook 
        generated using the ``mdx`` class.
        
        **Why should you use `` mdx `` ?**
        
        I found it clumsy to create markdown files with interactive live 
        python code snippets in it when using standard markdown only.
        
        Using the class ``mdx``, all cells in the notebook 
        can be code cells and the whole notebook can run as a single program.
        
        The cell contents are created by using the ``mdx.write()`` method.  There 
        are special codes starting with ``:::`` that can indicate headers, equations, 
        insert images, and many other things.  See the write-up for the ``write`` 
        method.
        
        **Initialisation Cell**
        
        This will be the first cell in the ``ipynb`` file and it will have the 
        following structure.  This is initialisation for a notebook with three chapter
        cells and one reference cell at the end.
            
        .. code-block:: python

            import math
            import numpy as np
            from IPython.display import Markdown as md
            import matplotlib.pyplot as plt
            import random
            import sys
            import os
            from datetime import datetime, date
            # import other packages as required
            # ...
            # ...
            Chapter="XXXX"  # or any other name
            YEAR=2021
            TOC=["Chapter 1", "Chapter 2", "Chapter 3", "References"]
            #
            SECTION=0
            MAKEZIP=True  # A zip file will be generated  (False otherwise)
            #
            # Module libraries
            sys.path.insert(0,r"H:\My Documents\python")  # provide full path
            sys.path.insert(0, r"H:\My Documents\melib_project\melib")  # provide full path
            #
            from xt import mdx, engfmt, mdxzipopen, mdzip, iswindows, openplot, plotanno
            from excel import Xcel
            LIBFILES=["xt.py", "library.py", "excel.py"]
            #
            if MAKEZIP: mdxzipopen(Chapter, LIBFILES)
            #
            MD=mdx(Chapter,0,title="Example Notebook")  # The markdown file pointer
            MD.write("Created on 6 April 2021.   Last Update - "+date.today().strftime("%d/%m/%Y"))
            MD.toc(TOC,"")  # Creates the table contents
            MD.write("* The notebook source file is `%s.ipynb`"%Chapter)
            #
            md(MD.out())  # End of the initiation segment

        The following is what you need to generate an HTML page from this notebook.
        
        ::
            
            jupyter nbconvert XXXX.ipynb --no-input --to html
            
        
        **Chapter 1**
        
        This is the first chapter in the notebook following the initial cell. 
        All contents will be inserted using the ``MD.write()`` function.

        .. code-block:: python

            SECTION+=1
            MD=mdx(Chapter, SECTION, TOC[SECTION-1])  # create the chapter file
            MD.write("\\n\\n")
            MD.write("... blah blah blah :::")
            MD.write("... even more blah blah blah :::")
            MD.write("\\n\\n")
            md(MD.out())            # close the chapter file
            
        **Chapter 2**
        
        This is the second chapter in the notebook following the initial cell. 
        All contents will be inserted using the ``MD.write()`` function.

        .. code-block:: python

            SECTION+=1
            MD=mdx(Chapter, SECTION, TOC[SECTION-1])  # create the chapter file
            MD.write("\\n\\n")
            MD.write("... blah blah blah :::")
            MD.write("... even more blah blah blah :::")
            MD.write("\\n\\n")
            md(MD.out())            # close the chapter file
            
        **Chapter 3**
        
        This is the third chapter in the notebook following the initial cell. 
        All contents will be inserted using the ``MD.write()`` function.

        .. code-block:: python

            SECTION+=1
            MD=mdx(Chapter, SECTION, TOC[SECTION-1])  # create the chapter file
            MD.write("\\n\\n")
            MD.write("... blah blah blah :::")
            MD.write("... even more blah blah blah :::")
            MD.write("\\n\\n")
            md(MD.out())            # close the chapter file
            
        One can have an arbitrary number of chapters.  It is preferred to 
        complete with one last segment on references:

        **The last content cell that contains the bibliography (optional)**
        
        ::
        
            SECTION=len(TOC)
            MD=mdx(Chapter, SECTION, TOC[SECTION-1])
            MD.write("Robert L. Mott, MECH2100 Machine Design (Custom Edition)\\n\\n")
            MD.write("Ashby, M.F., 2011.   Materials selection in mechanical design, Butterworth-Heinemann, Oxford, OX ; Boston, MA . \
            (Electronic resource, Call Number:TA403.6 .A74 2011eb )\\n\\n")
            MD.write("Standards Australia, 1993.  Engineering Drawing Handbook SAA HB7, Standards Association of Australia, (Call Number:T357 .M43 1993 )\\n\\n")
            md(MD.out())
            
        Read the following information on the `` write()`` method to see how you can 
        generate cells with interesting content.

    """
    Fdx = 0
    MDFile = ""
    OutputFile = ""
    Page = 1
    Initial = ""
    PageNpop = 0
    EQN = 0
    FIG = 0
    spop = ""
    mpl_backend_ = 0
    POPUPWINDOW_NUMBER = 0

    def __init__(self, notebook, page=1, title="", initial=""):
        global NOTEBOOK
        self.MDFile = notebook+".ipynb"
        NOTEBOOK = notebook
        self.OutputFile = "tmp/%s%d.md" % (notebook, page)
        self.Fdx = open(self.OutputFile, "w")

        self.Page = page
        if title != "":
            # self.Fdx.write('<a id="Page%d"></a>\n\n# %s\n\n'%(page, title))
            self.Fdx.write("# %s #\n\n" % (title))
        else:
            self.Fdx.write("\n")
        self.EQN = 0
        self.FIG = 0
        self.PageNpop = 0
        if initial == "":
            self.Initial = notebook[0]
        else:
            self.Initial = initial
        import matplotlib as mpl
        self.mpl_backend_ = mpl.get_backend()
        mpl.use("Agg")  # Prevent showing stuff
        if not os.path.exists("pop"):
            os.makedirs(ff2p(".", "pop"))
        if not os.path.exists("tmp"):
            os.makedirs(ff2p(".", "tmp"))

    def toc(self, sa, date=""):
        global POPUPWINDOW_NUMBER
        POPUPWINDOW_NUMBER = 0
        self.Fdx = open(self.OutputFile, "a")
        self.Fdx.write("#### Table of Contents ####\n\n")
        if date!="":
            self.Fdx.write("_%s_\n\n"%date)
        self.Fdx.write("\
|Section|Title|\n\
|:------|:-------|\n")
        k = 1
        for s in sa:
            # self.Fdx.write("|%d|%s|\n"%(k,s))
            self.Fdx.write("|%d|%s|\n"
                           % (k, '<a href="#%s">%s</a>' % (s.replace(" ", "-"), s)))
            k += 1
        # self.Fdx.write("| |References|\n\n")
        self.Fdx.write("\n\n")
        self.Fdx.close()
        #

    def heading(self, s, level):
        self.Fdx = open(self.OutputFile, "a")
        if level == "first":
            s = s.split(" ")
            self.Fdx.write("**%s** " % s[0])
            for j in range(1, len(s)):
                self.Fdx.write(" "+s[j])
        else:
            self.Fdx.write(level*"#"+" %s" % (s))
        self.Fdx.write("\n\n")
        self.Fdx.close()

    def tabulatedata(self, data, nd):
        self.write("|Parameter|Value|\n|:---|:---|\n")
        for (n, key) in zip(nd, data.keys()):
            if key == "SEPARATOR":
                self.write("|...|...|\n")
            else:
                if n == 'S':
                    s = data[key]
                else:
                    sf = ("%%.%df" % (int(n)))
                    s = sf % data[key]
                self.write("|%s|%s|\n" % (key, s))
        self.write("\n")

    def weq(self, s):
        self.EQN += 1
        eqno = "`%d.%d`" % (self.Page, self.EQN)
        self.write("%s : " % eqno+s)
        return(eqno)

    def seq(self, n=0):  # Set the equation number
        self.EQN = n

    def wfig(self, s):
        if s == "":
            return s
        self.FIG += 1
        figno = "%d.%d" % (self.Page, self.FIG)
        self.write("\n\n<i>Figure %s. %s</i>\n\n" % (figno, s))
        return(figno)

    def setpage(self, n):  # Set the section (page) number
        self.Page = n

    def oldwrite(self, s):
        self.Fdx = open(self.OutputFile, "a")
        self.Fdx.write(s)
        self.Fdx.close()

    def write(self, s):
        """ 
            This is the main method to populate the MDX notebook cells.  Apart
            from the code segments, the string ``s`` is copied to the markdown 
            file.  The code segments start with ``:::`` and end with ``::``

            They are of the following format:
                
                ``:::code|arg1|arg2::``
                    
            where
            
                ``code`` a number that defines the action
                
                ``arg1`` the first argument
                
                ``arg2`` the second argument
                
            The following lists what is available through this construct:
                
            **:::2**
                
            ``:::2|HTML link|text::``  The markdown document will display 
            ``text`` that will link to the address defined in the first argument
            
            *Code 2 Example:*
            
                ``:::2|www.uq.edu.au|University of Queensland::``
                
            **:::3**
            
            ``:::3|filename|caption::`` will display the image in the first 
            argument.
            
            The image file is expected to be in the ``pics`` folder.
            
            The figure numbers are automatically incremented.  The 
            second argument is optional.  If omitted, then only the figure number 
            will be shown:
                
            *Code 3 Examples*
            
            ``:::3|mohrcircle.png|Mohr's circle::``  # with caption text
            ``:::3|mohrcircle.png::``                # no caption

            **:::30**
            
            Similar to **:::3** except that the image file is expected to be in the ``tmp`` folder.

            **:::32**
            
            Similar to **:::3** except that the image file is expected to be in the ``..\\pics`` folder. 
            This is useful when several notebooks use the same picture collection in the parent folder.
                            
            **:::4**
            
            ``:::4|filename|cover text::`` the cover text will be a link to a pop-up window 
            
            The image file is expected to be in the ``pics`` folder.

            *Code 4 Examples*
            
            ``:::4|mohrcircle.png|Click to see Mohr's circle::``  # pop=up figure.  The second argument is the cover text.

            **:::42**
            
            Similar to **:::4** except that the image file is expected to be in the ``..\\pics`` folder. 
            This is useful when several notebooks use the same picture collection in the parent folder.
                            
            **:::5**
            
            ``:::5|equation|equation name::`` The equation name can later be used to refer to this equation by number 
            by using the ``eqnumber()`` function or :::6 command.  The equation name may be left out.

            *Code 5 Examples*
            
            ``:::5|$sin^2(x)+cos^2(x)=1$|trig::``

            ``:::5|F=ma|Newton::``

            ``:::5|$y=x^2$::``

                            
        """
        self.Fdx = open(self.OutputFile, "a")
        tokens = s.split("::")
        n = len(tokens)
        for i in range(0, n):
            z = tokens[i]
            if z != "" and z[0] == ":" and n > 1:
                # print("%02d: %s"%(i,z))
                a = z[1:].split("|")
                fnum = int(a[0])
                sf = "*** Unknown MD.write code (%d) ***" % fnum
                if len(a) == 3:
                    arg2 = a[2]
                else:
                    arg2 = ""
                if fnum == 1:  # Fpopup from the file MD.txt
                    if len(a) == 4:
                        sf = self.fpopup(int(a[1]), a[2], vars=a[3])
                    else:
                        sf = self.fpopup(int(a[1]), a[2])
                elif fnum == 2:  # reference to a web site
                    sf = urlref(a[1], a[2])
                elif fnum == 3 or fnum == 30 or fnum == 32:
                    if fnum == 3:  # show image  from pics folder
                        sf = "![alt text](pics/%s '%s')" % (a[1], a[1])
                        mdxziplist(["pics\\"+a[1]])
                    elif fnum == 30:  # show image from the tmp folder
                        sf = "![alt text](tmp/%s '%s')" % (a[1], a[1])
                    # show image from ../pics folder (used in the pages)
                    elif fnum == 32:
                        sf = "![alt text](../pics/%s '%s')" % (a[1], a[1])
                    self.FIG += 1
                    figno = "%d.%d" % (self.Page, self.FIG)
                    if arg2!="NONE":
                        sf += "\n\n<i>Figure %s. %s</i>\n\n" % (figno, arg2)
                elif fnum == 4 or fnum == 42:  # image pop up (pics folder)
                    if fnum == 4:
                        sf = imgref("pics/%s" % a[1], a[2])
                        mdxziplist(["pics"+chr(92)+a[1]])  # chr(92)="\\"
                    # show image from ../pics folder (used in the pages)
                    elif fnum == 42:
                        sf = imgref("../pics/%s" % a[1], a[2])
                        mdxziplist(["../pics"+chr(92)+a[1]])  # chr(92)="\\"
                elif fnum == 5:  # Equation line
                    self.EQN += 1
                    eqnum="`%d.%d`" % (self.Page, self.EQN)
                    sf = "\n\n" + eqnum+ " : " +a[1]
                    if len(a)==3:
                        global EQNUMS
                        EQNUMS[a[2]]=eqnum
                elif fnum == 6:  # Refer to the equation by number
                    sf=eqnumber(a[1])
                    print(sf)
                elif fnum == 7:   # Summary pop-up for the section below
                    covertext = "&#8595"
                    if len(a) == 3:
                        sf = self.fpopup(a[1], covertext, vars=a[2])
                    else:
                        sf = self.fpopup(a[1], covertext)
                # just pop-up text a[1]=covertext; a[2]:pop-up
                elif fnum == 8 or fnum == 80:
                    if fnum == 8:
                        sf = self.fpopup(a[2], a[1])
                    elif fnum == 80:
                        sf = self.jpopup(a[2], a[1])
                elif fnum == 9:  # link to anchor a[1]:anchor; a[2]:cover text
                    sf = urlref("#"+a[1], a[2])
                elif fnum == 10:  # quote
                    sf = ">"+a[1]+""
                elif fnum == 11:  # Heading
                    if len(a) == 3:
                        level = int(a[2])
                    else:
                        level = 2
                    sf = level*"#"+" %s" % (a[1])
                self.Fdx.write(sf)
            else:
                self.Fdx.write(z)
        self.Fdx.close()

    def note(self, s):
        self.Fdx = open(self.OutputFile, "a")
        self.Fdx.write("<i>"+s+"</i>")
        self.Fdx.close()

    def quote(self, s, source=""):
        self.Fdx = open(self.OutputFile, "a")
        self.Fdx.write(">"+s+"")  # The first '>' means indent
        if source == "":
            self.Fdx.write("\n\n")
        else:
            self.Fdx.write("%s\n\n" % cite(source))
        self.Fdx.close()

    def cb(self, bn, debug=False):
        if debug:
            print("CB in debug mode\n")
#        return
        s = "#:%05d" % bn
        filename = self.MDFile
        if debug:
            print("Will now open the file '%s' and search for '%s'" %
                  (filename, s))
        f = open(filename, "r")
        contents = f.read()
        scb = ""
        z = contents.split(s)
        if debug:
            print("Size of z = %d\n" % len(z))
            for i in range(0, len(z)):
                print("z[%d] length = %d\n" % (i, len(z[i])))
        v = z[1].split("\n")
        scb += "``` python\n"
        for line in v:
            z = line.split("\\n")
            z = z[0]
            if z == "":
                continue
            z = z.lstrip()
            if z[0] == '"':
                ss = "\n"+z[1:]
            else:
                ss = "\n"+z
            scb += ss
        scb += "```\n\n"
        self.write(scb)
    #    return v

    def page(self):
        return self.Page

    def out(self, onesection=0):
        if onesection > 0 and onesection != self.Page:
            #            print(onesection, self.Page)
            return ""
        import matplotlib as mpl
        mpl.use(self.mpl_backend_)  # Reset backend
        f = open(self.OutputFile, "r")
        return (f.read()+"\n\n\n\n")

    def pops(self, filecontents, linkname, filename=None):
        if filename == None:
            filename = "%s%03d%03d" % (self.Initial, self.Page, self.PageNpop)
            self.PageNpop += 1
        fdx = open(ff2p("pop", "%s" % filename+".html"), "w")
        fdx.write(filecontents)
        fdx.close()
        self.spop = "<a href=\"./pop/%s.html\" onclick=\
\"javascript:void window.open('./pop/%s.html','1556185057675',\
'width=600,height=300,toolbar=0,menubar=0,\
location=0,status=1,scrollbars=0,resizable=1,left=300,top=300,fullscreen=0');\
return false;\">%s</a>" % (filename, filename, linkname)
        return self.spop

    def readpoptext(self, tnum):
        textfile = (self.MDFile).split(".")[0]
        fdx = open(textfile+"_pop.txt", "r")
        contents = fdx.read()
        sa = contents.split("::")
        n = len(sa)
    #     print(n)
        for i in range(1, n, 2):
            num = int(sa[i])
    #         print("%d:%s"%(num,sa[i+1]))
            if num == tnum:
                break
        s = sa[i+1]
        fdx.close()
        return s[0:-1]

    def fpopup(self, tnum, covertext, vars=[""]):
        global POPUPWINDOW_NUMBER
        POPUPWINDOW_NUMBER += 1
        function_name = "myFunction%03d" % POPUPWINDOW_NUMBER
        if type(tnum) == int:
            s = self.readpoptext(tnum)
        else:
            s = tnum
        # Now check if there are any variables:
        sa = s.split("||")
        # print(sa)
        n = len(sa)
        sout = ""
        k = 0
        j = 0
        while j < n:
            # print(sa[j])
            #            sout+=poptext(sa[j])
            sout += sa[j]
            # print(sout)
            j += 1
            if j < (n-1):
                sout += vars[k]
                # print(sout)
                j += 1
                k += 1
        spopup = '\
<html>\
<script>\
function %s() {\
 var myWindow = window.open("", "MsgWindow", "width=300, height=300, left=50, top=300");\
  myWindow.document.write("%s");\
}\
</script>\
<style>\
.btn {\
 border:2px solid black;\
 padding: 1px 1px;\
 }\
.info {\
  border-color: #e7e7e7;\
  color: dodgerblue;\
}\
</style>\
<button class="btn info" onclick="%s()" >%s</button></html>\
' % (function_name, sout, function_name, covertext)
#<button class="btn info"; "onclick="%s()" >%s</button></html>\
#
        return spopup

    def jpopup(self, tnum, covertext, vars=[""]):  # This is not working
        global POPUPWINDOW_NUMBER
        POPUPWINDOW_NUMBER += 1
        function_name = "myFunction%03d" % POPUPWINDOW_NUMBER
        if type(tnum) == int:
            s = self.readpoptext(tnum)
        else:
            s = tnum
        # Now check if there are any variables:
        sa = s.split("||")
        n = len(sa)
        sout = ""
        k = 0
        j = 0
        while j < n:
            sout += sa[j]
            j += 1
            if j < (n-1):
                sout += vars[k]
                j += 1
                k += 1
        jaxstring = '<script type="text/javascript" async\
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML" async>\
</script>'+sout
        spopup = '\
<html>\
<script>\
function %s() {\
 var myWindow = window.open("", "MsgWindow", "width=300, height=300, left=50, top=300");\
  myWindow.document.write("%s");\
}\
</script>\
<button onclick="%s()">%s</button></html>\
' % (function_name, jaxstring, function_name, covertext)
#
        return spopup

    def fpop2spop(self, tnum, covertext, vars=[""]):
        textfile = (self.MDFile).split(".")[0]
        fdx = open(textfile+"_pop.txt", "r")
        contents = fdx.read()
        sa = contents.split("::")
        n = len(sa)
    #     print(n)
        for i in range(1, n, 2):
            num = int(sa[i])
    #         print("%d:%s"%(num,sa[i+1]))
            if num == tnum:
                break

        s = sa[i+1]
        fdx.close()
#
        popfile = textfile+"pop%d.html" % tnum
        fdx = open(ff2p("pop", popfile), "w")
        # Now check if there are any variables:
        sa = s.split("||")
        # print(sa)
        n = len(sa)
        sout = ""
        k = 0
        j = 0
        while j < n:
            # print(sa[j])
            sout += poptext(sa[j])
            # print(sout)
            j += 1
            if j < (n-1):
                sout += vars[k]
                # print(sout)
                j += 1
                k += 1
        fdx.write(poptext(sout))
        fdx.close()
        self.spop = "<a href='./pop/%s' onclick=\
    \"javascript:void window.open('./pop/%s','1556185057675',\
    'width=600,height=300,toolbar=0,menubar=0,\
    location=0,status=1,scrollbars=0,resizable=1,width=600, height=300, left=300,top=300,fullscreen=0');\
    return false;\">%s</a>" % (popfile, popfile, covertext)
        return self.spop

    def fpop(self, tnum, covertext, vars=[""]):
        self.fpop2spop(tnum, covertext, vars=vars)
        self.wpop()

    def pop(self, filecontents, linkname, filename=None):
        self.pops(filecontents, linkname, filename)
        self.wpop()

    def wpop(self, s=None):
        if s == None:
            s = self.spop
        self.write(s)

    def popimage(self, imagefile, referral, filename=None):
        self.pop("<img src='..\\pics\\%s'>" % imagefile, referral, filename)
        mdxziplist(['..\\pics\\%s' % imagefile])

    def popfile(self, referral, filename):
        if not ("." in filename):
            filename += ".html"
        self.write("<a href=\"./pop/%s\" onclick=\
\"javascript:void window.open('./pop/%s','1556185057675',\
'width=600,height=300,toolbar=0,menubar=0,\
location=0,status=1,scrollbars=0,resizable=1,left=300,top=300,fullscreen=0');\
return false;\">%s</a>" % (filename, filename, referral))

    def url(self, urla, cap):
        self.write('<a href=%s target="new">%s</a>' % (urla, cap))

    def showfig(self, figname, folder="pics", caption=""):
        self.write("\n\n![alt text](%s '%s')\n\n" %
                   (ff2p(folder, figname), figname))
        s = self.wfig(caption)
        if folder == "":
            mdxziplist([figname])
        else:
            mdxziplist([folder+"\\"+figname])
        return s

    def showplt(self, fig, figname, folder="tmp", caption=""):
        fullname = ff2p(folder, figname)
        fig.savefig(fullname)
        self.write("\n\n![alt text](%s '%s')\n\n" % (fullname, figname))
        s = self.wfig(caption)
        return s

    def mcq(self, fakes, correct, cq, unit="", showanswer=True, dig=2, pdf=None):
        nq = len(fakes)+1

        def isfloat(x):
            return(type(x) == np.float64 or type(x) == float)

        def pdfwrite(pdf, s):
            if pdf != None:
                sapp(pdf, s)
        if cq > (nq-1):
            sys.exit("MDMCQ ERROR nq=%d, cq=%d" % (nq, cq))
        j = 0
        fmt = "%%.%df %%s\n\n" % dig
        s = "\n\n"
        self.write("\n\n")
        pdfwrite(pdf, s)
        if showanswer:
            show = " $\\Leftarrow$__"
            preshow = "__"
        else:
            show = ""
            preshow = ""
        for i in range(0, nq):
            c = "abcdef"[i]
            s = "(%s)  " % c
            self.write(s)
            pdfwrite(pdf, s)
            if i == cq:
                if type(correct) == int:
                    spdf = "%d %s" % (correct, unit)
                    s = preshow+"%d %s\n\n" % (correct, unit+show)
                elif isfloat(correct):
                    s = preshow+fmt % (correct, unit+show)
                    spdf = fmt % (correct, unit)
                else:
                    s = preshow+"%s %s\n\n" % (correct, unit+show)
                    spdf = "%s %s\n\n" % (correct, unit)
            else:
                if type(correct) == int:
                    s = "%d %s\n\n" % (fakes[j], unit)
                elif isfloat(correct):
                    s = fmt % (fakes[j], unit)
                else:
                    s = "%s %s\n\n" % (fakes[j], unit)
                spdf = s
                j += 1
            self.write(s)
            pdfwrite(pdf, spdf)
        self.write("\n\n")
        pdfwrite(pdf, "\n\n")
# END OF MD CLASS
#
#


def engfmt(x, p=6, d=0, latex=False):
    if x > 1:
        y = x/(10**p)
        if latex:
            s = ("%%.%df \\times 10^{%%d}" % d) % (y, p)
        else:
            s = ("%%.%df x 10<sup>%%d</sup>" % d) % (y, p)
    else:
        y = x*(10**p)
        if latex:
            s = ("%%.%df \\times 10^{-%%d}" % d) % (y, p)
        else:
            s = ("%%.%df $\\times$ 10<sup>-%%d</sup>" % d) % (y, p)
    return s

# Print array elements separated by a comma


def pra(a, fmt="%.3f"):
    n = len(a)
    s = ""
    for i in range(0, n):
        if i > 0:
            s += ", "
        s += fmt % a[i]
    return s


def cite(s):
    return " -- <cite>%s</cite>" % s


def classinfo(pythonfile, classname, ending="def __in"):
    f = open(pythonfile, "r")
    s = f.read()
    z = s.split("class %s:" % classname)
    q = z[1].split('"""')
    # q=z[1].split(ending)
    # print(q)
    # s=q[0].replace('"""',"")
    return "__class %s__\n\n" % classname+q[1]


def anyinfo(pythonfile, sstart, ending):
    f = open(pythonfile, "r")
    s = f.read()
    z = s.split(sstart)
    q = z[1].split(ending)
    return q[0]


def thesame(x, y, eps=0.01, checksign=True):
    if not checksign:
        sign = (np.sign(x)*np.sign(y))
        x = abs(x)
        y = abs(y)
    if x == 0:
        return (abs(y) <= 0.0001)
    diff = abs(y-x)
    percentdiff = diff/x
    if checksign:
        return percentdiff < eps
    else:
        return (percentdiff < eps, sign > 0)


# Latex functions:
# import quantities as pq


def createx(title, subtitle):
    geometry_options = {"margin": "2cm"}
    doc = Document(geometry_options=geometry_options)
    # Add document header
    header = PageStyle("header")
    # Create left header
    with header.create(Head("L")):
        header.append("Date: ")
        header.append(LineBreak())
        header.append((date.today().strftime("%d/%m/%y")))
    # Create center header
    with header.create(Head("C")):
        header.append("MECH2100")
    # Create right header
    with header.create(Head("R")):
        header.append(simple_page_number())
    # Create left footer
    with header.create(Foot("L")):
        header.append("The University of Queensland")
    # Create center footer
    with header.create(Foot("C")):
        header.append("2019")
    # Create right footer
    with header.create(Foot("R")):
        header.append("Assignment #1")

    doc.preamble.append(header)
    doc.change_document_style("header")

    # Add Heading
    with doc.create(MiniPage(align='c')):
        doc.append(LargeText(pylatex.utils.bold(title)))
        doc.append(LineBreak())
        doc.append(MediumText(pylatex.utils.bold(subtitle)))
    return doc


def texhdg(s, level):
    if level == 0:
        return Section(s)
    elif level == 1:
        return Subsection(s)


def tapp(p, s):
    p.append(s)


def mathema(doc, s):
    with doc.create(Math(inline=True, escape=False)) as m:
        m.append(s)


def savepdf(doc, docfilename):
    import os
    filename = docfilename+".pdf"
    oktosave = True
    if os.path.exists(filename):
        try:
            os.rename(filename, 'tempfile.pdf')
            os.rename('tempfile.pdf', filename)
        except OSError:
            print('%s is still open.' % filename)
            oktosave = False
    if oktosave:
        doc.generate_pdf(docfilename, compiler='pdflatex', clean_tex=False)


def alignat(doc, s):
    with doc.create(Alignat(numbering=False, escape=False)) as agn:
        agn.append(s)


def newline(p):
    sapp(p, "\n")

# Append string ("" string).  Single quotes within the "" means italicised sections


def sapp(p, s):
    sa = s.split("'")
    i = 0
    for x in sa:
        xa = x.split('$')
        j = 0
        for y in xa:
            if (j % 2) == 0:
                if (i % 2) == 0:
                    p.append(y)
                else:
                    p.append(pylatex.utils.italic(y+" "))
            else:
                mathema(p, y)
#                alignat(p,y)

            j += 1
        i += 1

def xtver():
    return "4:04 pm 20 July 2021"
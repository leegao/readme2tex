# readme2tex
Renders TeXy Math for Github Readmes

<p align="center"><img src="https://rawgit.com/leegao/readme2tex/master/svgs/a72a8666c79e3e8072edd5f772ce0104.svg" valign=0px width=102.2858pt height=18.07476pt/></p>

> Make sure that pdflatex is installed.

`readme2tex` is a Python script that "texifies" your readme. It takes in Github Markdown and outputs
replaces anything enclosed between dollar signs with rendered <img src="https://rawgit.com/leegao/readme2tex/master/svgs/c068b57af6b6fa949824f73dcb828783.svg" valign=-4.289619999999996px width=50.9794pt height=17.86942pt/>.

In addition, unlike the other Github texifiers, `readme2tex` ensures that inline mathematical expressions
are properly aligned with the rest of the text to avoid giving a "jumpy" look to the document.

## Installation

Currently, you just need to have `render.py` on your path, and you can call

### Usage

# render.py --output README.md

It will then look for a file called `readother.md` and compile it down to a readable Github-ready
document.

In addition, you can specify other arguments to `render.py`, such as:

* `--readme READOTHER.md` The raw readme to process. Defaults to `READOTHER.md`.
* `--output README.md` The processed readme.md file. Defaults to `README_GH.md`.
* `--packages ...` A list of addition packages to use during <img src="https://rawgit.com/leegao/readme2tex/master/svgs/c068b57af6b6fa949824f73dcb828783.svg" valign=-4.289619999999996px width=50.9794pt height=17.86942pt/> compilation. This is optional.
* `--svgdir svgs/` The directory to store the output svgs. The default is `svgs/`
* `--branch master` *Experimental* Which branch to store the svgs into, the default is just master.
* `--username username` Your github username. This is optional, and `render.py` will try to infer this for you.
* `--project project` The current github project. This is also optional.
* `--nocdn True` Ticking this will use relative paths for the output images. Defaults to False.
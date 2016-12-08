# readme2tex
Renders TeXy Math for Github Readmes

$$
\text{Hello \LaTeX}
$$

> Make sure that pdflatex is installed.

`readme2tex` is a Python script that "texifies" your readme. It takes in Github Markdown and outputs
replaces anything enclosed between dollar signs with rendered $\text{\LaTeX}$.

In addition, unlike the other Github texifiers, `readme2tex` ensures that inline mathematical expressions
are properly aligned with the rest of the text to avoid giving a "jumpy" look to the document.

### Examples:

Here's a display level equation
$$
\frac{n!}{k!(n-k)!} = {n \choose k}
$$

which looks like

    $$
    \frac{n!}{k!(n-k)!} = {n \choose k}
    $$

In addition, you can escape \$ so that they don't render.

Here's an inline equation. It is well know that if $ax^2 + bx + c = 0$, then $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.

    Here's an inline equation. It is well know that if $ax^2 + bx + c = 0$, then $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.

Notice that the equations line up with the baseline of the text, even when the height of these two images are different.

Sometimes, you might run into equations that are bottom-heavy, like $x^2\sum\limits_{3^{n^{n^{n}}}}$. Here, `readme2tex`
can compute the correct offset to align this equation to the baseline of your paragraph of text as well.

#### Caveats

Github does not allow you to pass in custom style attributes to your images. While this is useful for security purposes,
it makes it incredibly difficult to ensure that images will align correctly to the text. `readme2tex` circumvents this
using one of two tricks:

1. In Chrome, the attribute `valign=offset` works for `img` tags as well. This allows us to shift the image directly.
Unfortunately, this is not supported within any of the other major browsers, therefore this mode is not enabled by
default.
2. In every (reasonably modern) browser, the `align=middle` attribute will vertically center an image. However, the
definition of the vertical "center" is different. In particular, for Chrome, Firefox, (and probably Safari), that center
is the exact middle of the image. For IE and Edge however, the center is about 5 pixels (the height of a lower-case character)
above the exact center. Since this looks great for non-IE browsers, and reasonably good on Edge, this is the default
rendering method. The trick here is to pad either the top or the bottom of the image with extra spaces until the
baseline of the equation is at the center. For most equations, this works great. However, if you have a tall equation,
like $\frac{~}{\sum\limits_{x^{x^{x^{x}}}}^{x^{x^{x^{x}}}} f(x)}$, you'll notice that there might be a lot
of slack vertical spacing between these lines. If this is a deal-breaker for you, you can always try the `--valign True`
mode. For most inline equations, this is usually a non-issue.

### Installation

Currently, you just need to have `render.py` on your path, and you can call

### Usage

    render.py --output README.md

It will then look for a file called `readother.md` and compile it down to a readable Github-ready
document.

In addition, you can specify other arguments to `render.py`, such as:

* `--readme READOTHER.md` The raw readme to process. Defaults to `READOTHER.md`.
* `--output README.md` The processed readme.md file. Defaults to `README_GH.md`.
* `--packages ...` A list of addition packages to use during $\text{\LaTeX}$ compilation. This is optional.
* `--svgdir svgs/` The directory to store the output svgs. The default is `svgs/`
* `--branch master` *Experimental* Which branch to store the svgs into, the default is just master.
* `--username username` Your github username. This is optional, and `render.py` will try to infer this for you.
* `--project project` The current github project. This is also optional.
* `--nocdn True` Ticking this will use relative paths for the output images. Defaults to False.
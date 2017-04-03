# readme2tex
Renders LaTeX for Github Readmes

<p align="center"><img alt="$$&#10;\huge\text{Hello \LaTeX}&#10;$$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/d27ecd9d6334c7a020001926c8000801.svg?invert_in_darkmode" align=middle width="159.690135pt" height="30.925785pt"/></p>

<p align="center"><img alt="\begin{tikzpicture}&#10;\newcounter{density}&#10;\setcounter{density}{20}&#10;    \def\couleur{blue}&#10;    \path[coordinate] (0,0)  coordinate(A)&#10;                ++( 60:6cm) coordinate(B)&#10;                ++(-60:6cm) coordinate(C);&#10;    \draw[fill=\couleur!\thedensity] (A) -- (B) -- (C) -- cycle;&#10;    \foreach \x in {1,...,15}{%&#10;        \pgfmathsetcounter{density}{\thedensity+10}&#10;        \setcounter{density}{\thedensity}&#10;        \path[coordinate] coordinate(X) at (A){};&#10;        \path[coordinate] (A) -- (B) coordinate[pos=.15](A)&#10;                            -- (C) coordinate[pos=.15](B)&#10;                            -- (X) coordinate[pos=.15](C);&#10;        \draw[fill=\couleur!\thedensity] (A)--(B)--(C)--cycle;&#10;    }&#10;\end{tikzpicture}" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/a00f34be6b1ce8e4820c9852c5e6163e.svg" align=middle width="0.0pt" height="0.0pt"/></p>

<sub>**Make sure that pdflatex is installed on your system.**</sub>

----------------------------------------

`readme2tex` is a Python script that "texifies" your readme. It takes in Github Markdown and
replaces anything enclosed between dollar signs with rendered <img alt="$\text{\LaTeX}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/c068b57af6b6fa949824f73dcb828783.svg?invert_in_darkmode" align=middle width="42.05817pt" height="22.407pt"/>.

In addition, while other Github TeX renderers tend to give a jumpy look to the compiled text, 
<p align="center">
<img src="http://i.imgur.com/XSV1rPw.png?1" width=500/>
</p>

`readme2tex` ensures that inline mathematical expressions
are properly aligned with the rest of the text to give a more natural look to the document. For example,
this equation <img alt="$\frac{dy}{dx}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/24a7d013bfb0af0838f476055fc6e1ef.svg?invert_in_darkmode" align=middle width="14.297415pt" height="30.58869pt"/> is preprocessed so that it lines up at the correct baseline for the text.
This is the one salient feature of this package compared to the others out there.

### Installation

Make sure that you have Python 2.7 or above and `pip` installed. In addition, you'll need to have the programs `latex` 
and `dvisvgm` on your `PATH`. In addition, you'll need to pre-install the `geometry` package in <img alt="$\LaTeX$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/87181ad2b235919e0785dee664166921.svg?invert_in_darkmode" align=middle width="45.56376pt" height="22.407pt"/>.

To install `readme2tex`, you'll need to run

```bash
sudo pip install readme2tex
```

or, if you want to try out the bleeding edge,

```bash
git clone https://github.com/leegao/readme2tex
cd readme2tex
python setup.py develop
```

To compile `INPUT.md` and render all of its equations, run

```bash
python -m readme2tex --output README.md INPUT.md
```

If you want to do this automatically for every commit of INPUT.md, you can use the `--add-git-hook` command once to
set up the post-commit hook, like so

```bash
git stash --include-untracked
git branch svgs # if this isn't already there

python -m readme2tex --output README.md --branch svgs --usepackage tikz INPUT.md --add-git-hook

# modify INPUT.md

git add INPUT.md
git commit -a -m "updated readme"

git stash pop
```

and every `git commit` that touches `INPUT.md` from now on will allow you to automatically run `readme2tex` on it, saving
you from having to remember how `readme2tex` works. The caveat is that if you use a GUI to interact with git, things
might get a bit wonky. In particular, `readme2tex` will just assume that you're fine with all of the changes and won't
prompt you for verification like it does on the terminal.

<p align="center">
<a href="https://asciinema.org/a/2am62r2x2udg1zqyb6r3kpm1i"><img src="https://asciinema.org/a/2am62r2x2udg1zqyb6r3kpm1i.png" width=600/></a>
</p>

You can uninstall the hook by deleting `.git/hooks/post-commit`. See `python -m readme2tex --help` for a list
of what you can do in `readme2tex`.

### Examples:

Here's a display level equation
<p align="center"><img alt="$$&#10;\frac{n!}{k!(n-k)!} = {n \choose k}&#10;$$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/32737e0a8d5a4cf32ba3ab1b74902ab7.svg?invert_in_darkmode" align=middle width="127.89183pt" height="39.30498pt"/></p>

The code that was used to render this equation is just

    $$
    \frac{n!}{k!(n-k)!} = {n \choose k}
    $$

<sub>*Note: you can escape \$ so that they don't render.*</sub>

Here's an inline equation. 

> It is well known that if <img alt="$ax^2 + bx + c =0$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/162f63774d8a882cc15ae1301cfd8ac0.svg?invert_in_darkmode" align=middle width="119.01186pt" height="26.70657pt"/>, then <img alt="$x = \frac{-b \pm \sqrt{b^2- 4ac}}{2a}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/584fa2612b78129d140fb208e9d76ae9.svg?invert_in_darkmode" align=middle width="112.3584pt" height="33.20526pt"/>.

The code that was used to render this is:

    It is well known that if $ax^2 + bx + c = 0$, then $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.

Notice that the equations line up with the baseline of the text, even when the height of these two images are different.

Sometimes, you might run into equations that are bottom-heavy, like <img alt="$x^2\sum\limits_{3^{n^{n^{n}}}}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/4cb4ead947a07837121937c807973436.svg?invert_in_darkmode" align=middle width="47.639295pt" height="37.03194pt"/>. Here, `readme2tex`
can compute the correct offset to align this equation to the baseline of your paragraph of text as well.

#### Tikz (Courtesy of http://www.texample.net/)

Did you notice the picture at the top of this page? That was also generated by <img alt="$\text{\LaTeX}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/c068b57af6b6fa949824f73dcb828783.svg?invert_in_darkmode" align=middle width="42.05817pt" height="22.407pt"/>. `readme2tex` is capable of
handling Tikz code. For reference, the picture

<p align="center"><img alt="\begin{tikzpicture}&#10;\newcounter{density}&#10;\setcounter{density}{20}&#10;    \def\couleur{red}&#10;    \path[coordinate] (0,0)  coordinate(A)&#10;                ++( 60:6cm) coordinate(B)&#10;                ++(-60:6cm) coordinate(C);&#10;    \draw[fill=\couleur!\thedensity] (A) -- (B) -- (C) -- cycle;&#10;    \foreach \x in {1,...,15}{%&#10;        \pgfmathsetcounter{density}{\thedensity+10}&#10;        \setcounter{density}{\thedensity}&#10;        \path[coordinate] coordinate(X) at (A){};&#10;        \path[coordinate] (A) -- (B) coordinate[pos=.15](A)&#10;                            -- (C) coordinate[pos=.15](B)&#10;                            -- (X) coordinate[pos=.15](C);&#10;        \draw[fill=\couleur!\thedensity] (A)--(B)--(C)--cycle;&#10;    }&#10;\end{tikzpicture}" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/522cbfbc866df378cb95b2ef083131b2.svg" align=middle width="0.0pt" height="0.0pt"/></p>

is given by the tikz code

    \begin{tikzpicture}
    \newcounter{density}
    \setcounter{density}{20}
        \def\couleur{red}
        \path[coordinate] (0,0)  coordinate(A)
                    ++( 60:6cm) coordinate(B)
                    ++(-60:6cm) coordinate(C);
        \draw[fill=\couleur!\thedensity] (A) -- (B) -- (C) -- cycle;
        \foreach \x in {1,...,15}{%
            \pgfmathsetcounter{density}{\thedensity+10}
            \setcounter{density}{\thedensity}
            \path[coordinate] coordinate(X) at (A){};
            \path[coordinate] (A) -- (B) coordinate[pos=.15](A)
                                -- (C) coordinate[pos=.15](B)
                                -- (X) coordinate[pos=.15](C);
            \draw[fill=\couleur!\thedensity] (A)--(B)--(C)--cycle;
        }
    \end{tikzpicture}

We can see a few other examples, such as this graphical proof of the Pythagorean Theorem.

<p align="center"><img alt="\begin{tikzpicture}&#10;\newcommand{\pythagwidth}{3cm}&#10;\newcommand{\pythagheight}{2cm}&#10;  \coordinate [label={below right:$A$}] (A) at (0, 0);&#10;  \coordinate [label={above right:$B$}] (B) at (0, \pythagheight);&#10;  \coordinate [label={below left:$C$}] (C) at (-\pythagwidth, 0);&#10;&#10;  \coordinate (D1) at (-\pythagheight, \pythagheight + \pythagwidth);&#10;  \coordinate (D2) at (-\pythagheight - \pythagwidth, \pythagwidth);&#10;&#10;  \draw [very thick] (A) -- (C) -- (B) -- (A);&#10;&#10;  \newcommand{\ranglesize}{0.3cm}&#10;  \draw (A) -- ++ (0, \ranglesize) -- ++ (-\ranglesize, 0) -- ++ (0, -\ranglesize);&#10;&#10;  \draw [dashed] (A) -- node [below] {$b$} ++ (-\pythagwidth, 0)&#10;            -- node [right] {$b$} ++ (0, -\pythagwidth)&#10;            -- node [above] {$b$} ++ (\pythagwidth, 0)&#10;            -- node [left]  {$b$} ++ (0, \pythagwidth);&#10;&#10;  \draw [dashed] (A) -- node [right] {$c$} ++ (0, \pythagheight)&#10;            -- node [below] {$c$} ++ (\pythagheight, 0)&#10;            -- node [left]  {$c$} ++ (0, -\pythagheight)&#10;            -- node [above] {$c$} ++ (-\pythagheight, 0);&#10;&#10;  \draw [dashed] (C) -- node [above left]  {$a$} (B)&#10;                     -- node [below left]  {$a$} (D1)&#10;                     -- node [below right] {$a$} (D2)&#10;                     -- node [above right] {$a$} (C);&#10;\end{tikzpicture}" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/e148d2d3bb31215788cc03f9b472e5ba.svg?invert_in_darkmode" align=middle width="13.2437415pt" height="11.3728725pt"/></p>

How about a few snowflakes?

<p align="center"><img alt="\begin{center}&#10;\usetikzlibrary{lindenmayersystems}&#10;&#10;\pgfdeclarelindenmayersystem{A}{&#10;    \rule{F -&gt; FF[+F][-F]}&#10;}&#10;&#10;\pgfdeclarelindenmayersystem{B}{&#10;    \rule{F -&gt; ffF[++FF][--FF]}&#10;}&#10;&#10;\pgfdeclarelindenmayersystem{C}{&#10;    \symbol{G}{\pgflsystemdrawforward}&#10;    \rule{F -&gt; F[+F][-F]FG[+F][-F]FG}&#10;}&#10;&#10;\pgfdeclarelindenmayersystem{D}{&#10;    \symbol{G}{\pgflsystemdrawforward}&#10;    \symbol{H}{\pgflsystemdrawforward}&#10;    \rule{F -&gt; H[+HG][-HG]G}&#10;    \rule{G -&gt; HF}&#10;}&#10;&#10;\tikzset{&#10;    type/.style={l-system={#1, axiom=F,order=3,step=4pt,angle=60},&#10;      blue, opacity=0.4, line width=.5mm, line cap=round   &#10;    },&#10;}&#10;&#10;\newcommand\drawsnowflake[2][scale=0.2]{&#10;    \tikz[#1]&#10;    \foreach \a in {0,60,...,300}  {&#10;    \draw[rotate=\a,#2] l-system;&#10;    };&#10;}&#10;&#10;\foreach \width in {.2,.4,...,.8} &#10;{  \drawsnowflake[scale=0.3]{type=A, line width=\width mm} }&#10;&#10;\foreach \width in {.2,.4,...,.8} &#10;{  \drawsnowflake[scale=0.38]{type=A, l-system={angle=90}, line width=\width mm} }    &#10;&#10;\foreach \width in {.2,.4,...,.8} &#10;{  \drawsnowflake[scale=0.3]{type=B, line width=\width mm} }&#10;&#10;\foreach \width in {.2,.4,...,.8} &#10;{  \drawsnowflake{type=B, l-system={angle=30}, line width=\width mm} }&#10;&#10;\drawsnowflake[scale=0.24]{type=C, l-system={order=2}, line width=0.2mm}&#10;\drawsnowflake[scale=0.25]{type=C, l-system={order=2}, line width=0.4mm}&#10;\drawsnowflake[scale=0.25]{type=C, l-system={order=2,axiom=fF}, line width=0.2mm}&#10;\drawsnowflake[scale=0.32]{type=C, l-system={order=2,axiom=---fff+++F}, line width=0.2mm}&#10;&#10;\drawsnowflake[scale=0.38]{type=D, l-system={order=4,angle=60,axiom=GF}, line width=0.7mm}&#10;\drawsnowflake[scale=0.38]{type=D, l-system={order=4,angle=60,axiom=GfF}, line width=0.7mm}&#10;\drawsnowflake[scale=0.38]{type=D, l-system={order=4,angle=60,axiom=FG}, line width=0.7mm}&#10;\drawsnowflake[scale=0.38]{type=D, l-system={order=4,angle=60,axiom=FfG}, line width=0.7mm}&#10;\end{center}" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/eb57748cb91d08bfc997b0d70f7f2774.svg?invert_in_darkmode" align=middle width="0.0pt" height="0.0pt"/></p>

### Usage

    python -m readme2tex --output README.md [READOTHER.md]

It will then look for a file called `readother.md` and compile it down to a readable Github-ready
document.

In addition, you can specify other arguments to `render.py`, such as:

* `--readme READOTHER.md` The raw readme to process. Defaults to `READOTHER.md`.
* `--output README.md` The processed readme.md file. Defaults to `README_GH.md`.
* `--usepackage tikz` Addition packages to use during <img alt="$\text{\LaTeX}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/c068b57af6b6fa949824f73dcb828783.svg?invert_in_darkmode" align=middle width="42.05817pt" height="22.407pt"/> compilation. You can specify this multiple times.
* `--svgdir svgs/` The directory to store the output svgs. The default is `svgs/`
* `--branch master` *Experimental* Which branch to store the svgs into, the default is just master.
* `--username username` Your github username. This is optional, and `render.py` will try to infer this for you.
* `--project project` The current github project. This is also optional.
* `--nocdn` Ticking this will use relative paths for the output images. Defaults to False.
* `--htmlize` Ticking this will output a `md.html` file so you can preview what the output looks like. Defaults to False.
* `--valign` Ticking this will use the `valign` trick (detailed below) instead. See the caveats section for tradeoffs.
* `--rerender` Ticking this will force a recompilation of all <img alt="$\text{\LaTeX}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/c068b57af6b6fa949824f73dcb828783.svg?invert_in_darkmode" align=middle width="42.05817pt" height="22.407pt"/> equations even if they are already cached.
* `--bustcache` Ticking this will ensure that Github renews its image cache. Github may sometimes take up to an hour for changed images to reappear. This is usually not necessary unless you've made stylistic changes.
* `--add-git-hook` Ticking this will generate a post-commit hook for git that runs readme2tex with the rest of the specified arguments after each `git commit`.

My usual workflow is to create a secondary branch just for the compiled svgs. You can accomplish this via

    python -m readme2tex --branch svgs --output README.md

However, be careful with this command, since it will switch over to the `svgs` branch without any input from you.

### Technical Tricks

#### How can you tell where the baseline of an image is?

By prepending every inline equation with an anchor. During post-processing, we can isolate the anchor, which
is fixed at the baseline, and crop it out. It's super clowny, but it does the job.

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
like <img alt="$\frac{~}{\sum\limits_{x^{x^{x^{x}}}}^{x^{x^{x^{x}}}} f(x)}$" src="https://rawgit.com/leegao/readme2tex/svgs/svgs/bdd0f9b91b7fff7fe5a2b1b7684a96ef.svg?invert_in_darkmode" align=middle width="56.16666pt" height="71.68953pt"/>, you'll notice that there might be a lot
of slack vertical spacing between these lines. If this is a deal-breaker for you, you can always try the `--valign True`
mode. For most inline equations, this is usually a non-issue.

#### How to compile this document
Make sure that you have the `tikz` and the `xcolor` packages installed locally.


    python -m readme2tex --usepackage "tikz" --usepackage "xcolor" --output README.md --branch svgs

and of course

    python -m readme2tex --usepackage "tikz" --usepackage "xcolor" --output README.md --branch svgs --add-git-hook

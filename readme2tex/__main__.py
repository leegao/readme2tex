from . import render

if __name__.endswith('__main__'):
    import argparse

    parser = argparse.ArgumentParser(description='Render LaTeX in Github Readmes')
    parser.add_argument('--readme', type=str)
    parser.add_argument('--engine', type=str, default="latex")
    parser.add_argument('--output', type=str, default="README_GH.md")
    parser.add_argument('--packages', type=list, action='append', default=['amsmath', 'amssymb'])
    parser.add_argument('--svgdir', type=str, default='svgs')
    parser.add_argument('--branch', type=str)
    parser.add_argument('--username', type=str)
    parser.add_argument('--project', type=str)
    parser.add_argument('--nocdn', default=False)
    parser.add_argument('--htmlize', default=False, type=bool)
    parser.add_argument('--valign', default=False)

    args = parser.parse_args()
    render(
        args.readme,
        args.output,
        args.engine,
        args.packages,
        args.svgdir,
        args.branch,
        args.username,
        args.project,
        args.nocdn,
        args.htmlize,
        args.valign)

# ImageStack Python

### A simple way to create images using svg and jinja2 templating

[![Build Status](https://github.com/skillor/imagestack-svg-python/actions/workflows/test-python.yml/badge.svg)](https://github.com/skillor/imagestack-svg-python/actions/workflows/test-python.yml) [![PyPi version](https://badgen.net/pypi/v/ImageStack-SVG/)](https://pypi.org/project/ImageStack-SVG)

## Installation

### Install with pip

    pip install imagestack-svg

### Running without display

    xvfb-run python3 {your application}
    
## Test Design

You can test your SVG Design here: https://skillor.github.io/imagestack-svg-python/

## Usage

    from imagestack_svg.imagecreator import ImageCreator
    from imagestack_svg.imageresolve import ImageStackResolveString
    ig = ImageCreator()
    s = ImageStackResolveString('<text>{{ dummy }}</text>')
    s(dummy='Hello World!')
    print(await ig.create_inner_svg(s))
    with open('test.png', 'wb') as f:
        f.write((await ig.create_bytes(s)).read())


more examples here: https://github.com/skillor/imagestack-svg-python/blob/master/test.py

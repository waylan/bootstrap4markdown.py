# Bootstrap4Markdown

A Python-Markdown extension which provides a simple syntax for including
[Bootstrap] objects within a Markdown document.

## Installation

To install the extension, run the following command:

```
pip install bootstrap4markdown
```

## Usage

To use the extension, include its name in the list of extensions passed to
Python-Markdown.

```python
import markdown
markdown.markdown(src, extensions=['bs4md'])
```

Note that this extension only generates the requisite HTML for the supported
Bootstrap components. The user is responsible for providing the necessary CSS
and Javascript for the Bootstrap theme being used. The generated HTML assumes
Bootstrap version 5.3.

## Syntax

Bootstrap4Markdown is built on top of the [Blocks] extension. Therefore, all
blocks use the same basic form.

```
/// name-of-block | argument
    option: value

content
///
```

Therefore, each supported Bootstrap object maps to a specific block name as
defined below.

### Alerts

Bootstrap based [alerts] can be defined using blocks named `alert`.

```
/// alert
This is an alert.
///
```

A title (or heading) can be defined using the block's argument.

```
/// alert | Title
This alert has a title.
///
```

The color of the alert can be altered using the `type` option. For example,
setting `type: warning` will result in the `alert-warning` style being used
from your Bootstrap theme.

```
/// alert | Warning
    type: warning

This is a **warning** alert with a title.
///
```

Valid types are the string names of any of Bootstraps contextual classes:
`primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, and
`dark`.

Notice that the body content body of the alert contains standard Markdown
content. By default the content will be parsed as a single block (paragraph)
and only inline level Markdown parsing will be applied to the content. However,
if the `markdown` option is set to `block`, then block-level parsing will be
applied to the content as well.

```
/// alert
    markdown: block

This alert contains two paragraphs of Markdown text.

This is the second paragraph.
///
```

An alert will include a dismiss button if `dismissable` is set to `true`.

```
/// alert
    dismissable: true

You can dismiss me!
///
```

Finally, any additional HTML attributes can be defined for the outer element of
the alert using the `attrs` option.

```
/// alert
    attrs:
        id: mycustomid
        class: p-5

Custom padding is set for this alert using on of Bootstraps'
[spacing](https://getbootstrap.com/docs/5.3/utilities/spacing/)
classes. (`p-5`).
///
```

#### Options

Option        | Type            | Description             | Default
------------- | --------------- | ----------------------- | -------
`type`        | string          | A string which matches one of Bootstrap's contextual classes. | `primary`
`dismissable` | boolean         | Enable or disable a dismiss button. | `false`
`markdown`    | string          | Indicate whether body content should be parsed as `block` or `inline` content. | `inline`
`attrs`       | key:value pairs | Define custom HTML attributes for the wrapping element. | `{}`

### Carousel

A Bootstrap based [carousel] (or slideshow) can be defined using two types of
blocks: the outer `carousel` block and a separate `slide` block for each
component of the slideshow.

```
//// carousel

/// slide | image1.jpg
    alt: Slide one.
///

/// slide | image2.jpg
    alt: Slide two.
///

////
```

Note that all `slide` blocks must be nested in a `carousel` block. Also, be sure
to use a different number of slashes for the parent `carousel` block than the
child `slide` blocks.

#### Carousel Block

The outer `carousel` block is used to define global options which apply to the
entire slideshow.

```
//// carousel
    attrs: {id: 'mycustomid'}
    controls: false
    indicators: true
    fade: true
    autoplay: carousel
    touch: false

...
////
```

Option        | Type     | Description                    | Default
------------- | ---------| ------------------------------ | -------
`controls`    | boolean  | Display previous/next buttons. | `true`
`indicators`  | boolean  | Display indicators to jump to a specific slide. | `false`
`fade`        | boolean  | Enable a crossfade transition between slides. | `false`
`autoplay`    | boolean or string | Enable autoplay. Set to `carousel` to autoplay on page load or `true` to autoplay after first interaction. | `false`
`attrs`       | key:value pairs | Define custom HTML attributes for the wrapping carousel element. | `{}`

Note that Boostrap requires each carousel to have a unique `id` defined for
it to work correctly. If one is not defined in the `attrs`, then a random [UUID]
string will be generated and assigned as the `id` of the carousel.

#### Slide Block

Nested within the `carousel` block, each slide is defined by a `slide` block.
Slides may take one of a few forms. The simplest form is an image.

```
///
slide | path/to/image.jpg
    alt: Some alt text for the image.
///
```

Note that the path to the image is defined in the argument and the alt text in
the `alt` option.

Image slides can also define a caption, which is text that overlays the image.
The caption is defined in the body of the image.

```
///
slide | path/to/image.jpg
    alt: Some alt text for the image.

# Caption Title

Caption Body.
///
```

However, if no argument is provided, then the body content is used as the body
of the slide. In both cases, Markdown processing is applied to the body content.

```
/// slide
    attrs: {class: 'text-center pt-5 bg-primary-subtle text-primary-emphasis min-vh-100'}

# HTML Slide

Slide Body
///
```

Note that various Bootstrap classes were set on the above slide. As Bootstrap's
documentation explains:

> Carousels don’t automatically normalize slide dimensions. As such, you may
> need to use additional utilities or custom styles to appropriately size
> content.

Of course, raw HTML can be used as well. For example, the following slide
includes a slide comprised of an SVG element.

```
/// slide
    markdown: inline

<svg class="d-block w-100" width="800" height="400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder" preserveAspectRatio="xMidYMid slice" focusable="false">
<title>Placeholder</title>
<rect width="100%" height="100%" fill="#777"></rect>
<text x="50%" y="50%" fill="#555" dy=".3em">SVG Slide</text>
</svg>
///
```

In the above slide, the `markdown` option was set to `inline` so that the `svg`
would not be wrapped in a Markdown paragraph. However, when using block-level
raw HTML, you will want to indent the content one level (4 spaces) and set the
`markdown` option to `raw` to ensure that Markdown parsing does not muck up
your custom crafted HTML.

```
/// slide
    markdown: raw

    <h4>Title</h4>
    <p>Custom Body Content</p>
///
```

Option        | Type     | Description                    | Default
------------- | ---------| ------------------------------ | -------
`alt`         | string   | Alt text for an image slide. Ignored for none-image slides. | `''`
`active`      | boolean  | Set this slide to be the active slide. | `false`
`interval`    | integer or `null` | Number of seconds to display slide when autoplaying. Set to `null` to use Bootstrap's default. | `null`
`markdown`    | string | Indicate whether body or caption content should be parsed as `block`,  `inline`, or `raw` content. | `block`.
`attrs`       | key:value pairs | Define custom HTML attributes for the slide element. | `{}`

Note that if more that one slide is set to  `active: true`, then only the first
of all "active" slides is actually set to active. If no slides are explicitly
set to be active, then the first slide in the carousel is set to be active by
default.

## License

The Bootstrap4Markdown Extension to Python-Markdown is licensed under the
[MIT License] as defined in `LICENSE`.

## Change Log

### Version 0.1 (2023-03-07)

The initial release. Includes support for Alerts and Carousels.

[Bootstrap]: https://getbootstrap.com/
[Blocks]: https://facelessuser.github.io/pymdown-extensions/extensions/blocks/
[alerts]: https://getbootstrap.com/docs/5.3/components/alerts/
[carousel]: https://getbootstrap.com/docs/5.3/components/carousel/
[UUID]: https://en.wikipedia.org/wiki/Universally_unique_identifier
[MIT License]: https://opensource.org/license/mit/

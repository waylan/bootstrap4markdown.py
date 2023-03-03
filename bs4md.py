from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_html_attribute_dict, type_html_identifier, type_string_in, \
                                  type_boolean, type_string, type_multi, type_integer, type_none
import xml.etree.ElementTree as etree
import uuid

def append_class(classstr, value):
    ''' Append a class string to an existing class string. '''
    classes = set(classstr.split(' '))
    classes.update(value.split(' '))
    classes.discard('')
    return ' '.join(list(classes))

def remove_class(classstr, value):
    ''' Remove a class from a class string. '''
    classes = classstr.split(' ')
    classes.remove(value)
    return ' '.join(classes)


class BsAlertBlock(Block):
    NAME = 'alert'
    ARGUMENT = None
    OPTIONS = {
        'type': ['primary', type_string_in([
            'primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'
            ], type_html_identifier)],
        'dismissable': [False, type_boolean],
        'markdown': ['inline', type_string_in(['block', 'inline'])]
    }

    def on_create(self, parent):
        ''' Create wrapper div '''

        # Define the basic attributes needed to make this a Bootstrap alert
        classes = f'alert alert-{self.options["type"]}'
        if self.options['dismissable']:
            # TODO: Maybe leave `fade show` out and let the user define them?
            classes = append_class(classes, 'alert-dismissible fade show')
        attrib = {
            'class': classes,
            'role': 'alert'
        }
        # Build the containing Element
        alert = etree.SubElement(parent, 'div', attrib=attrib)
        if self.argument:
            # Build the title Element
            title = etree.SubElement(alert, 'h4', attrib={'class': 'alert-heading'})
            title.text = self.argument
        return alert

    def on_markdown(self):
        return self.options['markdown']

    def on_end(self, block):
        ''' Add close button to end of block if dismissable '''
        if self.options['dismissable']:
            attrib = {
                'type':'button',
                'class': 'btn-close',
                'data-bs-dismiss': 'alert',
                'aria-label': 'Close'
            }
            etree.SubElement(block, 'button', attrib=attrib)


class BsCarouselBlock(Block):
    NAME = 'carousel'
    ARGUMENT = False
    OPTIONS = {
        'controls': [True, type_boolean],
        'indicators': [False, type_boolean],
        'fade': [False, type_boolean],
        'touch': [True, type_boolean],
        'autoplay': [False, type_multi(type_boolean, type_string_in(['carousel']))]
    }

    def on_init(self):
        self.inner_element = None

    def on_validate(self, parent):
        if 'id' not in self.options['attrs']:
            self.options['attrs']['id'] = str(uuid.uuid4())
        return True

    def on_create(self, parent):
        ''' Create wrapper and controls. '''
        attrib = {'class': 'carousel slide'}
        if self.options['fade']:
            # TODO: maybe add some class to the carousel-item? See Bootstrap docs.
            attrib['class'] = append_class(attrib['class'], 'carousel-fade')
        if self.options['autoplay'] is not False:
            attrib['data-bs-ride'] = str(self.options['autoplay']).lower()
        if not self.options['touch']:
            attrib['data-bs-touch'] = 'false'
        block = etree.SubElement(parent, 'div', attrib=attrib)
        self.inner_element = etree.SubElement(block, 'div', attrib={'class': 'carousel-inner'})
        if self.options['controls']:
            # Add next/previous controls
            for direction in ['prev', 'next']:
                attrib = {
                    'class': f'carousel-control-{direction}',
                    'type': 'button',
                    'data-bs-target': f'#{self.options["attrs"]["id"]}',
                    'data-bs-slide': direction
                }
                text = 'Previous' if direction == 'prev' else 'Next'
                el = etree.SubElement(block, 'button', attrib=attrib)
                etree.SubElement(el, 'span', attrib={'class': f'carousel-control-{direction}-icon', 'aria-hidden': 'true'})
                etree.SubElement(el, 'span', attrib={'class': 'visually-hidden'}).text = text
        return block

    def on_add(self, block):
        return self.inner_element

    def on_end(self, block):
        ''' Set up active item and indicators. '''
        active_item = None
        if self.options['indicators']:
            indicators = etree.Element('div', attrib={'class': 'carousel-indicators'})
            block.insert(0, indicators)
            for i, item in enumerate(self.inner_element):
                attrib = {
                    'data-bs-target': f'#{self.options["attrs"]["id"]}',
                    'data-bs-slide-to': f'{i}',
                    'aria-label': f'Slide {i+1}'
                }
                if 'active' in item.get('class', ''):
                    if active_item is None:
                        active_item = item
                        attrib['class'] = 'active'
                        attrib['aria-current'] = 'true'
                    else:
                        # We have multiple active items. Deactivate this one.
                        item.set('class', remove_class(item.get('class'), 'active'))
                etree.SubElement(indicators, 'button', attrib=attrib)
        if not active_item and len(self.inner_element):
            # Active item not explicitly set. Use first item.
            active_item = self.inner_element[0]
            active_item.set('class', append_class(active_item.get('class', ''), 'active'))
            indicators[0].set('class', 'active')
            indicators[0].set('aria-current', 'true')


class BsCarouselSlideBlock(Block):
    NAME = 'slide'
    ARGUMENT = None
    OPTIONS = {
        'alt': ['', type_string],
        'active': [False, type_boolean],
        'interval': [None, type_multi(type_integer, type_none)],
        'markdown': ['block', type_string_in(['block', 'inline', 'raw'])]
    }

    def on_init(self):
        self.caption = None

    def on_validate(self, parent):
        return parent.tag == 'div' and parent.get('class') == 'carousel-inner'

    def on_create(self, parent):
        ''' Return root element. If argument is set, insert img and caption wrapper. '''
        attrib={'class': 'carousel-item'}
        if self.options['interval'] is not None:
            attrib['data-bs-interval'] = str(self.options['interval'])
        if self.options['active']:
            attrib['class'] = append_class(attrib['class'], 'active')
        slide = etree.SubElement(parent, 'div', attrib=attrib)
        if self.argument:
            img_attrib = {
                'src': self.argument,
                'class': 'd-block w-100'
            }
            if self.options['alt']:
                img_attrib['alt'] = self.options['alt']
            etree.SubElement(slide, 'img', attrib=img_attrib)
            self.caption = etree.SubElement(slide, 'div', attrib={'class': 'carousel-caption d-none d-md-block'})
        return slide

    def on_markdown(self):
        return self.options['markdown']

    def on_add(self, block):
        ''' Return caption wrapper if argument is set, otherwise root element. '''
        if self.argument:
            return self.caption
        return block

    def on_end(self, block):
        ''' Remove the caption wrapper if it is empty. '''
        if self.caption is not None and len(self.caption) == 0 and not self.caption.text:
            block.remove(self.caption)
        # if self.options['markdown'] == 'raw':
        #     # TODO: handle this case. Waiting for API to be finalized.


class BsBlockExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(BsAlertBlock, self.getConfigs())
        block_mgr.register(BsCarouselBlock, self.getConfigs())
        block_mgr.register(BsCarouselSlideBlock, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return BsBlockExtension(*args, **kwargs)


if __name__ == '__main__':
    import markdown
    from textwrap import dedent
    src = dedent('''
    /// alert
    This is an alert.
    ///

    /// alert | Title
    This alert has a title.
    ///

    /// alert | Warning
        type: warning

    This is a **warning** alert with a title.
    ///

    /// alert
        type: secondary
        attrs: {id: custom, class: p-5}
        markdown: block

    This alert has custom attributes defined. We have a custom id and custom padding set.

    The custom padding is set using bootstraps' class `p-5` which adds padding to all sides.
    ///

    /// alert
        type: danger
        dismissable: true

    You can dismiss me!
    ///

    //// carousel
        #attrs: {id: 'random'}
        indicators: true
        #fade: true
        # autoplay: carousel
        # touch: false

    /// slide | img1.jpg
        alt: img 1
        # active: true
        interval: 2000
    ///

    /// slide | img2.jpg
        alt: img 2
        # active: true

    # Caption Title

    Caption Body.
    ///

    /// slide
        attrs: {class: 'text-center pt-5 bg-primary-subtle text-primary-emphasis min-vh-100'}

    # HTML Slide

    Slide Body
    ///

    /// slide
        markdown: inline
    <svg class="d-block w-100" width="800" height="400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: Fourth slide" preserveAspectRatio="xMidYMid slice" focusable="false">
    <title>Placeholder</title>
    <rect width="100%" height="100%" fill="#777"></rect>
    <text x="50%" y="50%" fill="#555" dy=".3em">SVG Slide</text>
    </svg>
    ///

    /// slide
        markdown: raw

    <h4>Title</h4>

    ///
    ////
    ''')
    body = markdown.markdown(src, extensions=[BsBlockExtension()])
    template = dedent(f'''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="file:///C:/code/bs4md/img1.jpgutf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Bootstrap demo</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktQOp6b7In1Zl3/Jr59b6EGGoI1aFkw7cmDA6j6gD" crossorigin="anonymous">
      </head>
      <body>
        <h1>Hello, world!</h1>
        {body}
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js" integrity="sha384-w76AqPfDkMBDXo30jS1Sgez6pr3x5MlQ1ZAGC+nuZB+EYdgRZgiwxhTBTkF7CXvN" crossorigin="anonymous"></script>
      </body>
    </html>
    ''')
    with open('example.html', 'w') as f:
        f.write(template)
    print(body)

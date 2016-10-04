# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.rsc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools for scraping documents from The Royal Society of Chemistry.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

from bs4 import UnicodeDammit
from lxml.etree import fromstring
from lxml.html import HTMLParser, Element
import six

from ...text.processors import Substitutor, Discard, Chain, LStrip, RStrip, LAdd
from ...text.normalize import normalize
from .. import BLOCK_ELEMENTS
from ..clean import Cleaner, clean
from ..entity import Entity, DocumentEntity
from ..fields import StringField, EntityField, UrlField
from ..scraper import RssScraper, SearchScraper, UrlScraper
from ..selector import Selector


log = logging.getLogger(__name__)


#: Map placeholder text to unicode characters.
CHAR_REPLACEMENTS = [
    ('\[?\[1 with combining macron\]\]?', '1\u0304'),
    ('\[?\[2 with combining macron\]\]?', '2\u0304'),
    ('\[?\[3 with combining macron\]\]?', '3\u0304'),
    ('\[?\[4 with combining macron\]\]?', '4\u0304'),
    ('\[?\[approximate\]\]?', '\u2248'),
    ('\[?\[bottom\]\]?', '\u22a5'),
    ('\[?\[c with combining tilde\]\]?', 'C\u0303'),
    ('\[?\[capital delta\]\]?', '\u0394'),
    ('\[?\[capital lambda\]\]?', '\u039b'),
    ('\[?\[capital omega\]\]?', '\u03a9'),
    ('\[?\[capital phi\]\]?', '\u03a6'),
    ('\[?\[capital pi\]\]?', '\u03a0'),
    ('\[?\[capital psi\]\]?', '\u03a8'),
    ('\[?\[capital sigma\]\]?', '\u03a3'),
    ('\[?\[caret\]\]?', '^'),
    ('\[?\[congruent with\]\]?', '\u2245'),
    ('\[?\[curly or open phi\]\]?', '\u03d5'),
    ('\[?\[dagger\]\]?', '\u2020'),
    ('\[?\[dbl greater-than\]\]?', '\u226b'),
    ('\[?\[dbl vertical bar\]\]?', '\u2016'),
    ('\[?\[degree\]\]?', '\xb0'),
    ('\[?\[double bond, length as m-dash\]\]?', '='),
    ('\[?\[double bond, length half m-dash\]\]?', '='),
    ('\[?\[double dagger\]\]?', '\u2021'),
    ('\[?\[double equals\]\]?', '\u2267'),
    ('\[?\[double less-than\]\]?', '\u226a'),
    ('\[?\[double prime\]\]?', '\u2033'),
    ('\[?\[downward arrow\]\]?', '\u2193'),
    ('\[?\[fraction five-over-two\]\]?', '5/2'),
    ('\[?\[fraction three-over-two\]\]?', '3/2'),
    ('\[?\[gamma\]\]?', '\u03b3'),
    ('\[?\[greater-than-or-equal\]\]?', '\u2265'),
    ('\[?\[greater, similar\]\]?', '\u2273'),
    ('\[?\[gt-or-equal\]\]?', '\u2265'),
    ('\[?\[i without dot\]\]?', '\u0131'),
    ('\[?\[identical with\]\]?', '\u2261'),
    ('\[?\[infinity\]\]?', '\u221e'),
    ('\[?\[intersection\]\]?', '\u2229'),
    ('\[?\[iota\]\]?', '\u03b9'),
    ('\[?\[is proportional to\]\]?', '\u221d'),
    ('\[?\[leftrightarrow\]\]?', '\u2194'),
    ('\[?\[leftrightarrows\]\]?', '\u21c4'),
    ('\[?\[less-than-or-equal\]\]?', '\u2264'),
    ('\[?\[less, similar\]\]?', '\u2272'),
    ('\[?\[logical and\]\]?', '\u2227'),
    ('\[?\[middle dot\]\]?', '\xb7'),
    ('\[?\[not equal\]\]?', '\u2260'),
    ('\[?\[parallel\]\]?', '\u2225'),
    ('\[?\[per thousand\]\]?', '\u2030'),
    ('\[?\[prime or minute\]\]?', '\u2032'),
    ('\[?\[quadruple bond, length as m-dash\]\]?', '\u2263'),
    ('\[?\[radical dot\]\]?', ' \u0307'),
    ('\[?\[ratio\]\]?', '\u2236'),
    ('\[?\[registered sign\]\]?', '\xae'),
    ('\[?\[reverse similar\]\]?', '\u223d'),
    ('\[?\[right left arrows\]\]?', '\u21C4'),
    ('\[?\[right left harpoons\]\]?', '\u21cc'),
    ('\[?\[rightward arrow\]\]?', '\u2192'),
    ('\[?\[round bullet, filled\]\]?', '\u2022'),
    ('\[?\[sigma\]\]?', '\u03c3'),
    ('\[?\[similar\]\]?', '\u223c'),
    ('\[?\[small alpha\]\]?', '\u03b1'),
    ('\[?\[small beta\]\]?', '\u03b2'),
    ('\[?\[small chi\]\]?', '\u03c7'),
    ('\[?\[small delta\]\]?', '\u03b4'),
    ('\[?\[small eta\]\]?', '\u03b7'),
    ('\[?\[small gamma, Greek, dot above\]\]?', '\u03b3\u0307'),
    ('\[?\[small kappa\]\]?', '\u03ba'),
    ('\[?\[small lambda\]\]?', '\u03bb'),
    ('\[?\[small micro\]\]?', '\xb5'),
    ('\[?\[small mu \]\]?', '\u03bc'),
    ('\[?\[small nu\]\]?', '\u03bd'),
    ('\[?\[small omega\]\]?', '\u03c9'),
    ('\[?\[small phi\]\]?', '\u03c6'),
    ('\[?\[small pi\]\]?', '\u03c0'),
    ('\[?\[small psi\]\]?', '\u03c8'),
    ('\[?\[small tau\]\]?', '\u03c4'),
    ('\[?\[small theta\]\]?', '\u03b8'),
    ('\[?\[small upsilon\]\]?', '\u03c5'),
    ('\[?\[small xi\]\]?', '\u03be'),
    ('\[?\[small zeta\]\]?', '\u03b6'),
    ('\[?\[space\]\]?', ' '),
    ('\[?\[square\]\]?', '\u25a1'),
    ('\[?\[subset or is implied by\]\]?', '\u2282'),
    ('\[?\[summation operator\]\]?', '\u2211'),
    ('\[?\[times\]\]?', '\xd7'),
    ('\[?\[trade mark sign\]\]?', '\u2122'),
    ('\[?\[triple bond, length as m-dash\]\]?', '\u2261'),
    ('\[?\[triple bond, length half m-dash\]\]?', '\u2261'),
    ('\[?\[triple prime\]\]?', '\u2034'),
    ('\[?\[upper bond 1 end\]\]?', ''),
    ('\[?\[upper bond 1 start\]\]?', ''),
    ('\[?\[upward arrow\]\]?', '\u2191'),
    ('\[?\[varepsilon\]\]?', '\u03b5'),
    ('\[?\[x with combining tilde\]\]?', 'X\u0303'),
]


#: Map image URL components to unicode characters.
RSC_IMG_CHARS = {
    '2041': '^',              # caret
    '224a': '\u2248',         # almost equal
    'e001': '=',              # equals
    'e002': '\u2261',         # equivalent
    'e003': '\u2263',         # strictly equivalent
    'e006': '=',              # equals
    'e007': '\u2261',         # equivalent
    'e009': '>',              # greater than
    'e00a': '<',              # less than
    'e00c': '\u269f',         # three lines converging left
    'e00d': '\u269e',         # three lines converging right
    'e010': '\u250c',         # box down and right
    'e011': '\u2510',         # box down and left
    'e012': '\u2514',         # box up and right
    'e013': '\u2518',         # box up and left
    'e038': '\u2b21',         # white hexagon
    'e059': '\u25cd',         # ?
    'e05a': '\u25cd',         # ?
    'e069': '\u25a9',         # square with diagonal crosshatch fill
    'e077': '\u2b13',         # square with bottom half black
    'e082': '\u2b18',         # diamond with top half black
    'e083': '\u2b19',         # diamond with bottom half black
    'e084': '\u27d0',         # white diamond with centred do
    'e090': '\u2504',         # box drawings light triple dash horizontal (not exactly)
    'e091': '\u2504',         # box drawings light triple dash horizontal
    'e0a2': '\u03b3\u0307',   # small gamma with dot
    'e0b3': '\u03bc\u0342',   # small mu with circumflex
    'e0b7': '\u03c1\u0342',   # small rho with circumflex
    'e0c2': '\u03b1\u0305',   # small alpha with macron
    'e0c3': '\u03b2\u0305',   # small beta with macron
    'e0c5': '\u03b4\u0305',   # small delta with macron
    'e0c6': '\u03b5\u0305',   # small epsilon with macron
    'e0ce': 'v\u0305',        # small v with macron
    'e0c9': '\u03b8\u0305',   # small theta with macron
    'e0cb': '\u03ba\u0305',   # small kappa with macron
    'e0cc': '\u03bb\u0305',   # small lambda with macron
    'e0cd': '\u03bc\u0305',   # small mu with macron
    'e0d1': '\u03c1\u0305',   # small rho with macron
    'e0d4': '\u03c4\u0305',   # small tau with macron
    'e0d5': '\u03bd\u0305',   # small nu with macron
    'e0d6': '\u03d5\u0305',   # small phi with macron (stroked)
    'e0d7': '\u03c6\u0305',   # small phi with macron
    'e0d8': '\u03c7\u0305',   # small chi with macron
    'e0da': '\u03bd\u0305',   # small omega with macron
    'e0db': '\u03a6\u0303',   # capital phi with tilde
    'e0dd': '\u03b3\u0303',   # small lambda with tilde
    'e0de': '\u03b5\u0303',   # small epsilon with tilde
    'e0e0': '\u03bc\u0303',   # small mu with tilde
    'e0e1': 'v\u0303',        # small v with tilde
    'e0e4': '\u03c1\u0303',   # small rho with tilde
    'e0e7': '\u03b5\u20d7',   # small epsilon with rightwards arrow above
    'e0e9': '\u03bc\u20d7',   # small mu with rightwards arrow above
    'e0eb': '\u29b5',         # circle with horizontal bar
    'e0ec': '|',              # ? http://www.rsc.org/images/entities/char_e0ec.gif
    'e0ed': '|',              # ? http://www.rsc.org/images/entities/char_e0ed.gif
    'e0ee': '3/2',            # 3/2
    'e0f1': '\U0001d302',     # ?
    'e0f5': '\u03bd',         # small nu
    'e0f6': '\u27ff',         # long rightwards squiggle arrow
    'e100': '\u2506',         # box drawings light triple dash vertical
    'e103': '\u2605',         # Black Star
    'e107': '\u03b5\u0342',   # small epsilon with circumflex
    'e108': '\u03b7\u0342',   # small eta with circumflex
    'e109': '\u03ba\u0342',   # small kappa with circumflex
    'e10d': '\u03c3\u0303',   # small sigma with tilde
    'e110': '\u03b7\u0303',   # small eta with tilde
    'e112': '\U0001d4a2',     # script G
    'e113': '\U0001d219',     # ? greek vocal notation symbol-51
    'e116': '\u2933',         # wave arrow pointing directly right
    'e117': '\u2501',         # box drawings heavy horizontal
    'e11a': '\u03bb\u0342',   # small lambda with circumflex
    'e11b': '\u03c7\u0303',   # small chi with tilde
    'e11f': '5/2',            # 5/2
    'e120': '5/4',            # 5/4
    'e124': '\u2b22',         # black hexagon
    'e131': '\u03bd\u0303',   # small nu with tilde
    'e132': '\u0393\u0342',   # capital gamma with circumflex
    'e13d': '\u2b1f',         # black pentagon
    'e142': '\u210b',         # script capital H
    'e144': '\u2112',         # script capital L
    'e146': '\u2113',         # script small l
    'e170': '\U0001d544',     # double-struck capital M
    'e175': '\u211d',         # double-struck capital R
    'e177': '\U0001d54b',     # double-struck capital T
    'e17e': '\U0001D580',     # fraktur bold capital U
    'e18f': '\U0001d57d',     # fraktur bold capital R
    'e1c0': '\u2b21',         # white hexagon
    'e520': '\U0001d49c',     # script capital A
    'e523': '\U0001d49f',     # script capital D
    'e529': '\U0001d4a5',     # script capital J
    'e52d': '\U0001d4a9',     # script capital N
    'e52f': '\U0001d4ab',     # script capital P
    'e531': '\u211b',         # script capital R
    'e533': '\U0001d4af',     # script capital T
}


#: HTML stripper that kills superscript references and anything with style="display:none;" (typically tooltips)
strip_rsc_html = Cleaner(strip_xpath='.//*', kill_xpath='.//span[@class="sup_ref"]|.//a[text()="†"]|.//i/small/sup/a|.//*[@style="display:none;"]')
#: HTML stripper that also kills text from buttons in references.
strip_cit_html = Cleaner(strip_xpath='.//*', kill_xpath='.//a')
#: Substitutor that replaces RSC escape codes with the actual unicode character
rsc_substitute = Substitutor(CHAR_REPLACEMENTS)


def parse_rsc_html(htmlstring):
    """Messy RSC HTML needs this special parser to fix problems before creating selector."""
    converted = UnicodeDammit(htmlstring)
    if not converted.unicode_markup:
        raise UnicodeDecodeError('Failed to detect encoding, tried [%s]')
    root = fromstring(htmlstring, parser=HTMLParser(recover=True, encoding=converted.original_encoding))
    # Add p.otherpara tags around orphan text
    newp = None
    for child in root.get_element_by_id('wrapper'):
        if newp is not None:
            if child.tag in BLOCK_ELEMENTS or child.get('id', '').startswith('sect') or child.getnext() is None:
                child.addprevious(newp)
                newp = None
            else:
                newp.append(child)
        if newp is None and child.tag in BLOCK_ELEMENTS and child.tail and child.tail.strip():
            newp = Element('p', **{'class': 'otherpara'})
            newp.text = child.tail
            child.tail = ''
    return root


def replace_rsc_img_chars(document):
    """Replace image characters with unicode equivalents."""
    image_re = re.compile('http://www.rsc.org/images/entities/(?:h[23]+_)?(?:[ib]+_)?char_([0-9a-f]{4})(?:_([0-9a-f]{4}))?\.gif')
    for img in document.xpath('.//img[starts-with(@src, "http://www.rsc.org/images/entities/")]'):
        m = image_re.match(img.get('src'))
        if m:
            u1, u2 = m.group(1), m.group(2)
            if not u2 and u1 in RSC_IMG_CHARS:
                rep = RSC_IMG_CHARS[u1]
            else:
                rep = (b'\u%s' % u1).decode('unicode-escape')
                if u2:
                    rep += (b'\u%s' % u2).decode('unicode-escape')
            if img.tail is not None:
                rep += img.tail  # Make sure we don't remove any tail text
            parent = img.getparent()
            if parent is not None:
                previous = img.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or '') + rep
                else:
                    parent.text = (parent.text or '') + rep
                parent.remove(img)
    return document


def space_references(document):
    """Ensure a space around reference links, so there's a gap when they are removed."""
    for ref in document.xpath('.//a/sup/span[@class="sup_ref"]'):
        a = ref.getparent().getparent()
        if a is not None:
            atail = a.tail or ''
            if not atail.startswith(')') and not atail.startswith(',') and not atail.startswith(' '):
                a.tail = ' ' + atail
    return document


class RscRssDocument(Entity):
    """Document information from RSC RSS feed."""
    doi = StringField('guid::text', lower=True)
    title = StringField('title::text')
    authors = StringField('dc|creator::text', all=True)
    landing_url = UrlField('guid::text', lower=True)

    process_title = Chain(rsc_substitute, normalize)

    def finalize_doi(self, value):
        """Derive the DOI from the GUID."""
        return '10.1039/%s' % value.rsplit('/', 1)[1].lower()


class RscRssScraper(RssScraper):
    """Scraper for RSC RSS feeds."""
    entity = RscRssDocument


class RscSearchDocument(Entity):
    """Document information from RSC search results page."""
    doi = StringField('.title_text_s4_jrnls a::attr("name")', lower=True)
    title = StringField('.title_text_s4_jrnls a')
    landing_url = UrlField('.title_text_s4_jrnls a::attr("href")', lower=True)
    pdf_url = UrlField('a.lnkPDF::attr("href")', lower=True, strip_querystring=True)
    html_url = UrlField('.search_link_s4_jrnls a::attr("href")', lower=True, strip_querystring=True)
    journal = StringField('.grey_left_box_text_s4_new a em strong::text')

    clean_title = Chain(replace_rsc_img_chars, strip_rsc_html)

    process_doi = LAdd('10.1039/')
    process_title = Chain(normalize, RStrip('§'), RStrip('‡'), RStrip('†'), six.text_type.strip)


class RscSearchScraper(SearchScraper):
    """Scraper for RSC search results."""

    entity = RscSearchDocument
    root = '.search_grey_box_middle_s4_jrnls'

    def perform_search(self, query, page):
        log.debug('Processing query: %s' % query)
        response = self.http.get('http://pubs.rsc.org/en/results', params={'searchtext': query, 'SortBy': 'Relevance', 'PageSize': 100})
        selector = Selector.from_html(response)
        sessionkey = selector.css('#SearchTerm::attr("value")').extract()[0]
        searchdata = {'searchterm': sessionkey, 'resultcount': 100, 'category': 'journal', 'pageno': page}
        response = self.http.post('http://pubs.rsc.org/en/search/journalresult', data=searchdata)
        return response


class RscLandingSupplement(Entity):
    name = StringField('a::text', strip=True)
    url = UrlField('a::attr("href")')


class RscLandingDocument(DocumentEntity):
    """Document information from RSC landing page."""
    supplements = EntityField(RscLandingSupplement, '.ESIright_highlight_txt_red, .ESIright_highlight_txt_red_hidden', all=True)
    # TODO: The meta abstract and title inherited from DocumentEntity are missing characters

    process_abstract = Chain(normalize, Discard('No abstract available', 'A graphical abstract is available for this content'))


class RscLandingScraper(UrlScraper):
    """Scraper for RSC Landing pages."""
    entity = RscLandingDocument


class RscChemicalMention(Entity):
    text = StringField('.', xpath=True)
    chemspider_id = StringField('a[href^="http://www.chemspider.com/Chemical-Structure."]::attr("href")')
    inchi = StringField('a[href^="http://www.chemspider.com/Search.aspx?q="]::attr("href")')

    clean_text = Chain(replace_rsc_img_chars, strip_rsc_html)

    process_text = normalize
    process_chemspider_id = Chain(LStrip('http://www.chemspider.com/Chemical-Structure.'), RStrip('.html'), Discard(''))
    process_inchi = Chain(LStrip('http://www.chemspider.com/Search.aspx?q='), six.moves.urllib.parse.unquote, six.text_type.strip)


class RscImage(Entity):
    """Embedded image. Includes both Schemes and Figures."""
    # First try image link, which provides high-res image in newer articles. Otherwise the image source.
    url = UrlField('.imgHolder a::attr("href"), .imgHolder img::attr("src")')
    label = StringField('.image_title > b::text', strip=True)
    reference = StringField('.image_title > span::attr("id")')
    caption = StringField('.graphic_title')

    clean_caption = Chain(replace_rsc_img_chars, strip_rsc_html)
    process_caption = normalize


class RscTable(Entity):
    """Table within document."""
    reference = StringField('span[id^="tab"]::attr("id")')
    label = StringField('b::text')
    caption = StringField('span[id^="tab"]')
    src = StringField('./following-sibling::table[1]/table', xpath=True, raw=True)

    clean_src = Chain(replace_rsc_img_chars, clean)
    clean_caption = Chain(replace_rsc_img_chars, strip_rsc_html)
    process_caption = normalize


class RscHtmlDocument(DocumentEntity):
    title = StringField('.title_heading')
    abstract = StringField('.abstract')
    # chemical_mentions = EntityField(RscChemicalMention, 'span.TC', all=True)
    pdf_url = UrlField('meta[name="citation_pdf_url"]::attr("content")', lower=True)
    html_url = UrlField('meta[name="citation_fulltext_html_url"]::attr("content")', lower=True)
    landing_url = UrlField('meta[name="citation_abstract_html_url"]::attr("content")', lower=True)
    # figures = EntityField(RscImage, '.image_table', all=True)
    # schemes = EntityField(RscImage, '.image_table', all=True)
    # tables = EntityField(RscTable, '.table_caption', all=True)
    # headings = StringField('.a_heading, .b_heading, .c_heading, .c_heading_indent, .d_heading, .d_heading_indent', all=True)
    # paragraphs = StringField('.otherpara, #wrapper > span, #wrapper > div:not(#art-admin):not(.left_head):not(right_head):not(.article_info):not(.table_caption):not(.otherpara) > span:not(.oa):not(.c_heading_indent):not(.d_heading_indent)', all=True)

    clean_title = Chain(replace_rsc_img_chars, strip_rsc_html)
    clean_abstract = Chain(replace_rsc_img_chars, strip_rsc_html)
    # clean_headings = Chain(replace_rsc_img_chars, strip_rsc_html)
    # clean_paragraphs = Chain(space_references, replace_rsc_img_chars, strip_rsc_html)

    process_title = Chain(normalize, RStrip('§'), RStrip('‡'), RStrip('†'), six.text_type.strip)
    process_abstract = normalize
    # process_headings = normalize
    # process_paragraphs = Chain(normalize, Discard('Notes and references', 'References', 'Literature', 'Acknowledgements', ''))

    # def process_figures(self, value):
    #     """Filter those without 'Fig' in label, they are Schemes."""
    #     return value if value.label and 'Fig' in value.label else None
    #
    # def process_schemes(self, value):
    #     """Filter those without 'Scheme' in label, they are Figures."""
    #     return value if value.label and 'Scheme' in value.label else None
    #
    # def finalize_chemical_mentions(self, value):
    #     """Remove duplicate chemical entities."""
    #     filtered = []
    #     for cm in value:
    #         if cm not in filtered:
    #             filtered.append(cm)
    #     return filtered


class RscHtmlScraper(UrlScraper):
    """Scraper for RSC Landing pages."""
    entity = RscHtmlDocument

# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.csstranslator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend cssselect to improve handling of pseudo-elements.

This is derived from csstranslator.py in the Scrapy project. The original file is available at:
https://github.com/scrapy/scrapy/blob/master/scrapy/selector/csstranslator.py

The original file was released under the BSD license:

Copyright (c) Scrapy developers.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Scrapy nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from cssselect import GenericTranslator, HTMLTranslator
from cssselect.xpath import _unicode_safe_getattr, XPathExpr, ExpressionError
from cssselect.parser import FunctionalPseudoElement


class CdeXPathExpr(XPathExpr):

    textnode = False
    attribute = None

    @classmethod
    def from_xpath(cls, xpath, textnode=False, attribute=None):
        x = cls(path=xpath.path, element=xpath.element, condition=xpath.condition)
        x.textnode = textnode
        x.attribute = attribute
        return x

    def __str__(self):
        path = super(CdeXPathExpr, self).__str__()
        if self.textnode:
            if path == '*':
                path = 'text()'
            elif path.endswith('::*/*'):
                path = path[:-3] + 'text()'
            else:
                path += '/text()'
        if self.attribute is not None:
            if path.endswith('::*/*'):
                path = path[:-2]
            path += '/@%s' % self.attribute
        return path

    def join(self, combiner, other):
        super(CdeXPathExpr, self).join(combiner, other)
        self.textnode = other.textnode
        self.attribute = other.attribute
        return self


class TranslatorMixin(object):

    def xpath_element(self, selector):
        xpath = super(TranslatorMixin, self).xpath_element(selector)
        return CdeXPathExpr.from_xpath(xpath)

    def xpath_pseudo_element(self, xpath, pseudo_element):
        if isinstance(pseudo_element, FunctionalPseudoElement):
            method = 'xpath_%s_functional_pseudo_element' % (pseudo_element.name.replace('-', '_'))
            method = _unicode_safe_getattr(self, method, None)
            if not method:
                raise ExpressionError("The functional pseudo-element ::%s() is unknown" % pseudo_element.name)
            xpath = method(xpath, pseudo_element)
        else:
            method = 'xpath_%s_simple_pseudo_element' % (pseudo_element.replace('-', '_'))
            method = _unicode_safe_getattr(self, method, None)
            if not method:
                raise ExpressionError("The pseudo-element ::%s is unknown" % pseudo_element)
            xpath = method(xpath)
        return xpath

    def xpath_attr_functional_pseudo_element(self, xpath, function):
        if function.argument_types() not in (['STRING'], ['IDENT']):
            raise ExpressionError("Expected a single string or ident for ::attr(), got %r" % function.arguments)
        return CdeXPathExpr.from_xpath(xpath, attribute=function.arguments[0].value)

    def xpath_text_simple_pseudo_element(self, xpath):
        """Support selecting text nodes using ::text pseudo-element"""
        return CdeXPathExpr.from_xpath(xpath, textnode=True)


class CssXmlTranslator(TranslatorMixin, GenericTranslator):
    pass


class CssHTMLTranslator(TranslatorMixin, HTMLTranslator):
    pass

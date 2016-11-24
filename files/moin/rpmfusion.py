# -*- coding: utf-8 -*-
"""
    MoinMoin technical theme

    @copyright: (c) 2003-2004 by Radomir Dopieralski
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.theme import ThemeBase
from MoinMoin import wikiutil
from MoinMoin.Page import Page


class Theme(ThemeBase):

    name = "rpmfusion"
    stylesheets = (
        # media         basename
        ('all',         'style'),
        )
    stylesheets_print=stylesheets
    stylesheets_projection=stylesheets

    def headscript(self, d):
        return u''

    def guiEditorScript(self, d):
        return u''

    def externalScript(self, d):
        return u''

    def header(self, d, **kw):
        """ Assemble wiki header
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),

            self.msg(d),
            u'<div id="header">',
            self.searchform(d),
            self.logo(),
            self.navibar(d),
            u'<hr>',
            u'</div>',
            self.actionbar(d, *kw),
            self.trail(d),
            self.login(d),

            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),

            # Start of page
            self.startPage(),
            self.pagepath(d),
            self.title(d),
        ]
        return u'\n'.join(html)

    def editorheader(self, d, **kw):
        html = [
            self.msg(d),
            # Start of page
            self.startPage(),
        ]
        return u'\n'.join(html)

    def footer(self, d, **keywords):
        """ Assemble wiki footer
        
        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        html = [
            # End of page
            self.pageinfo(page),
            self.endPage(),

            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),

            # Footer
            u'<div id="footer">',
            u'</div>',

            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)


    def actionbar(self, d, **kw):
        parts = (
                self.edit_link(d, *kw), ' ',
                self.info_link(d, *kw), ' ',
#                self.attach_link(d, *kw),
                self.more_link(d, *kw),
        )
        return '<div id="iconbar">%s</div>' % ''.join(parts)

    def externalScript(self, d):
        return u''

    def guiEditorScript(self, d):
        return u''

    def headscript(self, d):
        return u''

    def loggededitbar(self, d):
        """Display edit bar only for the logged in users"""
        if self.request.user.valid:
            return self.editbar(d)
        else:
            return ''

    def recentchanges_entry(self, d):
        _ = self.request.getText
        if d['comments']:
            rccomm = ''
            for c in d['comments']:
                rccomm += ' <b>%d</b> ' % c[0];
                rccomm += c[1];
        else:
            rccomm = ''
        html = (u'''<li><b class="rctime">%s</b> %s %s . . . . <span class="rcauth">%s</span> <i class="rccomm">%s</i></li>''' % (
            d['time_html'],
            d['pagelink_html'],
            d['icon_html'],
            ', '.join(d['editors']),
            rccomm,
        ))
        return html

    def recentchanges_daybreak(self, d):
        return u'</ul><h2 class="rcdaybreak">%s</h2><ul>' % d['date']

    def recentchanges_header(self, d):
        return u'<div class="recentchanges"%s><ul>' % self.ui_lang_attr()

    def recentchanges_footer(self, d):
        return u'</ul></div>'

    def login(self, d):
        request = self.request
        _ = request.getText
        
        if request.user.valid and request.user.name:
            return u''
        reg_link = d['page'].link_to(
                request,
                text=_('Create account'),
                querystr={'action': 'newaccount'},
                id='newaccount',
                rel='nofollow')

        return '''
<form action="" method="POST" id="loginform">
<div lang="en" dir="ltr">
    %s
    <fieldset><legend>Login</legend>
    <input type="hidden" name="action" value="login">
    <label>%s<input type="text" name="name" id="loginname"></label>
    <label>%s<input type="password" name="password" id="loginpass"></label>
    </fieldset>
    <input type="submit" name="login" value="Login" id="loginsubmit">
</div>
</form>
''' % (reg_link, _('User'), _('Password'))

    def info_link(self, d, **keywords):
        _ = self.request.getText
        page = d['page']
        if not self.shouldShowEditbar(page):
            return u''
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=info')
        text = _('Info', formatted=False)
        attrs = {'id': "infolink"}
        return wikiutil.link_tag(self.request, params, text, **attrs)

    def edit_link(self, d, **keywords):
        _ = self.request.getText
        page = d['page']
        text = _('Edit', formatted=False)
#        if not self.shouldShowEditbar(page):
#            return u''
        if not (page.isWritable() and
                self.request.user.may.write(page.page_name)):
            return u'<span id="editlink">%s</span>' % text
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=edit')
        attrs = {'id': "editlink"}
        return wikiutil.link_tag(self.request, params, text, **attrs)


    def more_link(self, d, **keywords):
        _ = self.request.getText
        page = d['page']
        if not self.shouldShowEditbar(page):
            return u''
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=allactions')
        text = _('Other', formatted=False)
        attrs = {'id': "otherlink"}
        return wikiutil.link_tag(self.request, params, text, **attrs)

    def attach_link(self, d, **keywords):
        _ = self.request.getText
        page = d['page']
        if not self.shouldShowEditbar(page):
            return u''
        if not (page.isWritable() and
                self.request.user.may.write(page.page_name)):
            return u''
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=AttachFile')
        text = _('Attach', formatted=False)
        attrs = {'id': "attachlink"}
        return wikiutil.link_tag(self.request, params, text, **attrs)

    def pagepath(self, d):
        """ Assemble the title (now using breadcrumbs)
        
        @param d: parameter dictionary
        @rtype: string
        @return: title html
        """
        _ = self.request.getText
        content = []
        if d['title_text'] == d['page_name']: # just showing a page, no action
            curpage = ''
            segments = d['page_name'].split('/')
            for s in segments[:-1]:
                curpage += s
                content.append("%s" % Page(self.request, curpage).link_to(self.request, s))
                content.append("/")
                curpage += '/'

        html = '''
<div id="pagepath">
%s
</div>
''' % "".join(content)
        return html

    def title(self, d):
        """ Assemble the title (now using breadcrumbs)
        
        @param d: parameter dictionary
        @rtype: string
        @return: title html
        """
        title = d['title_text'].split('/')[-1]
        html = '<h1 id="pagelocation">%s</h1>' % title
        return html

def execute(request):
    """ Generate and return a theme object
        
    @param request: the request object
    @rtype: Theme instance
    @return: Theme object
    """
    return Theme(request)


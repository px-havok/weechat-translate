## Language translation, by Niels, niels@w3b.net, license is GPL3.
# v0.0.3: Updated to support Python3 -@pX <px@havok.org> 03.30.2019
# v0.0.4: Py3 translate would fail if input included accented
#       : characters -@pX <px@havok.org> 04.01.2019
#       : py3-ok

import weechat
import sys

# try for py2 urllib2, else load py3 urllib
try:
    import urllib2
    ulib = urllib2
except:
    import urllib.request
    ulib = urllib.request

weechat.register('tr', 'Translator', '0.0.3', 'GPL3', 'Google Translate Script', '', '')

def timer_cb(data, remaining_calls):
    weechat.prnt(weechat.current_buffer(), '%s' % data)
    return weechat.WEECHAT_RC_OK

weechat.hook_timer(2000, 0, 1, 'timer_cb', '/tr:\t/tr, Google Translate in Weechat')

def tr_cb(data, buffer, args):
    a = args.split(' ')
    if len(a) < 2:
        weechat.prnt(weechat.current_buffer(), '/tr:\tUsage /tr lang[,lang] text')
        return weechat.WEECHAT_RC_OK

    o = 'nl'
    l = a[0]
    ol = l.split(',')
    tl = ol[0]

    if len(ol) > 1:
        o = ol[1]

    # fix py3 translation issue, else py2
    if sys.version_info >= (3,3):
        t = urllib.parse.quote(' '.join(a[1:]))
    else:
        t = ' '.join(a[1:])

    url = 'https://translate.googleapis.com/translate_a/single' + \
        '?client=gtx&sl=' + o + '&tl=' + tl + '&dt=t&q=' + t
    url = url.replace(' ', '%20')

    req = ulib.Request(url)

    req.add_header('User-Agent', 'Mozilla/5.0')

    response = ulib.urlopen(req)

    html = response.read()

    # support for py3, else py2
    if sys.version_info >= (3, 3):
        tr = html.decode().split('"')[1]
    else:
        tr = html.split('"')[1]

    if tr != 'nl':
        if o == 'nl':
            weechat.command(weechat.current_buffer(), '%s' % tr)
        else:
            weechat.prnt(weechat.current_buffer(), '/tr:\t%s' % tr)
    return weechat.WEECHAT_RC_OK

weechat.hook_command('tr', 'Google Translator', 'lang[,lang] text',
    'Language codes: https://sites.google.com/site/tomihasa/google-language-codes\n'
    'Github: https://github.com/nkoster/weechat-translate', '', 'tr_cb', '')

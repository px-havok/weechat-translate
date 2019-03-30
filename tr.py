## Language translation, by Niels, niels@w3b.net, license is GPL3.
# v0.0.3: Updated to support Python3 -@pX <px@havok.org>

import weechat
import sys

try:
    import urllib2
    ulib2 = True
except:
    import urllib.request
    ulib2 = False

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
    t = ' '.join(a[1:])
    url = 'https://translate.googleapis.com/translate_a/single' + \
        '?client=gtx&sl=' + o + '&tl=' + tl + '&dt=t&q=' + t
    url = url.replace(' ', '%20')

    if ulib2:
        req = urllib2.Request(url)
    else:
        req = urllib.request.Request(url)

    req.add_header('User-Agent', 'Mozilla/5.0')

    if ulib2:
        response = urllib2.urlopen(req)
    else:
        response = urllib.request.urlopen(req)

    html = response.read()

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

weechat.hook_command('tr', '', 'lang[,lang] text', \
    'Language codes: https://sites.google.com/site/tomihasa/google-language-codes\n'
    'Github: https://github.com/nkoster/weechat-translate\n', '', 'tr_cb', '')

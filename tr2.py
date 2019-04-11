#####################################################################
# Original 44 (v.0.0.2) lines of code were written by:              #
# Language translation, by Niels, niels@w3b.net, license is GPL3.   #
# https://github.com/nkoster/weechat-translate                      #
# 03.30.2019:                                                       #
# v0.0.3: Updated to support Python3 -@pX <px@havok.org> 03.30.2019 #
# v0.0.4: Py3 translate would fail if input included accented       #
#       : characters -@pX <px@havok.org> 04.01.2019                 #
#       : py3-ok                                                    #
#                                                                   #
#####################################################################
# [tr2] versions .01+ are (c) 2019 pX <px@havok.org>                #
# Find me in #pX on EFNet.                                          #
# License: GPL3 - https://www.gnu.org/licenses                      #
#                                                                   #
# [tr2] Translaion made simple.                                     #
# [tr2] uses google api for translations.                           #
# [tr2] use: /tr es Hello my friend!                                #
#      returns: Hola mi amigo!                                      #
# [tr2] use: /tr en,es Hola mi amigo!                               #
#      returns: Hello my friend!                                    #
# [tr2] will automatically translate incoming msgs if applicable.   #
#                                                                   #
# https://sites.google.com/site/tomihasa/google-language-codes      #
# https://github.com/px-havok/weechat-translate                     #
#                                                                   #
# 04.01.2019: px@havok.org                                          #
#   v0.1: Added auto-translate using 'langdetect'                   #
#       : Created functions for translate and autotranslate         #
# 04.03.2019:                                                       #
#   v0.2: Wrote regex to:                                           #
#           + strip all numbers and non-word symbols from message   #
#             to improve accurracy and decrease false-positives.    #
#           + If msg starts with '<word>:' assume its a nick and    #
#             strip up to and including the ':'.                    #
#           + If msg starts with . or ! then assume its a bot cmd   #
#             and strip up to and including first whitespace.       #
# 04.04.2019:                                                       #
#       : Added configurable options for: default language,         #
#       : autotranslate on/off, and translate while away on/off.    #
# 04.08.2019:                                                       #
#       : fixed sanitation order.                                   #
#                                                                   #
# KNOWN ISSUES:                                                     #
#   Some languages come through as a long string which cannot be    #
#   split, making it difficult to determine if they should be       #
#   autotranslated.  It's easier to just do a detect() to see if it #
#   it exitsts in the 'somelang' list and setting 'ch = True' if    #
#   it does.  Added so far:                                         #
#   [zh-cn, zh-tw, ja, ko]                                          #
#                                                                   #
#####################################################################

# ===================[ imports ]===================

try:
    import weechat
    import sys
    import re
except:
    print("WeeChat (https://weechat.org) required.")
    quit()

if sys.version_info >= (3,):
    import urllib.request as ulib
    import urllib.parse
else:
    import urllib2 as ulib

try:
    from langdetect import detect
    from langdetect import DetectorFactory
    langdetect = True
except:
    weechat.prnt('', "'langdetect' not found, %sautotranslate disabled%s."
                    % (weechat.color('red'), weechat.color('reset')))
    langdetect = False


# ===================[script info]===================

SCRIPT_NAME     = 'tr'
SCRIPT_VERSION  = '0.2'
SCRIPT_AUTHOR   = 'pX @ EFNet'
SCRIPT_DESC     = '[tr2] - Translation made simple.'
SCRIPT_LICENSE  = 'GPL3'


# ===================[settings]===================
SETTINGS = {
    'auto_trans'        : ('off', 'autotranslate incoming text'),
    'auto_trans_away'   : ('off', 'autotranslate while "/away"?'),
    'default_lang'      : ('en', 'default language code.  "/help tr" for codes'),
    }

somelang = ['zh-tw', 'zh-cn', 'ja', 'ko']

# ===================[functions]===================

def py3():
    if sys.version_info >= (3,0):
        return True


# called when /tr is executed
def tr_cb(data, buffer, args):
    arglist = args.split(' ')
    if len(arglist) < 2:
        weechat.prnt(weechat.current_buffer(), '[tr2]\tUsage /tr lang[,lang] text')
        return weechat.WEECHAT_RC_OK

    langlist = arglist[0].split(',')
    transto = langlist[0]
    transfrom = weechat.config_get_plugin('default_lang')
    if len(langlist) > 1:
        transfrom = langlist[1]

    # text formatted for py2, unless we're using py3
    text = ' '.join(arglist[1:])
    if py3():
        text = urllib.parse.quote(text)

    tr = translate(transfrom, transto, text)

    if tr:
        if len(langlist) > 1:
            weechat.prnt(buffer, '[tr2]\t%s' % tr)
        else:
            weechat.command(weechat.current_buffer(), '%s' % tr)
    else:
        weechat.prnt(weechat.current_buffer(), 'Query failed. '
                   'Please make sure you are using correct language codes.  '
                   '"/help tr" for options.' )

    return weechat.WEECHAT_RC_OK


# translate the text
def translate(transfrom, transto, text):
    url = ('https://translate.googleapis.com/translate_a/single'
        '?client=gtx&sl=' + transfrom + '&tl=' + transto + '&dt=t&q=' + text)
    url = url.replace(' ', '%20')

    try:
        req = ulib.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0')
        response = ulib.urlopen(req)
    except:
        weechat.prnt(weechat.current_buffer(), "[tr2]\tURL unavailble or error in syntax.  Query failed. :'(")
        return weechat.WEECHAT_RC_OK

    html = response.read()

    if py3():
        tr = html.decode().split('"')[1]
    else:
        tr = html.split('"')[1]

    return tr


def sanitize(message):
    m = re.sub(r'^[^:]*: ', '', message)
    m = re.sub(r'^[.!].*?(?=\s)', '', m)
    m = re.sub(r'[]+=_.:,;"!@#$%^&*()<>\\/{}[]*\d*', '', m)
    return m


# 'langdetect' required to autotrans incoming messages
def autoTrans(data, buffer, date, tags, displayed, highlight, prefix, message):

    if weechat.config_get_plugin('auto_trans') == 'off':
        return weechat.WEECHAT_RC_OK

    if (weechat.config_get_plugin('auto_trans_away') == 'off'
            and weechat.buffer_get_string(buffer, 'localvar_away')):
        return weechat.WEECHAT_RC_OK

    DetectorFactory.seed = 0

    m = sanitize(message)

    if py3():
        msg = m
    else:
        msg = m.decode('utf-8')

    if not len(m.strip()):
        return weechat.WEECHAT_RC_OK

    ch = False
    try:
        if detect(msg) in somelang:
            ch = True
    except:
        return weechat.WEECHAT_RC_OK

    msgb = msg.split()

    if len(msgb) >= 3 or ch:

        try:
            lang = detect(msg)
        except:
            return weechat.WEECHAT_RC_OK

        if lang != weechat.config_get_plugin('default_lang'):
            transfrom = 'auto'
            transto = weechat.config_get_plugin('default_lang')
            text = m
            if py3():
                text = urllib.parse.quote(text)

            tr = translate(transfrom, transto, text)

            # when langdetect is inaccurate, google sometimes returns the
            # string it was sent, if that's the case, drop it.
            if tr:
                if tr[1:] in m:
                    return weechat.WEECHAT_RC_OK

            weechat.prnt(buffer, "[autotr]\t%s: %s" % (lang, tr))

    return weechat.WEECHAT_RC_OK


def timer_cb(data, remaining_calls):
    weechat.prnt(weechat.current_buffer(), '%s' % data)
    return weechat.WEECHAT_RC_OK


def initsettings():
    for option, value in SETTINGS.items():

        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, value[0])
            SETTINGS[option] = value[0]
            weechat.config_set_desc_plugin(option, value[1] + ' [default: ' + value[0] + ']')
        else:
            SETTINGS[option] = weechat.config_get_plugin(option)


# ===================[main stuff]===================
if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):

        initsettings()

        weechat.hook_timer(2000, 0, 1, 'timer_cb', '[tr2]\t/tr, Translation made simple.\n'
                            '[tr2]\tOptions: /fset python.tr.')

        weechat.hook_command(SCRIPT_NAME, SCRIPT_DESC, 'lang[,lang] text',
            'Language codes: https://sites.google.com/site/tomihasa/google-language-codes\n'
            'Github: https://github.com/nkoster/weechat-translate\n'
            'Github: https://github.com/px-havok/weechat-translate\n'
            '"/fset python.tr." to configure [tr2]', '', 'tr_cb', '')

        # if 'langdetect' library is installed, hook incoming messages to autoTrans()
        if langdetect:
            weechat.hook_print('', 'notify_message', '', 1, 'autoTrans', '')

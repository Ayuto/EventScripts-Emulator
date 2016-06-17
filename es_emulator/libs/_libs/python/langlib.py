
from configobj import ConfigObj
from string import Template


# just include English by default
languages = {}
languages["english"] = {}
languages["english"]["id"] = "en"
languages["english"]["display"] = "English"

def loadLanguages(filename):
    global languages
    languages = ConfigObj(filename)

def getLanguages():
    return languages

def getLangAbbreviation(full):
    myl = str(full).lower()
    if myl in languages:
      return languages[myl]["id"]
    else:
      import es
      es.dbgmsg(0, 'langlib: Unrecognized language "' + myl + '"')
      return getDefaultLang()

langdefaultcallback = None
def setDefaultLangCallback(callback):
    global langdefaultcallback
    langdefaultcallback = callback

def getDefaultLang():
    if langdefaultcallback:
      return langdefaultcallback()
    else:
      return "en"


class Strings(ConfigObj):
    # this is used when all else fails
    fallback = "en"
    # this should be set to your default if nothing is provided
    expanddefault = "en"
    def __getitem__(self, name):
        if name in self:
            return super(Strings, self).__getitem__(name)
        else:
            return super(Strings, self).__getitem__(self.fallback)
    def expand(self, text, opts=None, lang=''):
        k = self[text]
        s = None
        val = None
        # without a working language, use the class default
        if not lang:
          lang = getDefaultLang()
        lang = str(lang).lower()
        # if the one they provided didn't work, use fallback
        if lang not in k:
            val = self[text][self.fallback]
        else:
            val = self[text][lang]
        if opts:
            s = Template(val)
            return s.substitute(opts)
        else:
            return val
    def setFallbackLang(self, language_abbreviation):
        fallback = language_abbreviation
    def __call__(self, text, opts=None, lang=''):
        return self.expand(text, opts, lang)

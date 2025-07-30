import os, re
from os.path import join, basename, exists
from .soup import Soup

class Ref:
    cli       = None
    raw:str   = ''
    soup:Soup = None
    _content  = None
    _bloked   = False

    def __init__(self, fpath , cli , space ):
        self.space    = space
        self.cli      = cli
        self.settings = cli.settings
        self.fpath    = fpath
        self.basename = basename(fpath)

        parts         = self.basename.split(".")
        self.name     = parts[0]
        self.lang     = 'xml' if len(parts) == 1 else parts[-1]

        # for non readable files
        self.justy_copy = False
        try:
            with open(self.fpath, 'rb') as f:
                while chunk := f.read(4096):
                    chunk.decode('utf-8')
        except UnicodeDecodeError:
            self.justy_copy = True


    def __repr__( self ):
        return f"<ref link='{self.name}' />"

    def _compile(self):
        if self._content != None:
            return

        with open(self.fpath,'r') as f:
            self.raw = f.read()

        self.soup    = Soup( self.raw , logger = self.settings.log )
        self._bloked = True

        for t in self.soup.refs():
            self.settings.log(f"     {t}" , color = 'green' )
            s    = t.get('space',self.space)
            name = t.ref()

            if s in self.cli._spaces \
               and not s in self.cli._refs:

                self.settings.log(f" -- ref is located in subrepo {s}" ,color='yellow')
                # append subrepos references
                self.cli._append_refs( s ,
                    join( self.cli._spaces[s]['path'],
                        '.ymvas',
                        'references'
                    )
                )

            for r in self.cli._refs.get(s,[]):
                if r.name == name:

                    # ---- data
                    self.settings.log(
                        f"  Found ref match [{r.fpath}]" ,
                        color = 'yellow'
                    )

                    if r is self:
                        t.set_replace(r.raw,r.lang)
                        break

                    t.set_replace(r.content,r.lang)
                    break

        self._content = self.soup.to_string()
        self._bloked  = False

    @property
    def content(self):
        if self._bloked:
            soup = Soup(self.raw)
            for t in soup.refs():
                t.set_replace('')
            return soup.to_string()
        self._compile()
        return self._content

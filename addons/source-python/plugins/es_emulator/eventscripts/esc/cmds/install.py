from . import Command

@Command(con=True, desc='Installs approved addons from the ESAM')
def install(argv):
  pass
  
@Command(con=True, desc='Uninstalls addons installed with es_install')
def uninstall(argv):
  pass

@Command(con=True, desc='Updates addons installed with es_install')
def update(argv):
  pass

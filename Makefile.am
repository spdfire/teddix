if LINUX 
CFG2HTML = src/extern/linux/cfg2html
endif
if AIX 
CFG2HTML = src/extern/aix/cfg2html
endif
if SUNOS 
CFG2HTML = src/extern/sunos/cfg2html
endif
if HPUX
CFG2HTML = src/extern/hpux/cfg2html
endif
if DARWIN
CFG2HTML = src/extern/darwin/cfg2html
endif


# bin scripts 
bin_SCRIPTS = build/TeddixServer build/TeddixAgent src/extern/ora2html $(CFG2HTML)

init_ddir = $(sysconfdir)/init.d
init_d_SCRIPTS = init.d/TeddixAgent init.d/TeddixServer

teddixconfdir=$(sysconfdir)/teddix
teddixconf_DATA = config/teddix.conf config/serverlist

teddixlogdir = $(localstatedir)/log/teddix

# libteddix
libteddix_PYTHON = src/TeddixLogger.py \
						 src/TeddixConfigFile.py \
						 src/TeddixInventory.py \
						 src/TeddixLinux.py \
						 src/TeddixAix.py \
						 src/TeddixDarwin.py \
						 src/TeddixHPUX.py \
						 src/TeddixSunOS.py \
						 src/TeddixWindows.py 

libteddixdir = $(pythondir)/teddix

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
						-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
						-e 's,[@]VERSION[@],$(VERSION),g' 

#do_substitution = sed -i 's,[@]pythondir[@],$(pythondir),g' \
#						-i 's,[@]PACKAGE[@],$(PACKAGE),g' \
#						-i 's,[@]VERSION[@],$(VERSION),g'

CLEANDIRS = build/*
clean-local:
	test -e "$(CLEANDIRS)" || rm -rf $(CLEANDIRS)
	test -d build || rmdir build

#install-exec-local:
#	$(mkinstalldirs) $(DESTDIR)$(localstatedir)/lib/teddix/archive
#	echo "Teddix workdir" > $(DESTDIR)$(localstatedir)/lib/teddix/.placekeeper

build/TeddixServer: Makefile
	test -e build || mkdir build
	$(do_substitution) src/TeddixServer.py > build/TeddixServer 
	$(do_substitution) src/TeddixAgent.py > build/TeddixAgent 
	$(do_substitution) src/TeddixCron.py > build/TeddixCron
	chmod +x $(bin_SCRIPTS) 

#make -f Makefile.cfg2html build 
#make -f Makefile.ora2html build 

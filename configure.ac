#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.59])
AC_INIT(teddix, 2.0, spdfire@plusinfinity.org)
AM_INIT_AUTOMAKE
AC_CONFIG_FILES([Makefile])

# macro that checks for specific modules in python
AC_DEFUN([AC_PYTHON_MODULE],
			[AC_MSG_CHECKING(for python module $1)
			echo "import $1" | python - >/dev/null 2>/dev/null
			if test $? -ne 0 ; then
				AC_MSG_RESULT(not found)
				AC_MSG_ERROR(You need $1 python module to build this package!)
				fi
				AC_MSG_RESULT(found)
				])

# Python version
AM_PATH_PYTHON(2.6)

# TCPServer 
AC_PYTHON_MODULE(Queue)
AC_PYTHON_MODULE(socket)
AC_PYTHON_MODULE(threading)
AC_PYTHON_MODULE(SocketServer)

# Daemon 
AC_PYTHON_MODULE(os)
AC_PYTHON_MODULE(grp)
AC_PYTHON_MODULE(pwd)
AC_PYTHON_MODULE(sys)
AC_PYTHON_MODULE(time)
AC_PYTHON_MODULE(signal)
AC_PYTHON_MODULE(daemon)
AC_PYTHON_MODULE(logging)
AC_PYTHON_MODULE(inspect)
AC_PYTHON_MODULE(lockfile)
AC_PYTHON_MODULE(subprocess)

# ConfigParser & OptionParser 
AC_PYTHON_MODULE(optparse)
AC_PYTHON_MODULE(ConfigParser)

# Inventory 
AC_PYTHON_MODULE(re)
AC_PYTHON_MODULE(psutil)
AC_PYTHON_MODULE(platform)
AC_PYTHON_MODULE(dmidecode)
AC_PYTHON_MODULE(subprocess)
AC_PYTHON_MODULE(xml.dom.minidom)
AC_PYTHON_MODULE(xml.etree.ElementTree)

# Checks for programs.
AC_PROG_AWK
AC_PROG_SED
AC_PROG_INSTALL
AC_PROG_GREP
AC_PROG_MKDIR_P
AC_PROG_MAKE_SET
AC_CANONICAL_HOST

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

# OS dependend 
case "$host_os" in
linux-gnu)
	AC_DEFINE(LINUX,1,[This is a GNU/Linux system])
	AM_CONDITIONAL(LINUX, true)
	AM_CONDITIONAL(SUNOS, false)
	AM_CONDITIONAL(DARWIN, false)
	AM_CONDITIONAL(AIX, false)
	AM_CONDITIONAL(HPUX, false)
	;;
solaris)
	AC_DEFINE(SUNOS,1,[This is Solaris system])
	AM_CONDITIONAL(LINUX, false)
	AM_CONDITIONAL(SUNOS, true)
	AM_CONDITIONAL(DARWIN, false)
	AM_CONDITIONAL(AIX, false)
	AM_CONDITIONAL(HPUX, false)
	;;
darwin)
	AC_DEFINE(DARWIN,1,[This is macos system])
	AM_CONDITIONAL(LINUX, false)
	AM_CONDITIONAL(SUNOS, false)
	AM_CONDITIONAL(DARWIN, true)
	AM_CONDITIONAL(AIX, false)
	AM_CONDITIONAL(HPUX, false)
	;;
aix)
	AC_DEFINE(DARWIN,1,[This is aix system])
	AM_CONDITIONAL(LINUX, false)
	AM_CONDITIONAL(SUNOS, false)
	AM_CONDITIONAL(DARWIN, false)
	AM_CONDITIONAL(AIX, true)
	AM_CONDITIONAL(HPUX, false)
	;;
hpux)
	AC_DEFINE(HPUX,1,[This is hpux system])
	AM_CONDITIONAL(LINUX, false)
	AM_CONDITIONAL(SUNOS, false)
	AM_CONDITIONAL(DARWIN, false)
	AM_CONDITIONAL(AIX, false)
	AM_CONDITIONAL(HPUX, true)
	;;

*)
	AC_MSG_ERROR(Unrecognised OS: $host_os)
	;;
esac

AC_OUTPUT

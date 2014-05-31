Summary:            Teddix server 
Name:               teddix-server
Version:            2.0
Release:            1%{?dist}
License:            BSD2
Source:             http://www.teddix.info/download/stable/%{name}-%{version}.tar.gz
BuildRequires:      python
Requires:           python
Requires:           python-daemon
Requires:           python-lockfile
Requires:           libxml2-python
Requires:           MySQL-python
Requires:           mysql
Requires:           mysql-server
Requires:           teddix-common

%description
The Teddix Agent is a program that allows the user to collect 
System/Software/Hardware informations from system 

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build  

%install
rm -rf %{buildroot}
python setup.py install --root %{buildroot} 

%clean
rm -rf %{buildroot}

%post
echo ""
echo "----------------------------------------------------------------"
echo "   Database configuration: "
echo "      CREATE DATABASE teddix;  "
echo "      CREATE USER 'teddix'@'localhost' IDENTIFIED BY 'mypass';  "
echo "      GRANT ALL PRIVILEGES ON teddix.* To 'teddix'@'localhost'; "
echo ""
echo "   Import tables: "
echo "      $ mysql -u root < /usr/share/teddix/initdb.sql "
echo ""
echo "----------------------------------------------------------------"
echo ""

%files
%defattr(-, root, root, -)
%{_bindir}/*
%{python_sitelib}/teddix_server*
%{_sysconfdir}/init.d/* 
%{_datarootdir}/teddix/*.sql

%changelog
* Fri Feb 08 2013 spdfire <spdfire@plusinfinity.org> 2.0
- Initial SPEC file


Summary:            Teddix Agent 
Name:               teddix-agent
Version:            2.0alpha2
Release:            1%{?dist}
License:            BSD2
Source:             http://www.teddix.info/download/stable/%{name}-%{version}.tar.gz
BuildRequires:      python
Requires:           python
Requires:           python-daemon
Requires:           python-lockfile
Requires:           libxml2-python 
Requires:           openssl
Requires:           cfg2html-linux
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
[ ! -d /etc/teddix ] && mkdir /etc/teddix
[ ! -f /etc/teddix/teddix.conf ] && cp -v /usr/share/teddix/teddix.conf /etc/teddix/teddix.conf
[ ! -f /etc/init.d/teddix-agent ] && cp -v /usr/share/teddix-agent/init.d/teddix-agent.rhel /etc/init.d/teddix-agent 
chmod +x /etc/init.d/teddix-agent

%files
%defattr(-, root, root, -)
%{_bindir}/*
%{python_sitelib}/teddix_agent*
%{_sysconfdir}/init.d/* 

%changelog
* Tue Jun 3 2014 spdfire <spdfire@plusinfinity.org> 2.0alpha1
- Initial SPEC file


Summary:            Teddix Agent 
Name:               teddix-agent
Version:            2.0
Release:            1%{?dist}
License:            BSD2
Source:             http://www.teddix.info/download/stable/%{name}-%{version}.tar.gz
BuildRequires:      python
Requires:           python
Requires:           python-daemon
Requires:           python-lockfile
Requires:           libxml2-python 
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

%files
%defattr(-, root, root, -)
%{_bindir}/*
%{python_sitelib}/teddix_agent*
%{_sysconfdir}/init.d/* 

%changelog
* Fri Feb 08 2013 spdfire <spdfire@plusinfinity.org> 2.0
- Initial SPEC file


Summary:            Teddix common 
Name:               teddix-common
Version:            2.0
Release:            1%{?dist}
License:            BSD2
Source:             file:///data/%{name}-%{version}.tar.gz
BuildRequires:      python
Requires:           python
Requires:           python-dmidecode
Requires:           python-psutil
Requires:           python-netifaces
Requires:           net-tools
Requires:           iproute
Requires:           pciutils
Requires:           ethtool
Requires:           kmod
Requires:           coreutils

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
%{python_sitelib}/teddix/*
%{python_sitelib}/teddix-*

%changelog
* Fri Feb 08 2013 spdfire <spdfire@plusinfinity.org> 2.0
- Initial SPEC file


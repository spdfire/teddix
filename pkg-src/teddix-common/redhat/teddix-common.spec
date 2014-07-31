Summary:            Teddix common 
Name:               teddix-common
Version:            2.0alpha2
Release:            1%{?dist}
License:            BSD2
Source:             http://www.teddix.info/download/stable/%{name}-%{version}.tar.gz
BuildRequires:      python
Requires:           python
Requires:           python-dmidecode
Requires:           python-psutil
Requires:           python-netifaces
Requires:           libxml2-python 
Requires:           MySQL-python
Requires:           net-tools
Requires:           iproute
Requires:           pciutils
Requires:           ethtool
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

%post
[ ! -d /etc/teddix ] && mkdir /etc/teddix
[ ! -f /etc/teddix/teddix.conf ] && cp /usr/share/teddix/teddix.conf /etc/teddix/

%files
%defattr(-, root, root, -)
%{python_sitelib}/teddix/*
%{python_sitelib}/teddix-*
%{_datarootdir}/teddix/*.conf

%changelog
* Tue Jun 3 2014 spdfire <spdfire@plusinfinity.org> 2.0alpha1
- Initial SPEC file


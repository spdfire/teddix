Summary:            Teddix common 
Name:               teddix-common
Version:            2.0
Release:            1%{?dist}
License:            BSD2
Source:             file:///data/%{name}-%{version}.tar.gz
BuildRequires:      make
BuildRequires:      gawk
BuildRequires:      wget
BuildRequires:      unzip
BuildRequires:      python
BuildRequires:      python-daemon
BuildRequires:      python-dmidecode
BuildRequires:      python-lockfile
BuildRequires:      python-psutil
Requires:           python
Requires:           python-daemon
Requires:           python-dmidecode
Requires:           python-lockfile
Requires:           python-psutil
Requires:           python-netifaces
Requires:           python-usb

%description
The Teddix Agent is a program that allows the user to collect 
System/Software/Hardware informations from system 

%prep
%setup -q -n %{name}-%{version}

%build
%configure
make  

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install 

%clean
rm -rf %{buildroot}

%files
%defattr(-, root, root, -)
%{python_sitelib}/%{name}/*

%changelog
* Fri Feb 08 2013 spdfire <spdfire@plusinfinity.org> 2.0
- Initial SPEC file


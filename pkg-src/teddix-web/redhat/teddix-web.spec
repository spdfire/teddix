Summary:            Teddix web 
Name:               teddix-web
Version:            2.0alpha1
Release:            1%{?dist}
License:            BSD2
Source:             http://www.teddix.info/download/stable/%{name}-%{version}.tar.gz
BuildRequires:      python
Requires:           python
Requires:           python-pygal
Requires:           Django
Requires:           python-flup
Requires:           nmap
Requires:           tcptraceroute
Requires:           curl
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
chmod 777 /usr/share/teddix-web/teddixweb/static/charts

[ -d /etc/teddix ] || mkdir /etc/teddix
[ -f /etc/teddix/websettings.py ] || cp /usr/share/teddix/websettings.py /etc/teddix/ 
chmod 600 /etc/teddix/websettings.py


%files
%defattr(-, root, root, -)
%{python_sitelib}/teddix_web*
%{_sysconfdir}/init.d/*
%{_datarootdir}/teddix-web/*
%{_datarootdir}/teddix/websettings.py

%changelog
* Tue Jun 3 2014 spdfire <spdfire@plusinfinity.org> 2.0alpha1
- Initial SPEC file


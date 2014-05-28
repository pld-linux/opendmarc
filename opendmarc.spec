Summary:	DMARC milter and library
Name:		opendmarc
Version:	1.2.0
Release:	0.1
License:	BSD
Group:		Daemons
Source0:        http://downloads.sourceforge.net/opendmarc/%{name}-%{version}.tar.gz
# Source0-md5:	bad2c454841cf7711fc148e114620051
URL:		http://www.trusteddomain.org/opendmarc.html
Requires:	lib%{name} = %{version}-%{release}
BuildRequires:	mysql-devel
BuildRequires:	sendmail-devel
BuildRequires:	openssl-devel
BuildRequires:	libtool
BuildRequires:	pkgconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
OpenDMARC (Domain-based Message Authentication, Reporting &
Conformance) provides an open source library that implements the DMARC
verification service plus a milter-based filter application that can
plug in to any milter-aware MTA, including sendmail, Postfix, or any
other MTA that supports the milter protocol.

The DMARC sender authentication system is still a draft standard,
working towards RFC status.

%package -n libopendmarc
Summary:	An open source DMARC library
Group:		Libraries

%description -n libopendmarc
This package contains the library files required for running services
built using libopendmarc.

%package -n libopendmarc-devel
Summary:	Development files for libopendmarc
Group:		Development/Libraries
Requires:	libopendmarc = %{version}-%{release}

%description -n libopendmarc-devel
This package contains the static libraries, headers, and other support
files required for developing applications against libopendmarc.

%prep
%setup -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT%{_initrddir}
cp -p contrib/init/redhat/%{name} $RPM_BUILD_ROOT%{_initrddir}/%{name}
cp -p opendmarc/%{name}.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
# Set some basic settings in the default config file
perl -pi -e 's|^# (HistoryFile /var/run)/(opendmarc.dat)|$1/opendmarc/$2/;
             s|^# (Socket )|$1|;
             s|^# (UserId )|$1|;
            ' $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

install -p -d $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/%{name}.conf <<EOF
D %{_localstatedir}/run/%{name} 0700 %{name} %{name} -
EOF

mv $RPM_BUILD_ROOT%{_datadir}/doc/%{name} $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{version}
rm $RPM_BUILD_ROOT%{_libdir}/*.{la,a}

install -d $RPM_BUILD_ROOT%{_includedir}/%{name}
cp -p libopendmarc/dmarc.h $RPM_BUILD_ROOT%{_includedir}/%{name}/

install -d $RPM_BUILD_ROOT%{_localstatedir}/spool/%{name}
install -d $RPM_BUILD_ROOT%{_localstatedir}/run/%{name}


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
	useradd -r -g %{name} -G mail -d %{_localstatedir}/run/%{name} -s /sbin/nologin \
	-c "OpenDMARC Milter" %{name}
exit 0

%post
/sbin/chkconfig --add %{name} || :

%preun
if [ $1 -eq 0 ]; then
	service %{name} stop >/dev/null || :
	/sbin/chkconfig --del %{name} || :
fi
exit 0

%postun
if [ "$1" -ge "1" ] ; then
	%service %{name} condrestart >/dev/null 2>&1 || :
fi
exit 0

%post -n libopendmarc -p /sbin/ldconfig
%postun -n libopendmarc -p /sbin/ldconfig


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc INSTALL README RELEASE_NOTES docs/draft-dmarc-base-00-02.txt
%doc db/README.schema db/schema.mysql
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%{_initrddir}/%{name}
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/*/*
%dir %attr(-,%{name},%{name}) %{_localstatedir}/spool/%{name}
%dir %attr(-,%{name},%{name}) %{_localstatedir}/run/%{name}

%files -n libopendmarc
%defattr(644,root,root,755)
%{_libdir}/libopendmarc.so.*

%files -n libopendmarc-devel
%defattr(644,root,root,755)
%doc libopendmarc/docs/*.html
%{_includedir}/%{name}
%{_libdir}/*.so

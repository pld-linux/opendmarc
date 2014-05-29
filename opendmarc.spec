# TODO
# - pld useradd/groupadd and register uid/gid
# - pldize initscript
Summary:	DMARC milter and library
Name:		opendmarc
Version:	1.2.0
Release:	0.1
License:	BSD
Group:		Daemons
Source0:	http://downloads.sourceforge.net/opendmarc/%{name}-%{version}.tar.gz
# Source0-md5:	bad2c454841cf7711fc148e114620051
URL:		http://www.trusteddomain.org/opendmarc.html
BuildRequires:	libtool
BuildRequires:	mysql-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sendmail-devel
Requires:	libopendmarc = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# unresolved __dn_expand, __dn_skipname, __res_query
%define		skip_post_check_so	libopendmarc.so.1.0.2

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
%configure \
	--disable-silent-rules \
	--disable-static
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -p contrib/init/redhat/%{name} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p opendmarc/%{name}.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
# Set some basic settings in the default config file
perl -pi -e 's|^# (HistoryFile /var/run)/(opendmarc.dat)|$1/opendmarc/$2/;
             s|^# (Socket )|$1|;
             s|^# (UserId )|$1|;
            ' $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

install -p -d $RPM_BUILD_ROOT%{systemdtmpfilesdir}
cat > $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf <<EOF
D %{_localstatedir}/run/%{name} 0700 %{name} %{name} -
EOF

rm $RPM_BUILD_ROOT%{_libdir}/*.la
# packaged as %doc
rm -r $RPM_BUILD_ROOT%{_docdir}/%{name}

install -d $RPM_BUILD_ROOT%{_includedir}/%{name}
cp -p libopendmarc/dmarc.h $RPM_BUILD_ROOT%{_includedir}/%{name}

install -d $RPM_BUILD_ROOT%{_localstatedir}/spool/%{name}
install -d $RPM_BUILD_ROOT%{_localstatedir}/run/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
	useradd -r -g %{name} -G mail -d %{_localstatedir}/run/%{name} -s /sbin/nologin \
	-c "OpenDMARC Milter" %{name}

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ $1 -eq 0 ]; then
	/sbin/chkconfig --del %{name}
	%service %{name} stop
fi

%post	-n libopendmarc -p /sbin/ldconfig
%postun	-n libopendmarc -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc INSTALL README RELEASE_NOTES docs/draft-dmarc-base-02.txt
%doc db/README.schema db/schema.mysql
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.conf
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/opendmarc
%attr(755,root,root) %{_sbindir}/opendmarc-check
%attr(755,root,root) %{_sbindir}/opendmarc-expire
%attr(755,root,root) %{_sbindir}/opendmarc-import
%attr(755,root,root) %{_sbindir}/opendmarc-importstats
%attr(755,root,root) %{_sbindir}/opendmarc-params
%attr(755,root,root) %{_sbindir}/opendmarc-reports
%{_mandir}/man5/opendmarc.conf.5*
%{_mandir}/man8/opendmarc*.8*
%{systemdtmpfilesdir}/%{name}.conf
%dir %attr(-,%{name},%{name}) %{_localstatedir}/spool/%{name}
%dir %attr(-,%{name},%{name}) %{_localstatedir}/run/%{name}

%files -n libopendmarc
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libopendmarc.so.*.*.*
%ghost %{_libdir}/libopendmarc.so.1

%files -n libopendmarc-devel
%defattr(644,root,root,755)
%doc libopendmarc/docs/*.html
%{_includedir}/%{name}
%{_libdir}/libopendmarc.so

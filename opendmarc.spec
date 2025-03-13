# TODO
# - pld useradd/groupadd and register uid/gid
# - pldize initscript
%define		ver 1-4-2
%define		ver_dot	%(echo %{ver} | tr '-' '.')
Summary:	DMARC milter and library
Name:		opendmarc
Version:	%{ver_dot}
Release:	2
License:	BSD
Group:		Daemons
Source0:	https://github.com/trusteddomainproject/OpenDMARC/archive/refs/tags/rel-%{name}-%{ver}.tar.gz
# Source0-md5:	658d951db84a0305b0c5d9312eff5b64
Source1:	%{name}.tmpfiles
Patch0:		ticket168.patch
Patch1:		ticket193.patch
Patch2:		ticket204.patch
Patch3:		ticket207.patch
Patch4:		ticket208.patch
Patch5:		ticket212.patch
Patch6:		insheader.patch
Patch7:		check_domain.patch
Patch8:		arcseal-segfaults.patch
Patch9:		conf_refcnt.patch
Patch10:	free-arcdomain.patch
Patch11:	arc-override-quarantine.patch
Patch12:	cleanup-buflen.patch
Patch13:	check-correct-domain.patch
Patch14:	arcares-segfaults.patch
Patch15:	parse-arc-leaks.patch
Patch16:	cve-2024-25768.patch
URL:		http://www.trusteddomain.org/opendmarc.html
BuildRequires:	libspf2-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sendmail-devel
Requires:	libopendmarc = %{version}-%{release}
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
%setup -q -n OpenDMARC-rel-%{name}-%{ver}
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1
%patch -P7 -p1
%patch -P8 -p1
%patch -P9 -p1
%patch -P10 -p1
%patch -P11 -p1
%patch -P12 -p1
%patch -P13 -p1
%patch -P14 -p1
%patch -P15 -p1
%patch -P16 -p1

%build
autoreconf -v -i
%configure \
	--disable-silent-rules \
	--disable-static \
	--with-spf \
	--with-spf2-include=%{_includedir}/spf2 \
	--with-spf2-lib=%{_libdir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/rc.d/init.d,%{systemdtmpfilesdir}} \
	$RPM_BUILD_ROOT%{_localstatedir}/{run,spool}/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p contrib/init/redhat/%{name} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p opendmarc/%{name}.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

# Set some basic settings in the default config file
perl -pi -e 's|^# (HistoryFile /var/run)/(opendmarc.dat)|$1/opendmarc/$2/;
             s|^# (Socket )|$1|;
             s|^# (UserId )|$1|;
            ' $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

install -d $RPM_BUILD_ROOT%{_includedir}/%{name}
cp -p libopendmarc/dmarc.h $RPM_BUILD_ROOT%{_includedir}/%{name}

rm $RPM_BUILD_ROOT%{_libdir}/*.la
# packaged as %doc
rm -r $RPM_BUILD_ROOT%{_docdir}/%{name}

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
%doc CONTRIBUTING INSTALL README README.md RELEASE_NOTES
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
%dir %attr(700,opendmarc,opendmarc) %{_localstatedir}/spool/%{name}
%dir %attr(700,opendmarc,opendmarc) %{_localstatedir}/run/%{name}

%files -n libopendmarc
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libopendmarc.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libopendmarc.so.2

%files -n libopendmarc-devel
%defattr(644,root,root,755)
%doc libopendmarc/docs/*.html
%{_includedir}/%{name}
%attr(755,root,root) %{_libdir}/libopendmarc.so

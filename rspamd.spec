%define rspamd_user      _rspamd
%define rspamd_group     %{rspamd_user}

Name:             rspamd
Version:          1.9.4
Release:          1%{dist}
Summary:          Rapid spam filtering system
Group:            System Environment/Daemons
License:          ASL 2.0
URL:              https://rspamd.com

Source0:          https://github.com/vstakhov/rspamd/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source2:          %{name}.logrotate.systemd
Source3:          80-rspamd.preset

# for 1.8.2 only
#Patch182:         182_fix_preprocessor_syntax.patch

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}

BuildRequires:    glib2-devel,libevent-devel,openssl-devel,pcre-devel
BuildRequires:    cmake,gmime-devel,file-devel,libunwind-devel
BuildRequires:    ragel < 7.0
BuildRequires:    perl-Digest-MD5
BuildRequires:    sqlite-devel
BuildRequires:    systemd
# TODO check this builddeps
BuildRequires:    luajit-devel libicu-devel

Requires:         logrotate
Requires(pre):    systemd
Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd


%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
#%%setup -q
%autosetup -p0

%build
%{__cmake} \
        -DCMAKE_C_OPT_FLAGS="%{optflags}" \
        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
        -DCONFDIR=%{_sysconfdir}/%{name} \
        -DMANDIR=%{_mandir} \
        -DDBDIR=%{_sharedstatedir}/%{name} \
        -DRUNDIR=%{_localstatedir}/run/%{name} \
        -DWANT_SYSTEMD_UNITS=ON \
        -DSYSTEMDDIR=%{_unitdir} \
        -DENABLE_LUAJIT=ON \
        -DLOGDIR=%{_localstatedir}/log/%{name} \
        -DEXAMPLESDIR=%{_datadir}/examples/%{name} \
        -DPLUGINSDIR=%{_datadir}/%{name} \
        -DLIBDIR=%{_libdir}/%{name}/ \
        -DINCLUDEDIR=%{_includedir} \
        -DNO_SHARED=ON \
        -DDEBIAN_BUILD=1 \
        -DRSPAMD_USER=%{rspamd_user} \
        -DENABLE_LIBUNWIND=ON

%{__make} %{_smp_mflags}


%install
%{__make} install DESTDIR=%{buildroot} INSTALLDIRS=vendor
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_presetdir}/80-rspamd.preset
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -d -p -m 0755 %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -d -p -m 0755 %{buildroot}%{_sharedstatedir}/%{name}
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/


%clean
rm -rf %{buildroot}


%pre
%{_sbindir}/groupadd -r %{rspamd_group} 2>/dev/null || :
%{_sbindir}/useradd -g %{rspamd_group} -c "Rspamd user" -s /bin/false -r -d %{_sharedstatedir}/%{name} %{rspamd_user} 2>/dev/null || :

%post
#Macro is not used as we want to do this on upgrade
#%%systemd_post %%{name}.service
systemctl --no-reload preset %{name}.service >/dev/null 2>&1 || :
%{__chown} %{rspamd_user}:%{rspamd_group}  %{_localstatedir}/log/%{name}

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%files
%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{_presetdir}/80-rspamd.preset
%dir  %{_localstatedir}/log/%{name}
%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*
%{_bindir}/%{name}
%{_bindir}/%{name}_stats
%{_bindir}/rspamc
%{_bindir}/rspamadm
%attr(-, %{rspamd_user}, %{rspamd_group}) %dir %{_sharedstatedir}/%{name}
%{_datadir}/%{name}
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*
%config(noreplace) %{_sysconfdir}/%{name}/modules.d/*
%config(noreplace) %{_sysconfdir}/%{name}/scores.d/*


%changelog
* Wed Oct 31 2018 Mark Verlinde <mark.verlinde@gmail.com> 1.8.1-1
- Update to 1.8.1
- Cleanup specfile

* Wed Jul 04 2018 Mark Verlinde <mark.verlinde@gmail.com> 1.7.5-1
- Update to 1.7.7
- Aditional buildbequires luajit-devel libicu-devel
- Sanitized specfile for (centos) el7 build

* Thu Sep 17 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 1.0.0-1
- Update to 1.0.0

* Fri May 29 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.9-1
- Update to 0.9.9

* Thu May 21 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.4-1
- Update to 0.9.4

* Tue May 19 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.3-1
- Update to 0.9.3

* Tue May 19 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.2-1
- Update to 0.9.2

* Sun May 17 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.1-1
- Update to 0.9.1

* Wed May 13 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.9.0-1
- Update to 0.9.0

* Fri Mar 13 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.3-1
- Update to 0.8.3

* Tue Mar 10 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.2-1
- Update to 0.8.2

* Fri Jan 23 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.1-1
- Update to 0.8.1

* Fri Jan 02 2015 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.8.0-1
- Update to 0.8.0

* Mon Nov 24 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.6-1
- Update to 0.7.6

* Mon Nov 17 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.5-1
- Update to 0.7.5

* Sat Nov 08 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.4-1
- Update to 0.7.4

* Mon Nov 03 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.3-1
- Update to 0.7.3

* Wed Oct 15 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.2-1
- Update to 0.7.2

* Tue Sep 30 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.1-1
- Update to 0.7.1

* Mon Sep 1 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.7.0-1
- Update to 0.7.0

* Fri Jan 10 2014 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.7-1
- Update to 0.6.7.

* Fri Dec 27 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.6-1
- Update to 0.6.6.

* Fri Dec 20 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.5-1
- Update to 0.6.5.

* Wed Dec 18 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.4-1
- Update to 0.6.4.

* Tue Dec 10 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.3-1
- Update to 0.6.3.

* Fri Dec 06 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.2-1
- Update to 0.6.2.

* Tue Nov 19 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.6.0-1
- Update to 0.6.0.

* Mon Jun 10 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.5.6-1
- Update to 0.5.6.

* Sat May 25 2013 Vsevolod Stakhov <vsevolod-at-highsecure.ru> 0.5.5-1
- Initial spec version.

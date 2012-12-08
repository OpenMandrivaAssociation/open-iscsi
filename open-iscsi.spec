%define module_name dkms-open-iscsi
%define revision 871
%define with_dkms 0

Name:       open-iscsi
Version:    2.0
Release:    %mkrel %{revision}.5
Summary:    An implementation of RFC3720 iSCSI
License:    GPL
Group:      Networking/Other
URL:        http://www.open-iscsi.org
Source0:    http://www.open-iscsi.org/bits/open-iscsi-%{version}-%{revision}.tar.gz
Source1:    open-iscsi.init
Source2:    initiatorname.iscsi
Patch0:      open-iscsi-1.0-awkfix.patch
Patch1:		open-iscsi-2.0-871-etc_iscsi.patch
Patch2:		open-iscsi-2.0-871-gcc451.diff
BuildRequires: glibc-static-devel
BuildRequires: db-devel
BuildRoot: %{_tmppath}/%{name}-%{version}

%description
Open-iSCSI project is a high-performance, transport independent, multi-platform
implementation of RFC3720 iSCSI. iSCSI is a protocol for distributed disk
access using SCSI commands sent over Internet Protocol networks.

%if %{with_dkms}
%package -n %{module_name}
Summary: open-iscsi initiator kernel module
Group: Networking/Other
Requires: kernel-source
Requires(preun): dkms
Requires(post): dkms

%description -n %{module_name}
This package contains the open-iscsi initiator kernel module.
%endif # dkms

%prep
%setup -q -n %{name}-%{version}-%{revision}
%patch1 -p1 -b .etc_iscsi
%patch2 -p0
chmod 0644 README Makefile COPYING etc/iscsid.conf

for arq in doc/{iscsiadm,iscsid}.8 README usr/initiator.h; do
	sed -i -e "s,/var/db/iscsi,%{_localstatedir}/lib/open-iscsi,g" $arq
done

%build
%serverbuild
%make user

%install
rm -rf %{buildroot}
# install only the user level part, so don't use makeinstall_dtd
# as it will use the "install" target, which will install the
# kernel part too
make \
                DESTDIR=%{buildroot} \
		initddir=%{_initrddir} \
		install_user

mkdir -p -m 0700 %{buildroot}%{_localstatedir}/lib/open-iscsi
mkdir -p -m 0755 %{buildroot}%{_sysconfdir}/iscsi/nodes
mkdir -p -m 0755 %{buildroot}%{_sysconfdir}/iscsi/send_targets

# init script
mkdir -p %{buildroot}%{_initrddir}
install -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/open-iscsi

# DKMS
%if %{with_dkms}
mkdir -p %{buildroot}/usr/src/%{module_name}-%{version}
cp -a kernel %{buildroot}/usr/src/%{module_name}-%{version}/
cp -a include %{buildroot}/usr/src/%{module_name}-%{version}/

cat > %{buildroot}/usr/src/%{module_name}-%{version}/dkms.conf <<EOF
PACKAGE_VERSION="%{version}"
PACKAGE_NAME="%{module_name}"
MAKE[0]="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build/kernel ; make"
CLEAN="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build/kernel ; make clean"

BUILT_MODULE_NAME[0]="iscsi_tcp"
BUILT_MODULE_LOCATION[0]="kernel"
DEST_MODULE_NAME[0]="iscsi_tcp"
DEST_MODULE_LOCATION[0]="/kernel/drivers/scsi"

BUILT_MODULE_NAME[1]="scsi_transport_iscsi"
BUILT_MODULE_LOCATION[1]="kernel"
DEST_MODULE_NAME[1]="scsi_transport_iscsi"
DEST_MODULE_LOCATION[1]="/kernel/drivers/scsi"

REMAKE_INITRD="no"
AUTOINSTALL=yes
POST_INSTALL="post-install"
POST_REMOVE="post-remove"
EOF
%endif # dkms

# sample initiatorname file
install -m 0644 %{_sourcedir}/initiatorname.iscsi %{buildroot}%{_sysconfdir}/iscsi

%post
%_post_service open-iscsi

%if %{with_dkms}
%post -n %{module_name}
dkms add -m %{module_name} -v %{version} --rpm_safe_upgrade
dkms build -m %{module_name} -v %{version} --rpm_safe_upgrade
dkms install -m %{module_name} -v %{version} --rpm_safe_upgrade
%endif

%preun
%_preun_service open-iscsi

%if %{with_dkms}
%preun -n %{module_name}
dkms remove -m %{module_name} -v %{version} --rpm_safe_upgrade --all || :
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README COPYING
%dir %{_sysconfdir}/iscsi
%{_sysconfdir}/iscsi/ifaces
%dir %{_sysconfdir}/iscsi/nodes
%dir %{_sysconfdir}/iscsi/send_targets
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/iscsi/iscsid.conf
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/iscsi/initiatorname.iscsi
%{_initrddir}/open-iscsi
/sbin/iscsiadm
/sbin/iscsid
/sbin/iscsi-iname
/sbin/iscsi_discovery
#/sbin/fwparam_ibft
%{_mandir}/man8/iscsiadm.8*
%{_mandir}/man8/iscsid.8*
%{_mandir}/man8/iscsi_discovery.8*
%dir %{_localstatedir}/lib/open-iscsi

%if %{with_dkms}
%files -n %{module_name}
%defattr(-,root,root)
%_usrsrc/%{module_name}-%{version}
%endif


%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 2.0-871.4mdv2011.0
+ Revision: 666945
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0-871.3mdv2011.0
+ Revision: 607175
- fix build
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0-871.2mdv2010.1
+ Revision: 523494
- rebuilt for 2010.1

* Sun Aug 30 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 2.0-871.1mdv2010.0
+ Revision: 422368
- new version 871 with current kernel support, including
  * patch1 - install contents of /etc/iscsi unconditionally
  * install ifaces.example as well
  * call top-level target `user' instead of explicitly listing sub-targets

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 2.0-869.2.2mdv2009.0
+ Revision: 268349
- rebuild early 2009.0 package (before pixel changes)

* Sun Jun 08 2008 Guillaume Rousse <guillomovitch@mandriva.org> 2.0-869.2.1mdv2009.0
+ Revision: 216909
- new version

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Dec 17 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.0-865.15.1mdv2008.1
+ Revision: 121685
- new version

* Wed Aug 08 2007 Olivier Thauvin <nanardon@mandriva.org> 2.0-865.9.1mdv2008.0
+ Revision: 60115
- 2.0-865.9

* Thu Jun 28 2007 Andreas Hasenack <andreas@mandriva.com> 2.0-865.3.1mdv2008.0
+ Revision: 45542
- updated to version 2.0-865.3
- using serverbuild macro (-fstack-protector-all)

* Mon May 14 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 2.0-754.2mdv2008.0
+ Revision: 26738
- Updated initscript for new version.

* Fri Apr 27 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 2.0-1.754mdv2008.0
+ Revision: 18675
- Updated to 2.0-754.
- Added missing BuildRequires for glibc-static-devel.
- Own nodes and send_targets directories.


* Wed Nov 22 2006 Andreas Hasenack <andreas@mandriva.com> 1.0-1.485.2mdv2007.0
+ Revision: 86334
- several initscript improvements, taken from CS4 package
- awk patch to fix kernel versioning detection during build
- provide a default initiatorname.iscsi file to ease configuration
- add support for dkms build, also taken from CS4 (disabled by default)
- cleanup on stop, touch on start
- workaround to kill the two daemons
- use HUP instead of KILL to stop the daemon
- fixed db path
- added sed to buildrequires
- added initial workings of an init script
- register service
- Import open-iscsi


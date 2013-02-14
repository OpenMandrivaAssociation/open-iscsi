%define module_name dkms-open-iscsi
%define revision 873
%define with_dkms 0

Summary:	An implementation of RFC3720 iSCSI
Name:		open-iscsi
Version:	2.0
Release:	%{revision}.1
License:	GPL
Group:		Networking/Other
Url:		http://www.open-iscsi.org
Source0:	http://www.open-iscsi.org/bits/open-iscsi-%{version}-%{revision}.tar.gz
Source1:	open-iscsi.init
Source2:	initiatorname.iscsi
Patch1:		open-iscsi-2.0-871-etc_iscsi.patch

BuildRequires:	glibc-static-devel
BuildRequires:	db-devel

%description
Open-iSCSI project is a high-performance, transport independent, multi-platform
implementation of RFC3720 iSCSI. iSCSI is a protocol for distributed disk
access using SCSI commands sent over Internet Protocol networks.

%if %{with_dkms}
%package -n %{module_name}
Summary:	open-iscsi initiator kernel module
Group:		Networking/Other
Requires:	kernel-source
Requires(preun,post):	dkms

%description -n %{module_name}
This package contains the open-iscsi initiator kernel module.
%endif # dkms

%prep
%setup -qn %{name}-%{version}-%{revision}
%apply_patches
chmod 0644 README Makefile COPYING etc/iscsid.conf

for arq in doc/{iscsiadm,iscsid}.8 README usr/initiator.h; do
	sed -i -e "s,/var/db/iscsi,%{_localstatedir}/lib/open-iscsi,g" $arq
done

%build
%serverbuild
%make user

%install
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
install -m 0644 %SOURCE2 %{buildroot}%{_sysconfdir}/iscsi

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

%files
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
%_usrsrc/%{module_name}-%{version}
%endif


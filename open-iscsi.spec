%global optflags %{optflags} -Wno-error=unused-command-line-argument -Wno-error=gnu-variable-sized-type-not-at-end -Wno-error=unknown-warning-option
%global _disable_ld_no_undefined 1

Summary: iSCSI daemon and utility programs
Name: open-iscsi
Version: 2.1.11
Release: 1
License: GPLv2+
URL: https://github.com/open-iscsi/open-iscsi
Source0: https://github.com/open-iscsi/open-iscsi/archive/refs/tags/%{version}.tar.gz
Source4: https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/04-iscsi
Source5: https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/iscsi-tmpfiles.conf

BuildRequires: flex bison doxygen kmod-devel systemd
BuildRequires: meson ninja
BuildRequires: pkgconfig(mount)
BuildRequires: pkgconfig(openssl)
BuildRequires: %mklibname -d isns
BuildRequires: pkgconfig(libsystemd)
Requires: %{name}-iscsiuio >= %{version}-%{release}

# Old NetworkManager expects the dispatcher scripts in a different place
Conflicts: NetworkManager < 1.20

%global _hardened_build 1
%global __provides_exclude_from ^(%{python3_sitearch}/.*\\.so)$

%rename iscsi-initiator-utils

%patchlist
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0001-meson-don-t-hide-things-with-Wno-all.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0002-Currently-when-iscsi.service-is-installed-it-creates.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0003-Use-DBROOT-in-iscsi-starter.-Include-iscsi-starter-i.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0004-fix-systemctl-path-in-iscsi-starter.service.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0005-improved-onboot-and-shutdown-services.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0006-iscsid.conf-Fedora-Red-Hat-defaults.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0007-Disable-Data-Digests.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0008-Revert-iscsiadm-return-error-when-login-fails.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0009-Coverity-scan-fixes.patch
# Don't blindly copy 0010-use-Red-Hat-version-string-to-match-RPM-package-vers.patch -- we don't use their incorrect faulty versioning.
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0101-libiscsi.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0102-libiscsi-introduce-sessions-API.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0103-fix-libiscsi-firmware-discovery-issue-with-NULL-drec.patch
https://src.fedoraproject.org/rpms/iscsi-initiator-utils/raw/rawhide/f/0104-libiscsi-build-fixes.patch
open-iscsi-compile.patch

%description
The iscsi package provides the server daemon for the iSCSI protocol,
as well as the utility programs used to manage it. iSCSI is a protocol
for distributed disk access using SCSI commands sent over Internet
Protocol networks.

%package iscsiuio
Summary: Userspace configuration daemon required for some iSCSI hardware
License: BSD
Requires: %{name} = %{version}-%{release}
%rename iscsi-initiator-utils-iscsiuio

%description iscsiuio
The iscsiuio configuration daemon provides network configuration help
for some iSCSI offload hardware.

%package devel
Summary: Development files for %{name}
Requires: %{name} = %{version}-%{release}
%rename iscsi-initiator-utils-devel

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package -n python-%{name}
%{?python_provide:%python_provide python-%{name}}
Summary: Python %{python3_version} bindings to %{name}
Requires: %{name} = %{version}-%{release}
BuildRequires: python-devel
BuildRequires: python-setuptools
BuildRequires: make

%description -n python-%{name}
The python-%{name} package contains Python %{python3_version} bindings to the
libiscsi interface for interacting with %{name}

%prep
%autosetup -p1

%conf
%meson

%build
%meson_build

%make_build LDFLAGS="%{build_ldflags} -L$(pwd)/build" DBROOT=/var/lib/iscsi libiscsi
pushd libiscsi
%py3_build
popd

%install
%meson_install

%if "%{_bindir}" == "%{_sbindir}"
cd %{buildroot}%{_prefix}
mv sbin bin
cd -
%endif

%{__install} -d %{buildroot}%{_sharedstatedir}/iscsi
%{__install} -d %{buildroot}%{_sharedstatedir}/iscsi/nodes
%{__install} -d %{buildroot}%{_sharedstatedir}/iscsi/send_targets
%{__install} -d %{buildroot}%{_sharedstatedir}/iscsi/static
%{__install} -d %{buildroot}%{_sharedstatedir}/iscsi/isns
%{__install} -d %{buildroot}%{_sharedstatedir}/iscsi/slp
%{__install} -d %{buildroot}%{_sharedstatedir}/iscsi/ifaces
 
# for %%ghost
%{__install} -d %{buildroot}%{_rundir}/lock/iscsi
touch %{buildroot}%{_rundir}/lock/iscsi/lock
 
%{__install} -d %{buildroot}%{_libexecdir}
%{__install} -pm 755 etc/systemd/iscsi-mark-root-nodes %{buildroot}%{_libexecdir}
 
%{__install} -d %{buildroot}%{_prefix}/lib/NetworkManager/dispatcher.d
%{__install} -pm 755 %{SOURCE4} %{buildroot}%{_prefix}/lib/NetworkManager/dispatcher.d
 
%{__install} -d %{buildroot}%{_tmpfilesdir}
%{__install} -pm 644 %{SOURCE5} %{buildroot}%{_tmpfilesdir}/iscsi.conf
 
%{__install} -d %{buildroot}%{_libdir}
%{__install} -pm 755 libiscsi/libiscsi.so.0 %{buildroot}%{_libdir}
%{__ln_s}    libiscsi.so.0 %{buildroot}%{_libdir}/libiscsi.so
%{__install} -d %{buildroot}%{_includedir}
%{__install} -pm 644 libiscsi/libiscsi.h %{buildroot}%{_includedir}
 
pushd libiscsi
  %{__install} -d %{buildroot}%{python3_sitearch}
  %py3_install
popd

# Avoid clash with the other libiscsi
cd %{buildroot}%{_libdir}
mv libiscsi.so libiscsi-compat.so

%files
%doc README
%dir %{_sharedstatedir}/iscsi
%dir %{_sharedstatedir}/iscsi/nodes
%dir %{_sharedstatedir}/iscsi/isns
%dir %{_sharedstatedir}/iscsi/static
%dir %{_sharedstatedir}/iscsi/slp
%dir %{_sharedstatedir}/iscsi/ifaces
%dir %{_sharedstatedir}/iscsi/send_targets
%ghost %attr(0700, root, root) %dir %{_rundir}/lock/iscsi
%ghost %attr(0600, root, root) %{_rundir}/lock/iscsi/lock
%{_unitdir}/iscsi.service
%{_unitdir}/iscsi-onboot.service
%{_unitdir}/iscsi-init.service
%{_unitdir}/iscsi-shutdown.service
%{_unitdir}/iscsid.service
%{_unitdir}/iscsid.socket
%{_libexecdir}/iscsi-mark-root-nodes
%{_prefix}/lib/NetworkManager/dispatcher.d/04-iscsi
%{_tmpfilesdir}/iscsi.conf
%dir %{_sysconfdir}/iscsi
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/iscsi/iscsid.conf
%{_sbindir}/iscsi-iname
%{_sbindir}/iscsiadm
%{_sbindir}/iscsid
%{_sbindir}/iscsistart
%{_libdir}/libiscsi.so.0
%{_libdir}/libopeniscsiusr.so.*
%{_sysconfdir}/iscsi/initiatorname.iscsi
%{_sysconfdir}/udev/rules.d/50-iscsi-firmware-login.rules
%{_sbindir}/brcm_iscsiuio
%{_sbindir}/iscsi-gen-initiatorname
%{_sbindir}/iscsi_discovery
%{_sbindir}/iscsi_fw_login
%{_sbindir}/iscsi_offload
%{_prefix}/lib/systemd/system-generators/ibft-rule-generator
%{_prefix}/lib/systemd/system/iscsi-starter.service
%{_localstatedir}/lib/iscsi
%{_mandir}/man8/iscsi-iname.8*
%{_mandir}/man8/iscsiadm.8*
%{_mandir}/man8/iscsid.8*
%{_mandir}/man8/iscsistart.8*
%{_mandir}/man8/iscsi-gen-initiatorname.8*
%{_mandir}/man8/iscsi_discovery.8*
%{_mandir}/man8/iscsi_fw_login.8*

%files iscsiuio
%{_sbindir}/iscsiuio
%{_unitdir}/iscsiuio.service
%{_unitdir}/iscsiuio.socket
%config(noreplace) %{_sysconfdir}/logrotate.d/iscsiuiolog
%{_mandir}/man8/iscsiuio.8*

%files devel
%doc libiscsi/html
%{_libdir}/libiscsi-compat.so
%{_includedir}/libiscsi.h
%{_libdir}/libopeniscsiusr.so
%{_includedir}/libopeniscsiusr.h
%{_includedir}/libopeniscsiusr_common.h
%{_includedir}/libopeniscsiusr_iface.h
%{_includedir}/libopeniscsiusr_node.h
%{_includedir}/libopeniscsiusr_session.h
%{_libdir}/pkgconfig/libopeniscsiusr.pc
%doc %{_mandir}/man3/iscsi_*.3*
%doc %{_mandir}/man3/libopeniscsiusr.h.3*

%files -n python-%{name}
%{python3_sitearch}/*

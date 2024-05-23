%define distro redhat 
%define polyinstatiate n
%define monolithic n
%define POLICYVER 33
%define POLICYCOREUTILSVER 3.4-1
%define CHECKPOLICYVER 3.2
%define LIBSEMANAGEVER 3.5-2
Name:   %{pkgname}
Version: %{version}
Release: %{release}
Summary: Policy Base Configuration Data
License: GPLv2+
Group: System Environment/Base
Source: %{pkgname}-%{version}.tar.gz
# Tool helps during policy development, to expand system m4 macros to raw allow rules
# Git repo: https://gitlab.cee.redhat.com/SELinux/macro-expander
Source1:  macro-expander
Source2:  rpm.macros
Source3:  Makefile.devel
Source4:  selinux-policy.conf
Source5: selinux-check-proper-disable.service
Source6: setrans-mcs.conf
Source7: setrans-mls.conf
Url: http:/oss.tresys.com/repos/refpolicy/
BuildRequires: python3 gawk checkpolicy >= %{CHECKPOLICYVER} m4 policycoreutils-devel >= %{POLICYCOREUTILSVER} bzip2
BuildRequires: make
BuildRequires: systemd-rpm-macros
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(post): /bin/awk /usr/bin/sha512sum
Requires(meta): rpm-plugin-selinux
Requires: libsemanage >= %{LIBSEMANAGEVER}
Requires: platform-python

%description 
This package contains the base components common across policy types.
This package does not contain the full policy, you will also need something like
selinux-policy-%{type} and any supplemental %{type}-specific RPMs.
It is part of the Certificable Linux Integration Platform code base
and has different security goals that typical vendor policies. Installing
these packages may require updates to system configuration or additional
policy modifications to support your use cases.

%files 
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING
%dir %{_datadir}/selinux
%dir %{_sysconfdir}/selinux
%ghost %config(noreplace) %{_sysconfdir}/selinux/config
%ghost %{_sysconfdir}/sysconfig/selinux
%{_usr}/lib/tmpfiles.d/selinux-policy.conf
%{_rpmconfigdir}/macros.d/macros.selinux-policy
%{_unitdir}/selinux-check-proper-disable.service

%package devel
Summary: SELinux policy devel
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Requires: m4 checkpolicy >= %{CHECKPOLICYVER}
Requires: /usr/bin/make
Requires(post): policycoreutils-devel >= %{POLICYCOREUTILSVER}

%description devel
SELinux policy development support.

%files devel
%{_bindir}/macro-expander
%dir %{_datadir}/selinux/devel
%dir %{_datadir}/selinux/devel/include
%{_datadir}/selinux/devel/include/*
%{_datadir}/selinux/devel/Makefile
%{_datadir}/selinux/devel/example.*
%{_datadir}/selinux/devel/policy.*
%ghost %verify(not md5 size mode mtime) %{_sharedstatedir}/sepolgen/interface_info

%post devel
%{_sbindir}/selinuxenabled && %{_bindir}/sepolgen-ifgen 2>/dev/null
exit 0

%package doc
Summary: SELinux policy documentation
Group: System Environment/Base
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}

%description doc
Policy documentation

%files doc
%defattr(-,root,root,-)
%doc %{_datadir}/doc/%{name}-%{version}
#%doc %%{_datadir}/selinux/devel/html
#%attr(755,root,root) %%{_datadir}/selinux/devel/policyhelp

%global genSeparatePolRPM() \
%package %2-%1 \
Summary: SELinux %2 policy for %1 \
Group: System Environment/Base \
Requires(pre): selinux-policy-%2 = %{version}-%{release} \
BuildRequires: m4 policycoreutils-devel python3 make gcc checkpolicy >= %{CHECKPOLICYVER} \
\
%description %2-%1  \
SELinux %2 policy for %1 \
\
%files %2-%1 \
%defattr(-,root,root,-) \
%verify(not md5 size mtime) /usr/share/selinux/%2/%1.pp \
\
%post %2-%1 \
echo %1.pp >> %{_datadir}/selinux/%2/modules.lst \
%{_sbindir}/semodule -n -s %2 -i %{_datadir}/selinux/%2/%1.pp \
if %{_sbindir}/selinuxenabled ; then \
    %{_sbindir}/load_policy \
fi;exit 0 \
%preun %2-%1 \
%{_sbindir}/semodule -n -s %2 -d %1 -X 100 2>/dev/null \
if %{_sbindir}/selinuxenabled ; then \
    %{_sbindir}/load_policy \
fi;exit 0

%{expand:%( for f in %{separatePkgs}; do echo "%%genSeparatePolRPM $f %{type}"; done)}

%define installCmds() \
make UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}  %{separatePkgs}" SEMOD_EXP="/usr/bin/semodule_expand" base.pp \
make %{?_smp_mflags} validate UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}" SEMOD_EXP="/usr/bin/semodule_expand" modules \
make %{?_smp_mflags} UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}" install \
make %{?_smp_mflags} UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules} %{separatePkgs}" install-appconfig \
mkdir -p %{buildroot}%{_datadir}/selinux/%1/ \
%{__cp} *.pp %{buildroot}%{_datadir}/selinux/%1/ \
make UNK_PERMS=%4 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=n DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} MLS_CATS=1024 MCS_CATS=1024 SEMODULE="semodule -p %{buildroot} -X 100 " APPS_MODS="%{enable_modules}" load \
%{__mkdir} -p %{buildroot}%{_sharedstatedir}/selinux/%1/active/modules/disabled \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/logins \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
if [[ %2 != "standard" ]]; then install -m0644 config/appconfig-%1/setrans.conf %{buildroot}%{_sysconfdir}/selinux/%1/setrans.conf; fi \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local.bin \
sefcontext_compile -o %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.bin %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/policy \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/contexts/files \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/logins \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/semanage.read.LOCK \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/semanage.trans.LOCK \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/booleans \
touch %{buildroot}%{_sysconfdir}/selinux/%1/seusers \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/active/seusers \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/active/file_contexts.local \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/active/file_contexts.homedirs \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/active/nodes.local \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/active/users_extra.local \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/active/users.local \
touch %{buildroot}%{_sharedstatedir}/selinux/%1/active/file_contexts.homedirs.bin \
find %{buildroot}%{_datadir}/selinux/%1/ -type f |xargs -P `/usr/bin/nproc` -n `/usr/bin/nproc`  bzip2 \
for i in %{buildroot}%{_datadir}/selinux/%1/*; do mv ${i} ${i%.bz2}; done \
awk '$1 !~ "/^#/" && $2 == "=" && $3 == "module" { printf "%%s.pp ", $1 }' ./policy/modules.conf > %{buildroot}%{_datadir}/selinux/%1/modules.lst \
[ x"%{enable_modules}" != "x" ] && for i in %{enable_modules}; do echo ${i}.pp >> %{buildroot}%{_datadir}/selinux/%1/modules.lst; done \
SORTED_PKGS=`for p in %{separatePkgs}; do echo $p | awk '{ print length($0) " " $0; }'; done | sort -r -n | cut -d ' ' -f 2` \
for f in ${SORTED_PKGS}; do grep $f\.pp\ %{buildroot}%{_datadir}/selinux/%1/modules.lst || (echo "failed to update module.lst for module $f" && exit -1); sed -i -e "s/$f.pp//g" %{buildroot}%{_datadir}/selinux/%1/modules.lst; done \
mkdir -p %{buildroot}%{_sharedstatedir}/selinux/%1/active/modules/100 \
mkdir -p %{buildroot}%{_sharedstatedir}/selinux/%1/active/modules/disabled \
/sbin/semodule -s %1 -p %{buildroot} -X 100 -r %{separatePkgs} \
/usr/bin/sha512sum %{buildroot}%{_sysconfdir}/selinux/%1/policy/policy.`/bin/checkpolicy --version|awk ' { print $1; } '` | cut -d' ' -f 1 > %{buildroot}%{_sysconfdir}/selinux/%1/.policy.sha512; \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/contexts/netfilter_contexts  \
rm -rf %{buildroot}%{_sharedstatedir}/selinux/%1/active/policy.kern \
ln -sf /etc/selinux/%1/policy/policy.`/bin/checkpolicy --version|awk ' { print $1; } '`  %{buildroot}%{_sharedstatedir}/selinux/%1/active/policy.kern \
rm -rf %{buildroot}/usr/share/selinux/devel/include
%nil

%global excludes() %(for f in %{separatePkgs}; do echo -e "%exclude %{_datadir}/selinux/%1/${f}.pp"; done )
 
%define fileList() \
%defattr(-,root,root) \
%dir %{_datadir}/selinux/%1 \
%dir %{_sysconfdir}/selinux/%1 \
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/seusers \
%dir %{_sysconfdir}/selinux/%1/logins \
%dir %{_sharedstatedir}/selinux/%1/active \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/semanage.read.LOCK \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/semanage.trans.LOCK \
%dir %attr(700,root,root) %dir %{_sharedstatedir}/selinux/%1/active/modules/ \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/commit_num \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules_checksum \
# TODO: stop globbing \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/modules/100/*/* \
%config(noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/users_extra \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/homedir_template \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/policy.kern \
%ghost %{_sharedstatedir}/selinux/%1/active/*.local \
%ghost %{_sharedstatedir}/selinux/%1/active/*.linked \
%ghost %{_sharedstatedir}/selinux/%1/active/*.bin \
%ghost %{_sharedstatedir}/selinux/%1/active/seusers \
%dir %{_sysconfdir}/selinux/%1/policy/ \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/policy/policy.* \
%{_sysconfdir}/selinux/%1/.policy.sha512 \
%dir %{_sysconfdir}/selinux/%1/contexts \
%config %{_sysconfdir}/selinux/%1/contexts/customizable_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/securetty_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/*_contexts \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/default_type \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/*_context \
%dir %{_sysconfdir}/selinux/%1/contexts/files \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/file_contexts \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs \
%verify(not md5 size mtime) %{_sharedstatedir}/selinux/%1/active/file_contexts.homedirs \
%ghost %{_sysconfdir}/selinux/%1/contexts/files/*.bin \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs_dist \
%config %{_sysconfdir}/selinux/%1/contexts/files/media \
%dir %{_sysconfdir}/selinux/%1/contexts/users \
%if "%1" != "standard" \
%config(noreplace) %{_sysconfdir}/selinux/%1/setrans.conf \
%endif \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/* \
%{_datadir}/selinux/%1/*.pp \
%{_datadir}/selinux/%1/modules.lst \

%build

%prep 
%setup -n %{pkgname} -q

%install
%{__rm} -fR %{buildroot}
mkdir -p %{buildroot}%{_sysconfdir}/selinux
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
touch %{buildroot}%{_sysconfdir}/selinux/config
touch %{buildroot}%{_sysconfdir}/sysconfig/selinux

# Always create policy module package directories
mkdir -p %{buildroot}%{_datadir}/selinux/%{type}/
mkdir -p %{buildroot}%{_datadir}/selinux/modules/

mkdir -p %{buildroot}%{_sharedstatedir}/selinux/%{type}

make %{?_smp_mflags} clean
cp -a %{SOURCE6} config/appconfig-mcs/setrans.conf
cp -a %{SOURCE7} config/appconfig-mls/setrans.conf
# installCmds NAME TYPE DIRECT_INITRC POLY UNKNOWN
%installCmds %{type} %{type}  n y deny

make %{?_smp_mflags} UNK_PERMS=deny NAME=%{type} TYPE=%{type}  DISTRO=%{distro} UBAC=y DIRECT_INITRC=n MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} PKGNAME=%{name}-%{version} POLY=y MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}" install-headers install-docs
touch %{buildroot}%{_sharedstatedir}/selinux/%{type}/active/seusers.linked
mkdir %{buildroot}%{_datadir}/selinux/devel/
mv %{buildroot}%{_datadir}/selinux/%{type}/include %{buildroot}%{_datadir}/selinux/devel/include
install -m 644 %{SOURCE3} %{buildroot}%{_datadir}/selinux/devel/Makefile
install -m 644 doc/example.* %{buildroot}%{_datadir}/selinux/devel/
install -m 644 doc/policy.* %{buildroot}%{_datadir}/selinux/devel/
# FIXME: sepolicy manpage errors out, might be an issue with non-rhel policy naming conventions, symlinking isnt fixing it (yet..)
# ln -s %{buildroot}/%{_sysconfdir}/selinux/%{type} %{buildroot}/%{_sysconfdir}/selinux/targeted
# ln -s %{buildroot}%{_datadir}/selinux/standard %{buildroot}%{_datadir}/selinux/targeted
# %{_bindir}/sepolicy manpage -a -p %{buildroot}%{_datadir}/man/man8/ -w -r %{buildroot}
# rm -f %{buildroot}/%{_sysconfdir}/selinux/targeted %{buildroot}%{_datadir}/selinux/targeted
# mkdir %{buildroot}%{_datadir}/selinux/devel/html
# mv %{buildroot}%{_datadir}/man/man8/*.html %{buildroot}%{_datadir}/selinux/devel/html
# mv %{buildroot}%{_datadir}/man/man8/style.css %{buildroot}%{_datadir}/selinux/devel/html

mkdir -p %{buildroot}%{_bindir}
install -m 755 %{SOURCE1} %{buildroot}%{_bindir}/

mkdir -p %{buildroot}%{_rpmconfigdir}/macros.d
install -m 644 %{SOURCE2} %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy
sed -i 's/SELINUXPOLICYVERSION/%{version}-%{release}/' %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy
sed -i 's@SELINUXSTOREPATH@%{_sharedstatedir}/selinux@' %{buildroot}%{_rpmconfigdir}/macros.d/macros.selinux-policy

mkdir -p %{buildroot}%{_usr}/lib/tmpfiles.d/
cp %{SOURCE4} %{buildroot}%{_usr}/lib/tmpfiles.d/

mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE5} %{buildroot}%{_unitdir}

%clean
%{__rm} -fR %{buildroot}

%post
%systemd_post selinux-check-proper-disable.service
if [ ! -s %{_sysconfdir}/selinux/config ]; then
#
#     New install so we will default to selinux-policy policy
#
echo "
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
#
# NOTE: Up to RHEL 8 release included, SELINUX=disabled would also
# fully disable SELinux during boot. If you need a system with SELinux
# fully disabled instead of SELinux running with no policy loaded, you
# need to pass selinux=0 to the kernel command line. You can use grubby
# to persistently set the bootloader to boot with selinux=0:
SELINUX=%{enforcing_mode}
# SELINUXTYPE= can take one of these two values:
#     mcs - standard Multi Category security policy,
#     mls - Multi Level Security security policy.
#     standard - SELinux policy without MLS (neight MCS nor MLS features are enabled, UBAC, RBAC, TE only)
SELINUXTYPE=%{type}

" > %{_sysconfdir}/selinux/config
fi

sed -e 's/^SELINUXTYPE=.*/SELINUXTYPE=%{type}/' -i /etc/selinux/config

ln -sf ../selinux/config %{_sysconfdir}/sysconfig/selinux
%{_sbindir}/restorecon %{_sysconfdir}/selinux/config 2> /dev/null || :

exit 0

%preun
%systemd_preun selinux-check-proper-disable.service

%postun
%systemd_postun selinux-check-proper-disable.service
if [ $1 = 0 ]; then
     %{_sbindir}/setenforce 0 2> /dev/null
     if [ ! -s %{_sysconfdir}/selinux/config ]; then
          echo "SELINUX=disabled" > %{_sysconfdir}/selinux/config
     else
          sed -i 's/^SELINUX=.*/SELINUX=disabled/g' %{_sysconfdir}/selinux/config
     fi
fi
exit 0

%define relabel() \
if [ -s %{_sysconfdir}/selinux/config ]; then \
    . %{_sysconfdir}/selinux/config &> /dev/null || true; \
fi; \
FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
if %{_sbindir}/selinuxenabled && [ "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT}.pre ]; then \
     %{_sbindir}/fixfiles -C ${FILE_CONTEXT}.pre restore &> /dev/null > /dev/null; \
     rm -f ${FILE_CONTEXT}.pre; \
fi; \
if %{_sbindir}/restorecon -e /run/media -R /root /var/log /var/run /etc/passwd* /etc/group* /etc/*shadow* 2> /dev/null;then \
    continue; \
fi;


%define preInstall() \
if [ $1 -ne 1 ] && [ -s %{_sysconfdir}/selinux/config ]; then \
     . %{_sysconfdir}/selinux/config; \
     FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
     if [ "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT} ]; then \
        [ -f ${FILE_CONTEXT}.pre ] || cp -f ${FILE_CONTEXT} ${FILE_CONTEXT}.pre; \
     fi; \
     touch %{_sysconfdir}/selinux/%1/.rebuild; \
     if [ -e %{_sysconfdir}/selinux/%1/.policy.sha512 ]; then \
        POLICY_FILE=`ls %{_sysconfdir}/selinux/%1/policy/policy.* | sort | head -1` \
        sha512=`sha512sum $POLICY_FILE | cut -d ' ' -f 1`; \
	checksha512=`cat %{_sysconfdir}/selinux/%1/.policy.sha512`; \
	if [ "$sha512" == "$checksha512" ] ; then \
		rm %{_sysconfdir}/selinux/%1/.rebuild; \
	fi; \
   fi; \
fi;

%define postInstall() \
if [ -s %{_sysconfdir}/selinux/config ]; then \
    . %{_sysconfdir}/selinux/config &> /dev/null || true; \
fi; \
#TODO: (cd /etc/selinux/%2/modules/active/modules; rm -f vbetool.pp l2tpd.pp shutdown.pp amavis.pp clamav.pp gnomeclock.pp nsplugin.pp matahari.pp xfs.pp kudzu.pp kerneloops.pp execmem.pp openoffice.pp ada.pp tzdata.pp hal.pp hotplug.pp howl.pp java.pp mono.pp moilscanner.pp gamin.pp audio_entropy.pp audioentropy.pp iscsid.pp polkit_auth.pp polkit.pp rtkit_daemon.pp ModemManager.pp telepathysofiasip.pp ethereal.pp passanger.pp qemu.pp qpidd.pp pyzor.pp razor.pp pki-selinux.pp phpfpm.pp consoletype.pp ctdbd.pp fcoemon.pp isnsd.pp rgmanager.pp corosync.pp aisexec.pp pacemaker.pp pkcsslotd.pp smstools.pp ) \
if [ -e %{_sysconfdir}/selinux/%2/.rebuild ]; then \
   rm %{_sysconfdir}/selinux/%2/.rebuild; \
fi; \
%{_sbindir}/semodule -B -n -s %2; \
[ "${SELINUXTYPE}" == "%2" ] && %{_sbindir}/selinuxenabled && load_policy; \
if [ %1 -eq 1 ]; then \
   %{_sbindir}/restorecon -R /root /var/log /run /etc/passwd* /etc/group* /etc/*shadow* 2> /dev/null; \
else \
%relabel %2 \
fi; \
echo -n " -F " > /.autorelabel


%package %{type}
Summary: SELinux selinux-policy base policy
Provides: selinux-policy-base = %{version}-%{release}
Group: System Environment/Base
Requires(pre): policycoreutils-python-utils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Conflicts:  audispd-plugins <= 1.7.7-1
Conflicts:  seedit
Obsoletes: selinux-policy-targeted, selinux-policy-minimum, selinux-policy-mls

%description %{type}
SELinux %{type} policy

%pre %{type}
%preInstall %{type}

%post %{type}
%postInstall $1 %{type}
exit 0

%files %{type} 
%defattr(-,root,root,-)
%fileList %{type}

%excludes %{type}

%changelog

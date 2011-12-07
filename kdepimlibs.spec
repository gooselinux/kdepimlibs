%global apidocs 1
%global akonadi_subpkg 1
%global akonadi_version 1.2.0

Name: kdepimlibs
Version: 4.3.4
Release: 4%{?dist}
Summary: K Desktop Environment 4 - PIM Libraries

# http://techbase.kde.org/Policies/Licensing_Policy
License: LGPLv2+
Group: System Environment/Libraries

URL: http://www.kde.org/
Source0: ftp://ftp.kde.org/pub/kde/stable/%{version}/src/kdepimlibs-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# upstream patches
Patch100: kdepimlibs-4.3.5.patch

%if ! 0%{?akonadi_subpkg}
Provides: %{name}-akonadi%{?_isa} = %{version}-%{release}
Requires: akonadi%{?_isa} >= %{akonadi_version}
%endif
Requires: kdelibs4 >= %{version}

BuildRequires: akonadi-devel >= %{akonadi_version} 
BuildRequires: boost-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: gpgme-devel
BuildRequires: kdelibs4-devel >= %{version}
BuildRequires: libXpm-devel libXtst-devel
BuildRequires: openldap-devel
BuildRequires: libical-devel >= 0.33

%if 0%{?apidocs}
BuildRequires: doxygen
BuildRequires: graphviz
BuildRequires: qt4-doc
%endif

# stuff moved kdepim -> kdepimlibs, help upgrade path
Conflicts: kdepim < 6:4.2.90

%description
Personal Information Management (PIM) libraries for the
K Desktop Environment 4.

%package devel
Group: Development/Libraries
Summary: Development files for %{name}
Requires: %{name} = %{version}-%{release}
%if 0%{?akonadi_subpkg}
Requires: %{name}-akonadi = %{version}-%{release}
%endif
Obsoletes: kdepimlibs4-devel < %{version}-%{release}
Provides: kdepimlibs4-devel = %{version}-%{release}
Requires: kdelibs4-devel
Requires: boost-devel
Requires: libical-devel

%description devel
Header files for developing applications using %{name}.

%package akonadi
Summary: Akonadi runtime support for %{name}
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}
Requires: akonadi%{?_isa} >= %{akonadi_version}

%description akonadi
%{summary}.

%package apidocs
Group: Development/Documentation
Summary: kdepimlibs API documentation
Requires: kde-filesystem
BuildArch: noarch

%description apidocs
This package includes the kdepimlibs API documentation in HTML
format for easy browsing.


%prep
%setup -q -n kdepimlibs-%{version}

# 4.3 upstream patches
%patch100 -p1 -b .kde435

%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kde4} ..
popd

make %{?_smp_mflags} -C %{_target_platform}

# build apidocs
%if 0%{?apidocs}
  export QTDOCDIR=`pkg-config --variable=docdir Qt`
  kde4-doxygen.sh --doxdatadir=%{_kde4_docdir}/HTML/en/common .
%endif


%install
rm -rf %{buildroot}

make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

# hack around HTML doc multilib conflicts
pushd %{buildroot}%{_kde4_docdir}/HTML/en/kcontrol/kresources
bunzip2 index.cache.bz2
sed -i -e 's!<a name="id[0-9]*"></a>!!g' index.cache
bzip2 -9 index.cache
popd

# move devel symlinks
mkdir -p %{buildroot}%{_kde4_libdir}/kde4/devel
pushd %{buildroot}%{_kde4_libdir}
for i in lib*.so
do
  case "$i" in
    # conflicts with kdelibs3
    libkabc.so | libkresources.so)
      linktarget=`readlink "$i"`
      rm -f "$i"
      ln -sf "../../$linktarget" "kde4/devel/$i"
      ;;
    # conflicts with kdepim3 (compat)
    libkcal.so)
      linktarget=`readlink "$i"`
      rm -f "$i"
      ln -sf "../../$linktarget" "kde4/devel/$i"
      ;;
  esac
done
popd

# install apidocs
%if 0%{?apidocs}
  mkdir -p %{buildroot}%{_kde4_docdir}/HTML/en
  cp -prf kdepimlibs-%{version}-apidocs %{buildroot}%{_kde4_docdir}/HTML/en/kdepimlibs-apidocs
%endif


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_kde4_appsdir}/kabc/
%{_kde4_appsdir}/kconf_update/*
%{_kde4_datadir}/config.kcfg/*
%{_datadir}/dbus-1/interfaces/*
%{_kde4_datadir}/kde4/services/*
%{_kde4_datadir}/kde4/servicetypes/*
%{_kde4_libdir}/lib*.so.*
%{_kde4_libdir}/kde4/*.so
%{_kde4_docdir}/HTML/en/kcontrol/
%{_kde4_docdir}/HTML/en/kioslave/
%{_kde4_appsdir}/libkholidays/
%{_kde4_datadir}/mime/packages/kdepimlibs-mime.xml
%if 0%{?akonadi_subpkg}
%exclude %{_kde4_libdir}/libakonadi-*.so.*
%files akonadi
%defattr(-,root,root,-)
%{_kde4_libdir}/libakonadi-*.so.*
%endif
%{_kde4_appsdir}/akonadi-kde/

%files devel
%defattr(-,root,root,-)
%{_kde4_appsdir}/cmake/modules/*
%{_kde4_includedir}/*
%{_kde4_libdir}/kde4/devel/lib*.so
%{_kde4_libdir}/lib*.so
%{_kde4_libdir}/cmake/KdepimLibs*
%{_kde4_libdir}/gpgmepp/

%if 0%{?apidocs}
%files apidocs
%defattr(-,root,root,-)
%{_kde4_docdir}/HTML/en/kdepimlibs-apidocs/
%endif


%changelog
* Tue Mar 30 2010 Than Ngo <than@redhat.com> - 4.3.4-4
- rebuilt against qt 4.6.2

* Tue Mar 30 2010 Than Ngo <than@redhat.com> - 4.3.4-3
- rebuilt against qt 4.6.2

* Fri Jan 22 2010 Than Ngo <than@redhat.com> - 4.3.4-2
- backport 4.3.5 fixes

* Tue Dec 01 2009 Than Ngo <than@redhat.com> - 4.3.4-1
- 4.3.4

* Fri Nov 13 2009 Than Ngo <than@redhat.com> - 4.3.3-2
- rhel cleanup, remove Fedora<=9 conditionals

* Sat Oct 31 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-1
- 4.3.3

* Mon Oct 05 2009 Than Ngo <than@redhat.com> - 4.3.2-1
- 4.3.2

* Fri Aug 28 2009 Than Ngo <than@redhat.com> - 4.3.1-1
- 4.3.1

* Tue Aug 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.0-2
- akonadi_version 1.2.0

* Thu Jul 30 2009 Than Ngo <than@redhat.com> - 4.3.0-1
- 4.3.0

* Wed Jul 29 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.98-3
- Conflicts: kdepim < 4.2.90

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.98-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Than Ngo <than@redhat.com> - 4.2.98-1
- 4.3rc3

* Thu Jul 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.96-2
- License: LGPLv2+

* Sat Jul 11 2009 Than Ngo <than@redhat.com> - 4.2.96-1
- 4.3rc2

* Thu Jul 02 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.95-3
- akonadi_version 1.1.95

* Mon Jun 29 2009 Than Ngo <than@redhat.com> - 4.2.95-2
- respin

* Thu Jun 25 2009 Than Ngo <than@redhat.com> - 4.2.95-1
- 4.3 RC1

* Wed Jun 03 2009 Rex Dieter <rdieter@fedoraproject.org> 4.2.90-1
- KDE-4.3 beta2 (4.2.90)

* Sun May 24 2009 Rex Dieter <rdieter@fedoraproject.org> 4.2.85-2
- (min) akonadi_version 1.1.85

* Mon May 11 2009 Than Ngo <than@redhat.com> 4.2.85-1
- 4.2.85

* Mon Apr 06 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.2.2-3
- fix libkcal devel symlink hack

* Thu Apr 02 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.2-2
- -apidocs noarch (f10+)
- package %%_kde4_appsdir/akonadi-kde only once

* Tue Mar 31 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.2-1
- KDE 4.2.2

* Mon Mar 09 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.2.1-4
- disable CMake debugging, #475876 should be fixed now

* Tue Mar 03 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.1-2
- avoid libkcal conflict with kdepim3

* Fri Feb 27 2009 Than Ngo <than@redhat.com> - 4.2.1-1
- 4.2.1

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Than Ngo <than@redhat.com> - 4.2.0-4
- enable akonadi subpkg

* Mon Feb 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-3
- include toggle for -akonadi subpkg (not enabled)
- Provides: -akonadi

* Mon Feb 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-2
- multilib conflicts (#485659)
- kde4/devel symlinks: blacklist only known conflicts

* Thu Jan 22 2009 Than Ngo <than@redhat.com> - 4.2.0-1
- 4.2.0
- exclude kdepimlibs-apidocs from main pkg

* Thu Jan 08 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.96-2
- fix build on Fedora 10 (cmake < 2.6.3 seems to have a different
  behaviour here)

* Wed Jan 07 2009 Than Ngo <than@redhat.com> - 4.1.96-1
- 4.2rc1

* Wed Dec 17 2008 Rex Dieter <rdieter@fedoraproject.org> - 4.1.85-2
- versioned akonadi(-devel) deps

* Thu Dec 11 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.85-1
- KDE 4.2beta2

* Wed Dec 10 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.82-2
- add --debug-output to our cmake call, that should fix a reproducible
  bug with cmake and ppc builds (this work-around should be
  removed anyway)

* Tue Dec 09 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.82-1
- 4.1.82

* Tue Dec 02 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.80-3
- -devel: Requires: libical-devel

* Thu Nov 20 2008 Than Ngo <than@redhat.com> 4.1.80-2
- merged

* Thu Nov 20 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.80-1
- 4.1.80
- BR cmake 2.6
- make install/fast

* Wed Nov 12 2008 Than Ngo <than@redhat.com> 4.1.3-1
- 4.1.3

* Sat Nov 01 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-4
- turn off system libical for now, crashes KOrganizer (#469228)

* Tue Oct 28 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-3
- build against the system libical (F10+ only for now)

* Sun Sep 28 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-2
- make VERBOSE=1
- respin against new(er) kde-filesystem

* Fri Sep 26 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-1
- 4.1.2

* Fri Sep 05 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.1-2
- invitations crasher/regression (kde #170203, rh#462103)

* Thu Aug 28 2008 Than Ngo <than@redhat.com> 4.1.1-1
- 4.1.1

* Tue Aug 05 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.0-2
- -devel: Requires: boost-devel

* Wed Jul 23 2008 Than Ngo <than@redhat.com> 4.1.0-1
- 4.1.0

* Fri Jul 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.99-1
- 4.0.99

* Thu Jul 10 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-1
- 4.0.98

* Sun Jul 06 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.85-1
- 4.0.85

* Fri Jun 27 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.84-1
- 4.0.84

* Tue Jun 24 2008 Than Ngo <than@redhat.com> 4.0.83-2
- respun

* Thu Jun 19 2008 Than Ngo <than@redhat.com> 4.0.83-1
- 4.0.83 (beta2)

* Sat Jun 14 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.82-1
- 4.0.82

* Mon May 26 2008 Than Ngo <than@redhat.com> 4.0.80-1
- 4.1 beta1

* Mon May 05 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.0.72-2
- add BR akonadi-devel
- update file list

* Fri May 02 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.0.72-1
- update to 4.0.72 (4.1 alpha 1)

* Thu Apr 03 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-3
- rebuild (again) for the fixed %%{_kde4_buildtype}

* Mon Mar 31 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-2
- rebuild for NDEBUG and _kde4_libexecdir

* Fri Mar 28 2008 Than Ngo <than@redhat.com> 4.0.3-1
- 4.0.3
- -apidocs: Drop Requires: %%name
- include noarch build hooks (not enabled)

* Thu Mar 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.2-2
- build apidocs and put them into an -apidocs subpackage (can be turned off)
- BR doxygen, graphviz and qt4-doc when building apidocs

* Thu Feb 28 2008 Than Ngo <than@redhat.com> 4.0.2-1
- 4.0.2

* Wed Jan 30 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.1-2
- don't delete kconf_update script, it has been fixed to do the right thing

* Wed Jan 30 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.1-1
- 4.0.1

* Mon Jan 07 2008 Than Ngo <than@redhat.com> 4.0.0-1
- 4.0.0

* Tue Dec 11 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-2
- rebuild for changed _kde4_includedir

* Wed Dec 05 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.97.0-1
- kde-3.97.0

* Thu Nov 29 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.96.2-1
- kde-3.96.2

* Tue Nov 27 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.96.1-2
- kde-3.96.1

* Thu Nov 15 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.96.0-1
- kde-3.96.0

* Fri Nov 09 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.95.2-1
- kde-3.95.2

* Mon Nov 05 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.95.0-1
- kde-3.95.0 (kde4 dev platform rc1)

* Thu Oct 18 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.94.0-1
- update to 3.94.0
- add new %%{_kde4_libdir}/Gpgmepp directory to file list

* Thu Oct 4 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-4
- drop ExcludeArch: ppc64 (#300591)

* Fri Sep 21 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-3
- ExcludeArch: ppc64 (#300591)

* Thu Sep 13 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-2
- delete KMail/KNode transport migration scripts which break KDE 3

* Sun Sep 9 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-1
- update to 3.93.0
- drop kde4home patch (no longer applied)
- list BR strigi-devel only once
- move devel symlinks to %%{_kde4_libdir}/kde4/devel/

* Tue Aug 14 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.92.0-4
- use macros.kde4
- License: LGPLv2

* Mon Jul 30 2007 Than Ngo <than@redhat.com> 3.92.0-2
- add BR: gpgme-devel

* Sat Jul 28 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.92.0-1
- kde-3.92 (kde-4-beta1)

* Thu Jun 29 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-3
- fix %%_sysconfdir for %%_prefix != /usr case.

* Thu Jun 28 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-2
- updated kde4home.diff
- CMAKE_BUILD_TYPE=RelWithDebInfo (we're already using %%optflags)
- drop SNPRINTF hack

* Wed Jun 27 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-1
- kde-3.91.0
- CMAKE_BUILD_TYPE=debug

* Sat Jun 23 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.90.1-2
- specfile cleanup (%%prefix issues mostly)

* Sun May 13 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.90.1-1
- update to 3.90.1
- bump cmake BR to 2.4.5 as required upstream now
- don't set execute bits by hand anymore, cmake has been fixed
- use multilibs in /opt/kde4
- add BR boost-devel

* Fri Mar 23 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.3-4
- restore minimum version requirement for cmake
- don't set QT4DIR and PATH anymore, qdbuscpp2xml has been fixed

* Mon Mar 05 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.80.3-3
- +eXecute perms for %%{prefix}/lib/*

* Fri Feb 23 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.3-2
- rebuild for patched FindKDE4Internal.cmake

* Wed Feb 21 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.3-1
- update to 3.80.3
- update and improve parallel-installability patch
- readd BR cyrus-sasl-devel
- don't set LD_LIBRARY_PATH
- set QT4DIR and PATH so CMake's direct $QT4DIR/qdbuscpp2xml calls work
- define HAVE_SNPRINTF to work around vsnprintf.c build failure

* Wed Nov 29 2006 Chitlesh Goorah <chitlesh [AT] fedoraproject DOT org> 3.80.2-0.3.20061003svn
- dropped -DCMAKE_SKIP_RPATH=TRUE from cmake
- compiling with QA_RPATHS=0x0003; export QA_RPATHS
- added libXtst-devel libXpm-devel as BR

* Fri Nov 24 2006 Chitlesh Goorah <chitlesh [AT] fedoraproject DOT org> 3.80.2-0.2.20061003svn
- parallel build support
- added -DCMAKE_SKIP_RPATH=TRUE to cmake to skip rpath
- dropped qt4-devel >= 4.2.0, cyrus-sasl-devel  as BR
- spec file cleanups and added clean up in %%install
- fixed PATH for libkdecore.so.5; cannot open shared object file;

* Sat Oct 07 2006 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.2-0.1.20061003svn
- first Fedora RPM (parts borrowed from the OpenSUSE kdepimlibs 4 RPM and the Fedora kdelibs 3 RPM)
- apply parallel-installability patch

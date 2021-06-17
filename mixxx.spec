# Build out-of-source (default since Fedora 33)
%undefine __cmake_in_source_build

# Disable LTO for ppc64
%ifarch %{power64}
%global _lto_cflags %{nil}
%endif

# Optional: Package version suffix for pre-releases, e.g. "beta" or "rc"
%global extraver beta

# Optional: Only used for untagged snapshot versions
%global gitcommit 060b86aa7bc36e99df0ede476b04eec0f19735d4
# Format: <yyyymmdd>
%global gitcommitdate 20210615

# Additional sources
%global libkeyfinder_archive v2.2.4.zip

%if "%{?gitcommit}" == ""
  # (Pre-)Releases
  %global sources release-%{version}%{?extraver:-%{extraver}}
%else
  # Snapshots
  %global sources %{gitcommit}
  %global snapinfo %{?gitcommit:%{?gitcommitdate}git%{?gitcommit:%(c=%{gitcommit}; echo ${c:0:7})}}
%endif

Name:           mixxx
Version:        2.3.0
Release:        0.24%{?extraver:.%{extraver}}%{?snapinfo:.%{snapinfo}}%{?dist}
Summary:        Mixxx is open source software for DJ'ing
License:        GPLv2+
URL:            http://www.mixxx.org
Source0:        https://github.com/mixxxdj/%{name}/archive/%{sources}/%{name}-%{sources}.tar.gz
# Temporarily rename the libkeyfinder archive for disambiguation while downloading sources
Source1:        https://github.com/mixxxdj/libkeyfinder/archive/%{libkeyfinder_archive}#/libkeyfinder_%{libkeyfinder_archive}

# Build Tools
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  protobuf-compiler
BuildRequires:  cmake3
BuildRequires:  ccache
BuildRequires:  gcc-c++
BuildRequires:  ninja-build

# Build Requirements
BuildRequires:  chrpath
# The runtime libraries of FAAD2 are needed during the build for testing
BuildRequires:  faad2
BuildRequires:  ffmpeg-devel
BuildRequires:  flac-devel
BuildRequires:  hidapi-devel
BuildRequires:  lame-devel
BuildRequires:  libebur128-devel
BuildRequires:  libGL-devel
BuildRequires:  libGLU-devel
BuildRequires:  libchromaprint-devel
BuildRequires:  fftw-devel
BuildRequires:  libid3tag-devel
BuildRequires:  libmad-devel
BuildRequires:  libmodplug-devel
BuildRequires:  libmp4v2-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libusbx-devel
BuildRequires:  lilv-devel
BuildRequires:  libvorbis-devel
BuildRequires:  opus-devel
BuildRequires:  opusfile-devel
BuildRequires:  portaudio-devel
BuildRequires:  portmidi-devel
BuildRequires:  protobuf-lite-devel
BuildRequires:  qt5-linguist
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtscript-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qtx11extras-devel
BuildRequires:  qt5-qtxmlpatterns-devel
BuildRequires:  qtkeychain-qt5-devel
BuildRequires:  rubberband-devel
BuildRequires:  soundtouch-devel
BuildRequires:  sqlite-devel
BuildRequires:  taglib-devel
BuildRequires:  upower-devel
BuildRequires:  wavpack-devel

# Runtime Requirements
Requires: faad2
Requires: open-sans-fonts
Requires: qt5-qttranslations

%description
Mixxx is open source software for DJ'ing. You can use
AIFF/FLAC/M4A/MP3/OggVorbis/Opus/WAV/WavPack files, and
other formats as audio input. Playback can be controlled
through the GUI or with external controllers including
MIDI and HID devices.


%prep

%autosetup -p1 -n %{name}-%{sources}

echo "#pragma once" > src/build.h
%if "%{?extraver}" != ""
  echo "#define BUILD_BRANCH \"%{extraver}\"" >> src/build.h
%endif
%if "%{?snapinfo}" != ""
  echo "#define BUILD_REV \"%{snapinfo}\"" >> src/build.h
%endif

# Copy the libkeyfinder archive from the sources folder into the
# dedicated download folder of the build directory. Thereby rename
# the archive back into the original name as expected by the CMake
# build.
mkdir -p %{__cmake_builddir}/download/libkeyfinder
cp %{SOURCE1} %{__cmake_builddir}/download/libkeyfinder/%{libkeyfinder_archive}


%build
%cmake3 \
  -GNinja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DOPTIMIZE=portable \
  -DINSTALL_USER_UDEV_RULES=ON \
  -DWARNINGS_FATAL=ON \
  -DBATTERY=ON \
  -DBROADCAST=ON \
  -DBULK=ON \
  -DFAAD=ON \
  -DFFMPEG=ON \
  -DHID=ON \
  -DKEYFINDER=ON \
  -DLOCALECOMPARE=ON \
  -DLILV=ON \
  -DMAD=ON \
  -DMODPLUG=ON \
  -DOPUS=ON \
  -DQTKEYCHAIN=ON \
  -DVINYLCONTROL=ON \
  -DWAVPACK=ON

%cmake3_build


%install

# Install build artifacts
%cmake3_install

# Install desktop launcher
desktop-file-install \
  --vendor "" \
  --dir %{buildroot}%{_datadir}/applications \
  res/linux/%{name}.desktop

# Install custom USB HID permissions before 70-uaccess.rules
install -DT \
  %{buildroot}%{_datadir}/%{name}/udev/rules.d/%{name}-usb-uaccess.rules \
  %{buildroot}%{_udevrulesdir}/69-%{name}-usb-uaccess.rules


# Delete unpackaged/unused files and directories
rm -rf \
  %{buildroot}%{_prefix}%{_sysconfdir}/ \
  %{buildroot}%{_datadir}/doc/ \
  %{buildroot}%{_datadir}/%{name}/udev/


%check

# TODO: Enable EngineBufferE2ETest after spurious failures for
# x86_64 when run on AMD EPYC have been resolved. Varying tests
# are failing sometimes.
%ifarch x86_64
  %global ctest_timeout_secs 180
  %global ctest_exclude_regex EngineBufferE2ETest
%endif

# TODO: Enable ControllerEngine NaN tests on ARM after the cause for
# the failing tests has been found and fixed.
%ifarch %{arm32} %{arm64}
  %global ctest_timeout_secs 300
  %global ctest_exclude_regex setValue_IgnoresNaN|setParameter_NaN
%endif

%ifarch %{power64}
  %global ctest_timeout_secs 240
%endif

# Run tests
%if "%{?ctest_exclude_regex}" == ""
  %ctest3 --timeout %ctest_timeout_secs
%else
  %ctest3 --timeout %ctest_timeout_secs --exclude-regex "%ctest_exclude_regex"
%endif

# Validate AppStream data
appstream-util \
  validate-relax \
  --nonet \
  %{buildroot}%{_metainfodir}/%{name}.metainfo.xml


%files
%license COPYING LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_metainfodir}/%{name}.metainfo.xml
%{_udevrulesdir}/69-%{name}-usb-uaccess.rules

%changelog
* Wed Jun 16 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.24.beta.20210615git060b86a
- New upstream snapshot 2.3.0-beta

* Sun May 09 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.23.beta.20210509gite409a0e
- New upstream snapshot 2.3.0-beta
- Fixes an unnoticed regression: 2.3.0-0.22 used ~/local/share/Mixxx instead of ~/.mixxx
  for storing application data

* Wed May 05 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.22.beta.20210505git30af05c
- New upstream snapshot 2.3.0-beta
- Unbundle offline PDF manual

* Mon Mar 22 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.20.beta.20210322git25f342e
- New upstream snapshot 2.3.0-beta
- Fix column reordering

* Sat Mar 20 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.19.beta.20210320git672fea1
- New upstream snapshot 2.3.0-beta

* Tue Jan 26 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.17.beta.20210126gitf009e06
- New upstream snapshot 2.3.0-beta

* Fri Jan  1 2021 Leigh Scott <leigh123linux@gmail.com> - 2.3.0-0.16.beta.20201211git18f698d
- Rebuilt for new ffmpeg snapshot

* Fri Dec 11 23:48:31 CET 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.15.beta.20201211git18f698d
- New upstream snapshot 2.3.0-beta

* Sat Dec  5 15:01:55 CET 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.14.beta.20201205gitbf343d2
- New upstream snapshot 2.3.0-beta

* Thu Nov 26 08:56:41 CET 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.13.beta.20201126git7e18fc4
- New upstream snapshot 2.3.0-beta

* Wed Nov 11 08:59:48 CET 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.12.beta.20201110git6b0fb69
- Fix default folder for loading resources

* Tue Nov 10 11:35:54 CET 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.11.beta.20201110git6b0fb69
- New upstream snapshot 2.3.0-beta
- Fix ALSA real-time scheduling

* Wed Nov  4 14:48:50 CET 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.10.beta.20201104git8e90a47
- New upstream snapshot 2.3.0-beta
- Disable LTO on all platforms after crash reports for x86_64

* Sat Oct 31 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.9.beta.20201031gitab6d8ee
- New upstream snapshot 2.3.0-beta

* Sun Aug 16 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.8.beta.20200816git64fd2d6
- New upstream snapshot 2.3.0-beta
- Re-enable faad2 for decoding MP4/M4A files (actually now)

* Wed Jun 24 2020 Leigh Scott <leigh123linux@gmail.com> - 2.3.0-0.7.beta.20200614git3a734c0
- Rebuild for new protobuf

* Sun Jun 14 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.6.beta.20200614git3a734c0
- New upstream snapshot 2.3.0-beta
- Re-enable faad2 for decoding MP4/M4A files

* Sun May 17 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.5.beta.20200516git293ffd7
- New upstream snapshot 2.3.0-beta

* Fri May 08 2020 Leigh Scott <leigh123linux@gmail.com> - 2.3.0-0.4.alpha.20200507git0786536
- Use cmake3 and switch to ninja-build
- Fix source URL
- Fix doc install
- Clean up appdata install
- Remove Group tag

* Fri May 08 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.3.alpha.20200507git0786536
- New upstream snapshot 2.3.0-pre-alpha
- Temporarily disabled broken faad2 support

* Fri Mar 20 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.2.alpha.20200320git7980941
- New upstream snapshot 2.3.0-pre-alpha
- Fix udev rules for USB HID devices
- Build debuginfo packages
- Use cmake macros for the build

* Tue Mar 17 2020 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-0.1.alpha.20200316gite16b6a6
- New upstream snapshot 2.3.0-pre-alpha
- Replaced build system SCons with CMake

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Dec 22 2019 Leigh Scott <leigh123linux@googlemail.com> - 2.2.3-2
- Rebuild for new protobuf version

* Mon Dec 09 2019 Uwe Klotz <uwe.klotz@gmail.com> - 2.2.3-1
- New upstream release 2.2.3

* Mon Nov 11 2019 Uwe Klotz <uklotz@mixxx.org> - 2.2.2-4
- Add appdata patch

* Wed Nov 06 2019 Uwe Klotz <uklotz@mixxx.org> - 2.2.2-3
- Fix desktop launcher patch

* Thu Oct 31 2019 Uwe Klotz <uklotz@mixxx.org> - 2.2.2-2
- Use XCB instead of the default Qt Wayland platform adapter
- Use system libebur128

* Wed Aug 14 2019 Uwe Klotz <uklotz@mixxx.org> - 2.2.2-1
- New upstream release 2.2.2

* Wed Aug 07 2019 Leigh Scott <leigh123linux@gmail.com> - 2.2.1-2
- Rebuild for new ffmpeg version

* Tue Apr 23 2019 Uwe Klotz <uklotz@mixxx.org> - 2.2.1-1
- New upstream release 2.2.1

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 24 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-1
- New upstream release 2.2.0

* Wed Dec 12 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-0.7.rc.20181212gitbd42189
- 7th upstream release candidate snapshot for 2.2.0
- Remove remaining Qt4 dependencies (QtKeychain)
- Fix a performance regression

* Thu Dec 06 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-0.6.rc.20181205git5752e91
- 6th upstream release candidate snapshot for 2.2.0
- New build dependency and workaround for Xlib deadlock

* Mon Nov 26 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-0.5.rc.20181126git9fb543c
- 5th upstream release candidate snapshot for 2.2.0
- Rename plugin directories

* Sat Nov 10 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-0.4.rc.20181106gitfaf1a67
- Upstream release candidate snapshot for 2.2.0
- Rename plugin directories

* Sun Oct 28 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-0.3.beta.20181027git96f139d
- 3rd upstream beta snapshot for 2.2.0

* Tue Oct 09 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-0.2.beta.20181009gitb488246
- 2nd upstream beta snapshot for 2.2.0

* Mon Sep 24 2018 Uwe Klotz <uklotz@mixxx.org> - 2.2.0-0.1.beta.20180924git33e0cc3
- 1st upstream beta test release for 2.2.0
- Update build and dependencies from Qt 4 to Qt 5
- Add support for QtKeychain to store broadcasting credentials

* Thu Sep 06 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.4-1
- New upstream release 2.1.4

* Mon Aug 20 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.3-1
- New upstream release 2.1.3

* Sun Aug 19 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.2-1
- Update to upstream release 2.1.2
- Re-enable FFmpeg
- Remove obsolete build flag

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 14 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.1-2
- Update to upstream release 2.1.1
- Use system library SoundTouch v2.0+ if available

* Sun Apr 15 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.0-1
- Initial release of Mixxx 2.1.0

* Wed Apr 11 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.0-0.7.rc1
- Re-add missing install option

* Wed Apr 11 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.0-0.6.rc1
- Update build requirements and options
- Switch from debug to release build
- Enable USB HID and bulk support
- Remove obsolete/redundant/unused build requirements
- Remove obsolete lower version boundaries from build requirements

* Tue Apr 10 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.0-0.5.rc1
- Update to 2.1.0-rc1 pre-release version

* Tue Apr 10 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.0-0.4.20180407git66028dd
- Update to (inofficial) 2.1.0-rc1 snapshot
- Remove pkgrel macro
- Fix distinction between snapshots and releases

* Wed Apr 04 2018 Uwe Klotz <uklotz@mixxx.org> - 2.1.0-0.3.20180404gitf77cf96
- Update to 2.1 snapshot
- Add support for Opus, WavPack, and Mod tracker files
- Adjust and optimize build options

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 2.1.0-0.2.20180204git22f78d2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Feb 05 2018 Leigh Scott <leigh123linux@googlemail.com> - 2.1.0-0.1.20180204git22f78d2
- Update to 2.1 snapshot
- Add build requires upower-devel

* Sat Dec 16 2017 Leigh Scott <leigh123linux@googlemail.com> - 2.0.0-12
- Rebuild for new protobuf .so version (f28)

* Tue Sep 12 2017 Leigh Scott <leigh123linux@googlemail.com> - 2.0.0-11
- Fix sqlite typedef issue

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.0.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Mar 24 2017 Leigh Scott <leigh123linux@googlemail.com> - 2.0.0-9
- Add aarch64 to arm build patch

* Mon Mar 20 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.0.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 07 2016 Leigh Scott <leigh123linux@googlemail.com> - 2.0.0-7
- Fix udev rules (rfbz#4329)

* Thu Oct 27 2016 Leigh Scott <leigh123linux@googlemail.com> - 2.0.0-6
- Fix appdata (rfbz#4311)

* Sun Aug 21 2016 Leigh Scott <leigh123linux@googlemail.com> - 2.0.0-5
- Add udev rule (rfbz#4064)

* Sun Aug 21 2016 Leigh Scott <leigh123linux@googlemail.com> - 2.0.0-4
- Patch so it builds on ARM (rfbz#2413)
- Validate appdata file
- Clean up files section

* Thu Jul 14 2016 Sérgio Basto <sergio@serjux.com> - 2.0.0-3
- Add gcc6 patch

* Tue Feb 09 2016 Sérgio Basto <sergio@serjux.com> - 2.0.0-2
- Remove rpath in linkage,
  https://bugzilla.rpmfusion.org/show_bug.cgi?id=3873#c7

* Sun Feb 07 2016 Sérgio Basto <sergio@serjux.com> - 2.0.0-1
- Review BuildRequires from
  https://github.com/mixxxdj/mixxx/blob/master/.travis.yml

* Fri Feb 05 2016 Martin Milata <b42@srck.net>
- Update to 2.0.0

* Sun May 03 2015 Nicolas Chauvet <kwizart@gmail.com> - 1.11.0-4
- Add ExclusiveArch - Workaround rfbz#2413
- Add m4a support - rhbz#3488
- Spec file clean-up

* Mon Sep 01 2014 Sérgio Basto <sergio@serjux.com> - 1.11.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri May 17 2013 Steven Boswell <ulatekh@yahoo.com> - 1.11.0-1
- Update to 1.11.0

* Thu May 03 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.10.0-1
- Update to 1.10.0

* Fri Mar 02 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.9.2-3
- Rebuilt for c++ ABI breakage

* Wed Feb 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 8 2011 John Brier <johnbrier@gmail.com> - 1.9.2-1
- Update to 1.9.2
- build with shoutcast support
- remove -n option to setup since upstream source extracts
  into a directory of name-version format now
- remove old experimental build options that are no longer
  relevant

* Mon May 9 2011 John Brier <johnbrier@gmail.com> - 1.9.0-2
- add BuildRequires phonon-backend-gstreamer since phonon-backend-vlc
  is broken in rpmfusion currently

* Tue Feb 22 2011 John Brier <johnbrier@gmail.com>- 1.9.0-1
- Update to 1.9.0
- Added BuildRequires to spec file for taglib-devel and flac-devel header files

* Fri Jan 21 2011 Nicolas Chauvet <kwizart@gmail.com> - 1.8.2-1
- Update to 1.8.2

* Wed Oct 13 2010 Nicolas Chauvet <kwizart@gmail.com> - 1.8.0.2-1
- Update to 1.8.0.2

* Mon Sep 06 2010 Nicolas Chauvet <kwizart@gmail.com> - 1.7.2-1
- Update to 1.7.2

* Sat Oct 17 2009 kwizart < kwizart at gmail.com > - 1.7.0-1
- Update to 1.7.0

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 1.6.1-2
- rebuild for new F11 features

* Mon Sep 29 2008 kwizart < kwizart at gmail.com > - 1.6.1-1
- Update to 1.6.1

* Thu Sep 11 2008 kwizart < kwizart at gmail.com > - 1.6.0-1
- Initial version

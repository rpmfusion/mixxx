# Optional: Package version suffix for pre-releases, e.g. "beta" or "rc"
%global extraver alpha

# Optional: Only used for untagged snapshot versions
%global gitcommit e16b6a63b28eab4d3c3ce919ed661a91d7fc664d
# Format: <yyyymmdd>
%global gitcommitdate 20200316

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
Release:        0.1%{?extraver:.%{extraver}}%{?snapinfo:.%{snapinfo}}%{?dist}
Summary:        Mixxx is open source software for DJ'ing
Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://www.mixxx.org
Source0:        https://github.com/mixxxdj/%{name}/archive/%{sources}.tar.gz#/%{name}-%{sources}.tar.gz
Patch0:         usb_hidapi_udev_rules0.patch
Patch1:         usb_hidapi_udev_rules1.patch

# Build Tools
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  protobuf-compiler
BuildRequires:  cmake
BuildRequires:  ccache
BuildRequires:  gcc-c++

# Build Requirements
BuildRequires:  chrpath
BuildRequires:  faad2-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  fftw-devel
BuildRequires:  flac-devel
BuildRequires:  hidapi-devel
BuildRequires:  libebur128-devel
BuildRequires:  libGL-devel
BuildRequires:  libGLU-devel
BuildRequires:  libchromaprint-devel
BuildRequires:  libid3tag-devel
BuildRequires:  libmad-devel
BuildRequires:  libmodplug-devel
BuildRequires:  libmp4v2-devel
BuildRequires:  libshout-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libusbx-devel
BuildRequires:  lilv-devel
BuildRequires:  libvorbis-devel
BuildRequires:  opus-devel
BuildRequires:  opusfile-devel
BuildRequires:  portaudio-devel
BuildRequires:  portmidi-devel
BuildRequires:  protobuf-devel
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


%description
Mixxx is open source software for DJ'ing. You can use
AIFF/FLAC/M4A/MP3/OggVorbis/Opus/WAV/WavPack files, and
other formats as audio input. Playback can be controlled
through the GUI or with external controllers including
MIDI and HID devices.


%global debug_package %{nil}


%prep
%autosetup -p1 -n %{name}-%{sources}
echo "#pragma once" > src/build.h
%if 0%{?extraver:1}
  echo "#define BUILD_BRANCH \"%{extraver}\"" >> src/build.h
%endif
%if 0%{?snapinfo:1}
  echo "#define BUILD_REV \"%{snapinfo}\"" >> src/build.h
%endif


%build
ccache -s
mkdir -p cmake_build
cd cmake_build
cmake \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DCMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES=%{_includedir} \
  -DCMAKE_INSTALL_PREFIX=%{_prefix} \
  -DCMAKE_BUILD_TYPE=Release \
  -DOPTIMIZE=portable \
  -DINSTALL_GTEST=OFF \
  -DWITH_STATIC_PIC=ON \
  -DBATTERY=ON \
  -DBROADCAST=ON \
  -DBULK=ON \
  -DFAAD=ON \
  -DFFMPEG=ON \
  -DHID=ON \
  -DLOCALECOMPARE=ON \
  -DLILV=ON \
  -DMAD=ON \
  -DMODPLUG=ON \
  -DOPUS=ON \
  -DQTKEYCHAIN=ON \
  -DVINYLCONTROL=ON \
  -DWAVPACK=ON \
  ..
cmake \
  --build . \
  --target mixxx \
  %{?_smp_mflags}


%install

# Executable
install -Dpsm 0755 \
  -t %{buildroot}%{_bindir} \
  cmake_build/%{name}

# Icon
install -Dpm 0644 \
  -t %{buildroot}%{_datadir}/pixmaps \
  res/images/%{name}_icon.svg \

# Resources
for subdir in controllers fonts keyboard skins translations
do
  pushd .
  cd res/$subdir
  find . \
    -type f \
    -exec install -Dpm 0644 "{}" "%{buildroot}%{_datadir}/%{name}/$subdir/{}" \;
  popd
done

# Docs
install -Dpm 0644 \
  -t %{buildroot}%{_docdir}/%{name} \
  README \
  README.md \
  Mixxx-Manual.pdf

# USB HID permissions
# Order custom rules before 70-uaccess.rules
install -Dpm 0644 \
  res/linux/%{name}-usb-uaccess.rules \
  %{buildroot}%{_udevrulesdir}/69-%{name}-usb-uaccess.rules

# Desktop launcher
desktop-file-install \
  --vendor "" \
  --dir %{buildroot}%{_datadir}/applications \
  --add-category=X-Synthesis \
  res/linux/%{name}.desktop

# AppStream metadata
appstream-util \
  validate-relax \
  --nonet \
  res/linux/%{name}.appdata.xml
install -Dpm 0644 \
  -t %{buildroot}%{_datadir}/appdata \
  res/linux/%{name}.appdata.xml


%files
%license COPYING LICENSE
%doc Mixxx-Manual.pdf README README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}_icon.svg
%{_datadir}/appdata/%{name}.appdata.xml
%{_udevrulesdir}/69-%{name}-usb-uaccess.rules


%changelog
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

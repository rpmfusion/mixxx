# Disable LTO for ppc64
%ifarch %{power64}
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%global _lto_cflags %{nil}
%endif

# https://github.com/mixxxdj/mixxx/issues/14714
# https://bugreports.qt.io/browse/QTBUG-135623
#
# /builddir/build/BUILD/mixxx-2.5.2-build/mixxx-2.5.2/src/sources/soundsourceflac.cpp: In member function ‘void mixxx::SoundSourceFLAC::flacError(FLAC__StreamDecoderErrorStatus)’:
# /builddir/build/BUILD/mixxx-2.5.2-build/mixxx-2.5.2/src/sources/soundsourceflac.cpp:571:12: error: enumeration value ‘FLAC__STREAM_DECODER_ERROR_STATUS_OUT_OF_BOUNDS’ not handled in switch [-Werror=switch]
#   571 |     switch (status) {
#      |            ^
# /builddir/build/BUILD/mixxx-2.5.2-build/mixxx-2.5.2/src/sources/soundsourceflac.cpp:571:12: error: enumeration value ‘FLAC__STREAM_DECODER_ERROR_STATUS_MISSING_FRAME’ # not handled in switch [-Werror=switch]

%global optflags %{optflags} -Wno-array-bounds -Wno-error=switch

# Optional: Package version suffix for pre-releases, e.g. "beta" or "rc"
#global extraver beta

# Optional: Only used for untagged snapshot versions
#global gitcommit d225a5112166e9224e0c61cdc413b9145d009c06 
# Format: <yyyymmdd>
#global gitcommitdate 20240214

# Additional sources
%global libkeyfinder_version 2.2.8

# Additional sources
%global libdjinterop_version 0.24.3

%if "%{?gitcommit}" == ""
  # (Pre-)Releases
  %global sources %{version}%{?extraver:-%{extraver}}
%else
  # Snapshots
  %global sources %{gitcommit}
  %global snapinfo %{?gitcommit:%{?gitcommitdate}git%{?gitcommit:%(c=%{gitcommit}; echo ${c:0:7})}}
%endif

Name:           mixxx
Version:        2.5.3
Release:        1%{?dist}
Summary:        Mixxx is open source software for DJ'ing
License:        GPLv2+
URL:            http://www.mixxx.org
Source0:        https://github.com/mixxxdj/%{name}/archive/%{sources}/%{name}-%{sources}.tar.gz
# Append the actual downloaded file name with a preceding slash '/'
# as a fragment identifier to the URL to populate SOURCE<n> correctly
Source1:        https://github.com/mixxxdj/libkeyfinder/archive/refs/tags/%{libkeyfinder_version}.zip#/libkeyfinder-%{libkeyfinder_version}.zip
Source2:        https://github.com/xsco/libdjinterop/archive/refs/tags/%{libdjinterop_version}.tar.gz#/libdjinterop-%{libdjinterop_version}.tar.gz
Patch0:         desktop-file-qpa-platform-xcb.patch

# Build Tools
BuildRequires:  desktop-file-utils
BuildRequires:  appstream
BuildRequires:  protobuf-compiler
BuildRequires:  cmake
BuildRequires:  ccache
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  gtest-devel
BuildRequires:  gmock-devel
BuildRequires:  google-benchmark-devel

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
BuildRequires:  guidelines-support-library-devel
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
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-qtshadertools-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qtkeychain-qt6-devel
BuildRequires:  rubberband-devel
BuildRequires:  soundtouch-devel
BuildRequires:  sqlite-devel
BuildRequires:  taglib-devel
BuildRequires:  upower-devel
BuildRequires:  wavpack-devel
BuildRequires:  zlib-devel

# Runtime Requirements
#Requires: faad2
Requires: open-sans-fonts
Requires: qt6-qttranslations

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

# Copy the source archives from the sources folder into the
# dedicated downloads folder of the build directory.
mkdir -p %{__cmake_builddir}/downloads
cp %{SOURCE1} %{__cmake_builddir}/downloads
cp %{SOURCE2} %{__cmake_builddir}/downloads

%build

# CMAKE_DISABLE_PRECOMPILE_HEADERS: <https://github.com/mixxxdj/mixxx/issues/12073>
%cmake \
  -GNinja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON \
  -DOPTIMIZE=portable \
  -DINSTALL_USER_UDEV_RULES=ON \
  -DWARNINGS_FATAL=ON \
  -DBATTERY=ON \
  -DBROADCAST=ON \
  -DBULK=ON \
  -DENGINEPRIME=ON \
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

%cmake_build


%install

# Install build artifacts
%cmake_install

# Install desktop launcher
desktop-file-install \
  --vendor "" \
  --dir %{buildroot}%{_datadir}/applications \
  res/linux/org.mixxx.Mixxx.desktop

# Delete unpackaged/unused files and directories
rm -rf \
  %{buildroot}%{_prefix}%{_sysconfdir}/ \
  %{buildroot}%{_datadir}/doc/ \
  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}_macos.svg \
  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}_ios.svg 


%check

# TODO: Enable EngineBufferE2ETest after spurious failures have been resolved.
# TODO: Enable LoopingControlTest after spurious failures have been resolved.
#%%global ctest_exclude_regex EngineBufferE2ETest|LoopingControlTest

%ifarch x86_64
  %global ctest_timeout_secs 180
%endif

# TODO: Enable ControllerEngine NaN tests on ARM after the cause for
# the failing tests has been found and fixed.
%ifarch %{arm32} %{arm64}
  %global ctest_timeout_secs 300
  #%%global ctest_exclude_regex %{?ctest_exclude_regex:%{ctest_exclude_regex}|}setValue_IgnoresNaN|setParameter_NaN|MovingInterquartileMeanTest
%endif

%ifarch %{power64}
  %global ctest_timeout_secs 240
%endif

# Run tests
%if "%{?ctest_exclude_regex}" == ""
  %ctest --timeout %ctest_timeout_secs || :
%else
  %ctest --timeout %ctest_timeout_secs --exclude-regex "%ctest_exclude_regex"
%endif

# Validate AppStream data
appstreamcli \
  validate \
  --no-net \
  %{buildroot}%{_metainfodir}/org.mixxx.Mixxx.metainfo.xml


%files
%license COPYING LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/org.mixxx.Mixxx.desktop
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
%{_datadir}/icons/hicolor/512x512/apps/%{name}.png
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_metainfodir}/org.mixxx.Mixxx.metainfo.xml
%{_udevrulesdir}/69-%{name}-usb-uaccess.rules

%changelog
* Wed Sep 17 2025 Sérgio Basto <sergio@serjux.com> - 2.5.3-1
- Update mixxx to 2.5.3

* Tue Jul 29 2025 Sérgio Basto <sergio@serjux.com> - 2.5.2-1
- Update mixxx to 2.5.2

* Sun Jul 27 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 2.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Tue Apr 29 2025 Luís Correia <luis.f.correia@gmail.com> - 2.5.1-1
- New upstream release 2.5.1

* Tue Jan 28 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 2.5.0-1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Sat Dec 28 2024 Luís Correia <luis.f.correia@gmail.com> - 2.5.0-1
- New upstream release 2.5.0, fix dependencies

* Sat Dec 28 2024 Luís Correia <luis.f.correia@gmail.com> - 2.5.0-0
- New upstream release 2.5.0

* Thu Nov 28 2024 Luís Correia <luis.f.correia@gmail.com> - 2.4.2-3
- New upstream release 2.4.2

* Thu Nov 28 2024 Luís Correia <luis.f.correia@gmail.com> - 2.4.2-2
- New upstream release 2.4.2

* Thu Nov 28 2024 Luís Correia <luis.f.correia@gmail.com> - 2.4.2-1
- New upstream release 2.4.2

* Fri Nov 01 2024 Luís Correia <luis.f.correia@gmail.com> - 2.4.1-3
- Add new dependency and prepare for F41

* Fri Nov 01 2024 Luís Correia <luis.f.correia@gmail.com> - 2.4.1-4
- rebuilt

* Fri Nov 01 2024 Luís Correia <luis.f.correia@gmail.com> - 2.4.1-3
- rebuilt

* Fri Aug 02 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 2.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Wed May 29 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.1-1
- New upstream release 2.4.1

* Fri Feb 16 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.0-2
- New upstream release 2.4.0

* Wed Feb 14 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.0-1
- New upstream release 2.4.0

* Mon Feb 12 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.0-0.17.beta.20240212git81066fd
- New upstream snapshot 2.4.0-0.17.beta.20240212git81066fd

* Fri Feb 09 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.0-0.16.beta.20240209gitd112e4c
- New upstream snapshot 2.4.0-0.16.beta.20240209gitd112e4c

* Fri Feb 09 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.0-0.15.beta.20240208git40be3fe
- Disable a test for aarch64

* Thu Feb 08 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.0-0.14.beta.20240208git40be3fe
- New upstream snapshot 2.4.0-0.14.beta.20240208git40be3fe

* Thu Feb 08 2024 Luis Correia <luis.f.correia@gmail.com> - 2.4.0-0.13.beta.20240208git40be3fe
- New upstream snapshot 2.4.0-0.13.beta.20240208git40be3fe

* Sat Feb 03 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 2.4.0-0.12.beta.20240117git55decf0
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Wed Jan 17 2024 Uwe Klotz <uwe.klotz@gmail.com> - 2.4.0-0.11.beta.20240117git55decf0
- New upstream snapshot 2.4.0-beta

* Wed May 10 2023 Uwe Klotz <uwe.klotz@gmail.com> - 2.3.5-1
- New upstream release 2.3.5

* Sat Apr 22 2023 Uwe Klotz <uwe.klotz@gmail.com> - 2.3.4-4
- Switch back to GCC 13

* Mon Apr 17 2023 Uwe Klotz <uwe.klotz@gmail.com> - 2.3.4-3
- Switch from GCC 13 to Clang 16

* Mon Mar 13 2023 Leigh Scott <leigh123linux@gmail.com> - 2.3.4-2
- rebuilt

* Fri Mar 03 2023 Uwe Klotz <uklotz@mixxx.org> - 2.3.4-1
- New upstream release 2.3.4

* Wed Feb 08 2023 Leigh Scott <leigh123linux@gmail.com> - 2.3.3-3
- Rebuild for new flac

* Sun Aug 07 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 2.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Tue Jun 21 2022 Uwe Klotz <uklotz@mixxx.org> - 2.3.3-1
- New upstream release 2.3.3

* Wed Feb 09 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 2.3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Tue Feb 01 2022 Uwe Klotz <uklotz@mixxx.org> - 2.3.2-2
- Fix missing release date in AppStream metadata

* Mon Jan 31 2022 Uwe Klotz <uklotz@mixxx.org> - 2.3.2-1
- New upstream release 2.3.2

* Wed Sep 29 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.1-1
- New upstream release 2.3.1

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Mon Jun 28 2021 Uwe Klotz <uklotz@mixxx.org> - 2.3.0-1
- Release version 2.3.0

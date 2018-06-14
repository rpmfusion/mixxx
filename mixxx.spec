# Optional: Package version suffix for pre-releases, e.g. "beta1", "beta2", "rc1", ...
#global extraver rc1

# Optional: Only used for untagged snapshot versions
#global gitcommit 66028ddb1a16722285fcc999c2e7170c446b7c03 
# Format: <yyyymmdd>
#global gitcommitdate 20180407

%if "%{?gitcommit}" == ""
# (Pre-)Releases
%global sources release-%{version}%{?extraver:-%{extraver}}
%else
# Snapshots
%global sources %{gitcommit}
%global snapinfo %{?gitcommit:%{?gitcommitdate}git%{?gitcommit:%(c=%{gitcommit}; echo ${c:0:7})}}
%endif

Name:           mixxx
Version:        2.1.1
Release:        2%{?extraver:.%{extraver}}%{?snapinfo:.%{snapinfo}}%{?dist}
Summary:        Mixxx is open source software for DJ'ing
Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://www.mixxx.org
Source0:        https://github.com/mixxxdj/%{name}/archive/%{sources}.tar.gz#/%{name}-%{sources}.tar.gz

# Build Tools
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  protobuf-compiler
BuildRequires:  python2-scons

# Build Requirements
BuildRequires:  faad2-devel
# 2018-04-11 uklotzde: FFmpeg support has been disabled temporarily
# due to incompatibilities causing build errors in rawhide/f29
# See below: SCons build option ffmpeg=0/1
#BuildRequires:  ffmpeg-devel
BuildRequires:  fftw-devel
BuildRequires:  flac-devel
BuildRequires:  hidapi-devel
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
BuildRequires:  libvorbis-devel
BuildRequires:  opus-devel
BuildRequires:  opusfile-devel
BuildRequires:  portaudio-devel
BuildRequires:  portmidi-devel
BuildRequires:  protobuf-devel
BuildRequires:  qt4-devel
BuildRequires:  rubberband-devel
BuildRequires:  soundtouch-devel
BuildRequires:  sqlite-devel
BuildRequires:  taglib-devel
BuildRequires:  upower-devel
BuildRequires:  wavpack-devel

# Bundled Requirements
# The following essential libraries for audio processing are
# currently bundled and statically linked to avoid unexpected
# behavior due to version differences.
#BuildRequires:  libebur128-devel
#BuildRequires:  vamp-plugin-sdk-devel


%description
Mixxx is open source software for DJ'ing. You can use
AIFF/FLAC/M4A/MP3/OggVorbis/Opus/WAV/WavPack files, and
other formats as audio input. Playback can be controlled
through the GUI or with external controllers including
MIDI and HID devices.


%prep
%autosetup -p1 -n %{name}-%{sources}

# TODO: Remove bundled libs before build?
#rm -rf \
#  lib/gmock* \
#  lib/gtest* \
#  lib/libebur128* \
#  lib/soundtouch* \
#  lib/vamp \
#  lib/xwax \


%build
export CFLAGS=$RPM_OPT_FLAGS
export LDFLAGS=$RPM_LD_FLAGS
export LIBDIR=%{_libdir}
scons %{?_smp_mflags} \
  prefix=%{_prefix} \
  qtdir=%{_qt4_prefix} \
  build=release \
  optimize=portable \
  qdebug=1 \
  bulk=1 \
  faad=1 \
  ffmpeg=0 \
  hid=1 \
  modplug=1 \
  opus=1 \
  shoutcast=1 \
  wv=1 \


%install
export CFLAGS=$RPM_OPT_FLAGS
export LDFLAGS=$RPM_LD_FLAGS
export LIBDIR=%{_libdir}
scons %{?_smp_mflags} \
  prefix=%{_prefix} \
  qtdir=%{_qt4_prefix} \
  install_root=$RPM_BUILD_ROOT%{_prefix} \
  install

# Install udev rule
install -d ${RPM_BUILD_ROOT}/%{_udevrulesdir}
install -p -m 0644 res/linux/mixxx.usb.rules ${RPM_BUILD_ROOT}/%{_udevrulesdir}/90-mixxx.usb.rules

desktop-file-install \
  --vendor "" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --add-category=X-Synthesis \
  res/linux/mixxx.desktop

appstream-util \
  validate-relax \
  --nonet \
  $RPM_BUILD_ROOT/%{_datadir}/appdata/%{name}.appdata.xml

# Remove docdir
rm -rf $RPM_BUILD_ROOT%{_docdir}


%files
%license COPYING LICENSE
%doc Mixxx-Manual.pdf README README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_udevrulesdir}/90-mixxx.usb.rules
%{_libdir}/%{name}/
%{_datadir}/applications/mixxx.desktop
%{_datadir}/pixmaps/mixxx-icon.png
%{_datadir}/appdata/%{name}.appdata.xml


%changelog
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


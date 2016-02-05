Name:           mixxx
Version:        2.0.0
Release:        1%{?dist}
Summary:        Mixxx is open source software for DJ'ing

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://www.mixxx.org
Source0:        http://downloads.mixxx.org/mixxx-%{version}/%{name}-%{version}-src.tar.gz
Patch0:         %{name}-%{version}-build.patch

ExclusiveArch:  i686 x86_64

#Build tools
BuildRequires:  desktop-file-utils
BuildRequires:  scons

#Mandatory Requirements
BuildRequires:  alsa-lib-devel >= 1.0.10
BuildRequires:  faad2-devel
#BuildRequires:  jack-audio-connection-kit-devel >= 0.61.0 #jack seems deprecated to portaudio
BuildRequires:  qt4-devel >= 4.3
BuildRequires:  qt4-webkit-devel
BuildRequires:  libGL-devel
BuildRequires:  libGLU-devel
BuildRequires:  libid3tag-devel
BuildRequires:  libmad-devel
BuildRequires:  libmp4v2-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libusb1-devel
BuildRequires:  libvorbis-devel
BuildRequires:  portaudio-devel
BuildRequires:  portmidi-devel
BuildRequires:  protobuf-devel
BuildRequires:  taglib-devel
BuildRequires:  flac-devel
BuildRequires:  sqlite-devel
BuildRequires:  rubberband-devel
BuildRequires:  libchromaprint-devel

#Optionals Requirements
BuildRequires:  libshout-devel
#BuildRequires:  python-devel
#BuildRequires:  lua-devel, tolua++-devel
%{?_with_bpm:BuildRequires: fftw-devel}
%{?_with_djconsole:BuildRequires: libdjconsole-devel}
BuildRequires: ladspa-devel
%{?_with_libgpod:BuildRequires: libgpod-devel}
BuildRequires: wavpack-devel

# workaround to use phonon-backend-gstreamer instead of phonon-backend-vlc since phonon-backend-vlc
# is broken in rpmfusion currently
BuildRequires: phonon-backend-gstreamer

%description
Mixxx is open source software for DJ'ing. You can use MP3s,
Ogg Vorbis files, and other formats as audio input. Mixxx
can be controlled through the GUI and with external
controllers including MIDI devices, and more.


%prep
%setup -q
%patch0 -p1


%build
export CFLAGS=$RPM_OPT_FLAGS
export LDFLAGS=$RPM_LD_FLAGS
export LIBDIR=%{_libdir}
scons %{?_smp_mflags} \
  prefix=%{_prefix} \
  qtdir=%{_qt4_prefix} \
  faad=1 \
  ladspa=0 \
  shoutcast=1 hifieq=1 script=0 optimize=0 \



%install
export CFLAGS=$RPM_OPT_FLAGS
export LDFLAGS=$RPM_LD_FLAGS
export LIBDIR=%{_libdir}
scons %{?_smp_mflags} \
  install_root=$RPM_BUILD_ROOT%{_prefix} \
  qtdir=%{_qt4_prefix} \
  prefix=%{_prefix} install

desktop-file-install --vendor ""  \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --add-category=X-Synthesis \
  res/linux/mixxx.desktop

#Remove docdir
rm -rf $RPM_BUILD_ROOT%{_docdir}


%files
%doc COPYING LICENSE README README.md
%doc Mixxx-Manual.pdf
%{_bindir}/%{name}
%{_datadir}/%{name}/
%dir %{_libdir}/%{name}/plugins/vamp
%{_libdir}/%{name}/plugins/vamp/libmixxxminimal.so
%dir %{_libdir}/%{name}/plugins/soundsource
%{_libdir}/%{name}/plugins/soundsource/libsoundsourcem4a.so
%{_datadir}/applications/mixxx.desktop
%{_datadir}/pixmaps/mixxx-icon.png
%{_datadir}/appdata/%{name}.appdata.xml

%changelog
* Fri Feb 05 2016 Martin Milata <b42@srck.net> - 2.0.0-1
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


Name:           mixxx
Version:        1.11.0
Release:        2%{?dist}
Summary:        Mixxx is open source software for DJ'ing

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://www.mixxx.org
Source0:        http://downloads.mixxx.org/mixxx-%{version}/%{name}-%{version}-src.tar.gz
Patch0:         %{name}-%{version}-20130517bzr.patch
Patch1:         %{name}-%{version}-installpath.patch
Patch2:         %{name}-%{version}-wtf.patch
# Updated manual...build it yourself with:
# 1) bzr checkout lp:~mixxxdevelopers/mixxx/manual-1.11.x
# 2) cd manual-1.11.x; make html; make latexpdf; make latexpdf
Source1:        %{name}-%{version}-20130517bzr.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Build tools
BuildRequires:  desktop-file-utils
BuildRequires:  scons

#Mandatory Requirements
BuildRequires:  alsa-lib-devel >= 1.0.10
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
%patch1 -p1
%patch2 -p1
%setup -T -D -a 1

# Fix file permissions.  (Already fixed upstream.)
chmod -x \
    "res/controllers/Vestax VCI-300.midi.xml" \
    "res/controllers/Vestax-VCI-300-scripts.js" \
    "res/skins/Outline1024x600-Netbook/CHANGELOG.txt" \
    "res/skins/Outline1024x600-Netbook/skin.xml" \
    "res/skins/Outline1024x768-XGA/CHANGELOG.txt" \
    "res/skins/Outline1024x768-XGA/skin.xml" \
    "res/skins/Outline800x480-WVGA/skin.xml"



%build
export CFLAGS=$RPM_OPT_FLAGS
export LIBDIR=$RPM_BUILD_ROOT/%{_libdir}
scons %{?_smp_mflags} \
  prefix=%{_prefix} \
  qtdir=%{_qt4_prefix} \
  ladspa=0 \
  shoutcast=1 hifieq=1 script=0 optimize=0 \



%install
rm -rf $RPM_BUILD_ROOT

export CFLAGS=$RPM_OPT_FLAGS
export LIBDIR=$RPM_BUILD_ROOT/%{_libdir}
scons %{?_smp_mflags} \
  install_root=$RPM_BUILD_ROOT%{_prefix} \
  qtdir=%{_qt4_prefix} \
  prefix=%{_prefix} install

desktop-file-install --vendor ""  \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --add-category=X-Synthesis \
  src/mixxx.desktop

#Remove docdir
rm -rf $RPM_BUILD_ROOT%{_docdir}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING LICENSE README README.macro
%doc Mixxx-Manual.pdf
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_libdir}/%{name}/plugins/vamp/libmixxxminimal.so
%{_datadir}/applications/mixxx.desktop
%{_datadir}/pixmaps/mixxx-icon.png

%changelog
* Fri May 17 2013 Steven Boswell <ulatekh@yahoo.com> - 1.11.0-1
- Update to 1.11.0

* Thu May 03 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.10.0-1
- Update to 1.10.0

* Fri Mar 02 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.9.2-3
- Rebuilt for c++ ABI breakage

* Wed Feb 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 1.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 8 2011 John Brier <johnbrier@gmail.com> - 1.9.2-1
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


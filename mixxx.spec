Name:           mixxx
Version:        1.6.1
Release:        2%{?dist}
Summary:        Mixxx is open source software for DJ'ing

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://www.mixxx.org
Source0:        http://downloads.mixxx.org/mixxx-%{version}/mixxx-%{version}-src.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Build tools
BuildRequires:  desktop-file-utils
BuildRequires:  scons

#Mandatory Requirements
BuildRequires:  alsa-lib-devel >= 1.0.10
#BuildRequires:  jack-audio-connection-kit-devel >= 0.61.0 #jack seems deprecated to portaudio
BuildRequires:  qt4-devel
BuildRequires:  libGL-devel
BuildRequires:  libGLU-devel
BuildRequires:  libid3tag-devel
BuildRequires:  libmad-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libvorbis-devel
BuildRequires:  portaudio-devel

#Optionals Requirements
#BuildRequires:  ffmpeg-devel
#BuildRequires:  libshout-devel
#BuildRequires:  python-devel
#BuildRequires:  lua-devel, tolua++-devel
%{?_with_bpm:BuildRequires: fftw-devel}
%{?_with_djconsole:BuildRequires: libdjconsole-devel}
%{?_with_ladspa:BuildRequires: ladspa-devel}
%{?_with_libgpod:BuildRequires: libgpod-devel}



%description
Mixxx is open source software for DJ'ing. You can use MP3s,
Ogg Vorbis files, and other formats as audio input. Mixxx
can be controlled through the GUI and with external
controllers including MIDI devices, and more.

Non-default rpmbuild options:
--with bpm:        Enable bpm support
--with djconsole:  Enable djconsole support
--with ladspa:     Enable ladspa support (EXPERIMENTAL)
--with libgpod:    Enable libgpod support



%prep
%setup -q
#removal of internal dependencies
rm -rf lib/{portaudio-v18,portaudio-v18mac}
#libsamplerate, older version, better than having compat-libsamplerate for now

#Fix ladspa in any cases
sed -i -e 's|/usr/lib/ladspa/|%{_libdir}/ladspa/|' src/ladspaloader.cpp

#Fix perm for sources
find lib src -type f -name \* -exec chmod 644 {} \;


%build
export CFLAGS=$RPM_OPT_FLAGS
export CXXFLAGS=$RPM_OPT_FLAGS
scons %{?_smp_mflags} \
  prefix=%{_prefix} \
  shoutcast=0 hifieq=1 script=0 optimize=0 \
  %{?_with_bpm:       experimentalbpm=1} \
  %{?_with_djconsole: djconsole=1} \
  %{?_with_ladspa:    ladspa=1} \
  %{?_with_libgpod:   ipod=1} \



%install
rm -rf $RPM_BUILD_ROOT

export CFLAGS=$RPM_OPT_FLAGS
export CXXFLAGS=$RPM_OPT_FLAGS
scons %{?_smp_mflags} \
  install_root=$RPM_BUILD_ROOT%{_prefix} \
  prefix=%{_prefix} install

#Recreate desktop file to better handle encoding convertion
rm $RPM_BUILD_ROOT%{_datadir}/applications/mixxx.desktop
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mixxx.desktop <<EOF
[Desktop Entry]
Version=1.0
Encoding=UTF-8
Name=Mixxx
Comment=A digital DJ interface
Exec=mixxx
Terminal=false
Icon=mixxx-icon
Type=Application
Categories=AudioVideo;Audio;
EOF

desktop-file-install --vendor "" --delete-original \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --remove-category Application \
  $RPM_BUILD_ROOT%{_datadir}/applications/mixxx.desktop

#Remove docdir
rm -rf $RPM_BUILD_ROOT%{_docdir}

#Fix script perms
chmod +x $RPM_BUILD_ROOT%{_datadir}/mixxx/midi/convert
chmod +x $RPM_BUILD_ROOT%{_datadir}/mixxx/skins/outlineMini/shifter.sh


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING HERCULES.txt LICENSE README README.macro
%doc Mixxx-Manual.pdf
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/mixxx.desktop
%{_datadir}/pixmaps/mixxx-icon.png

%changelog
* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 1.6.1-2
- rebuild for new F11 features

* Mon Sep 29 2008 kwizart < kwizart at gmail.com > - 1.6.1-1
- Update to 1.6.1

* Thu Sep 11 2008 kwizart < kwizart at gmail.com > - 1.6.0-1
- Initial version


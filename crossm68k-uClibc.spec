#
%bcond_with	bootstrap	# Build only headers
#
# TODO:
#
%define		kernel_version	2.4.32-uc0

Summary:	C library optimized for size (m68k version)
Summary(pl.UTF-8):	Biblioteka C zoptymalizowana na rozmiar (dla m68k)
Name:		crossm68k-uClibc
Version:	0.9.27
Release:	1
Epoch:		0
License:	LGPL
Group:		Libraries
Source0:	http://www.uclibc.org/downloads/uClibc-%{version}.tar.bz2
# Source0-md5:	6250bd6524283bd8e7bc976d43a46ec0
Source1:	linux-%{kernel_version}.tar.bz2
# Source1-md5:	bf6e3843ca122e3ad9ad28b94f4b8ed5
Source2:	%{name}.config
Source3:	%{name}-kernel.config
Patch0:		%{name}-clone.patch
Patch1:		%{name}-uCLinux.patch
URL:		http://www.uclibc.org/
%{!?with_bootstrap:BuildRequires:	crossm68k-gcc}
BuildRequires:	sed >= 4.0
BuildRequires:	which
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		m68k-elf
%define		arch		%{_prefix}/%{target}

%define         _noautostrip    .*%{arch}/lib/.*\\.[ao]$

%description
Small libc for building embedded applications.
Version compiled for m68k.

%description -l pl.UTF-8
Mała libc do budowania aplikacji wbudowanych.
Wersja dla m68k.

%prep
%setup -q -n uClibc-%{version} -a1
%patch0 -p1
%patch1 -p1

install -m 600 %{SOURCE2} .config

sed -i "s@^.*KERNEL_SOURCE.*\$@KERNEL_SOURCE=\"$PWD/linux-%{kernel_version}\"@"	\
	.config

cd linux-%{kernel_version}
install -m 600 %{SOURCE3} .config
make ARCH=m68knommu oldconfig
make ARCH=m68knommu dep
cd ..

%build
rm -rf $RPM_BUILD_ROOT-obj && install -d $RPM_BUILD_ROOT-obj

%if %{with bootstrap}
    %{__make} headers < /dev/null
%else
    _build () {
	local MULTILIB_SUBDIR=$1
	local PIC_CODE=$2
	local COMPILE_FLAGS=$3

	if [ $PIC_CODE -ne 0 ]; then
    	    sed -i 's/^.*DOPIC.*$/DOPIC=y/'		.config
	else
    	    sed -i 's/^.*DOPIC.*$/# DOPIC is not set/'	.config
	fi

        %{__make} clean						|| exit 1
        %{__make} all		\
	    CROSS=m68k-elf-	\
	    ARCH_CFLAGS="$COMPILE_FLAGS" </dev/null		|| exit 1

	install -d			$RPM_BUILD_ROOT-obj/$MULTILIB_SUBDIR
	install -m 600 lib/*.[ao]	$RPM_BUILD_ROOT-obj/$MULTILIB_SUBDIR
	%{target}-strip --strip-debug -R.comment -R.note	\
					$RPM_BUILD_ROOT-obj/$MULTILIB_SUBDIR/*.[ao]
    }

    _build	"m5200"				0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5200 -Wa,-m5200"
    _build	"m5200/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5200 -Wa,-m5200 -msep-data"

    _build	"m5206e"			0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5206e -Wa,-m5206e"
    _build	"m5206e/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5206e -Wa,-m5206e -msep-data"

    _build	"m528x"				0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m528x -Wa,-m528x"
    _build	"m528x/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m528x -Wa,-m528x -msep-data"

    _build	"m5307"				0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5307 -Wa,-m5307"
    _build	"m5307/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5307 -Wa,-m5307 -msep-data"

    _build	"m5407"				0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5407 -Wa,-m5407"
    _build	"m5407/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m5407 -Wa,-m5407 -msep-data"

    _build	"m68040"			0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m68040 -Wa,-m68040"
    _build	"m68040/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m68040 -Wa,-m68040 -msep-data"

    _build	"m68060"			0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m68060 -Wa,-m68060"
    _build	"m68060/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m68060 -Wa,-m68060 -msep-data"

    _build	"mcpu32"			0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -mcpu32 -Wa,-mcpu32"
    _build	"mcpu32/msep-data"		1	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -mcpu32 -Wa,-mcpu32 -msep-data"

    _build	"m68000"			0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -m68000 -Wa,-m68000"

    _build	"msoft-float"			0	"-ffunction-sections -fdata-sections -Wa,--bitwise-or -D__linux__=1 -msoft-float"

%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d			$RPM_BUILD_ROOT%{arch}/include
cp -RL include/*		$RPM_BUILD_ROOT%{arch}/include
ln -s include			$RPM_BUILD_ROOT%{arch}/sys-include

install -d			$RPM_BUILD_ROOT%{arch}/lib

%if %{without bootstrap}
cp -R $RPM_BUILD_ROOT-obj/*	$RPM_BUILD_ROOT%{arch}/lib
%endif

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT-obj

%files
%defattr(644,root,root,755)
%doc Changelog* DEDICATION.mjn3 README TODO docs/threads.txt
%{arch}/include
%{arch}/lib
%{arch}/sys-include

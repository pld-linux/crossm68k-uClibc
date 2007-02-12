#
%bcond_with	bootstrap	# Build only headers
#
# TODO:
#	- compile for m5307
#	- add support for flat shared libraries (-mid-shared-library)
#	- make less ugly ?

%define		llh_version	2.4.31

Summary:	C library optimized for size (m68k version)
Summary(pl.UTF-8):	Biblioteka C zoptymalizowana na rozmiar (dla m68k)
Name:		crossm68k-uClibc
Version:	0.9.28
Release:	1
Epoch:		0
License:	LGPL
Group:		Libraries
Source0:	http://www.uclibc.org/downloads/uClibc-%{version}.tar.bz2
# Source0-md5:	1ada58d919a82561061e4741fb6abd29
Source1:	http://www.uclibc.org/downloads/toolchain/linux-libc-headers-%{llh_version}.tar.bz2
# Source1-md5:	997d36627baf6825c712431dee4d79d3
Source2:	%{name}.config
Patch0:		%{name}-clone.patch
URL:		http://www.uclibc.org/
%{?!with_bootstrap:BuildRequires:	crossm68k-gcc}
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

install %{SOURCE2} .config

sed -i "s@^.*KERNEL_SOURCE.*\$@KERNEL_SOURCE=\"$PWD/linux-libc-headers-%{llh_version}\"@"	\
	.config

cd linux-libc-headers-%{llh_version}/include/asm-m68knommu
grep '#include[[:space:]]\+<asm-m68k/.\+\.h>' * | cut -f1 -d: | while read file; do
    cat "../asm-m68k/$file" > "$file"
done

%build
%if %{with bootstrap}
    %{__make} headers < /dev/null
%else
    _build () {
	local MULTILIB_SUBDIR=$1
	local PIC_CODE=$2
	local COMPILE_FLAGS=$3

	cat .config	| grep -v "HAVE_SHARED"		> .config.tmp
	cat .config.tmp | grep -v "BUILD_UCLIBC_LDSO"	> .config

	if [ $PIC_CODE -ne 0 ]; then
    	    sed -i 's/^.*DOPIC.*$/DOPIC=y/'		.config
	    echo "HAVE_SHARED=n"		>>	.config
	else
    	    sed -i 's/^.*DOPIC.*$/# DOPIC is not set/'	.config
	fi

        %{__make} clean						|| exit 1
        %{__make} all	ARCH_CFLAGS="$COMPILE_FLAGS" </dev/null	|| exit 1

	install -d		$RPM_BUILD_ROOT%{arch}/lib/$MULTILIB_SUBDIR
	install lib/*.[ao]	$RPM_BUILD_ROOT%{arch}/lib/$MULTILIB_SUBDIR
	%{target}-strip --strip-debug -R.comment -R.note	\
				$RPM_BUILD_ROOT%{arch}/lib/$MULTILIB_SUBDIR/*.[ao]
    }

    rm -rf $RPM_BUILD_ROOT

    _build	"m5200"				0	"-Wa,--bitwise-or -D__linux__=1 -m5200 -Wa,-m5200"
    _build	"m5200/msep-data"		1	"-Wa,--bitwise-or -D__linux__=1 -m5200 -Wa,-m5200 -msep-data"

    _build	"m68000"			0	"-Wa,--bitwise-or -D__linux__=1 -m68000 -Wa,-m68000"
    _build	"m68000/msep-data"		1	"-Wa,--bitwise-or -D__linux__=1 -m68000 -Wa,-m68000 -msep-data"
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d		$RPM_BUILD_ROOT%{arch}/include
cp -RL include/*	$RPM_BUILD_ROOT%{arch}/include
ln -s include		$RPM_BUILD_ROOT%{arch}/sys-include

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog* DEDICATION.mjn3 MAINTAINERS README TODO docs/threads.txt
%{arch}/include
%{arch}/lib
%{arch}/sys-include

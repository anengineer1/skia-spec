%global debug_package %{nil}

# Headers to exclude from installation
%global REMOVE_HEADERS include/codec/SkRawDecoder.h include/codec/SkJpegxlDecoder.h include/codec/SkAvifDecocer.h

Name:           libskia
Version:        146
Release:        1%{?dist}
Summary:        2D graphics library

License:        BSD-3-Clause
URL:            https://skia.org
Source0:        https://skia.googlesource.com/skia/+archive/refs/heads/chrome/m%{version}.tar.gz
Provides:       skia = %{version}-%{release}
Obsoletes:      skia < %{version}-%{release}
Patch0:         enable-rtti.patch
Patch1:         loong-build.patch
Patch2:         unsupported-attributes.patch
Patch3:         vk_malloc-location.patch
Patch4:         include_installer.patch

BuildRequires:  abseil-cpp
BuildRequires:  brotli-devel
BuildRequires:  gcc-c++
BuildRequires:  expat-devel
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  glibc-devel
BuildRequires:  gn
BuildRequires:  graphite2-devel
BuildRequires:  harfbuzz-devel
BuildRequires:  highway-devel
BuildRequires:  libicu-devel
BuildRequires:  libglvnd-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libjxl-devel
BuildRequires:  libmicrohttpd-devel
BuildRequires:  libpng-devel
BuildRequires:  libyuv-devel
BuildRequires:  libwebp-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  pkgconfig
BuildRequires:  python3-devel
BuildRequires:  procps-ng-devel
BuildRequires:  spirv-tools-devel
BuildRequires:  ninja-build

%description
Skia is an open source 2D graphics library which provides common APIs that work across a variety of hardware and software platforms.

%package devel
Summary:        Skia development files
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development header files and libraries for skia graphics engine.

%prep
%setup -c -n skia-%{version}
install -d bin
cp %{_bindir}/gn bin/gn
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1
%patch -P 3 -p1
%patch -P 4 -p1


%build
# Disable musttail for GCC compatibility (fixes skcms build errors)
# export CXXFLAGS="${CXXFLAGS} -DSKCMS_HAS_MUSTTAIL=0"

# Enable system Zlib to be used. Bug noted at:
# https://git.savannah.gnu.org/cgit/guix.git/tree/gnu/packages/graphics.scm#n2148
# sed -i 's|deps = \[ "//third_party/zlib" \]|deps = \[\]|g' BUILD.gn
# This is checked before the GN build flags are set, and results in an error if
# it has not been downloaded, even if it is not used
sed -i 's|deps += \[ "//third_party/externals/spirv[\-]tools:spvtools_val" \]|deps += \[\]|g' BUILD.gn
# dng_sdk is not packaged
# wuffs is not packaged
# ganesh builds successfully with current configuration
GN_DEFINES_MAIN=" cc=\"%{__cc}\""
GN_DEFINES_MAIN+=" cxx=\"%{__cxx}\""
# Parsing Fedora build flags is problematic - Skia manages its own optimization
#GN_DEFINES_MAIN+=" extra_cflags=[\"%{optflags}\"]
GN_DEFINES_MAIN+=" extra_cflags=[\"-frtti\", \"-DSKCMS_HAS_MUSTTAIL=0\"]"
# Parsing Fedora linker flags is problematic
#GN_DEFINES_MAIN+=" extra_ldflags=[\"%{__global_ldflags}\"]"
GN_DEFINES_MAIN+=" is_official_build=true"
GN_DEFINES_MAIN+=" is_component_build=true"
GN_DEFINES_MAIN+=" is_debug=false"
GN_DEFINES_MAIN+=" skia_use_dng_sdk=false"
GN_DEFINES_MAIN+=" skia_use_icu=true"
GN_DEFINES_MAIN+=" skia_use_wuffs=false"
GN_DEFINES_MAIN+=" skia_use_zlib=false"
# GN_DEFINES_MAIN+=" skia_enable_gpu=true"
GN_DEFINES_MAIN+=" skia_enable_ganesh=true"
GN_DEFINES_MAIN+=" skia_enable_graphite=true"
GN_DEFINES_MAIN+=" skia_enable_pdf=true"
GN_DEFINES_MAIN+=" skia_enable_spirv_validation=false"
GN_DEFINES_MAIN+=" skia_compile_sksl_tests=false"
GN_DEFINES_MAIN+=" skia_use_system_expat=true"
GN_DEFINES_MAIN+=" skia_use_system_freetype2=true"
GN_DEFINES_MAIN+=" skia_use_system_harfbuzz=true"
GN_DEFINES_MAIN+=" skia_use_system_icu=true"
GN_DEFINES_MAIN+=" skia_use_system_libjpeg_turbo=true"
GN_DEFINES_MAIN+=" skia_use_system_libpng=true"
GN_DEFINES_MAIN+=" skia_use_system_libwebp=true"
#GN_DEFINES_MAIN+=" skia_use_system_zlib=true"
GN_DEFINES_MAIN+=" skia_use_vulkan=false"
# Main build
gn gen out/Build --args="${GN_DEFINES_MAIN}"

# Builds
ninja -C ./out/Build %{?_smp_mflags}
ls out/Build

%install
install -d %{buildroot}%{_libdir}
install -pm644 out/Build/*.so* %{buildroot}%{_libdir}/

# Install public API headers (preserve structure)
# mkdir -p %%{buildroot}/%%{_includedir}/%%{name}
# find include -type f -name "*.h" -exec bash -c 'dest=%{buildroot}%{_includedir}/%{name}/${1#include/}; install -v -D -m644 "$1" "$dest"' _ {} \;

# Install module headers (skcms, skparagraph, etc.)
# mkdir -p %%{buildroot}/%%{_includedir}/%%{name}
# find modules -type f -name "*.h" -exec install -v -D -m644 {} %%{buildroot}%%{_includedir}/%%{name}/{} \;

# Install generated headers (public API only, if needed)
# Note: out/Build/gen/skia.h is internal and should NOT be installed

# Install via debian's script
install -d %{buildroot}%{_includedir}/skia
python3 bin/install-headers.py --src include/ --dest %{buildroot}%{_includedir}/skia --ignore '.*/android/.*' --ignore '.*/SkRawDecoder\.h' --ignore '.*/SkJpegxlDecoder\.h' --ignore '.*/SkAvifDecocer\.h'
install -pm644 modules/skcms/src/skcms_public.h %{buildroot}%{_includedir}/skia/skcms.h

install -d %{buildroot}%{_libdir}/pkgconfig

cat <<'EOF' > %{buildroot}%{_libdir}/pkgconfig/skia.pc
prefix=%{_prefix}
exec_prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}

Name: %{name}
Description: 2D graphics library
Version: %{version}
Cflags: -I${includedir}/skia
Libs: -L${libdir} -lskia
EOF

%check
#need a build with tests

%files
%license LICENSE
%doc README
%{_libdir}/*.so*

%files devel
%{_includedir}/skia/
%{_libdir}/pkgconfig/skia.pc

%changelog
* Sat Oct 24 2026 Francisco Parra <franparpe@firemail.cc> - 146-1
- Initial Fedora package

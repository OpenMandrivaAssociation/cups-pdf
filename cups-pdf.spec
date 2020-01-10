%define pre beta2

Summary:        Extension for creating pdf-Files with CUPS
Name:           cups-pdf
Version:        3.0
%if "%{pre}" != ""
Release:	0.%{pre}.1
%else
Release:        1
%endif
Group:          System/Printing 
Source0:        http://cups-pdf.de/src/%{name}_%{version}%{pre}.tar.gz
Source1:	http://cups-pdf.de/contrib/n_kondrashov/pstitleiconv_0.2.tar.gz
Source2:	http://cups-pdf.de/contrib/n_kondrashov/cups-pdf-dispatch_0.1.tar.gz
Patch1:         cups-pdf-conf.patch
Patch2:         cups-pdf-desktop.patch
URL:            http://cups-pdf.de/
# Mirror: http://cip.physik.uni-wuerzburg.de/~vrbehr/cups-pdf/
License:        GPLv2+
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Requires:       ghostscript
Requires:       cups
BuildRequires:  cups-devel

# These are the defaults paths defined in config.h
# CUPS-PDF spool directory
%define CPSPOOL   %{_localstatedir}/spool/cups-pdf/SPOOL

# CUPS-PDF output directory
%define CPOUT     %{_localstatedir}/spool/cups-pdf

# CUPS-PDF log directory
%define CPLOG     %{_localstatedir}/log/cups

# CUPS-PDF cups-pdf.conf config file
%define ETCCUPS   %(cups-config --serverroot 2>/dev/null || echo %{_sysconfdir}/cups)

# Additional path to backend directory
%define CPBACKEND %(cups-config --serverbin  2>/dev/null || echo %{_libdir}/cups)/backend


%description
"cups-pdf" is a backend script for use with CUPS - the "Common UNIX Printing
System" (see more for CUPS under http://www.cups.org/). 
"cups-pdf" uses the ghostscript pdfwrite device to produce PDF Files.

This version has been modified to store the PDF files on the Desktop of the 
user. This behavior can be changed by editing the configuration file.

%prep
%setup -q -n %{name}-%{version}%{pre}
%autopatch -p1

mkdir contrib
cd contrib
tar xf %{SOURCE1}
tar xf %{SOURCE2}

%build
pushd src
%{__cc} $RPM_OPT_FLAGS -o cups-pdf cups-pdf.c -lcups
popd

# Avoid perl dependencies
chmod -x contrib/pstitleiconv-0.2/pstitleiconv
chmod -x contrib/cups-pdf-dispatch-0.1/cups-pdf-dispatch


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{CPBACKEND}
mkdir -p %{buildroot}%{CPSPOOL}
mkdir -p %{buildroot}%{CPOUT}
mkdir -p %{buildroot}%{CPLOG}
mkdir -p %{buildroot}%{CPBACKEND}
mkdir -p %{buildroot}%{ETCCUPS}
mkdir -p %{buildroot}%{_datadir}/cups/model/
install -m644 extra/CUPS-PDF_opt.ppd %{buildroot}%{_datadir}/cups/model/
install -m644 extra/CUPS-PDF_noopt.ppd %{buildroot}%{_datadir}/cups/model/
install -m644 extra/cups-pdf.conf %{buildroot}%{ETCCUPS}/
install -m700 src/cups-pdf %{buildroot}%{CPBACKEND}/

%post
# First install : create the printer if cupsd is running
if [ "$1" -eq "1" -a -f "%{_var}/run/cupsd.pid" ]
then
    if [ -d /proc/$(cat %{_var}/run/cupsd.pid) ]
    then
        /usr/sbin/lpadmin -p Cups-PDF -v cups-pdf:/ -m CUPS-PDF_opt.ppd -E || :
    fi
fi

%postun
if [ "$1" -eq "0" ]; then
    # Delete the printer
    /usr/sbin/lpadmin -x Cups-PDF || :
fi

%files
%defattr(-,root,root)
%doc ChangeLog README contrib/
%dir %{CPSPOOL}
%dir %{CPOUT}
%attr(700, root, root) %{CPBACKEND}/cups-pdf
%config(noreplace) %{ETCCUPS}/cups-pdf.conf
%{_datadir}/cups/model/CUPS-PDF_opt.ppd
%{_datadir}/cups/model/CUPS-PDF_noopt.ppd

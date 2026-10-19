Name:           two
Version:        1.0.0
Release:        1%{?dist}
Summary:        Test app two
License:        MIT
BuildArch:      x86_64

Source0:        two

%description
Test-only package. Installs a single binary to /usr/bin. No scriptlets.

%prep

%build

%install
install -d %{buildroot}/usr/bin
install -m 0755 %{SOURCE0} %{buildroot}/usr/bin/two

%files
/usr/bin/two

%changelog
* Sun Oct 19 2025 fishfinal <contact.fishfinal@gmail.com> - 1.0.0-1
- initial test package

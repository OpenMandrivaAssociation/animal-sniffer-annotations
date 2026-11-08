Name:		animal-sniffer-annotations
Version:	1.29
Release:	1
Summary:	Annotation that marks APIs Animal Sniffer should ignore
Group:		Development/Java
License:	MIT
URL:		https://www.mojohaus.org/animal-sniffer/
Source0:	https://github.com/mojohaus/animal-sniffer/archive/refs/tags/%{version}.tar.gz#/animal-sniffer-%{version}.tar.gz

BuildArch:	noarch
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name animal-sniffer-annotations --link %{name}

%description
Animal Sniffer Annotations is the IgnoreJRERequirement annotation.
The Maven plugin is not packaged. The annotation class is unchanged
in 1.29. That release improves signature checking, Ant suppression
order, and Maven signature resolution in the plugin and enforcer
rule, which this package does not build.

%prep
%autosetup -n animal-sniffer-%{version}
# The annotation module has no dependencies. Drop the parent so the
# build does not need animal-sniffer-parent or mojo-parent.
python - <<'PY'
import re
import shutil
from pathlib import Path

text = Path("animal-sniffer-annotations/pom.xml").read_text()
text, n = re.subn(r"\s*<parent>.*?</parent>", "", text, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f"parent {n}")
old = "  <artifactId>animal-sniffer-annotations</artifactId>\n  <name>Animal Sniffer Annotations</name>"
new = """  <groupId>org.codehaus.mojo</groupId>
  <artifactId>animal-sniffer-annotations</artifactId>
  <version>%{version}</version>
  <name>Animal Sniffer Annotations</name>
  <description>Annotation that marks APIs Animal Sniffer should ignore.</description>
  <url>https://www.mojohaus.org/animal-sniffer/</url>
  <properties>
    <maven.compiler.source>8</maven.compiler.source>
    <maven.compiler.target>8</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>"""
if old not in text:
    raise SystemExit("artifact block missing")
Path("pom.xml").write_text(text.replace(old, new, 1))
shutil.rmtree("src", ignore_errors=True)
shutil.move("animal-sniffer-annotations/src", "src")
PY

%files -f .mfiles
%doc LICENSE README.md

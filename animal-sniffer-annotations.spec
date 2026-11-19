Name:		animal-sniffer-annotations
Version:	1.29.1
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
The Maven plugin is not packaged. 1.29.1 stops flagging
signature-polymorphic MethodHandle and VarHandle calls in the
checker. The annotation class in this package is unchanged.

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

%check -a
mkdir -p chk
cat > chk/AnimalSnifferCheck.java << 'EOF'
import org.codehaus.mojo.animal_sniffer.IgnoreJRERequirement;

@IgnoreJRERequirement
public class AnimalSnifferCheck {
	public static void main(String[] args) {
		if (!IgnoreJRERequirement.class.isAnnotation()) {
			throw new RuntimeException("not an annotation");
		}
		String name = IgnoreJRERequirement.class.getSimpleName();
		if (!"IgnoreJRERequirement".equals(name)) {
			throw new RuntimeException(name);
		}
		System.out.println("animal_sniffer_annotations_ok %{version} " + name);
	}
}
EOF
test -s target/animal-sniffer-annotations-%{version}.jar
javac -cp target/animal-sniffer-annotations-%{version}.jar -d chk chk/AnimalSnifferCheck.java
java -cp chk:target/animal-sniffer-annotations-%{version}.jar AnimalSnifferCheck > chk/out.txt
cat chk/out.txt
grep -q '^animal_sniffer_annotations_ok %{version} IgnoreJRERequirement$' chk/out.txt

%files -f .mfiles
%doc LICENSE README.md

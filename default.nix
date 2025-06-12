let
  nixpkgs = fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/c1064e7c1ff1ddff79ba961ebfedb7d83eff13ed.tar.gz";
    sha256 = "0na57f7pfq0v51lc9mwnyqyxqw57wis3zhglxz3mlhqg07fkx4g9";
  };
  pkgs = import nixpkgs {
    overlays = [];
    config = {};
  };
  inherit (pkgs.lib) fileset;
in

with pkgs.python3.pkgs;

let
  # mypy does not find type annotations otherwise
  mypyEnv = (python.withPackages (ps: [
    ps.mypy
    ps.PyGithub
  ]));
in buildPythonPackage {
  name = "inactive-maintainers";
  src = fileset.toSource {
    root = ./.;
    fileset = fileset.unions [
      ./inactive_maintainers
      ./setup.py
      ./setup.cfg
    ];
  };
  propagatedBuildInputs = [
    PyGithub
  ];
  checkPhase = ''
    ${mypyEnv}/bin/mypy inactive_maintainers
  '';
}

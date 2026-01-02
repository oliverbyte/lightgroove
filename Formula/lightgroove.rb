class Lightgroove < Formula
  include Language::Python::Virtualenv

  desc "DMX controller with simple web UI"
  homepage "https://github.com/oliverbyte/lightgroove"
  url "https://github.com/oliverbyte/lightgroove/archive/refs/heads/main.tar.gz"
  version "0.0.0-main"
  sha256 :no_check
  license "AGPL-3.0-only"
  head "https://github.com/oliverbyte/lightgroove.git", branch: "main"

  depends_on "python@3.11"

  def install
    venv = virtualenv_create(libexec, "python3")

    # Install Python deps (keep in sync with requirements.txt).
    venv.pip_install "pyserial==3.5"
    venv.pip_install "stupidArtnet==1.4.0"

    # Install project files into libexec.
    libexec.install Dir["*"]

    # Wrapper to run the app with venv Python and proper module path.
    (bin/"lightgroove").write <<~EOS
      #!/bin/bash
      export PYTHONPATH="#{libexec}/src:${PYTHONPATH}"
      exec "#{libexec}/bin/python3" "#{libexec}/main.py" "$@"
    EOS
    chmod 0555, bin/"lightgroove"
  end

  def caveats
    <<~EOS
      Usage: lightgroove
      Config lives in: #{libexec}/config
      Web UI serves from: #{libexec}/ui_dist (default port 5555; override LIGHTGROOVE_HTTP_PORT)

      Note: This tap uses :no_check and installs PyPI deps at build time.
    EOS
  end

  test do
    system "#{bin}/lightgroove", "--help"
  end
end

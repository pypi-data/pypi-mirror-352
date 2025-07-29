class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/fb/6c/7da1560378b0a3cbf1b318d683ddc60f0b1c8e7ac8222def82670833478d/trmd-0.1.7.tar.gz"
  sha256 "b69da2cfb9ead0aa4d1d3c6d3e40ba364333b564d21b72f3fc22fbdcbf4b2d7f"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end

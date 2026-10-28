"""Контекст HTTPS с системными доверенными сертификатами macOS."""

from functools import lru_cache
import ssl
import subprocess
import sys

SUCCESS = 0
KEYCHAINS = ("/System/Library/Keychains/SystemRootCertificates.keychain",
             "/Library/Keychains/System.keychain")


@lru_cache(maxsize=1)
def https_context():
    """Дополнить стандартный CA-набор публичными сертификатами macOS."""
    context = ssl.create_default_context()
    if sys.platform != "darwin":
        return context
    for keychain in KEYCHAINS:
        try:
            result = subprocess.run(
                ["/usr/bin/security", "find-certificate", "-a", "-p", keychain],
                capture_output=True, text=True, timeout=10, check=False)
            if (result.returncode == SUCCESS
                    and "BEGIN CERTIFICATE" in result.stdout):
                context.load_verify_locations(cadata=result.stdout)
        except (OSError, subprocess.SubprocessError, ssl.SSLError):
            continue
    return context

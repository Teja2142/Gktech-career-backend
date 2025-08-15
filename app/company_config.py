from urllib.parse import urlparse
from typing import Optional, Dict


class CompanyConfig:
    """Simple mapping from known origin domains to HR email addresses."""

    # adjust these addresses to the real HR inboxes
    EMAIL_MAP: Dict[str, str] = {
        "kgktechnologies.com": "Hr@kgktechnologies.com",
        "dglobal.com": "hr@dglobaltech.com",
        "localhost": "kgktechnologies.stl@gmail.com"  # for local testing
    }

    @staticmethod
    def extract_domain(origin: str) -> Optional[str]:
        """Return normalized domain (no www, no port) or None on parse error."""
        try:
            domain = urlparse(origin).netloc.lower()
            if not domain:
                return None
            domain = domain.split(":")[0]
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return None

    @staticmethod
    def get_hr_email(domain: str) -> Optional[str]:
        """Return HR email for the known domain, else None."""
        return CompanyConfig.EMAIL_MAP.get(domain)

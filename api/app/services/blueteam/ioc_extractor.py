from dataclasses import dataclass
import re


@dataclass
class IOCExtractionResult:
    urls: list[str]
    domains: list[str]
    suspicious_domains: list[str]
    phone_numbers: list[str]
    base64_chunks: list[str]
    suspicious_extensions: list[str]


URL_RE = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.IGNORECASE)
DOMAIN_RE = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b", re.IGNORECASE
)
PHONE_TN_RE = re.compile(r"(?:\+216|00216)?[\s-]?(\d{2})[\s-]?(\d{3})[\s-]?(\d{3})")
BASE64_RE = re.compile(r"\b(?:[A-Za-z0-9+/]{16,}={0,2})\b")
EXT_RE = re.compile(
    r"\b[^\s]+\.(exe|scr|bat|cmd|js|vbs|ps1|jar|apk|zip|rar)\b", re.IGNORECASE
)

KNOWN_BRANDS = [
    "poste.tn",
    "tunisietelecom.tn",
    "biat.com.tn",
    "ooredoo.tn",
    "stb.com.tn",
]


def _levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            ins = curr[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            curr.append(min(ins, delete, sub))
        prev = curr
    return prev[-1]


def _is_typosquat(domain: str) -> bool:
    candidate = domain.lower()
    for legit in KNOWN_BRANDS:
        if candidate == legit:
            return False
        if _levenshtein_distance(candidate, legit) <= 2:
            return True
    return False


def extract_iocs(text: str) -> IOCExtractionResult:
    urls = URL_RE.findall(text)
    domains = DOMAIN_RE.findall(text)
    suspicious_domains = [d for d in domains if _is_typosquat(d)]

    phone_numbers = ["".join(parts) for parts in PHONE_TN_RE.findall(text)]
    base64_chunks = BASE64_RE.findall(text)
    suspicious_extensions = [m.group(1).lower() for m in EXT_RE.finditer(text)]

    return IOCExtractionResult(
        urls=urls,
        domains=domains,
        suspicious_domains=suspicious_domains,
        phone_numbers=phone_numbers,
        base64_chunks=base64_chunks,
        suspicious_extensions=suspicious_extensions,
    )

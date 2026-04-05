from app.services.blueteam.feature_builder import (
    build_handcrafted_features,
    combine_feature_vector,
)
from app.services.blueteam.ioc_extractor import extract_iocs


def test_extract_iocs_finds_expected_signals() -> None:
    text = (
        "Alerte urgente: verify password at https://poste-tn.com/login "
        "Call +216 12 345 678 and open update.exe QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
    )
    iocs = extract_iocs(text)
    assert len(iocs.urls) >= 1
    assert len(iocs.domains) >= 1
    assert len(iocs.phone_numbers) >= 1
    assert len(iocs.base64_chunks) >= 1
    assert "exe" in iocs.suspicious_extensions


def test_feature_builder_and_vector_assembly() -> None:
    text = "urgent verify password poste tunisienne https://example.com"
    iocs = extract_iocs(text)
    handcrafted = build_handcrafted_features(text, iocs)
    assert len(handcrafted.names) == len(handcrafted.values)
    assert len(handcrafted.values) >= 10

    embedding = [0.1, 0.2, 0.3]
    combined = combine_feature_vector(embedding, handcrafted)
    assert len(combined.names) == len(combined.values)
    assert len(combined.values) == len(embedding) + len(handcrafted.values)

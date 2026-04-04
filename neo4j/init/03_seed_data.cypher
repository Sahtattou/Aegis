// Seed project-aligned graph data (MITRE, ANCS, Tunisian signatures, sample attacks)

// Knowledge sources
MERGE (mitre:KnowledgeSource {name: "MITRE ATT&CK"})
SET mitre.url = "https://attack.mitre.org", mitre.updated_at = datetime();

MERGE (ancs:KnowledgeSource {name: "ANCS"})
SET ancs.url = "https://www.ancs.tn", ancs.updated_at = datetime();

MERGE (tuncert:KnowledgeSource {name: "tunCERT"})
SET tuncert.url = "https://www.financialcert.tn", tuncert.updated_at = datetime();

// Target organizations (local relevance)
MERGE (o1:Organization {name: "Poste Tunisienne"})
MERGE (o2:Organization {name: "BIAT"})
MERGE (o3:Organization {name: "STB"})
MERGE (o4:Organization {name: "Tunisie Telecom"})
MERGE (o5:Organization {name: "Ooredoo Tunisie"});

// Minimal MITRE techniques used by project scenarios
MERGE (t1566:MitreTechnique {id: "T1566"})
SET t1566.name = "Phishing", t1566.tactic = "Initial Access", t1566.updated_at = datetime()
MERGE (t1566)-[:PUBLISHED_BY]->(mitre);

MERGE (t1110:MitreTechnique {id: "T1110"})
SET t1110.name = "Brute Force", t1110.tactic = "Credential Access", t1110.updated_at = datetime()
MERGE (t1110)-[:PUBLISHED_BY]->(mitre);

// Rules (same IDs as api/data/kb/tunisian_signatures.json)
MERGE (r1:Rule {id: "R-001"})
SET r1.name = "Password verification lure",
    r1.pattern = "verify password",
    r1.matcher = "substring",
    r1.decision = "malicious",
    r1.confidence = 0.95,
    r1.enabled = true,
    r1.created_at = datetime();

MERGE (r2:Rule {id: "R-002"})
SET r2.name = "Urgent transfer request",
    r2.pattern = "urgent transfer",
    r2.matcher = "substring",
    r2.decision = "malicious",
    r2.confidence = 0.93,
    r2.enabled = true,
    r2.created_at = datetime();

MERGE (r3:Rule {id: "R-003"})
SET r3.name = "Credential phishing regex",
    r3.pattern = "(reset|verify).*(account|password)",
    r3.matcher = "regex",
    r3.decision = "suspicious",
    r3.confidence = 0.82,
    r3.enabled = true,
    r3.created_at = datetime();

MERGE (r1)-[:PUBLISHED_BY]->(ancs)
MERGE (r2)-[:PUBLISHED_BY]->(ancs)
MERGE (r3)-[:PUBLISHED_BY]->(tuncert)
MERGE (r1)-[:DETECTS_TECHNIQUE]->(t1566)
MERGE (r2)-[:DETECTS_TECHNIQUE]->(t1566)
MERGE (r3)-[:DETECTS_TECHNIQUE]->(t1110);

// Sample advisories
MERGE (a1:Advisory {id: "ANCS-2026-001"})
SET a1.title = "Campagne de phishing ciblant les banques tunisiennes",
    a1.description = "L'ANCS signale des messages de vérification de mot de passe frauduleux.",
    a1.published_date = datetime("2026-03-05T09:00:00Z"),
    a1.severity = "high"
MERGE (a1)-[:PUBLISHED_BY]->(ancs)
MERGE (a1)-[:RELATED_TO_TECHNIQUE]->(t1566)
MERGE (a1)-[:TARGETS]->(o2)
MERGE (a1)-[:TARGETS]->(o3);

MERGE (a2:Advisory {id: "TUNCERT-2026-014"})
SET a2.title = "Alerte credential stuffing sur services télécom",
    a2.description = "TunCERT observe une hausse des tentatives de brute force sur portails client.",
    a2.published_date = datetime("2026-03-18T11:30:00Z"),
    a2.severity = "medium"
MERGE (a2)-[:PUBLISHED_BY]->(tuncert)
MERGE (a2)-[:RELATED_TO_TECHNIQUE]->(t1110)
MERGE (a2)-[:TARGETS]->(o4)
MERGE (a2)-[:TARGETS]->(o5);

// Seed attack samples for pipeline/GraphRAG demos
MERGE (s1:AttackSample {id: "ATTACK-S-001"})
SET s1.text = "Alerte BIAT: verify password now to avoid suspension",
    s1.label = "phishing",
    s1.language = "fr",
    s1.source_tag = "tn_curated_manual"
MERGE (s1)-[:TARGETS]->(o2)
MERGE (s1)-[:USES_TECHNIQUE]->(t1566)
MERGE (s1)-[:MATCHED_BY]->(r1);

MERGE (s2:AttackSample {id: "ATTACK-S-002"})
SET s2.text = "تم رصد نشاط مشبوه على حسابك، قم بإعادة تعيين كلمة المرور الآن",
    s2.label = "phishing",
    s2.language = "ar",
    s2.source_tag = "tn_curated_manual"
MERGE (s2)-[:TARGETS]->(o1)
MERGE (s2)-[:USES_TECHNIQUE]->(t1566)
MERGE (s2)-[:MATCHED_BY]->(r3);

MERGE (s3:AttackSample {id: "ATTACK-S-003"})
SET s3.text = "Message officiel Tunisie Telecom: maintenance réseau planifiée sans action requise",
    s3.label = "benign",
    s3.language = "fr",
    s3.source_tag = "tn_curated_manual"
MERGE (s3)-[:TARGETS]->(o4);

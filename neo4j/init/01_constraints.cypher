// Constraints & indexes
CREATE CONSTRAINT attack_id IF NOT EXISTS
FOR (a:Attack)
REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT attack_sample_id IF NOT EXISTS
FOR (a:AttackSample)
REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT rule_id IF NOT EXISTS
FOR (r:Rule)
REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT advisory_id IF NOT EXISTS
FOR (a:Advisory)
REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT mitre_technique_id IF NOT EXISTS
FOR (m:MitreTechnique)
REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT source_name IF NOT EXISTS
FOR (s:KnowledgeSource)
REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT organization_name IF NOT EXISTS
FOR (o:Organization)
REQUIRE o.name IS UNIQUE;

CREATE CONSTRAINT audit_event_id IF NOT EXISTS
FOR (e:AuditEvent)
REQUIRE e.id IS UNIQUE;

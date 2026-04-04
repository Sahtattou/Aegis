// Initial KB data (MITRE, ANCS)
MERGE (m:KnowledgeSource {name: 'MITRE ATT&CK'})
MERGE (a:KnowledgeSource {name: 'ANCS/tunCERT'})
MERGE (m)-[:RELATED_TO]->(a);

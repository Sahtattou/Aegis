// Initial KB data (MITRE, ANCS)
MERGE (m:KnowledgeSource {name: 'MITRE ATT&CK'})
MERGE (a:KnowledgeSource {name: 'ANCS/tunCERT'})
MERGE (m)-[:RELATED_TO]->(a);

MERGE (t:KnowledgeSource {name: 'Tunisian signatures'})
MERGE (t)-[:RELATED_TO]->(a)
MERGE (t)-[:RELATED_TO]->(m);

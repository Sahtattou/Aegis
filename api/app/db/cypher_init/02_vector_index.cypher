// Vector index for GraphRAG
CREATE VECTOR INDEX attack_embedding_index IF NOT EXISTS
FOR (a:Attack)
ON (a.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
  }
};

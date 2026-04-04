# HARIS — حارس  
**AI Cyber Human Shield**  
**Project Context & Full Specification for Claude (Code Generation)**

**Date**: April 2026  
**Hackathon**: AI x CYBER – FST / Cyber Horizon  
**Theme**: "AI Augmented Cyber Defense, but Human Controlled"  
**Target Users**: Cyber analysts / SOC operators (NOT citizens)  
**Database**: Neo4j 5.26 Community (graph + vector index for GraphRAG)  
**Time available**: 12 hours

---

## 1. Hackathon Golden Rules (MUST be respected 100%)

- **XAI – Zero black-box**: Every alert must explain WHY (SHAP + French narrative + full graph provenance path in Neo4j).
- **Human-in-the-loop**: AI only **proposes**. No critical action (rule creation, remediation) without explicit analyst confirmation.
- **No No-Code / No basic LLM wrapper**: Full custom pipeline (LangChain structured agents + pre/post-processing + GraphRAG + scikit-learn + graph rules).
- **Data engineering**: Curated Tunisian dataset + real ANCS/tunCERT + MITRE ATT&CK.
- **Local relevance**: All attacks in Darija/Arabic/French, targeting Tunisian brands (Poste Tunisienne, BIAT, STB, Tunisie Telecom, Ooredoo).

---

## 2. Project Vision

HARIS is a **professional SOC co-pilot** that continuously runs a **Red Team vs Blue Team loop** to find its own blind spots, explains them in plain French, and lets the human analyst approve new detection rules.  

It protects Tunisian citizens by making their cyber defenders unstoppable.

**Core Loop** (exactly as requested):
**Red Agent attacks → Rules applied (pre-filter) → ML Model + GraphRAG → Results → (if blind spot) → Analyst approval → new rule**

---

## 3. Updated System Architecture (Corrected Flow)

**Exact data flow** (this is the final, correct order):

1. **Red Team Agent** generates a fresh Tunisian attack (JSON).
2. **Rules Engine** applies all existing approved rules as a fast **pre-filter** (Préventif phase).
3. If no rule matches → **ML Model** (scikit-learn + AraBERT) + **GraphRAG** (Neo4j vector + graph retrieval) performs deep detection.
4. **Results** (detection decision + SHAP + French XAI narrative).
5. If blind spot detected → Blind Spot Analyzer creates proposed rule.
6. Analyst reviews in SOC Console → explicit APPROVE → new rule is created in Neo4j graph.
7. Loop repeats — new rule is immediately active on the next Red Team run (Adaptatif phase).

```mermaid
graph TD
    A[Red Team Agent<br/>LangChain + Claude<br/>(Tunisian personas)] 
    --> B[Rules Engine<br/>Pre-filter<br/>(Graph-based)]
    B --> C[ML Model + GraphRAG<br/>AraBERT + scikit-learn + Neo4j]
    C --> D[Results + XAI<br/>SHAP + French narrative]
    D --> E{Blind Spot?}
    E -->|Yes| F[Blind Spot Analyzer]
    F --> G[Human SOC Console<br/>React + SSE]
    G -->|Analyst APPROVES| B
    subgraph "Neo4j Graph DB"
        B
        C
        F
        H[Audit Graph<br/>:Attack → :Detection → :BlindSpot → :Rule]
    end

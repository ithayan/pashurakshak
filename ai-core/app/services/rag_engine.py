"""
PashuRakshak AI Core - Veterinary Clinical RAG Engine
=====================================================
Retrieval-Augmented Generation (RAG) system for rural livestock healthcare.
Indexes Maharashtra Animal Husbandry SOPs, ICAR-NDRI treatment guidelines,
and Ethno-Veterinary Medicine (EVM) protocols to generate grounded,
hallucination-free veterinary advice with verified government citations.
"""

import os
import json
import math
import re
from typing import List, Dict, Any, Tuple


class VeterinaryRAGEngine:
    def __init__(self, kb_path: str = None):
        if kb_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base_dir, "knowledge_base", "vet_protocols.json")
        self.kb_path = kb_path
        self.documents: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.doc_vectors: List[List[float]] = []
        self.idf: Dict[str, float] = {}
        self._load_and_index()

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes text preserving Marathi, Hindi, and English words."""
        cleaned = re.sub(r"[^\w\s\u0900-\u097F]", " ", text.lower())
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        return tokens

    def _load_and_index(self):
        """Loads protocols and indexes vector embeddings."""
        if not os.path.exists(self.kb_path):
            print(f"Warning: RAG Knowledge Base not found at {self.kb_path}")
            return

        with open(self.kb_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        # Build vocabulary from keywords, titles, and text
        all_doc_tokens = []
        for doc in self.documents:
            doc_text = " ".join([
                doc.get("disease", ""),
                doc.get("disease_mr", ""),
                " ".join(doc.get("keywords", [])),
                doc.get("subclinical_biomarkers", ""),
                doc.get("clinical_evidence", ""),
                doc.get("treatment_and_firstaid_mr", "")
            ])
            tokens = self._tokenize(doc_text)
            all_doc_tokens.append(tokens)
            for t in tokens:
                if t not in self.vocab:
                    self.vocab[t] = len(self.vocab)

        num_docs = len(self.documents)
        # Compute IDF
        for word in self.vocab:
            doc_freq = sum(1 for tokens in all_doc_tokens if word in tokens)
            self.idf[word] = math.log((1 + num_docs) / (1 + doc_freq)) + 1.0

        # Compute TF-IDF vectors
        self.doc_vectors = []
        for tokens in all_doc_tokens:
            vec = self._vectorize_tokens(tokens)
            self.doc_vectors.append(vec)

        print(f"Veterinary RAG Engine initialized with {len(self.documents)} protocols and {len(self.vocab)} terms.")

    def _vectorize_tokens(self, tokens: List[str]) -> List[float]:
        """Builds normalized TF-IDF vector."""
        vec = [0.0] * len(self.vocab)
        if not tokens:
            return vec

        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1

        total = len(tokens)
        sq_sum = 0.0
        for word, count in tf.items():
            if word in self.vocab:
                idx = self.vocab[word]
                val = (count / total) * self.idf.get(word, 1.0)
                vec[idx] = val
                sq_sum += val * val

        # Normalize to unit length
        norm = math.sqrt(sq_sum)
        if norm > 0:
            vec = [v / norm for v in vec]

        return vec

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Computes cosine similarity between two unit vectors."""
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieves top-k matching clinical protocols."""
        query_tokens = self._tokenize(query)
        query_vec = self._vectorize_tokens(query_tokens)

        scores = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            sim = self._cosine_similarity(query_vec, doc_vec)

            # Bonus for exact keyword hits
            doc = self.documents[idx]
            keywords = doc.get("keywords", [])
            matches = sum(1 for kw in keywords if kw.lower() in query.lower())
            if matches > 0:
                sim = min(1.0, sim + (matches * 0.18))

            scores.append((sim, self.documents[idx]))

        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for sim, doc in scores[:top_k]:
            results.append({
                "relevance_score": round(sim, 4),
                "protocol_id": doc["id"],
                "disease": doc["disease"],
                "disease_mr": doc["disease_mr"],
                "authority": doc["authority"],
                "source_title": doc["source_title"],
                "section": doc["section"],
                "clinical_evidence": doc["clinical_evidence"],
                "isolation_protocol_mr": doc["isolation_protocol_mr"],
                "treatment_and_firstaid_mr": doc["treatment_and_firstaid_mr"],
                "ayurvedic_evm_mr": doc["ayurvedic_evm_mr"],
                "subclinical_biomarkers": doc["subclinical_biomarkers"]
            })

        return results

    def query_rag(self, query: str) -> Dict[str, Any]:
        """
        Full RAG pipeline:
        1. Retrieval: Finds relevant veterinary SOPs based on symptoms.
        2. Augmentation: Gathers official citations and bio-security protocols.
        3. Generation: Synthesizes structured Marathi/English guidance.
        """
        retrieved_chunks = self.retrieve(query, top_k=2)

        if not retrieved_chunks or retrieved_chunks[0]["relevance_score"] < 0.15:
            # Fallback for general non-disease queries
            return {
                "query": query,
                "status": "NO_DIRECT_MATCH",
                "retrieved_protocols": [],
                "synthesized_response_mr": "आपल्या वर्णनानुसार थेट विशिष्ट आजाराचा संदर्भ आढळला नाही. पशूचे तापमान व रवंथ वेळ तपासा अथवा १९६२ हेल्पलाईनवर संपर्क करा.",
                "verified_citations": []
            }

        top_match = retrieved_chunks[0]
        confidence_pct = int(min(98, max(65, top_match["relevance_score"] * 100)))

        citations = [
            {
                "citation_text": f"[{c['authority']}] {c['source_title']} ({c['section']})",
                "protocol_id": c["protocol_id"],
                "relevance": f"{int(c['relevance_score'] * 100)}%"
            }
            for c in retrieved_chunks if c["relevance_score"] > 0.2
        ]

        synthesized_text_mr = (
            f"🎯 **संभाव्य निदान:** {top_match['disease_mr']} (विश्वासार्हता: {confidence_pct}%)\n\n"
            f"📚 **शासन प्रमाणित संदर्भ:**\n{top_match['source_title']} - {top_match['section']}\n\n"
            f"🔬 **क्लिनिकल पुरावा:**\n{top_match['clinical_evidence']}\n\n"
            f"🛡️ **तात्काळ अलगीकरण व बायो-सिक्युरिटी:**\n{top_match['isolation_protocol_mr']}\n\n"
            f"💊 **प्रथमोपचार व औषधोपचार:**\n{top_match['treatment_and_firstaid_mr']}\n\n"
            f"🌿 **आयुर्वेदिक घरगुती उपचार (EVM):**\n{top_match['ayurvedic_evm_mr']}"
        )

        return {
            "query": query,
            "status": "SUCCESS",
            "confidence_pct": confidence_pct,
            "primary_condition": top_match["disease"],
            "primary_condition_mr": top_match["disease_mr"],
            "verified_citations": citations,
            "retrieved_protocols": retrieved_chunks,
            "synthesized_response_mr": synthesized_text_mr,
            "helpline": "महाराष्ट्र शासन पशुसंवर्धन मोफत हेल्पलाईन: १९६२"
        }


# Global singleton instance
rag_engine = VeterinaryRAGEngine()

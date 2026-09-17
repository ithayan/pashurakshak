"""
PashuRakshak AI Core - RAG (Retrieval-Augmented Generation) Endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.rag_engine import rag_engine

router = APIRouter(prefix="/rag", tags=["Veterinary Retrieval-Augmented Generation (RAG)"])


class RAGQueryRequest(BaseModel):
    query: str = Field(..., example="गायीची कास सुजली आहे आणि दुधात गुठळ्या दिसत आहेत", description="Farmer symptom query in Marathi, Hindi, or English")
    top_k: Optional[int] = Field(2, description="Number of knowledge chunks to retrieve")


class CitationItem(BaseModel):
    citation_text: str
    protocol_id: str
    relevance: str


class RAGResponse(BaseModel):
    query: str
    status: str
    confidence_pct: Optional[int] = None
    primary_condition: Optional[str] = None
    primary_condition_mr: Optional[str] = None
    verified_citations: List[CitationItem] = []
    retrieved_protocols: List[Dict[str, Any]] = []
    synthesized_response_mr: str
    helpline: Optional[str] = None


@router.post("/query", response_model=RAGResponse)
async def query_rag_knowledge_base(req: RAGQueryRequest):
    """
    Sub-module RAG: Ingests symptom descriptions in Marathi/Hindi/English,
    retrieves verified Maharashtra Animal Husbandry SOPs & ICAR protocols,
    and returns hallucination-free augmented veterinary guidance with exact citations.
    """
    try:
        result = rag_engine.query_rag(req.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query execution failed: {str(e)}")


@router.get("/corpus")
async def get_indexed_protocols():
    """
    Returns the full indexed corpus of Maharashtra veterinary SOPs,
    prevention circulars, and ethno-veterinary guidelines.
    """
    return {
        "total_documents": len(rag_engine.documents),
        "total_vocabulary_terms": len(rag_engine.vocab),
        "corpus": rag_engine.documents
    }

from typing import List
from src.retriever import CandidateChunk


class PromptBuilder:
    """
    Constructs citation-aware, grounded prompts separating Primary Retrieved Evidence from Supporting Sibling Context.
    """

    SYSTEM_PROMPT = """You are an expert Obsidian Vault Knowledge Assistant.
Your sole task is to answer user questions based STRICTLY and EXCLUSIVELY on the retrieved PRIMARY RETRIEVED EVIDENCE passages provided below.

CRITICAL DIRECT EVIDENCE & GROUNDING RULES:
1. DIRECT EVIDENCE MANDATE: Before answering, verify if the PRIMARY RETRIEVED EVIDENCE passages contain explicit, direct factual evidence for the specific question asked.
2. NO SPECULATION OR INFERENCE: If the primary passages only contain peripheral mentions or broader topic notes but DO NOT contain direct evidence answering the exact details requested, you MUST respond with EXACTLY:
   "No relevant information found in the vault."
   Do NOT attempt to infer, guess, extrapolate, or reconstruct an answer from partial or peripheral mentions.
3. MULTI-PART QUESTION COMPLETENESS: If direct evidence IS present for a multi-part query, answer ALL parts thoroughly using the primary retrieved passages.
4. CITATION REQUIREMENT: Every factual claim in your answer MUST cite its exact source note and section using inline bracket markup: `[Note Name#Section]`.
5. SUPPORTING CONTEXT IS AUXILIARY: Use Supporting Sibling Context ONLY to clarify surrounding terminology in primary passages; do NOT treat supporting context as independent answers.
6. TONE & FORMAT: Maintain a professional, structured, technical tone. Use bullet points and code blocks where appropriate.
"""

    @staticmethod
    def build_user_prompt(query: str, chunks: List[CandidateChunk]) -> str:
        """
        Formats user question, primary evidence chunks, and sibling context into a grounded prompt.
        """
        if not chunks:
            return f"USER QUESTION: {query}\n\nRETRIEVED VAULT CONTEXT:\n[No relevant context chunks found.]"

        formatted_context = []
        for idx, chunk in enumerate(chunks, 1):
            source_tag = (
                f"Passage {idx} | File: {chunk.file_name} | Note: {chunk.note_name} | Section: {chunk.heading} | "
                f"Raw Cosine Similarity: {chunk.raw_semantic_score} | BM25 Score: {chunk.lexical_bm25_score} | Hybrid Score: {chunk.hybrid_score}"
            )
            passage_block = [f"=== {source_tag} ==="]

            if chunk.supporting_prev_text:
                passage_block.append(f"[SUPPORTING PREVIOUS SIBLING CONTEXT]\n... {chunk.supporting_prev_text}")

            passage_block.append(f"[PRIMARY RETRIEVED EVIDENCE]\n{chunk.text}")

            if chunk.supporting_next_text:
                passage_block.append(f"[SUPPORTING NEXT SIBLING CONTEXT]\n... {chunk.supporting_next_text} ...")

            formatted_context.append("\n".join(passage_block) + "\n")

        context_block = "\n\n".join(formatted_context)
        return (
            f"USER QUESTION: {query}\n\n"
            f"RETRIEVED VAULT CONTEXT:\n{context_block}\n\n"
            f"INSTRUCTION: Evaluate if the PRIMARY RETRIEVED EVIDENCE above contains direct factual evidence answering '{query}'. "
            f"If direct evidence is missing, output 'No relevant information found in the vault.'. "
            f"Otherwise, provide a complete, grounded answer with source citations `[Note Name#Section]` covering all query aspects."
        )

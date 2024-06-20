import argparse
import re
from typing import List, Tuple

from milvus_model.hybrid import BGEM3EmbeddingFunction
from milvus_model.reranker import BGERerankFunction
from pymilvus import AnnSearchRequest, Collection, RRFRanker, connections


class Ragsearch:
    def __init__(self):
        connections.connect("default", host="localhost", port="19530")
        self.col = Collection("snu_milvus_final")
        self.col.load()
        self.ef = BGEM3EmbeddingFunction(
            model_name="BAAI/bge-m3", use_fp16=False, device="mps"
        )
        self.rf = BGERerankFunction(
            model_name="BAAI/bge-reranker-v2-m3", use_fp16=False, device="mps"
        )

    def retrieve(
        self,
        query: str,
        k: int = 10,
    ) -> List[str]:

        # Prepare the query embedding
        query_embeddings = self.ef([query])

        # Prepare the search requests for both vector fields
        sparse_search_params = {"metric_type": "IP"}
        sparse_req = AnnSearchRequest(
            query_embeddings["sparse"],
            "sparse_embedding",
            sparse_search_params,
            limit=k,
        )
        dense_search_params = {"metric_type": "IP"}
        dense_req = AnnSearchRequest(
            query_embeddings["dense"], "embedding", dense_search_params, limit=k
        )

        result = self.col.hybrid_search(
            [sparse_req, dense_req],
            rerank=RRFRanker(),
            limit=k,
            output_fields=["content", "summary"],
        )[0]

        return [{"summary": hit.summary, "detail": hit.content} for hit in result]

    def rerank(
        self,
        query: str,
        candidates: List[str],
        l: int = 3,
    ) -> List[str]:

        texts = [
            f"{candidate['summary']}: {candidate['detail']}" for candidate in candidates
        ]

        reranked = self.rf(query, texts, top_k=l)

        return [candidates[hit.index] for hit in reranked]

    def make_rag_prompt(self, query: str, candidates: List[str]) -> str:

        pattern = re.compile(r"\[(.*?)\]")
        str = "너는 학사 상담을 해주는 챗봇이야. 다음 질문에 대해 관련 학칙들을 바탕으로 정확하게 답변해줘.\n"
        str += f"질문: {query}\n"
        str += "\n관련 학칙들: \n"

        modified = []
        for candidate in candidates:
            text = f"{candidate['summary']}: {candidate['detail']}"
            modified.append(re.sub(pattern, "", text))
        str += "\n".join(modified)

        return str

    def rag_search(
        self,
        query: str,
        k: int = 10,
        l: int = 3,
    ) -> tuple:

        retrieved = self.retrieve(query, k)
        reranked = self.rerank(query, retrieved, l)
        prompt = self.make_rag_prompt(query, reranked)

        return (prompt, reranked)

import argparse
import re
from typing import List

from milvus_model.hybrid import BGEM3EmbeddingFunction
from milvus_model.reranker import BGERerankFunction
from pymilvus import AnnSearchRequest, Collection, RRFRanker, connections


def retrieve(
    query: str,
    col: Collection,
    ef: BGEM3EmbeddingFunction,
    k: int = 10,
    verbose: bool = False,
) -> List[str]:

    # Prepare the query embedding
    query_embeddings = ef([query])

    # Prepare the search requests for both vector fields
    sparse_search_params = {"metric_type": "IP"}
    sparse_req = AnnSearchRequest(
        query_embeddings["sparse"], "sparse_embedding", sparse_search_params, limit=k
    )
    dense_search_params = {"metric_type": "IP"}
    dense_req = AnnSearchRequest(
        query_embeddings["dense"], "embedding", dense_search_params, limit=k
    )

    result = col.hybrid_search(
        [sparse_req, dense_req],
        rerank=RRFRanker(),
        limit=k,
        output_fields=["content", "summary"],
    )[0]

    if verbose:
        for hit in result:
            print(f"{hit.summary}, score: {hit.score:.4f}")

    return [{"summary": hit.summary, "detail": hit.content} for hit in result]


def rerank(
    query: str,
    rf: BGERerankFunction,
    candidates: List[str],
    l: int = 5,
    verbose: bool = False,
) -> List[str]:
    texts = [
        f"{candidate['summary']}: {candidate['detail']}" for candidate in candidates
    ]
    reranked = rf(query, texts, top_k=l)
    if verbose:
        for hit in reranked:
            print(f"{hit.text[:30]},  score {hit.score:.4f}")

    return [candidates[hit.index] for hit in reranked]


def make_rag_prompt(query: str, candidates: List[str]) -> str:

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default="서울대 학부생의 졸업 연한이 어떻게 되나요?",
        help="Query string for RAG",
    )
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default="snu_milvus_final",
        help="Name of collection to drop",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="BAAI/bge-m3",
        help="BGE checkpoint to get embeddings",
    )
    parser.add_argument(
        "--reranker",
        "-r",
        type=str,
        default="BAAI/bge-reranker-v2-m3",
        help="BGE reranker checkpoint",
    )
    parser.add_argument(
        "--top_k",
        "-k",
        type=int,
        default=10,
        help="Number of candidates to retrieve from DB",
    )
    parser.add_argument(
        "--top_l",
        "-l",
        type=int,
        default=5,
        help="Number of candidates to return after reranking",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show retrieved results and scores"
    )
    parser.add_argument(
        "--only_prompt", "-p", action="store_true", help="Only print RAG prompt"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    assert (
        not args.only_prompt or not args.verbose
    ), "--only_prompt and --verbose cannot be true at the same time"

    # Initialize models and collection
    if not args.only_prompt:
        print("> Initializing...")
    connections.connect("default", host="localhost", port="19530")
    col = Collection(args.name)
    col.load()
    ef = BGEM3EmbeddingFunction(model_name=args.model, use_fp16=False, device="mps")
    rf = BGERerankFunction(model_name=args.reranker, use_fp16=False, device="mps")

    # 1. Retrieve top-k candidates
    if not args.only_prompt:
        if args.verbose:
            print()
        print("> Retrieving top-k candidates...")
    retrieved = retrieve(args.query, col, ef, args.top_k, args.verbose)

    # 2. Rerank and select top-l candidates
    if not args.only_prompt:
        if args.verbose:
            print()
        print("> Reranking...")
    reranked = rerank(args.query, rf, retrieved, args.top_l, args.verbose)

    if not args.only_prompt:
        print("\nGenerated RAG prompt")
        print("======================")

    print(make_rag_prompt(args.query, reranked))

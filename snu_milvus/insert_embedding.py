import argparse
import sys
from typing import List

import pandas as pd
from milvus_model.hybrid import BGEM3EmbeddingFunction
from pymilvus import Collection, connections, utility


def insert_embedding(
    data: List[str],
    col: Collection,
    ef: BGEM3EmbeddingFunction,
) -> None:

    # Inference and Insert Embeddings
    print("> Start Inference")
    docs_embeddings = ef(data)
    entities = [data, docs_embeddings["sparse"], docs_embeddings["dense"]]

    # Load Collection as insert data
    col.load()
    col.insert(entities)
    col.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default="snu_milvus_final",
        help="Name of the db collection to insert embeddings",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="output_final.csv",
        help="CSV file with crawled result",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="BAAI/bge-m3",
        help="BGE checkpoint to get embeddings",
    )
    parser.add_argument(
        "--batch", "-b", type=int, default=4, help="Batch size for inference"
    )
    parser.add_argument(
        "--device", "-d", type=str, default="cpu", help="Device for inference"
    )
    args = parser.parse_args()

    # Connect with Milvus Collection
    print(f"> Conneting to Milcollection: {args.name}")
    connections.connect("default", host="localhost", port="19530")
    if not utility.has_collection(args.name):
        print(f"No existing collection: {args.name}")
        sys.exit()

    # Read Data file
    print(f"> Reading data from: {args.input}")
    df = pd.read_csv(args.input)
    input_data = []
    summaries = []
    contents = []
    max = 0
    for idx in range(len(df)):
        place = df.loc[idx]["위치"]
        num = df.loc[idx]["조항"]
        title = df.loc[idx]["제목"]
        content = df.loc[idx]["내용"]

        input_data.append(f"{place} 제{num}조 ({title}): {content}")
        contents.append(content)
        summaries.append(f"{place} 제 {num}조({title})")

    for data in input_data:
        if max < len(data):
            max = len(data)
    print(f"> Num entries: {len(df)}, Maximum length: {max}")

    # Initialize Embedding
    print("> Initializing Embedding function")
    use_fp16 = True if args.device == "cuda" else False
    ef = BGEM3EmbeddingFunction(
        model_name=args.model,
        batch_size=args.batch,
        device=args.device,
        use_fp16=use_fp16,
    )

    # Inference and Insert Embeddings
    print("> Start Inference")
    docs_embeddings = ef(input_data)
    entities = [
        contents,
        summaries,
        docs_embeddings["sparse"],
        docs_embeddings["dense"],
    ]

    # Load Collection as insert data
    print("> Inserting Data")
    col = Collection(args.name)
    col.load()
    col.insert(entities)
    col.flush()

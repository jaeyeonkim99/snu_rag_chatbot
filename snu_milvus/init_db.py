import argparse
import sys

from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusClient

fmt = "\n=== {:30} ===\n"


def init_db(
    name: str = "snu_milvus",
    dim: int = 1024,
    max_len: int = 8192,
    port: int = 19530,
) -> bool:

    # 1. connect to DB
    print(fmt.format("start connecting to Milvus"))
    client = MilvusClient(uri=f"http://localhost:{port}")

    # 2. initialize DB
    has = client.has_collection(name)
    if has:
        print(fmt.format(f"DB {name} already exists"))
        sys.exit()

    print(fmt.format("Create collection `{name}`", name=name))
    schema = client.create_schema(
        auto_id=False,
        enable_dynamic_fields=True,
        description="snu milvus - 창통설 A조 최종",
    )

    # 3. define schema and create collection
    fields = [
        FieldSchema(
            name="pk",
            dtype=DataType.VARCHAR,
            is_primary=True,
            auto_id=True,
            max_length=100,
        ),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=max_len),
        FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=max_len),
        FieldSchema(name="sparse_embedding", dtype=DataType.SPARSE_FLOAT_VECTOR),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
    ]
    schema = CollectionSchema(fields, "")

    client.create_collection(
        collection_name=name, schema=schema, consistency_level="Strong"
    )

    # 4. create index
    print(fmt.format("Start Creating index"))
    index_params = client.prepare_index_params()

    index_params.add_index(field_name="embedding")

    index_params.add_index(
        field_name="embedding",
        index_type="IVF_FLAT",
        metric_type="IP",
        params={"nlist": 1},
    )

    index_params.add_index(field_name="sparse_embedding")

    index_params.add_index(
        field_name="sparse_embedding",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP",
        params={"drop_ratio_build": 0},
    )

    client.create_index(collection_name=name, index_params=index_params)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default="snu_milvus_final",
        help="Name of db collection",
    )
    parser.add_argument(
        "--dim", "-d", type=int, default=1024, help="Dimension of the dense embedding"
    )
    parser.add_argument(
        "--max_len",
        "-l",
        type=int,
        default=8192,
        help="Maximum length of each content entry",
    )
    args = parser.parse_args()

    init_db(name=args.name, dim=args.dim, max_len=args.max_len, port=19530)

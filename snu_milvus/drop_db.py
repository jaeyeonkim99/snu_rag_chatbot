from pymilvus import connections, utility
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", "-n", type=str, default="snu_milvus", help="Name of collection to drop")
    args = parser.parse_args()

    connections.connect("default", host="localhost", port="19530")
    utility.drop_collection(args.name)
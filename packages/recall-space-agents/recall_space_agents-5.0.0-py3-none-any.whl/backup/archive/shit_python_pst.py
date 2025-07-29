from psycopg import Connection
from langgraph.checkpoint.postgres import PostgresSaver
#import psycopg
conn_string = "postgresql://recall-space:pleaseletmein@localhost:5432/demo-db"

with Connection.connect(conn_string) as conn:
    checkpointer = PostgresSaver(conn)
    # NOTE: you need to call .setup() the first time you're using your checkpointer
    checkpointer.setup()
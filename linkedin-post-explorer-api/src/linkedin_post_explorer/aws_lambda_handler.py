import os

import boto3

BUCKET_NAME = os.environ["BUCKET_NAME"]

POSTS_JSON_PATH = f"s3://{BUCKET_NAME}/posts.json"

# use the resource api to fetch the posts.json file from s3
s3 = boto3.resource("s3")
posts_json = s3.Object(BUCKET_NAME, "posts.json")


def sqlite_vec_run():
    import sqlite3

    import sqlite_vec
    from linkedin_post_explorer.utils import (
        console,
        pprint_query,
        pprint_result_set,
    )
    from sqlalchemy import (
        Column,
        Text,
        func,
    )
    from sqlmodel import (
        Field,
        Session,
        SQLModel,
        create_engine,
        select,
    )

    # Create and configure the SQLite database with sqlite_vec extension
    db = sqlite3.connect(":memory:")
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    # Create SQLModel engine
    engine = create_engine("sqlite://", creator=lambda: db)

    class Document(SQLModel, table=True):
        id: int = Field(primary_key=True)
        contents: str
        contents_embedding: str = Field(sa_column=Column(Text))  # Store vector as string

    # Create the table
    SQLModel.metadata.create_all(engine)

    # Create a session
    with Session(engine) as session:
        # Print vec_version
        vec_version = session.exec(select(func.vec_version())).one()
        console.print(f"[bold green]vec_version=[/bold green][cyan]{vec_version}[/cyan]")

        # Insert data
        documents = [
            Document(id=1, contents="alex", contents_embedding="[1.1, 1.1, 1.1, 1.1, 1.1]"),
            Document(id=2, contents="brian", contents_embedding="[2.2, 2.2, 2.2, 2.2, 2.2]"),
            Document(id=3, contents="craig", contents_embedding="[3.3, 3.3, 3.3, 3.3, 3.3]"),
        ]
        session.add_all(documents)
        session.commit()

        # Query data
        query = select(
            Document.id,
            Document.contents,
            func.vec_distance_L2(Document.contents_embedding, "[2.2, 2.2, 2.2, 2.2, 2.2]").label("distance"),
        ).order_by("distance")

        pprint_query(query)
        results = session.exec(query)
        pprint_result_set(results)


def handler(event, context):
    # print the contents of posts.json
    print(posts_json.get()["Body"].read())

    print(event)
    return {"statusCode": 200, "body": "Hello from Lambda!"}

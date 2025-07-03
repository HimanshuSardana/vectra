import chromadb

client = chromadb.PersistentClient(path="./vector_store/")
collection = client.get_or_create_collection(name="Documents")

# collection.add(
#     ids=["1", "2"],
#     documents=[
#         "My favourite anime is Fullmetal Alchemist Brotherhood",
#         "My favourite manga is 20th Century Boys"
#     ]
# )

result = collection.query(query_texts=["What is the user's favourite anime"], n_results=1)
print(result)

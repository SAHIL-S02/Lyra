from app.memory.manager import MemoryManager


memory = MemoryManager()


print("=" * 60)
print("              LYRA MEMORY TEST")
print("=" * 60)


print("\n1. Remember")
saved = memory.remember(
    "favorite_programming_language",
    "Java",
    category="preference",
    retention="permanent",
)

print(saved)


print("\n2. Recall")
result = memory.recall(
    "favorite_programming_language"
)

print(result)


print("\n3. Search")
results = memory.search("Java")

for item in results:
    print(item)


print("\n4. All memories")
for item in memory.all_memories():
    print(item)


print("\n5. Forget")
deleted = memory.forget(
    "favorite_programming_language"
)

print("Deleted:", deleted)


print("\n6. Verify deletion")
print(
    memory.recall(
        "favorite_programming_language"
    )
)


print("\nMemory system test complete.")

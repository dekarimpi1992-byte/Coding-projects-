
import enum

print("Python is loading enum from:")
print(enum.__file__)

print("\nDoes global_enum exist?")
print(hasattr(enum, "global_enum"))
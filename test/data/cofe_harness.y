# Uses SemiColonTransformer
import python_api;

say_hello = python_api.say_hello;

print("Testing python_api.y.");

print(f"Testing n = 'Joe': ");
say_hello("Joe");

print(f"Testing n = '': ");
say_hello("");

print(f"Testing n = 'Becky': "); 
say_hello("Becky");
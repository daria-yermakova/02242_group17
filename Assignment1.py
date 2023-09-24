import os

root = "course-02242-examples"

arr_files = []

for path, subdirs, files in os.walk(root):
    for name in files:
      if name.endswith(".java"):
        file_path = os.path.join(path, name)
        arr_files.append(file_path)
        cur_file = open(file_path, 'r')
        lines = cur_file.readlines()
        for line in lines:
          print(line)
        #   TODO: here should be analysis of the each line


############################# This is a different way to open the files
import glob
import re
import os

files = glob.glob("**/*.java", recursive=True, root_dir=root)

print("files:", files)

# \s* -> 0 to many spaces and tabs
# \s+ -> 1 to many spaces and tabs
# ([a-zA-Z\_][a-zA-Z0-9\_]*(?:\.[a-zA-Z\_][a-zA-Z0-9\_]*)*(?:\.\*)?) -> capture group of imported class / package
#   [a-zA-Z\_] -> must start with lowercase letter, uppercase letter or underscore
#   [a-zA-Z0-9\_]* -> can be followed by 0 to many lowercase letter, uppercase letter, underscore or number
#   (?:\.[a-zA-Z\_][a-zA-Z0-9\_]*)* -> group after the first package name, can be followed by a . and then a new subpackage name, 0 to many times
#     ?: -> do not capture this group, just using group for the 0 to many (*)
#   (?:\.\*)? -> group to capture package imports that end with .*
#     ?: -> do not capture this group, just using group for 0 to 1 (?)


# Find known classes from project
pPackage = re.compile(r"^\s*package\s+([a-zA-Z\_][a-zA-Z0-9\_]*(?:\.[a-zA-Z\_][a-zA-Z0-9\_]*)*);")
dependencies = dict()
for file in files:
    with open(root + "/" + file) as f:
        content = f.read()
        m = re.search(pPackage, content)
        className = os.path.splitext(os.path.basename(file))[0]
        packageName = m.group(1)
        dependencies[packageName + "." + className] = set()

print("classes to parse:", dependencies.keys())

# Parse project
print("imports:")
pSpecific = re.compile(r"\s*import\s+([a-zA-Z\_][a-zA-Z0-9\_]*(?:\.[a-zA-Z\_][a-zA-Z0-9\_]*)*)\s*;")
pWildcard = re.compile(r"\s*import\s+([a-zA-Z\_][a-zA-Z0-9\_]*(?:\.[a-zA-Z\_][a-zA-Z0-9\_]*)*)(?:\.\*)\s*;")
pSingleLineComment = re.compile(r"\/\/.*")
pMultiLineComment = re.compile(r"\/\*([^\*]*(\*(?!\/))?)*\*(?=\/)\/", re.MULTILINE) # Using combination of negative and positive lookahead
pFunctionsDefinitions = re.compile(r"(?:public|private|protected)(?:\s+static)?\s+(?P<returnType>\S+)\s+[a-zA-Z]+\((?P<args>[^)]*)\)")
pArgs = re.compile(r"(?:\s*(?P<type>\S+)\s+\S+\s*)")
pBuiltInTypes = re.compile(r"void|int|byte|short|long|float|double|boolean|char")
pArray = re.compile(r"\s*\[\s*\]\s*")
pGeneric = re.compile(r"([^>]+)<([^>]+)>$")

# Extract separate types from a type statement
# i.e. generics, arrays etc.
def process_types(type):
   # Remove array
   type = re.sub(pArray, "", type)
   # Process generics
   m = re.search(pGeneric, type)
   if m is None: 
      # Not generic
      m = re.search(pBuiltInTypes, type)
      if m is None:
        v = set([type])
        return v
      else: # Empty set, built-in type
         return set()
   else:
      # Generic, add type and search its generic part recursively for more types
      v = set([m.group(1)])
      v.update(process_types(m.group(2)))
      return v

for file in files:
    with open(root + "/" + file) as f:
        # Read file content
        content = f.read()
        # Remove comments
        content = re.sub(pMultiLineComment, "", content)
        content = re.sub(pSingleLineComment, "", content)
        #print(content)
        # Get package name # Classes from same package doesnt need to be imported
        m = re.search(pPackage, content)
        packageName = m.group(1)
        # Get class name again
        className = os.path.splitext(os.path.basename(file))[0]
        className = packageName + "." + className
        # Find import statements
        directlyImportedClasses = set(re.findall(pSpecific, content))
        packagesImported = set(re.findall(pWildcard, content))
        # Add directly imported classes to list of dependencies
        dependencies[className].update(directlyImportedClasses)
        # Find usages of classes
        m = re.findall(pFunctionsDefinitions, content)
        for match in m:
           types = set()
           returnType = match[0]
           returnTypes = process_types(returnType)
           types.update(returnTypes)
           args = match[1]
           margs = re.findall(pArgs, args)
           for matchargs in margs:
              argTypes = process_types(matchargs)
              types.update(argTypes)
           # Add types to dependnecies
           for type in types:
              found = False
              # Check own package
              dependency = packageName + "." + type
              if dependency in dependencies:
                 found = True
                 dependencies[className].update([dependency])
              # Check directly imported
              if not found:
                for importedClass in directlyImportedClasses:
                  if importedClass.endswith("." + type):
                      found = True
                      break
              # Check wildcards
              if not found:
                 for importedPackage in packagesImported:
                    dependency = importedPackage + "." + type
                    if dependency in dependencies.keys():
                       found = True
                       dependencies[className].update([dependency])
                       break
              # Assume java.lang if not found
              if not found:
                 dependencies[className].update(["java.lang." + type])  

print("dependencies", dependencies)

# Construct graph
nodes = set()
edges = set()

for key in dependencies:
    nodes.add(f'"{key}" [label="{key}"]\n')

    for dependency in dependencies[key]:
        edges.add(f'"{key}" -> "{dependency}";\n')

with open("./output.dot", "w") as f:
    first_line = "digraph SourceGraph {\n"
    last_line = "}"

    lines = [first_line]
    lines.extend(nodes)
    lines.extend(edges)
    lines.append(last_line)

    f.writelines(lines)

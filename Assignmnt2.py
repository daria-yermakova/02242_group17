from tree_sitter import Language, Parser

FILE = "./languages.so"
Language.build_library(FILE, ["tree-sitter-java"])
JAVA_LANGUAGE = Language(FILE, "java")

parser = Parser()
parser.set_language(JAVA_LANGUAGE)

fields = []

def print_field_names(node):
    #print("node type is " + node.type)
    if node.type == "identifier":
        print(node)
        fields.append(node)
        #print(field_name)

    for child in node.children:
        print_field_names(child)

# the tree is now ready for analysing
#print(tree.root_node.sexp())

if __name__ == '__main__':
    # with open("Test.java", "rb") as f:
    #     tree = parser.parse(f.read())
    #     print_field_names(tree.root_node)

    with open("Test.java", "rb") as f:
        content = f.readlines()

    # for i in range(len(content)):
    #     print(i)
    #     print(content[i])

    for field in content:
        # print(field)
        curField = content[field.start_point[0]][field.start_point[1]:field.end_point[1]]
        if curField.startswith('public class'):
            print(curField)

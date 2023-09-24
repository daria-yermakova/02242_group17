import json

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def print_json(data):
    for item in data:
        print(item)

def construct_graph(dependencies):
    nodes = set()
    edges = set()
    for key in dependencies:
        nodes.add(f'"{key}" [label="{key}"]\n')
        for dependency in dependencies[key]:
            edges.add(f'"{key}" -> "{dependency}";\n')
    with open("./output.dot", "w") as f:
        first_line = "digraph DetailedClassDiagram {\n"
        last_line = "}"
        lines = [first_line]
        lines.extend(nodes)
        lines.extend(edges)
        lines.append(last_line)
        f.writelines(lines)


def analyze(data):
    dep = {}
    for item in data:
        dep[item.get('name')] = []
        print('--------------', item.get('name'), '--------------')
        print('Fields')
        for i in item.get('fields'):
            if i.get('type') and i.get('type').get('name'):
                typeStr = f"class <{i.get('type').get('name')}>"
            else:
                typeStr = i.get('type').get('base')
            if i.get('access') != []:
                access = i.get('access')[0]
                if access == 'private':
                    accStr = '-private'
                elif access == 'public':
                    accStr = '-public'
                else:
                    accStr = '-protected'
            else: accStr = '-'
            obj = f"{accStr} {i.get('name')}: {typeStr}"
            dep[item.get('name')].append(obj)
            print(obj)
        print('Methods')
        for i in item.get('methods'):
            # returns
            if i.get('returns').get('type') == None:
                returns = 'void'
            elif i.get('returns').get('type').get('kind') == 'class':
                returns = i.get('returns').get('type').get('name')
            else:
                returns = i.get('returns').get('type').get('base')
            # access
            if i.get('access') != []:
                access = i.get('access')[0]
                if access == 'private':
                    accStr = '-private'
                elif access == 'public':
                    accStr = '-public'
                else:
                    accStr = '-protected'
            else:
                accStr = '-'
            # params
            if i.get('typeparams') != []:
                for j in range(0, len(i.get('typeparams'))):
                    name_param = i.get('typeparams')[j].get('name')
                    type_param = i.get('params')[j].get('type').get('name')
                    params = f"{type_param} {name_param}"
            else: params = ''
            obj = f"{accStr} {returns} {i.get('name')}({params}):"
            dep[item.get('name')].append(obj)
            print(obj)
        print('--------------------------------------------')
    print('DEPS', dep)
    return dep


if __name__ == '__main__':
    file_path = 'output.json'
    data = read_json(file_path)
    # print_json(data)
    deps = analyze(data)
    construct_graph(deps)

# To generate png, run: dot -Tpng output.dot -o output.png
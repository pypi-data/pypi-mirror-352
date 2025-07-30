from trie_search import TRIESearch

root = {}
dict_file = '/Users/chanhyeok/Downloads/lexicon.txt'
sc = TRIESearch(root)
with open(dict_file, 'r') as f:
    for line in f:
        if ';;' in line[:2]: continue
        k, v = line.strip().split('\t')
        sc.build_trie_search(k, v)
    # print(root)
word = '고용 노동부'
values, value_data = sc.trie_search(word, True)
print(values, value_data)

word = '2시뉴스외전'
values, value_data = sc.trie_search( word, True)
print(values, value_data)
word = '2시 뉴스외전'
values, value_data = sc.trie_search( word, True)
print(values, value_data)

word = 'gbc'
values, value_data = sc.trie_search( word, True)
print(values, value_data)

from lib.db import db

def get_channel(func):
    def inner(*args, **kwargs):
        print(args, '\n', kwargs)
        channel_id = db.field("SELECT LogChannelID FROM Guilds WHERE GuildID = (?)", args[2])
        if channel_id is None:
            raise ValueError(args[0], 'log')
        print(22)
        print(channel_id)
        channel = args[0].get_channel(channel_id)
        return func(channel)
    print(26)
    return inner
class test:
    def __init__(self, name):
        self.name = name

    @get_channel
    def get_name(self, name='', test='234342'):
        self.name = name
        return self.name

    def print_name(self):
        print(self.name)


# test1 = test(name='felix')
# test1.print_name()
# print(test1.get_name('armin', 810428719796977704))
"""sub_str = ['tee'*idx for idx in range(1, 6)]
v1 = len(max(sub_str))
print(v1)
for ele in sub_str:
    print(f'{ele:<{v1}} moin')

table = ("\n".join(
            f"{idx}. {'awd':<{10}}"
            f"(Elo: {idx} | Level: {idx})"
            for idx, entry in enumerate(sub_str))
        )
print(table)

list1 = [[0, 1, 2, 3, 4, 5],
 [6, 7, 8, 9, 10, 11],
 [12, 13, 14, 15, 16, 17],
 [18, 19, 20, 21, 22, 23]]
tlist = list(zip(*list1))
for ele in tlist:
    print(ele)
"""
print(bool({}))
print('TeT'[1])

import json
with open('data/roles/predefined.json') as js:
    data = json.load(js)

for ele in data['roles']:
    print(ele['Ratio'])

print(int('0x9c5221', base=16))
if __name__ == '__main__':
    pass
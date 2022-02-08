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
print("#2830498203948"[1:])

if __name__ == '__main__':
    pass
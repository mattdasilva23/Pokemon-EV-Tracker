
ITEMS = {
    'Macho Brace': lambda evs: evs * 2,
    'Power Weight': lambda evs: evs + EvSet(hp=4),
    'Power Bracer': lambda evs: evs + EvSet(attack=4),
    'Power Belt': lambda evs: evs + EvSet(defense=4),
    'Power Lens': lambda evs: evs + EvSet(special_attack=4),
    'Power Band': lambda evs: evs + EvSet(special_defense=4),
    'Power Anklet': lambda evs: evs + EvSet(speed=4)
}

class EvSet(object):

    STATS = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
    LABELS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']

    MAX_STAT = 255
    MAX_EV = 510

    operator = ''

    @staticmethod
    def label(stat):
        return EvSet.LABELS[EvSet.STATS.index(stat)]

    def __init__(self, hp=0, attack=0, defense=0, special_attack=0, special_defense=0, speed=0):
        self.hp = int(hp)
        self.attack = int(attack)
        self.defense = int(defense)
        self.special_attack = int(special_attack)
        self.special_defense = int(special_defense)
        self.speed = int(speed)
        # print('\n\tEVS init\n\t-----------')
        # print(self)

    # this works, but can definitely be improved
    def __iadd__(self, other):
        print('IADD')
        print('self', self)
        print('other', other)
        EvSet.operator = '+'
        for stat in EvSet.STATS:
            print('before', stat, self.__dict__[stat])
            print('before total', self.check_if_maxed_510())
            self.__dict__[stat] += other.__dict__[stat]
            print(self.check_if_maxed_510())
            if (self.check_if_maxed_510() >= 510):
                print("maxed 510")
                self.__dict__[stat] -= (self.check_if_maxed_510() - EvSet.MAX_EV)
            print('after', stat, self.__dict__[stat])
        return self

    def __add__(self, other):
        evs = self.clone()
        evs += other
        return evs

    def __isub__(self, other):
        EvSet.operator = '-'
        for stat in EvSet.STATS:
            self.__dict__[stat] -= other.__dict__[stat]
            if (self.__dict__[stat] < 0):
                self.__dict__[stat] = 0
        return self

    def __sub__(self, other):
        evs = self.clone()
        evs -= other
        return evs

    def __imul__(self, integer):
        for stat in EvSet.STATS:
            self.__dict__[stat] *= integer
        return self

    def __mul__(self, integer):
        evs = self.clone()
        for stat in EvSet.STATS:
            evs.__dict__[stat] *= integer
        return evs

    def __str__(self):
        ev_string = [EvSet.operator + str(ev) + ' ' + str(EvSet.label(stat)) for stat, ev in self.to_dict().items() if ev > 0]
        return ', '.join(ev_string)

    def verbose(self):
        ev_string = [str(ev).zfill(3) + ' | +' + ('{0:05.2f}'.format(ev/4)).zfill(2) + ' | ' + str(EvSet.label(stat)) for stat, ev in self.to_dict().items()]
        return '\n'.join(ev_string)

    def clone(self):
        return EvSet(**self.to_dict())

    def check_if_maxed_510(self):
        total = 0
        for stat in EvSet.STATS:
            total += self.__dict__[stat]
        return total

    def check_evs_max_stat_255(self, other):
        print('\ncheck_evs_max_stat_255')
        for stat in EvSet.STATS:
            myStat = self.__dict__[stat]
            myOtherStat = other.__dict__[stat]
            print(myStat, myOtherStat, stat)
            if (myStat + myOtherStat > EvSet.MAX_STAT):
                print('adjusting stat', myOtherStat - ((myStat + myOtherStat) - EvSet.MAX_STAT))
                other.__dict__[stat] = myOtherStat - ((myStat + myOtherStat) - EvSet.MAX_STAT)
        return other
    
    def check_evs_max_510(self, other):
        print('\ncheck_evs_max_510')
        for stat in EvSet.STATS:
            myStat = self.__dict__[stat]
            myOtherStat = other.__dict__[stat]
            print(myStat, myOtherStat, stat)
            # if (myStat + myOtherStat )


        return other

    def compare_evs(self, other):
        for stat in EvSet.STATS:
            if (self.__dict__[stat] != other.__dict__[stat]):
                print(self.__dict__[stat])
                return False
        return True

    def to_dict(self):
        dict = {}
        for stat in EvSet.STATS:
            dict[stat] = self.__dict__[stat]
        return dict


class Species(object):

    def __init__(self, id, name, evs=None):
        self.id = int(id)
        self.name = name
        self.evs = EvSet() if evs is None else evs
        # print('\n\tSpecies init\n\t-----------')
        # print(self)

    def __str__(self):
        return '#%03d %-10s %s' % (self.id, self.name, self.evs)


class Pokemon(object):

    @classmethod
    def from_dict(cls, dict):
        import pokedex
        # print('\n\tfrom_dict\n\t-----------')
        # print(dict)
        dict['species'] = pokedex.fetch_by_id(dict['species'])
        dict['evs'] = EvSet(**dict['evs'])
        return cls(**dict)

    @staticmethod
    def get_pokemon_by_id(ID):
        import pokedex
        return pokedex.fetch_by_id(ID)

    def __init__(self, id, species, name=None, item=None, pokerus=False, evs=None):
        self.id = int(id)
        self.species = species
        self._name = None
        self.name = name
        self.item = item
        self.pokerus = pokerus
        self.evs = EvSet() if evs is None else evs
        # print('\n\tPokemon init\n\t-----------')
        # print(self)

    name = property(lambda self: self.get_name(),
                    lambda self, name: self.set_name(name))

    item = property(lambda self: self._item,
                    lambda self, item: self.set_item(item))

    def get_name(self):
        return self.species.name if self._name is None else self._name

    def set_name(self, name):
        if name is not None and len(name.strip()) > 0:
            self._name = name.strip()

    def set_item(self, item):
        if item is not None and item not in ITEMS:
            raise ValueError("Invalid item '%s'" % item)
        self._item = ITEMS[item] if item is not None else None
        self._itemName = item

    def get_item(self):
        return self._itemName

    def get_evs(self):
        return self.evs

    def clear_evs(self):
        self.evs = EvSet()

    def clear_item(self):
        self.item = None

    def status(self):
        status = str(self)
        if self.item:
            status +=  ' | ' + str(self.get_item())
        if self.pokerus:
            status += ' | Pokerus'
        status += '\n' + str(self.evs.verbose())
        status += '\n' + str(self.evs.check_if_maxed_510()) + ' | Total EVs\n'
        return status

    def listing(self, active):
        padding = '* ' if self is active else '  '
        return '%s%s' % (padding, self)

    def battle(self, species, number, undo=False):
        '''
        Alter's a tracked Pokemons EVs to simulate having battled a Species.
        These values are altered by pokerus and any item held. The EV
        increment can be multiplied by number to simulate multiple battles.
        '''
        evs = species.evs.clone()

        if self.item is not None:
            evs = self.item(evs)
        if self.pokerus:
            evs *= 2

        # this doesn't work for undo
        evs = (self.evs.check_evs_max_stat_255(evs))
        evs = (self.evs.check_evs_max_510(evs))
        print('New Evs: ', evs)

        if not undo:
            self.evs += evs * number
        else:
            self.evs -= evs * number
    
        return (evs * number)

    def to_dict(self):
        return {'species': self.species.id, 'name': self._name,
                'pokerus': self.pokerus, 'item': self._itemName,
                'evs': self.evs.to_dict(), 'id': self.id}

    def __str__(self):
        name = self.name
        if self._name is not None:
            name = '%s (%s)' % (name, self.species.name)
        if self.id is None:
            return name
        else:
            return '%d %s' % (self.id, name)
#!/usr/local/bin/python3
# coding=utf-8

import os
import sys
import argparse
import json
from datetime import datetime
from shutil import copyfile
from pokemon import EvSet, Pokemon
import pokedex
import pprint

# print(sys.version_info)

TRACKER_FILENAME = '.ev-'
TRACKER_PATH = os.path.expanduser(os.path.join('~', TRACKER_FILENAME))

class History(object):
    
    def __init__(self, filename):
        self._historyArr = {}
        self.activePokeID = None
        self.filename = filename
        self.full = False

    @classmethod 
    def from_json(cls, filename):
        # print('\n\tfrom_json_history\n\t----------')
        history = cls(filename)
        try:
            fp = open(filename, 'r')
            data = json.load(fp)
            for poke_id, his in data.items():
                history._historyArr[poke_id] = his
        except IOError:
            pass  # Ignore missing tracking file.
        history.activePokeID = str(_tracker.active.id)
        return history

    @staticmethod
    def to_json(history, filename=None):
        # print('\n\tto_json\n\t----------')
        filename = history.filename if filename is None else filename
        fp = open(filename, 'w')
        data = {}
        if (len(history._historyArr) > 0):
            data = history._historyArr
        json.dump(data, fp)
        fp.close()

    def get_active_poke_history_arr(self):
        if self.activePokeID not in self._historyArr:
            self._historyArr[self.activePokeID] = []
            _save_history()
        return self._historyArr[self.activePokeID]

    # add pokemon you battled to history - will always history to the active pokemon 
    def add_poke_to_history(self, id, evs):
        dateNow = datetime.today().strftime('%d-%m-%Y-%H:%M:%S')
        self.get_active_poke_history_arr().append([id, dateNow, str(evs)])
        print('\nAdded Pokemon to history: ' + str(id) + ' (' + str(Pokemon.get_pokemon_by_id(id).name) + ') at ' + dateNow)

    def add_item_to_history(self, item):
        dateNow = datetime.today().strftime('%d-%m-%Y-%H:%M:%S')
        self.get_active_poke_history_arr().append([item, dateNow, "---"])
        print('\nAdded Item to history: ' + str(item) + ' at ' + dateNow)

    def remove_poke_from_history(self, id):
        currentHistory = self.get_active_poke_history_arr()
        # loop through backwards to remove latest pokemon, otherwise it will remove earliest from the list
        for i, v in enumerate(currentHistory[::-1]):
            if id in v:
                print("\nFound a match with id: " + str(id) + ' (' + str(Pokemon.get_pokemon_by_id(id).name) + ')')
                print('Removed from history: ' + str(currentHistory[(len(currentHistory)-1)-i]))
                del currentHistory[(len(currentHistory)-1)-i]
                return
        print('\nNo match was found for: ' + str(id) + ' (' + str(Pokemon.get_pokemon_by_id(id).name) + ')')

    def clear_history(self):
        print('\nHistory cleared')
        self._historyArr[self.activePokeID] = []

    # temporary function to add evs to history json file 
    # def recalculate_history(self):
    #     print(self.get_active_poke_history_arr())
    #     for e in self.get_active_poke_history_arr():
    #         evs = str(Pokemon.get_pokemon_by_id(e[0]).evs)
    #         e[2] = evs.__str__()
    #         print(evs)
    #     _save_history()
    #     print(_history)

    # if true, view full history (rather than latest 5 pokemon)
    def set_full(self, boolean):
        self.full = boolean

    def __str__(self):
        # print('>> history __str__')
        currentHistory = self.get_active_poke_history_arr()
        myStr = 'Checking history for current active pokemon: ' + str(_tracker.active) + '\n'
        if (len(currentHistory) > 0):
            elements = currentHistory
            if (len(currentHistory) > 5 and not self.full):
                elements = currentHistory[-5:]      # print latest 5 history
                myStr += '(' + str(len(currentHistory)-5) + ' other pokemon in history)\n.........\n'
            myStr += '\n'.join([
                str(date) + ' | '
                + ('#' + str(ele).zfill(3) if type(ele) is int else "Item") + ' | '
                + '{:^13}'.format((Pokemon.get_pokemon_by_id(ele).name) if type(ele) is int else ele) + ' | '
                + str(evs)
                for ele, date, evs in elements])
            return myStr + '\n'
        return 'History file is empty for active pokemon!'

class Tracker(object):

    def __init__(self, filename):
        self._active = None
        self.counter = 1
        self.filename = filename

    @classmethod
    def from_json(cls, filename):
        # print('\n\tfrom_json_tracker\n\t----------')
        tracker = cls(filename)
        try:
            fp = open(filename, 'r')
            data = json.load(fp)
            # pprint.pprint(data)
            for spec in data['pokemon']:
                pokemon = Pokemon.from_dict(spec)
                tracker.track(pokemon)
                if 'active' in data and int(data['active']) == pokemon.id:
                    tracker.active = pokemon
        except IOError:
            pass  # Ignore missing tracking file.
        return tracker

    @staticmethod
    def to_json(tracker, filename=None):
        # print('\n\tto_json\n\t----------')
        filename = tracker.filename if filename is None else filename
        fp = open(filename, 'w')
        data = {}
        if tracker.has_active():
            data['active'] = tracker.active.id
        data['pokemon'] = [pokemon.to_dict() for pokemon in tracker.pokemon.values()]
        # pprint.pprint(data)
        json.dump(data, fp)
        fp.close()

    pokemon = {}
    active = property(lambda self: self.get_active(), lambda self, pokemon: self.set_active(pokemon))

    def has_active(self):
        return self._active is not None

    def get_active(self):
        if self._active is None:
            raise NoActivePokemon()
        return self._active

    def set_active(self, pokemon):
        self._active = pokemon

    def get_pokemon(self, id):
        if id not in self.pokemon:
            raise NoTrackedPokemon(id)
        return self.pokemon[id]

    def unique_id(self):
        while self.counter in self.pokemon:
            self.counter += 1
        return self.counter

    def track(self, pokemon):
        self.pokemon[pokemon.id] = pokemon

    def untrack(self, pokemon):
        del self.pokemon[pokemon.id]
        pokemon.id = None
        if self._active is pokemon:
            self._active = None

    def get_tracked_pokemon(self):
        return self.pokemon

    def __str__(self):
        # print('>> tracker __str__')
        if len(self.pokemon):
            return '\n'.join([pokemon.listing(self._active) for pokemon in self.pokemon.values()])
        else:
            return '\nNo tracked Pokemon!'


class NoActivePokemon(Exception):
    """
    Raised when an operation that assumes the existence of an active Pokemon
    is carried out.
    """
    pass


class NoTrackedPokemon(Exception):
    """
    Raised when an id is requested from a Tracker but the Tracker does not
    have a Pokemon with the provided id.
    """
    def __init__(self, id):
        super(NoTrackedPokemon, self).__init__()
        self.id = id

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

_tracker = None
_history = None


def _save_tracker():
    if os.path.exists(_tracker.filename):
        copyfile(_tracker.filename,  _tracker.filename + '.bak')  # Create backup
    Tracker.to_json(_tracker)


def _save_history():
    if os.path.exists(_history.filename):
        copyfile(_history.filename,  _history.filename + '.bak')  # Create backup
    History.to_json(_history)


def _cmd_ev(args):
    print(pokedex.search(args.species))


def _cmd_track(args):
    species = pokedex.search(args.species)
    pokemon = Pokemon(id=_tracker.unique_id(), species=species, name=args.name, item=args.item, pokerus=args.pokerus)
    _tracker.track(pokemon)
    print(pokemon)
    _save_tracker()


def _cmd_active(args):
    if args.switch:
        _tracker.active = _tracker.get_pokemon(args.switch)
        _history.activePokeID = str(_tracker.active.id)
        _save_tracker()
        print('\nPokemon Swtiched!')
    print('\n' + _tracker.active.status())
    print(_history)


def _cmd_list(args):
    print(_tracker)


def _cmd_status(args):
    pokemon = _tracker.active
    if args.id is not None:
        pokemon = _tracker.get_pokemon(args.id)
    print('\n' + pokemon.status())


def _cmd_history(args):
    if args.clear:
        _history.clear_history()
        _save_history()
        return
    if args.add:
        _history.add_poke_to_history(pokedex.search(args.add).id)
        _save_history()
        return
    if args.addi:
        _history.add_item_to_history(args.addi)
        _save_history()
    if args.remove:
        _history.remove_poke_from_history(pokedex.search(args.remove).id)
        _save_history()
        return
    if args.full:
        _history.set_full(True)
    print()
    print(_history)


def _cmd_overview(args):
    print('\n' + _tracker.active.status())
    print(_history)


def _cmd_update(args):
    # do pokerus + items here
    pokemon = _tracker.active
    if args.id is not None:
        pokemon = _tracker.get_pokemon(args.id)
    if (args.item):
        print("adding item")
        pokemon.set_item(args.item)
        _history.add_item_to_history(args.item)
        _save_tracker()
        _save_history()
        

def _cmd_battle(args):
    species = pokedex.search(args.species)

    pokemon = _tracker.active
    if args.id is not None:
        pokemon = _tracker.get_pokemon(args.id)

    num = 1
    if args.number is not None:
        num = args.number

    if args.undo:
        undoEvs = pokemon.battle(species, num, args.undo)
        print("\nUndo Battle:\n----------\n" + str(species.name) + ' x' + str(num) + ' | ' + str(undoEvs) + ' (Evs)')
    else:
        gainedEvs = pokemon.battle(species, num)
        print("\nGained Evs:\n----------\n" + str(species.name) + ' x' + str(num) + ' | ' + str(gainedEvs) + ' (Evs)')

    for _ in range(0, num):
        if args.undo:
            _history.remove_poke_from_history(species.id)
        else:
            _history.add_poke_to_history(species.id, gainedEvs)
    
    print('\n' + str(pokemon.status()))
    print(_history)
    _save_tracker()
    _save_history()
    

def _cmd_clear(args):
    print('\nClearing data...')
    pokemon = _tracker.active
    if args.id is not None:
        pokemon = _tracker.get_pokemon(args.id)
    pokemon.clear_evs()
    pokemon.clear_item()
    print("\nPokemon data cleared")
    _history.clear_history()

    print('\n' + str(pokemon.status()))
    print(_history)
    _save_tracker()
    _save_history()


def _cmd_release(args):
    pokemon = _tracker.get_pokemon(args.id)
    _tracker.untrack(pokemon)
    print('No longer tracking %s' % pokemon)
    _save_tracker()


def _cmd_testing(args):
    # _history.recalculate_hisStory()
    # _tracker.active.set_item("Macho Brace")
    # _history.add_item_to_history("Macho Brace")
    # _save_tracker()
    # _save_history()
    pass


def _build_parser():
    parser = argparse.ArgumentParser(prog='ev', description='A small utility for keeping track of Effort Values while training Pokemon.')
    parser.add_argument('--infile', '-i', dest='filename', default=TRACKER_PATH, help=' Optional location of the file to save tracking information to. This defaults to %s in your home directory' % TRACKER_FILENAME)

    subparsers = parser.add_subparsers()

    ev_parser = subparsers.add_parser('ev', help='List Effort Values for a Pokemon')
    ev_parser.add_argument('species', help='Name or number of Pokemon species to search for')
    ev_parser.set_defaults(func=_cmd_ev)

    list_parser = subparsers.add_parser('list', help='List tracked Pokemon')
    list_parser.set_defaults(func=_cmd_list)

    track_parser = subparsers.add_parser('track', help='Add a Pokemon to track')
    track_parser.add_argument('species', help='Name of number of Pokemon species to track')
    track_parser.add_argument('--name', '-n', help='Nickname of Pokemon')
    track_parser.add_argument('--pokerus', '-p', action='store_true', default=False, help='Indicates the given Pokemon has Pokerus')
    track_parser.add_argument('--item', '-i')
    track_parser.set_defaults(func=_cmd_track)

    active_parser = subparsers.add_parser('active', help='List the active Pokemon')
    active_parser.add_argument('--switch', '-s', type=int, help='Switch the active Pokemon')
    active_parser.set_defaults(func=_cmd_active)

    status_parser = subparsers.add_parser('status', help='Show the status of the active Pokemon')
    status_parser.add_argument('--id', '-i', type=int)
    status_parser.set_defaults(func=_cmd_status)

    # currently history only works for 1 pokemon, not based on active (i.e. cant switch to different pokemon in the list and see battle history for that newly switched pokemon)
    # the optional args 'add' and 'remove' are not recommended to use; they are there for manual overriding & testing purposes - these methods will automatically be called when battling with a pokemon (and when a battle is undone)
    history_parser = subparsers.add_parser('history', help='Show the history of battles for the active Pokemon')
    history_parser.add_argument('--full', '-f', action='store_true', default=False, help='Print the full history of battled pokemon. By default, the history will only print the 5 most recent pokemon battled')
    history_parser.add_argument('--clear', '-c', action='store_true', default=False, help='DEV COMMAND (not recommended) Clear battle history for specific pokemon')
    history_parser.add_argument('--add', '-a', help='DEV COMMAND (not recommended) Choose specific pokemon to add to the battle history')
    history_parser.add_argument('--addi', '-ai', type=str, help='DEV COMMAND (not recommended) Choose specific item to add to the history')
    history_parser.add_argument('--remove', '-r', help='DEV COMMAND (not recommended) Choose specific pokemon to remove from the battle history (will remove the latest pokemon found)')
    history_parser.set_defaults(func=_cmd_history)

    update_parser = subparsers.add_parser('update', help='Update a tracked Pokemon\'s details')
    update_parser.add_argument('--id', '-i', type=int)
    update_parser.add_argument('--item', '-it', help='Name of item to give to the active Pokemon')
    update_parser.set_defaults(func=_cmd_update)

    overview_parser = subparsers.add_parser('overview', help='Summary of the active Pokemon\'s stats and battle history')
    overview_parser.set_defaults(func=_cmd_overview)

    battle_parser = subparsers.add_parser('battle', help='Record a battle for a tracked Pokemon')
    battle_parser.add_argument('species', help='Name or id of Pokemon species to battle')
    battle_parser.add_argument('--id', '-i', type=int, help='Choose specific pokemon - default is active')
    battle_parser.add_argument('--number', '-n', type=int, help='Number of times you want to battle')
    battle_parser.add_argument('--undo', '-u', action='store_true', default=False, help='Undo battle with a specific pokemon (subtract EVs)')
    battle_parser.set_defaults(func=_cmd_battle)

    clear_parser = subparsers.add_parser('clear', help='Clear a Pokemon\'s details (EVs, History, etc.)')
    clear_parser.add_argument('--id', '-i', type=int, help='Choose specific pokemon - default is active')
    clear_parser.set_defaults(func=_cmd_clear)

    release_parser = subparsers.add_parser('release', help='Stop tracking a Pokemon')
    release_parser.add_argument('id', type=int)
    release_parser.set_defaults(func=_cmd_release)

    testing_parser = subparsers.add_parser('testing', help='Purely for debugging - remove later')
    testing_parser.set_defaults(func=_cmd_testing)

    return parser


if __name__ == '__main__':
    clear_console()
    try:
        args = _build_parser().parse_args()
        _tracker = Tracker.from_json(args.filename + 'tracker')
        _history = History.from_json(args.filename + 'history')
        args.func(args)
    except pokedex.NoSuchSpecies as e:
        print("No match found for '%s'." % e.identifier)
        if isinstance(e, pokedex.AmbiguousSpecies):
            print("Did you mean:")
            for match in e.matches:
                print("  %s" % match)
    except NoActivePokemon:
        print("No tracked Pokemon is marked as active.")
        print("Set an active pokemon using the 'active --switch' command.")
    except NoTrackedPokemon as e:
        print("No tracked Pokemon with id '%d' was found." % e.id)

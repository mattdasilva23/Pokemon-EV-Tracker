# Pokémon EV Tracker

A small command line utility for keeping track of Effort Values while training
Pokemon.

## Usage examples

To query the database for a Pokemon species and their EV yield, use the `ev`
command. This takes either the Pokedex number of a species or the species 
name. If the name is provided but not found, a fuzzy search is done to return
possible matches:
	
	ev ev 600
	>#600 Klang      +2 Defense
	
	ev ev charizard
	>#006 Charizard  +3 Special Attack
	
	ev ev lia
	> No match found for 'lia'.
	> Did you mean:
	>   #484 Palkia     +3 Special Attack
	>   #281 Kirlia     +2 Special Attack
	>   #207 Gligar     +1 Defense

To see which Pokemon you are currently tracking use the `list` command:

	ev list
	> No tracked Pokemon

To track a new Pokemon use the `track` command. The integer value is the id
of the newly tracked Pokemon:

	ev track Magikarp --name=Ultrados --pokerus
	> 1 Ultrados (Magikarp)

You can also track a new Pokemon by it's Pokedex number.
	
	ev track 610
	> 2 Axew

The tracker always has an active Pokemon that other commands will operate on
by default. You can see the current Pokemon using the `active` command, or the
`list` command and looking for the `*` symbol.
	
	ev active
	> No tracked Pokemon is marked as active.
	> Set an active pokemon using the 'active --switch' command.
	
	ev active --switch=2
	> 2 Axew
	
	ev list
	>   1 Ultrados (Magikarp)
	>   2 Axew

You can switch the active Pokemon using the `active` command:

	ev active --switch=1
	> 1 Ultrados (Magikarp)

You can get the full status of the current Pokemon using the `status` command:

	ev status
	> 1 Ultrados (Magikarp)
	> Pokerus
	> No EVs

To record battles and update EV values, use the `battle` command:

	ev battle Lillipup
	> Battled #506 Lillipup   +1 Attack
	> 1 Ultrados - +2 Attack

You can also record multiple battles using the `-n` or `--number` option of 
the `battle` command:

	ev battle Lillipup -n3
	> Battled 3 × #506 Lillipup   +1 Attack
	> 1 Ultrados (Magikarp) - +6 Attack
	
	ev status
	> 1 Ultrados (Magikarp)
	> Pokerus
	> Attack: 8

To update the status of the current Pokemon, use the `update` command:
	
	ev update --item="Power Bracer"
	> 1 Ultrados (Magikarp)

As with the other commands, you can refer to a Pokemon species by number:
	
	ev battle Trubish
	> No match found for 'Trubish'
	> Did you mean:
	>   #568 Trubbish   +1 Speed
	
	ev battle 568
	> Battled #568 Trubbish  +1 Speed
	> 1 Ultrados (Magikarp) - +8 Attack, +2 Speed

To stop tracking a Pokemon, use the `release` command:
	
	ev release 2
	> Stopped tracking Axew

## EV Calculations

I'm still new to Pokemon EV training, but Effort Values for each battle are
calculated as such:

	ev[stat] = max(ev[stat] + (pokemon.evs[stat] + item.evs[stat]) * pokerus, 255)

The total EVs for a Pokemon are also capped at 510.

## Storage

Currently the tracker saves after every operation to a file your User 
directory called `.ev-tracker`. This will be a different location depending on 
your operating system. If you would like to use a custom tracker file 
location, set the `--infile` option before the sub-command. See `ev --help`
for more information.

The tracker file is stored as JSON and is fairly trivial to include in other
projects, or directly using Javascript.

## Issues, Contact etc.

`ev-tracker` was hacked together very quickly to provide a fairly minimal set
of functionality for my own personal needs. If you use this and have any 
issues then please let me know.

If you'd like to contribute or provide feedback, then 
[github](https://github.com/mathewbyrne/ev-tracker) is the best place to do 
that.

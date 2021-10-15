import csv
import sys
from dataclasses import dataclass
from io import StringIO
from typing import List

import requests

from scryfall.client import ScryfallClient
from scryfall.models import ScryfallCard


@dataclass
class InspectionResults:
    cube_id: str
    set_ids: List[str]
    duplicates: List[str]
    not_present: List[ScryfallCard]


BASICS = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest'}


def is_basic(card_name: str) -> bool:
    return card_name in BASICS


def inspect_cubecobra_set_cube(cube_id: str, set_ids: List[str]) -> InspectionResults:
    result = requests.get(f'https://cubecobra.com/cube/download/plaintext/{cube_id}')
    if result.status_code != 200:
        raise RuntimeError()
    names = result.text.splitlines()
    dedup_names = set()
    duplicates = []
    for name in names:
        if name in dedup_names:
            duplicates.append(name)
        else:
            dedup_names.add(name)
    client = ScryfallClient()
    missing = []
    for set_id in set_ids:
        cards = client.get_cards_for_set_code(set_id)
        for card in cards:
            card_name = card.name.split(' // ')[0]
            if card_name not in dedup_names and not is_basic(card_name):
                missing.append(card)
    return InspectionResults(
        cube_id=cube_id,
        set_ids=set_ids,
        duplicates=duplicates,
        not_present=missing,
    )


def describe_results(results: InspectionResults) -> str:
    sets_formatted = ', '.join(results.set_ids)
    lines = [f'Inspection for {results.cube_id}, {sets_formatted}']

    if len(results.duplicates) == 0:
        lines.append('No duplicates found')
    else:
        lines.append('Duplicates:')
        for dup in results.duplicates:
            lines.append(f'  {dup}')

    if len(results.not_present) == 0:
        lines.append('All cards in set exist in cube')
    else:
        lines.append('Not in cube:')
        for card in results.not_present:
            lines.append(f'  {card.name}')

    return '\n'.join(lines)


def cubecobra_to_untap(cube_id: str) -> str:
    result = requests.get(f'https://cubecobra.com/cube/download/csv/{cube_id}')
    if result.status_code != 200:
        raise RuntimeError()
    f = StringIO(result.text)
    reader = csv.DictReader(f, delimiter=',')
    lines = []
    for row in reader:
        name = row['Name']
        set_code = row['Set'].lower()
        maybeboard = row['Maybeboard'].lower() == 'true'
        if not maybeboard:
            lines.append(f'1 {name} ({set_code})')

    return '\n'.join(lines)


if __name__ == '__main__':
    try:
        results = inspect_cubecobra_set_cube(sys.argv[1], sys.argv[2].split(','))
        output = describe_results(results)
        print(output)
    except IndexError:
        print('This script requires two arguments: cube_id and set_id')

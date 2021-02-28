import random
import uuid
from typing import Optional, List

from django.contrib.auth.models import User
from django.db import models

from cards.models import Card, Printing
from cubes.models import Cube


class Draft(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    current_round = models.IntegerField(default=0)
    max_players = models.IntegerField(default=8)
    creator = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL)
    cube = models.ForeignKey(Cube, null=True, default=None, on_delete=models.SET_NULL)

    @property
    def is_started(self):
        return self.current_round > 0

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.shortcuts import reverse
        return reverse('draft-detail', args=[self.uuid])

    def join(self, user: User) -> Optional['DraftEntry']:
        try:
            return self.entries.get(player_id=user.id)
        except DraftEntry.DoesNotExist:
            entries_count = self.entries.count()
            if entries_count >= self.max_players:
                return None
            return DraftEntry.objects.create(draft=self, player=user)

    def begin(self, add_bots=True) -> bool:
        if self.entries.count() == 0 or self.current_round != 0:
            return False
        players: List[Optional[User]] = []
        for entry in self.entries.all():
            players.append(entry.player)
        if add_bots:
            while len(players) < self.max_players:
                players.append(None)
        random.shuffle(players)
        for seat, player in enumerate(players):
            DraftSeat.objects.create(draft=self, user=player, position=seat)
        self.entries.all().delete()

        if self.cube is not None:
            packs_needed = self.cube.default_pack_count * len(players)
            packs = self.cube.generate_packs(pack_count=packs_needed)
            for seat in self.seats.all():
                for i in range(1, self.cube.default_pack_count + 1):
                    card_ids = packs.pop()
                    pack = DraftPack.objects.create(draft=self, round_number=i, seat_number=seat.position)
                    for card_id in card_ids:
                        DraftCard.objects.create(pack=pack, card_uuid=card_id)

        self.current_round = 1
        self.save()
        return True

    def is_user_in_draft(self, user: User) -> bool:
        if self.is_started:
            for seat in self.seats.all():
                if user == seat.user:
                    return True
        else:
            for entry in self.entries.all():
                if user == entry.player:
                    return True
        return False

    def get_seat_for_user(self, user: User) -> Optional['DraftSeat']:
        try:
            return self.seats.get(user=user)
        except DraftSeat.DoesNotExist:
            return None

    def heartbeat(self):
        self.make_all_bot_selections()
        self.check_end_of_round()

    def check_end_of_round(self):
        for pack in self.packs.filter(round_number=self.current_round):
            if pack.cards.count() > 0:
                return False
        self.current_round += 1
        self.save()
        return True

    def make_all_bot_selections(self):
        seats = self.seats.filter(user=None)
        # Odd rounds pass left (inc)
        if self.current_round % 2 == 1:
            seats = seats.order_by('position')
        else:
            seats = seats.order_by('-position')
        all_packs = self.packs.prefetch_related('cards').all()
        for seat in seats.all():
            filtered_packs = [pack for pack in all_packs if pack.seat_number == seat.position]
            for pack in filtered_packs:
                ids = list(pack.cards.values_list('uuid', flat=True))
                if len(ids) > 0:
                    card_id = random.choice(ids)
                    if not seat.make_selection(card_id=card_id, current_pack=pack):
                        raise Exception()


class DraftEntry(models.Model):
    """
    Represents a player's entry in a draft that has not yet started
    """
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name='entries')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')

    def __str__(self):
        return f'Entry for {self.player.username} in {self.draft}'


class DraftSeat(models.Model):
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name='seats')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    position = models.IntegerField()

    def short_display_name(self):
        if self.user is None:
            return 'Bot'
        else:
            return self.user.username

    def __str__(self):
        if self.user is None:
            seat_name = 'Bot'
        else:
            seat_name = self.user.username
        return f'Seat #{self.position} of {self.draft}: {seat_name}'

    def get_waiting_packs(self):
        return self.draft.packs.filter(
            seat_number=self.position,
            round_number=self.draft.current_round
        ).order_by('pick_number')

    def get_pack_count(self) -> int:
        return self.get_waiting_packs().count()

    def get_current_pack(self) -> Optional['DraftPack']:
        packs = self.get_waiting_packs()
        if packs.count() == 0:
            return None
        return packs[0]

    def make_selection(self, card_id: str, current_pack: Optional['DraftPack'] = None) -> bool:
        if current_pack is None:
            current_pack = self.get_current_pack()
        if current_pack is None:
            return False
        try:
            selected_card = current_pack.cards.get(uuid=card_id)
        except DraftCard.DoesNotExist:
            return False

        # Take the card out of its pack and place is in this seat's pool
        selected_card.pack = None
        selected_card.seat = self

        # Now, move the pack and increment the pick number
        if self.draft.current_round % 2 == 1:  # Odd rounds pass left (inc)
            current_pack.seat_number = (current_pack.seat_number + 1) % self.draft.max_players
        else:  # Even rounds pass right (decrement seat number)
            current_pack.seat_number = (current_pack.seat_number - 1) % self.draft.max_players
        current_pack.pick_number += 1

        selected_card.save()
        current_pack.save()

        return True


class DraftPack(models.Model):
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name='packs')
    round_number = models.IntegerField()
    pick_number = models.IntegerField(default=1)
    seat_number = models.IntegerField()


class DraftCard(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    pack = models.ForeignKey(DraftPack, null=True, on_delete=models.CASCADE, related_name='cards')
    seat = models.ForeignKey(DraftSeat, null=True, default=None, on_delete=models.CASCADE, related_name='picks')
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    printing = models.ForeignKey(Printing, on_delete=models.SET_NULL, null=True)

    card_name = models.CharField(max_length=20, null=True, default=None)
    card_uuid = models.UUIDField(null=True, default=None)

    def get_image_url(self):
        if self.card is None:
            if self.card_uuid is None:
                return None
            self.card = Card.objects.get(id=self.card_uuid)
            self.save()
        if self.printing is None:
            self.printing = self.card.printings.first()
            self.save()
        return self.printing.image_url

    def display_name(self):
        if self.printing is not None:
            return self.printing.card.name
        if self.card is not None:
            return self.card.name
        if self.card_name is not None:
            return self.card_name
        if self.card_uuid is not None:
            self.card = Card.objects.get(id=self.card_uuid)
            self.printing = self.card.printings.first()
            self.save()
            return self.card.name
        return 'None'

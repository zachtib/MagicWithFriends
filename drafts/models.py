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
        self.seats.all().delete()
        for seat, player in enumerate(players):
            DraftSeat.objects.create(draft=self, user=player, position=seat)
        self.entries.all().delete()

        if self.cube is not None:
            packs_needed = self.cube.default_pack_count * len(players)
            packs = self.cube.generate_packs(pack_count=packs_needed)
            for seat in self.seats.all():
                round_no: int
                for round_no in range(1, self.cube.default_pack_count + 1):
                    card_ids = packs.pop()
                    pack = Pack.objects.create(seat=seat, round=round_no)
                    entries = [PackEntry(printing_id=printing_id, pack=pack) for printing_id in card_ids]
                    pack.entries.bulk_create(entries)

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
        seats_with_bots = self.seats.prefetch_related('packs__entries__printing').filter(user=None)
        for _ in range(seats_with_bots.count()):
            for seat in seats_with_bots.all():
                pack: Pack
                for pack in seat.packs.all():
                    ids = list(pack.entries.values_list('id', flat=True))
                    if len(ids) > 0:
                        pick = random.choice(ids)
                        if not seat.make_selection(pick=pick, current_pack=pack):
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
        current_round = self.draft.current_round
        return self.packs.filter(round=current_round).order_by('pick')

    def get_pack_count(self) -> int:
        return self.get_waiting_packs().count()

    def get_current_pack(self) -> Optional['Pack']:
        packs = self.get_waiting_packs()
        if packs.count() == 0:
            return None
        return packs[0]

    def make_selection(self, pick: int, current_pack: Optional['Pack'] = None) -> bool:
        if current_pack is None:
            current_pack = self.get_current_pack()
            if current_pack is None:
                return False

        try:
            current_pack: Pack = current_pack
            selected_card: PackEntry = current_pack.entries.get(id=pick)
        except PackEntry.DoesNotExist:
            return False

        # Take the card out of its pack and place is in this seat's pool
        self.picks.create(printing=selected_card.printing)
        selected_card.delete()
        # Now, move the pack and increment the pick number
        if self.draft.current_round % 2 == 1:  # Odd rounds pass left (inc)
            current_pack.seat = self.seat_to_the_left()
        else:  # Even rounds pass right (decrement seat number)
            current_pack.seat = self.seat_to_the_right()
        current_pack.pick = current_pack.pick + 1
        # Save any relevant models
        current_pack.save()

        return True

    def seat_to_the_left(self) -> 'DraftSeat':
        position = (self.position + 1) % self.draft.max_players
        return self.draft.seats.get(position=position)

    def seat_to_the_right(self) -> 'DraftSeat':
        position = (self.position - 1) % self.draft.max_players
        return self.draft.seats.get(position=position)


class Pack(models.Model):
    seat = models.ForeignKey(DraftSeat, on_delete=models.CASCADE, related_name='packs')
    round = models.IntegerField()
    pick = models.IntegerField(default=1)

    @property
    def draft(self) -> Draft:
        return self.seat.draft


class PackEntry(models.Model):
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name='entries')
    printing = models.ForeignKey(Printing, on_delete=models.CASCADE)

    def get_image_url(self):
        return self.image_url

    def display_name(self):
        return self.name

    @property
    def name(self) -> str:
        return self.printing.card.name

    @property
    def image_url(self) -> str:
        return self.printing.image_url

    @property
    def card(self) -> Card:
        """
        Convenience getter for self.printing.card
        :return: [Card] instance
        """
        return self.printing.card


class DraftPick(models.Model):
    seat = models.ForeignKey(DraftSeat, on_delete=models.CASCADE, related_name='picks')
    printing = models.ForeignKey(Printing, on_delete=models.CASCADE)

    @property
    def card_name(self) -> str:
        return self.printing.card.name

    @property
    def image_url(self) -> str:
        return self.printing.image_url

    @property
    def card(self) -> Card:
        """
        Convenience getter for self.printing.card
        :return: [Card] instance
        """
        return self.printing.card

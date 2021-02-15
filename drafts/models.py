import uuid
from random import shuffle
from typing import Optional, List

from django.contrib.auth.models import User
from django.db import models

from cubes.models import Cube


class Draft(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    current_round = models.IntegerField(default=0)
    max_players = models.IntegerField(default=8)
    cube = models.ForeignKey(Cube, null=True, default=None, on_delete=models.SET_NULL)

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
        shuffle(players)
        for seat, player in enumerate(players):
            DraftSeat.objects.create(draft=self, user=player, position=seat)
        self.entries.all().delete()
        if self.cube is not None:
            packs = self.cube.generate_packs()
            for seat in self.seats.all():
                for i in range(1, self.cube.default_pack_count + 1):
                    pack = DraftPack.objects.create(draft=self, round_number=i, seat_number=seat.position)

        self.current_round = 1
        return True

    def is_user_in_draft(self, user: User) -> bool:
        for seat in self.seats.all():
            if user == seat.user:
                return True
        return False

    def get_seat_for_user(self, user: User) -> Optional['DraftSeat']:
        try:
            return self.seats.get(user=user)
        except DraftSeat.DoesNotExist:
            return None


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

    def __str__(self):
        if self.user is None:
            seat_name = 'Bot'
        else:
            seat_name = self.user.username
        return f'Seat #{self.position} of {self.draft}: {seat_name}'

    def get_pack_count(self) -> int:
        return self.draft.packs.filter(seat_number=self.position).count()

    def get_current_pack(self) -> Optional['DraftPack']:
        packs = self.draft.packs.filter(seat_number=self.position).order_by('pick_number')
        if packs.count() == 0:
            return None
        return packs[0]

    def make_selection(self, card_id: str) -> bool:
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
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4)
    pack = models.ForeignKey(DraftPack, null=True, on_delete=models.CASCADE, related_name='cards')
    seat = models.ForeignKey(DraftSeat, null=True, default=None, on_delete=models.CASCADE, related_name='picks')
    card_name = models.CharField(max_length=20)

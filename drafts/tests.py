from django.contrib.auth.models import User
from django.test import TestCase

from drafts.models import Draft, DraftSeat, DraftEntry, DraftPack, DraftCard


class DraftCreationTestCase(TestCase):
    def setUp(self) -> None:
        self.draft: Draft = Draft.objects.create(name="Test Draft")
        self.user: User = User.objects.create_user("testuser")

    def test_draft_url(self):
        url = self.draft.get_absolute_url()
        self.assertEqual(f'/drafts/{self.draft.uuid}/', url)

    def test_joining_draft(self):
        entry: DraftEntry = self.draft.join(self.user)
        self.assertEqual(entry.draft, self.draft)
        self.assertEqual(entry.player, self.user)

    def test_entry_string(self):
        entry: DraftEntry = self.draft.join(self.user)
        string = str(entry)
        self.assertEqual('Entry for testuser in Test Draft', string)

    def test_attempting_to_join_twice_does_not_create_extra_entry(self):
        entry_a: DraftEntry = self.draft.join(self.user)
        entry_b: DraftEntry = self.draft.join(self.user)
        self.assertEqual(entry_a.id, entry_b.id)

    def test_beginning_a_draft(self):
        self.draft.join(self.user)
        self.draft.begin()
        self.assertEqual(self.draft.max_players, self.draft.seats.count())

    def test_beginning_a_draft_sets_round_to_one(self):
        self.draft.join(self.user)
        self.draft.begin()
        self.assertEqual(1, self.draft.current_round)

    def test_getting_a_users_seat(self):
        self.draft.join(self.user)
        self.draft.begin()
        seat: DraftSeat = self.draft.get_seat_for_user(self.user)
        self.assertEqual(seat.user, self.user)

    def test_full_draft_disallows_joining(self):
        self.draft.join(self.user)
        user2: User = User.objects.create_user("testuser2")
        self.draft.join(user2)
        self.draft.max_players = 2
        user3: User = User.objects.create_user("testuser3")
        entry = self.draft.join(user3)
        self.assertIsNone(entry)

    def test_rejoining_full_draft_returns_entry(self):
        entry1 = self.draft.join(self.user)
        user2: User = User.objects.create_user("testuser2")
        self.draft.join(user2)
        self.draft.max_players = 2
        entry2 = self.draft.join(self.user)
        self.assertEqual(entry1, entry2)

    def test_draft_will_not_begin_with_no_entrants(self):
        started = self.draft.begin()
        self.assertEqual(False, started)
        seats = self.draft.seats.count()
        self.assertEqual(0, seats)

    def test_user_is_in_draft(self):
        self.draft.join(self.user)
        self.draft.begin()
        in_draft = self.draft.is_user_in_draft(self.user)
        self.assertTrue(in_draft)

    def test_user_is_not_in_draft(self):
        self.draft.join(self.user)
        self.draft.begin()
        user2: User = User.objects.create_user("testuser2")
        in_draft = self.draft.is_user_in_draft(user2)
        self.assertFalse(in_draft)

    def test_getting_seat_for_nonparticipant_returns_none(self):
        self.draft.join(self.user)
        self.draft.begin()
        user2: User = User.objects.create_user("testuser2")
        seat = self.draft.get_seat_for_user(user2)
        self.assertIsNone(seat)

    def test_beginning_a_draft_deletes_the_entries(self):
        self.draft.join(self.user)
        begun = self.draft.begin()
        self.assertTrue(begun)
        self.assertEqual(0, self.draft.entries.count())


class DraftProgressTestCase(TestCase):
    def setUp(self) -> None:
        self.draft: Draft = Draft.objects.create(name="Test Draft", max_players=4, current_round=1)

        self.user_a: User = User.objects.create_user("user_a")
        self.user_b: User = User.objects.create_user("user_b")
        self.user_c: User = User.objects.create_user("user_c")
        self.user_d: User = User.objects.create_user("user_d")

        self.seat_a: DraftSeat = DraftSeat.objects.create(draft=self.draft, user=self.user_a, position=0)
        self.seat_b: DraftSeat = DraftSeat.objects.create(draft=self.draft, user=self.user_b, position=1)
        self.seat_c: DraftSeat = DraftSeat.objects.create(draft=self.draft, user=self.user_c, position=2)
        self.seat_d: DraftSeat = DraftSeat.objects.create(draft=self.draft, user=self.user_d, position=3)

        self.pack_a: DraftPack = DraftPack.objects.create(draft=self.draft,
                                                          round_number=1,
                                                          pick_number=1,
                                                          seat_number=0)
        self.pack_a.cards.bulk_create([
            DraftCard(card_name="Lorem Ipsum", pack_id=self.pack_a.id),
            DraftCard(card_name="Dolor", pack_id=self.pack_a.id),
            DraftCard(card_name="Sit Amet", pack_id=self.pack_a.id),
        ])

    def test_getting_pack(self):
        pack = self.seat_a.get_current_pack()
        self.assertEqual(self.pack_a, pack)

    def test_seat_str(self):
        string = str(self.seat_a)
        self.assertEqual('Seat #0 of Test Draft: user_a', string)

    def test_seat_str_bot(self):
        seat = DraftSeat.objects.create(draft=self.draft, user=None, position=0)
        string = str(seat)
        self.assertEqual('Seat #0 of Test Draft: Bot', string)

    def test_getting_pack_at_a_seat_with_more_than_one(self):
        DraftPack.objects.bulk_create([
            DraftPack(draft=self.draft, round_number=1, seat_number=0, pick_number=2),
            DraftPack(draft=self.draft, round_number=1, seat_number=0, pick_number=3),
            DraftPack(draft=self.draft, round_number=1, seat_number=0, pick_number=4),
        ])
        pack = self.seat_a.get_current_pack()
        self.assertEqual(self.pack_a, pack)

    def test_counting_packs_at_a_seat(self):
        count = self.seat_a.get_pack_count()
        self.assertEqual(1, count)

    def test_counting_packs_at_a_seat_with_more_than_one(self):
        DraftPack.objects.bulk_create([
            DraftPack(draft=self.draft, round_number=1, seat_number=0, pick_number=2),
            DraftPack(draft=self.draft, round_number=1, seat_number=0, pick_number=3),
            DraftPack(draft=self.draft, round_number=1, seat_number=0, pick_number=4),
        ])
        count = self.seat_a.get_pack_count()
        self.assertEqual(4, count)

    def test_counting_packs_at_a_seat_with_none(self):
        self.pack_a.seat_number = 1
        self.pack_a.save()
        count = self.seat_a.get_pack_count()
        self.assertEqual(0, count)

    def test_getting_pack_when_none_at_seat(self):
        self.pack_a.seat_number = 1
        self.pack_a.save()
        pack = self.seat_a.get_current_pack()
        self.assertIsNone(pack)

    def test_making_a_selection(self):
        pack_id = self.pack_a.id
        card_id = self.pack_a.cards.get(card_name='Dolor').uuid
        result = self.seat_a.make_selection(card_id)
        self.assertTrue(result)

        with self.assertRaises(DraftPack.DoesNotExist):
            DraftPack.objects.get(id=pack_id, seat_number=self.seat_a.position)

        picks_count = self.seat_a.picks.count()
        self.assertEqual(1, picks_count)
        pick: DraftCard = self.seat_a.picks.all()[0]
        self.assertEqual(card_id, pick.uuid)

        pack = DraftPack.objects.get(id=pack_id)
        self.assertEqual(1, pack.seat_number)
        self.assertEqual(2, pack.pick_number)

    def test_making_a_selection_when_no_pack_at_seat(self):
        self.pack_a.seat_number = 1
        self.pack_a.save()
        card_id = DraftCard.objects.get(card_name='Dolor').uuid
        result = self.seat_a.make_selection(card_id)
        self.assertFalse(result)

    def test_making_invalid_selection(self):
        arbitrary_id = 'cc65092b-385a-494c-a00e-611d6c794f88'
        result = self.seat_a.make_selection(arbitrary_id)
        self.assertFalse(result)

    def test_making_a_selection_in_even_round_passes_right(self):
        self.draft.current_round = 2
        pack_id = self.pack_a.id
        card_id = self.pack_a.cards.get(card_name='Dolor').uuid
        self.seat_a.make_selection(card_id)
        pack = DraftPack.objects.get(id=pack_id)
        self.assertEqual(3, pack.seat_number)

    def test_deleting_a_started_draft(self):
        self.draft.begin()
        self.draft.delete()

        self.assertEqual(0, DraftPack.objects.count())
        self.assertEqual(0, DraftCard.objects.count())
        self.assertEqual(0, DraftSeat.objects.count())
        self.assertEqual(0, DraftEntry.objects.count())

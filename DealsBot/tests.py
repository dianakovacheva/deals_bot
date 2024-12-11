# import os.path
# import pathlib
# import unittest
#
# from DealsBot.models import UserSentDeal, Profile, BotUser
# from DealsBot.bot_functions.functions import filter_out_user_sent_deals
#
# from selenium import webdriver
#
#
# # Create your tests here.
#
#
# # def file_uri(filename):
# #     return pathlib.Path(os.path.abspath(filename)).as_uri()
# #
# #
# # driver = webdriver.Firefox()
#
#
# class FilterOutUserSentDealsTest(unittest.TestCase):
#
#     def setUp(self):
#         # Mock data setup
#         self.user1 = BotUser.objects.create(telegram_user_id=1, telegram_username="User 1", telegram_user_first_name="User 1", telegram_user_last_name="User 1", telegram_chat_id=1)
#         self.user2 = BotUser.objects.create(telegram_user_id=2, telegram_username="User 2", telegram_user_first_name="User 2", telegram_user_last_name="User 2", telegram_chat_id=2)
#
#         # Deals
#         self.deal1 = {"id": 1, "title": "Deal 1"}
#         self.deal2 = {"id": 2, "title": "Deal 2"}
#         self.deal3 = {"id": 3, "title": "Deal 3"}
#
#         # UserSentDeal to mark deals as sent
#         UserSentDeal.objects.create(sent_deal=self.deal1, bot_user=self.user1)
#         UserSentDeal.objects.create(sent_deal=self.deal2, bot_user=self.user2)
#
#         # Input data
#         self.unfiltered_list = [
#             {
#                 "dealSubscriptionId": 101,
#                 "userId": self.user1.id,
#                 "results": [self.deal1, self.deal2]
#             },
#             {
#                 "dealSubscriptionId": 102,
#                 "userId": self.user2.id,
#                 "results": [self.deal2, self.deal3]
#             },
#         ]
#
#     def test_filter_out_user_sent_deals(self):
#         # Expected output
#         expected_output = [
#             {
#                 "dealSubscriptionId": 101,
#                 "userId": self.user1.id,
#                 "results": [self.deal2]
#             },
#             {
#                 "dealSubscriptionId": 102,
#                 "userId": self.user2.id,
#                 "results": [self.deal3]
#             },
#         ]
#
#         # Function call
#         result = filter_out_user_sent_deals(self.unfiltered_list)
#
#         # Assert
#         self.assertEqual(result, expected_output)

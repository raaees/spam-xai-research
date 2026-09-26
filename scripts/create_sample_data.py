#!/usr/bin/env python3
"""Generate sample Cresci-2017-like data for testing Phase 1."""

import csv
from pathlib import Path

# Create directories
raw_dir = Path("data/raw/cresci2017")
raw_dir.mkdir(parents=True, exist_ok=True)

# Sample genuine accounts
genuine_data = [
    {"user_id": "123456", "screen_name": "user_real_1", "followers_count": "5000", "statuses_count": "2000", 
     "text": "just finished my morning coffee", "created_at": "2015-06-15", "verified": "False"},
    {"user_id": "123457", "screen_name": "user_real_2", "followers_count": "3000", "statuses_count": "1500",
     "text": "beautiful sunset today", "created_at": "2015-06-16", "verified": "False"},
    {"user_id": "123458", "screen_name": "journalist_1", "followers_count": "15000", "statuses_count": "5000",
     "text": "breaking news from the field", "created_at": "2015-06-17", "verified": "True"},
]

# Sample traditional spambots
spam_trad_data = [
    {"user_id": "999001", "screen_name": "spam_bot_1", "followers_count": "100", "statuses_count": "50000",
     "text": "BUY NOW!!! Click here for free money http://bit.ly/123456", "created_at": "2015-06-20", "verified": "False"},
    {"user_id": "999002", "screen_name": "spam_bot_2", "followers_count": "50", "statuses_count": "100000",
     "text": "LIKE AND FOLLOW FOR PRIZES", "created_at": "2015-06-21", "verified": "False"},
]

# Sample social spambots
spam_social_data = [
    {"user_id": "888001", "screen_name": "social_spam_1", "followers_count": "200", "statuses_count": "30000",
     "text": "RT @brand1 amazing product check it out now", "created_at": "2015-06-25", "verified": "False"},
    {"user_id": "888002", "screen_name": "social_spam_2", "followers_count": "150", "statuses_count": "25000",
     "text": "RT @celebrity you are awesome", "created_at": "2015-06-26", "verified": "False"},
]

# Sample fake followers
fake_followers_data = [
    {"user_id": "777001", "screen_name": "fake_acc_1", "followers_count": "0", "statuses_count": "1",
     "text": "", "created_at": "2015-06-30", "verified": "False"},
    {"user_id": "777002", "screen_name": "fake_acc_2", "followers_count": "0", "statuses_count": "0",
     "text": "", "created_at": "2015-07-01", "verified": "False"},
]

# Write genuine accounts
genuine_dir = raw_dir / "genuine_accounts"
genuine_dir.mkdir(exist_ok=True)

with (genuine_dir / "users.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=genuine_data[0].keys())
    writer.writeheader()
    writer.writerows(genuine_data)

print("✓ Created: data/raw/cresci2017/genuine_accounts/users.csv")

# Write traditional spambots
trad_spam_dir = raw_dir / "traditional_spambots_1"
trad_spam_dir.mkdir(exist_ok=True)

with (trad_spam_dir / "users.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=spam_trad_data[0].keys())
    writer.writeheader()
    writer.writerows(spam_trad_data)

print("✓ Created: data/raw/cresci2017/traditional_spambots_1/users.csv")

# Write social spambots
social_spam_dir = raw_dir / "social_spambots_1"
social_spam_dir.mkdir(exist_ok=True)

with (social_spam_dir / "users.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=spam_social_data[0].keys())
    writer.writeheader()
    writer.writerows(spam_social_data)

print("✓ Created: data/raw/cresci2017/social_spambots_1/users.csv")

# Write fake followers
fake_dir = raw_dir / "fake_followers"
fake_dir.mkdir(exist_ok=True)

with (fake_dir / "users.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fake_followers_data[0].keys())
    writer.writeheader()
    writer.writerows(fake_followers_data)

print("✓ Created: data/raw/cresci2017/fake_followers/users.csv")

print("\nSample data created successfully!")
print(f"Total accounts: {len(genuine_data) + len(spam_trad_data) + len(spam_social_data) + len(fake_followers_data)}")
print("  - Genuine: 3")
print("  - Traditional spambots: 2")
print("  - Social spambots: 2")
print("  - Fake followers: 2 (will be excluded)")

#!/usr/bin/env python3
"""
Create Test Wearable Data for VitaNexus Platform
Generates realistic daily activity metrics for test members
"""

import sys
sys.path.append('/Users/somtonweke/Inversion Health/Vita')

from sqlalchemy import text
from datetime import datetime, date, timedelta
import uuid
import random

from api.database import SessionLocal

def generate_wearable_data():
    """Generate 30 days of wearable data for each test member"""

    db = SessionLocal()

    # Get all test members
    result = db.execute(
        text("SELECT member_id, external_member_id, first_name, last_name FROM members ORDER BY external_member_id")
    )
    members = result.fetchall()

    print("=" * 80)
    print("CREATING WEARABLE DATA FOR VITANEXUS TEST MEMBERS")
    print("=" * 80)
    print()

    # Define activity profiles for different member types
    activity_profiles = {
        "M100001": {  # Sarah Johnson - Very active
            "steps_range": (8000, 12000),
            "sleep_hours_range": (7, 8.5),
            "hr_range": (65, 75),
            "active_minutes_range": (45, 70)
        },
        "M100002": {  # Michael Chen - Low activity
            "steps_range": (3000, 6000),
            "sleep_hours_range": (5.5, 7),
            "hr_range": (75, 85),
            "active_minutes_range": (10, 25)
        },
        "M100003": {  # Emily Rodriguez - Very active
            "steps_range": (9000, 13000),
            "sleep_hours_range": (7.5, 9),
            "hr_range": (62, 72),
            "active_minutes_range": (50, 80)
        },
        "M100004": {  # David Williams - Sedentary
            "steps_range": (2000, 5000),
            "sleep_hours_range": (5, 6.5),
            "hr_range": (72, 82),
            "active_minutes_range": (5, 20)
        },
        "M100005": {  # Jessica Martinez - Moderate activity
            "steps_range": (6000, 9000),
            "sleep_hours_range": (6.5, 8),
            "hr_range": (68, 78),
            "active_minutes_range": (30, 50)
        }
    }

    total_records = 0

    for member in members:
        member_id = str(member[0])
        external_id = member[1]
        name = f"{member[2]} {member[3]}"

        profile = activity_profiles.get(external_id, activity_profiles["M100005"])

        print(f"Creating data for {name} ({external_id})...")

        # Generate 30 days of data
        for days_ago in range(30, 0, -1):
            metric_date = date.today() - timedelta(days=days_ago)

            # Simulate device connection on day 1
            if days_ago == 30:
                device_type = random.choice(["fitbit", "apple_watch", "garmin"])
            else:
                device_type = None  # Only set on first record

            # Generate realistic daily metrics with some variability
            steps = random.randint(*profile["steps_range"])
            sleep_hours = round(random.uniform(*profile["sleep_hours_range"]), 1)
            avg_hr = random.randint(*profile["hr_range"])
            active_minutes = random.randint(*profile["active_minutes_range"])

            # Calculate calories (rough estimate based on activity)
            calories = int(1500 + (steps * 0.04) + (active_minutes * 5))

            # Insert wearable metric
            # Use timestamp for the recorded_timestamp (date + time component)
            recorded_timestamp = datetime.combine(metric_date, datetime.min.time())

            try:
                db.execute(
                    text("""
                    INSERT INTO wearable_metrics (
                        metric_id, member_id, recorded_timestamp, device_type,
                        steps, distance_meters, active_minutes, calories_burned,
                        sleep_minutes, resting_heart_rate, sleep_quality_score
                    ) VALUES (
                        :metric_id, :member_id, :recorded_timestamp, :device_type,
                        :steps, :distance_meters, :active_minutes, :calories_burned,
                        :sleep_minutes, :resting_heart_rate, :sleep_quality_score
                    )
                    """),
                    {
                        "metric_id": str(uuid.uuid4()),
                        "member_id": member_id,
                        "recorded_timestamp": recorded_timestamp,
                        "device_type": device_type,
                        "steps": steps,
                        "distance_meters": int(steps * 0.8),  # ~0.8m per step
                        "active_minutes": active_minutes,
                        "calories_burned": calories,
                        "sleep_minutes": int(sleep_hours * 60),
                        "resting_heart_rate": avg_hr - 5,
                        "sleep_quality_score": random.randint(70, 95)  # Sleep quality percentage
                    }
                )
                total_records += 1
            except Exception as e:
                print(f"  Error creating metric for {metric_date}: {e}")
                db.rollback()
                continue

        db.commit()
        print(f"  ✓ Created 30 days of metrics")
        print()

    db.close()

    print("=" * 80)
    print(f"SUMMARY: Created {total_records} wearable metric records")
    print(f"         ({len(members)} members × 30 days)")
    print("=" * 80)
    print()

    # Show sample data for verification
    db = SessionLocal()
    print("SAMPLE WEARABLE DATA (Last 7 Days):")
    print("-" * 80)

    for member in members:
        member_id = str(member[0])
        name = f"{member[2]} {member[3]}"

        result = db.execute(
            text("""
            SELECT DATE(recorded_timestamp), steps, active_minutes,
                   sleep_minutes, resting_heart_rate
            FROM wearable_metrics
            WHERE member_id = :member_id
            ORDER BY recorded_timestamp DESC
            LIMIT 7
            """),
            {"member_id": member_id}
        )

        metrics = result.fetchall()

        if metrics:
            print(f"\n{name}:")
            print(f"  {'Date':<12} {'Steps':<8} {'Active Min':<12} {'Sleep Hrs':<12} {'Rest HR'}")
            print(f"  {'-'*12} {'-'*8} {'-'*12} {'-'*12} {'-'*7}")

            for metric in metrics:
                sleep_hours = round(metric[3] / 60.0, 1)  # Convert minutes to hours
                print(f"  {str(metric[0]):<12} {metric[1]:<8} {metric[2]:<12} "
                      f"{sleep_hours:<12.1f} {metric[4]}")

            # Calculate 7-day averages
            avg_steps = sum(m[1] for m in metrics) / len(metrics)
            avg_active = sum(m[2] for m in metrics) / len(metrics)
            avg_sleep_mins = sum(m[3] for m in metrics) / len(metrics)
            avg_sleep_hrs = avg_sleep_mins / 60.0

            print(f"  {'7-Day Avg:':<12} {int(avg_steps):<8} {int(avg_active):<12} "
                  f"{avg_sleep_hrs:<12.1f}")

    db.close()

    print()
    print("-" * 80)
    print("\n✅ Wearable data ready!")
    print("   View in API: http://localhost:8000/docs")
    print("   Test query: SELECT COUNT(*) FROM wearable_metrics;")
    print()

    return total_records

if __name__ == "__main__":
    total = generate_wearable_data()
    print(f"✅ Successfully created {total} wearable metric records")

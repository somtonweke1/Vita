#!/usr/bin/env python3
"""
Create Test Members for VitaNexus Platform
Generates realistic member profiles with health data and calculates initial risk scores
"""

import sys
sys.path.append('/Users/somtonweke/Inversion Health/Vita')

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import random

from api.database import SessionLocal, engine
from services.analytics.health_scoring.scoring_engine import (
    HealthScoringEngine,
    MemberHealthData
)

def create_test_members():
    """Create 20 test members with varied health profiles"""

    db = SessionLocal()

    test_members = [
        {
            "external_member_id": "M100001",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "date_of_birth": date(1985, 3, 15),
            "gender": "F",
            "email": "sarah.johnson@example.com",
            "phone": "555-0101",
            "address_line1": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "enrollment_date": date.today() - timedelta(days=30),
            "status": "active",
            "profile": {
                "height_cm": 165,
                "weight_kg": 62,
                "bmi": 22.8,
                "blood_pressure_systolic": 118,
                "blood_pressure_diastolic": 76,
                "resting_heart_rate": 68,
                "smoker": False,
                "exercise_frequency": "4-5 times/week"
            }
        },
        {
            "external_member_id": "M100002",
            "first_name": "Michael",
            "last_name": "Chen",
            "date_of_birth": date(1972, 8, 22),
            "gender": "M",
            "email": "michael.chen@example.com",
            "phone": "555-0102",
            "address_line1": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "enrollment_date": date.today() - timedelta(days=45),
            "status": "active",
            "profile": {
                "height_cm": 178,
                "weight_kg": 95,
                "bmi": 30.0,
                "blood_pressure_systolic": 145,
                "blood_pressure_diastolic": 92,
                "resting_heart_rate": 78,
                "smoker": False,
                "exercise_frequency": "1-2 times/week"
            }
        },
        {
            "external_member_id": "M100003",
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "date_of_birth": date(1990, 12, 5),
            "gender": "F",
            "email": "emily.rodriguez@example.com",
            "phone": "555-0103",
            "address_line1": "789 Pine Rd",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "enrollment_date": date.today() - timedelta(days=20),
            "status": "active",
            "profile": {
                "height_cm": 160,
                "weight_kg": 58,
                "bmi": 22.7,
                "blood_pressure_systolic": 115,
                "blood_pressure_diastolic": 72,
                "resting_heart_rate": 65,
                "smoker": False,
                "exercise_frequency": "5+ times/week"
            }
        },
        {
            "external_member_id": "M100004",
            "first_name": "David",
            "last_name": "Williams",
            "date_of_birth": date(1965, 4, 18),
            "gender": "M",
            "email": "david.williams@example.com",
            "phone": "555-0104",
            "address_line1": "321 Elm St",
            "city": "Chicago",
            "state": "IL",
            "zip_code": "60601",
            "enrollment_date": date.today() - timedelta(days=60),
            "status": "active",
            "profile": {
                "height_cm": 175,
                "weight_kg": 88,
                "bmi": 28.7,
                "blood_pressure_systolic": 138,
                "blood_pressure_diastolic": 88,
                "resting_heart_rate": 75,
                "smoker": True,
                "exercise_frequency": "Rarely"
            }
        },
        {
            "external_member_id": "M100005",
            "first_name": "Jessica",
            "last_name": "Martinez",
            "date_of_birth": date(1988, 7, 9),
            "gender": "F",
            "email": "jessica.martinez@example.com",
            "phone": "555-0105",
            "address_line1": "654 Maple Dr",
            "city": "Seattle",
            "state": "WA",
            "zip_code": "98101",
            "enrollment_date": date.today() - timedelta(days=15),
            "status": "active",
            "profile": {
                "height_cm": 168,
                "weight_kg": 70,
                "bmi": 24.8,
                "blood_pressure_systolic": 122,
                "blood_pressure_diastolic": 78,
                "resting_heart_rate": 70,
                "smoker": False,
                "exercise_frequency": "3-4 times/week"
            }
        }
    ]

    scoring_engine = HealthScoringEngine()
    created_members = []

    print("=" * 80)
    print("CREATING TEST MEMBERS FOR VITANEXUS")
    print("=" * 80)
    print()

    for member_data in test_members:
        try:
            # Generate member ID
            member_id = str(uuid.uuid4())

            # Insert member
            db.execute(
                text("""
                INSERT INTO members (
                    member_id, external_member_id, first_name, last_name,
                    date_of_birth, gender, email, phone, address_line1,
                    city, state, zip_code, enrollment_date, status,
                    created_at, updated_at
                ) VALUES (
                    :member_id, :external_member_id, :first_name, :last_name,
                    :date_of_birth, :gender, :email, :phone, :address_line1,
                    :city, :state, :zip_code, :enrollment_date, :status,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                """),
                {
                    "member_id": member_id,
                    "external_member_id": member_data["external_member_id"],
                    "first_name": member_data["first_name"],
                    "last_name": member_data["last_name"],
                    "date_of_birth": member_data["date_of_birth"],
                    "gender": member_data["gender"],
                    "email": member_data["email"],
                    "phone": member_data["phone"],
                    "address_line1": member_data["address_line1"],
                    "city": member_data["city"],
                    "state": member_data["state"],
                    "zip_code": member_data["zip_code"],
                    "enrollment_date": member_data["enrollment_date"],
                    "status": member_data["status"]
                }
            )

            # Insert health profile
            profile = member_data["profile"]
            db.execute(
                text("""
                INSERT INTO member_health_profiles (
                    profile_id, member_id, height_cm, weight_kg, bmi,
                    blood_pressure_systolic, blood_pressure_diastolic,
                    resting_heart_rate, smoker, exercise_frequency,
                    last_updated
                ) VALUES (
                    :profile_id, :member_id, :height_cm, :weight_kg, :bmi,
                    :blood_pressure_systolic, :blood_pressure_diastolic,
                    :resting_heart_rate, :smoker, :exercise_frequency, CURRENT_TIMESTAMP
                )
                """),
                {
                    "profile_id": str(uuid.uuid4()),
                    "member_id": member_id,
                    "height_cm": profile["height_cm"],
                    "weight_kg": profile["weight_kg"],
                    "bmi": profile["bmi"],
                    "blood_pressure_systolic": profile["blood_pressure_systolic"],
                    "blood_pressure_diastolic": profile["blood_pressure_diastolic"],
                    "resting_heart_rate": profile["resting_heart_rate"],
                    "smoker": profile["smoker"],
                    "exercise_frequency": profile["exercise_frequency"]
                }
            )

            # Calculate initial health score
            age = (date.today() - member_data["date_of_birth"]).days // 365

            health_data = MemberHealthData(
                member_id=member_id,
                age=age,
                gender=member_data["gender"],
                bmi=profile["bmi"],
                blood_pressure_systolic=profile["blood_pressure_systolic"],
                blood_pressure_diastolic=profile["blood_pressure_diastolic"],
                avg_resting_heart_rate=profile["resting_heart_rate"],
                # Add more fields as needed
                chronic_conditions=[],
                medications=[],
                emergency_visits=0,
                hospital_admissions=0
            )

            score_result = scoring_engine.calculate_score(health_data)

            # Insert health score
            db.execute(
                text("""
                INSERT INTO health_risk_scores (
                    member_id, calculation_timestamp, overall_score,
                    risk_category, confidence_level, predicted_annual_cost,
                    model_version
                ) VALUES (
                    :member_id, CURRENT_TIMESTAMP, :overall_score, :risk_category,
                    :confidence_level, :predicted_annual_cost, :model_version
                )
                """),
                {
                    "member_id": member_id,
                    "overall_score": float(score_result.score),
                    "risk_category": score_result.risk_category.value,
                    "confidence_level": float(score_result.confidence_level),
                    "predicted_annual_cost": float(score_result.predicted_annual_cost),
                    "model_version": score_result.model_version
                }
            )

            # Update member with current risk score
            db.execute(
                text("""
                UPDATE members
                SET current_risk_score = :current_risk_score,
                    current_risk_category = :current_risk_category
                WHERE member_id = :member_id
                """),
                {
                    "current_risk_score": float(score_result.score),
                    "current_risk_category": score_result.risk_category.value,
                    "member_id": member_id
                }
            )

            db.commit()

            created_members.append({
                "name": f"{member_data['first_name']} {member_data['last_name']}",
                "external_id": member_data["external_member_id"],
                "score": float(score_result.score),
                "risk": score_result.risk_category.value,
                "cost": float(score_result.predicted_annual_cost)
            })

            print(f"✓ Created: {member_data['first_name']} {member_data['last_name']}")
            print(f"  ID: {member_data['external_member_id']}")
            print(f"  Risk Score: {score_result.score:.1f}/100 ({score_result.risk_category.value})")
            print(f"  Predicted Cost: ${score_result.predicted_annual_cost:,.2f}/year")
            print()

        except Exception as e:
            print(f"✗ Error creating {member_data['first_name']} {member_data['last_name']}: {e}")
            db.rollback()
            continue

    db.close()

    print("=" * 80)
    print(f"SUMMARY: Created {len(created_members)} test members")
    print("=" * 80)
    print()

    # Print summary table
    print("MEMBER SUMMARY:")
    print("-" * 80)
    print(f"{'Name':<25} {'ID':<12} {'Risk Score':<15} {'Risk':<12} {'Est. Cost'}")
    print("-" * 80)

    for member in created_members:
        print(f"{member['name']:<25} {member['external_id']:<12} "
              f"{member['score']:<15.1f} {member['risk']:<12} "
              f"${member['cost']:>10,.2f}")

    print("-" * 80)

    if created_members:
        avg_score = sum(m['score'] for m in created_members) / len(created_members)
        avg_cost = sum(m['cost'] for m in created_members) / len(created_members)
        print(f"{'AVERAGES':<25} {'':<12} {avg_score:<15.1f} {'':<12} ${avg_cost:>10,.2f}")
    else:
        print("No members were created successfully.")
    print()

    return created_members

if __name__ == "__main__":
    created = create_test_members()
    print(f"\n✅ Test members ready! View them at http://localhost:8000/docs")
    print(f"   Database: psql -U somtonweke vitanexus_dev")

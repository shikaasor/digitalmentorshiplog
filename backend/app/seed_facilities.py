"""
Facility Seed Script

This script loads the 91 predefined facilities into the database.
Run this script once to populate the facilities table with all supported facilities.

Usage:
    python -m app.seed_facilities

Note: This script will skip facilities that already exist (based on facility code).
"""

import json
import os
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import engine, Base
from app.models import Facility


def load_facilities_from_json(json_path: str) -> list[dict]:
    """Load facility data from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def seed_facilities(db: Session, facilities_data: list[dict]) -> dict:
    """
    Seed facilities into the database.

    Returns a dictionary with statistics:
    - created: number of new facilities created
    - skipped: number of facilities that already exist
    - total: total facilities in seed data
    """
    stats = {
        'created': 0,
        'skipped': 0,
        'total': len(facilities_data)
    }

    for facility_data in facilities_data:
        # Check if facility already exists (by code)
        existing = db.query(Facility).filter(
            Facility.code == facility_data['code']
        ).first()

        if existing:
            print(f"⏭️  Skipping '{facility_data['name']}' - already exists")
            stats['skipped'] += 1
            continue

        # Create new facility
        facility = Facility(
            name=facility_data['name'],
            code=facility_data['code'],
            state=facility_data['state'],
            lga=facility_data['lga'],
            facility_type=facility_data['facility_type'],
        )

        db.add(facility)
        print(f"✅ Created '{facility_data['name']}' ({facility_data['state']} - {facility_data['facility_type']})")
        stats['created'] += 1

    # Commit all changes
    db.commit()

    return stats


def main():
    """Main function to run the seed script."""
    print("=" * 80)
    print("FACILITY SEED SCRIPT")
    print("=" * 80)
    print()

    # Get the path to the JSON file
    current_dir = Path(__file__).parent
    json_path = current_dir / 'seed_data' / 'facilities.json'

    if not json_path.exists():
        print(f"❌ Error: Seed data file not found at {json_path}")
        return

    print(f"📄 Loading facility data from: {json_path}")
    facilities_data = load_facilities_from_json(str(json_path))
    print(f"📊 Found {len(facilities_data)} facilities in seed data")
    print()

    # Create database session
    from app.database import SessionLocal
    db = SessionLocal()

    try:
        print("🚀 Starting to seed facilities...")
        print("-" * 80)

        stats = seed_facilities(db, facilities_data)

        print("-" * 80)
        print()
        print("📊 SUMMARY:")
        print(f"   Total facilities in seed data: {stats['total']}")
        print(f"   ✅ Created: {stats['created']}")
        print(f"   ⏭️  Skipped (already exist): {stats['skipped']}")
        print()

        if stats['created'] > 0:
            print("✨ Facility seeding completed successfully!")
        else:
            print("ℹ️  No new facilities were created (all already exist)")

        # Display breakdown by state
        print()
        print("📍 Facilities by State:")
        for state in ['Kano', 'Jigawa', 'Bauchi']:
            count = db.query(Facility).filter(Facility.state == state).count()
            print(f"   {state}: {count} facilities")

        # Display breakdown by type
        print()
        print("🏥 Facilities by Type:")
        for facility_type in ['Primary', 'Secondary', 'Tertiary']:
            count = db.query(Facility).filter(Facility.facility_type == facility_type).count()
            print(f"   {facility_type}: {count} facilities")

        print()
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

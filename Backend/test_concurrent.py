"""Test that two concurrent booking requests for the same slot
don't result in a double booking.

Run:  .venv\Scripts\python.exe test_concurrent.py
"""

import asyncio
from datetime import datetime, timedelta, timezone

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)
from app.services.appointment_service import create_appointment


async def main():
    await connect_to_mongodb()

    try:
        # Use a unique slot far in the future so it doesn't collide
        # with existing test data.
        start = datetime(2030, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        end = start + timedelta(minutes=30)

        base_data = {
            "service": "Dental cleaning",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "doctor_id": "doctor_test_concurrent",
        }

        booking_a = {**base_data, "patient_name": "jk", "patient_phone": "7890090090"}
        booking_b = {**base_data, "patient_name": "RM", "patient_phone": "8967890000"}

        print("=" * 50)
        print("Firing two concurrent bookings for the same slot...")
        print(f"  Doctor: {base_data['doctor_id']}")
        print(f"  Slot:   {start.isoformat()} → {end.isoformat()}")
        print("=" * 50)

        # Fire both at the same time
        result_a, result_b = await asyncio.gather(
            create_appointment(booking_a),
            create_appointment(booking_b),
        )

        print()
        print("Result A (JK):", result_a["success"], "—", result_a["message"])
        print("Result B (RM):  ", result_b["success"], "—", result_b["message"])
        print()

        # Verify: exactly one should succeed, one should fail
        if result_a["success"] and not result_b["success"]:
            print("PASS: Only Alice's booking succeeded. No double booking.")
        elif result_b["success"] and not result_a["success"]:
            print("PASS: Only Bob's booking succeeded. No double booking.")
        elif result_a["success"] and result_b["success"]:
            print("FAIL: BOTH bookings succeeded — double booking detected!")
        else:
            print("FAIL: Neither booking succeeded — something went wrong.")

    finally:
        await close_mongodb_connection()


asyncio.run(main())

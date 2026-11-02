import pytest

from pet_walking_service import (
    process_walking_routes,
    inspect_gps_collars
)


# 1. Invalid input: routes must be a list
def test_invalid_routes():
    with pytest.raises(ValueError):
        process_walking_routes("invalid", 5.0)


# 2. Invalid input: transport fee cannot be negative
def test_negative_transport_fee():
    with pytest.raises(ValueError):
        process_walking_routes([], -5.0)


# 3. Empty routes
def test_empty_routes():
    result = process_walking_routes([], 5.0)
    assert result == {
        "total_revenue": 0.0,
        "status": "ZERO_EARNINGS"
    }


# 4. Unconfirmed route
def test_unconfirmed_route():
    routes = [
        {"route_confirmed": False}
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


# 5. Test all valid session types
def test_all_session_types():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_60",
            "walks": [{"num_pets": 1}]
        },
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [{"num_pets": 1}]
        },
        {
            "route_confirmed": True,
            "session_type": "express_15",
            "walks": [{"num_pets": 1}]
        }
    ]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 86.0
    assert result["status"] == "COMPLETED"


# 6. Invalid session type
def test_invalid_session_type():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "unknown",
            "walks": []
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


# 7. Empty walks and missing optional values
def test_empty_walks():
    routes = [
        {
            "route_confirmed": True,
            "walks": []
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 0.0


# 8. Invalid pet counts
def test_invalid_pet_counts():
    routes = [
        {
            "route_confirmed": True,
            "walks": [
                {"num_pets": 0},
                {"num_pets": -1}
            ]
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


# 9. More than three pets
def test_multiple_pets():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [{"num_pets": 4}]
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 48.6


# 10. Medication charges
def test_medication_charge():
    routes = [
        {
            "route_confirmed": True,
            "walks": [
                {
                    "num_pets": 1,
                    "needs_meds": True
                }
            ]
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 33.0


# 11. Weekend transport fee
def test_weekend_transport_fee():
    routes = [
        {
            "route_confirmed": True,
            "is_weekend": True,
            "walks": [{"num_pets": 1}]
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 32.0


# 12. Aggression alert in a standard 30-minute session
def test_aggression_alert_standard_30():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [
                {
                    "num_pets": 1,
                    "aggression_alert": True,
                    "needs_meds": True
                }
            ]
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 6.0


# 13. Aggression alert in a standard 60-minute session
def test_aggression_alert_standard_60():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_60",
            "walks": [
                {
                    "num_pets": 1,
                    "aggression_alert": True
                }
            ]
        }
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


# 14. Incident audit
def test_incident_audit():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "unknown",
            "walks": []
        }
        for _ in range(5)
    ]

    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "INCIDENT_AUDIT"


# 15. GPS collar with no data
def test_gps_no_data():
    assert inspect_gps_collars([]) == "NO_DATA"


# 16. GPS collar with normal signal
def test_gps_online():
    assert inspect_gps_collars([[80, 75, 60]]) == "ONLINE"


# 17. GPS signal drops once and recovers
def test_gps_signal_recovers():
    assert inspect_gps_collars([[10, 80, 15]]) == "ONLINE"


# 18. GPS signal lost for two consecutive readings
def test_gps_lost_signal():
    assert inspect_gps_collars([[10, 15, 80]]) == "LOST_SIGNAL_ALERT"


# 19. Multiple GPS collars
def test_multiple_gps_collars():
    assert inspect_gps_collars([
        [80, 70],
        [60, 50]
    ]) == "ONLINE"
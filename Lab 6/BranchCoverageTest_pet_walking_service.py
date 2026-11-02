
import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


def test_invalid_routes_type():
    with pytest.raises(ValueError):
        process_walking_routes("invalid", 5.0)


def test_negative_transport_fee():
    with pytest.raises(ValueError):
        process_walking_routes([], -5.0)


def test_empty_routes():
    result = process_walking_routes([], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


def test_unconfirmed_route_is_skipped():
    routes = [{"route_confirmed": False, "walks": []}]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


def test_standard_60_aggression_alert():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_60",
        "walks": [
            {"num_pets": 2, "aggression_alert": True, "needs_meds": True}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 0.0


def test_standard_30_aggression_alert():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [
            {"num_pets": 1, "aggression_alert": True, "needs_meds": True}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 6.0


def test_standard_60_normal_walk():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_60",
        "walks": [
            {"num_pets": 2, "aggression_alert": False, "needs_meds": False}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 45.0


def test_standard_30_normal_walk():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [
            {"num_pets": 2, "aggression_alert": False, "needs_meds": False}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 32.0


def test_express_15_normal_walk():
    routes = [{
        "route_confirmed": True,
        "session_type": "express_15",
        "walks": [
            {"num_pets": 1, "aggression_alert": False, "needs_meds": False}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 19.0


def test_unknown_session_type():
    routes = [{
        "route_confirmed": True,
        "session_type": "unknown",
        "walks": []
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


def test_invalid_pet_count():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{"num_pets": 0}]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


def test_more_than_three_pets():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [
            {"num_pets": 4, "aggression_alert": False, "needs_meds": False}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 48.6


def test_medication_fee():
    routes = [{
        "route_confirmed": True,
        "session_type": "express_15",
        "walks": [
            {"num_pets": 1, "aggression_alert": False, "needs_meds": True}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 25.0


def test_weekend_transport_fee():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "is_weekend": True,
        "walks": [
            {"num_pets": 1, "aggression_alert": False, "needs_meds": False}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 32.0


def test_empty_walks_with_weekend_fee():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "is_weekend": True,
        "walks": []
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 5.0


def test_incident_audit_status():
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


def test_completed_status():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [
            {"num_pets": 1, "aggression_alert": False, "needs_meds": False}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "COMPLETED"


def test_gps_no_data():
    assert inspect_gps_collars([]) == "NO_DATA"


def test_gps_empty_collar_logs():
    assert inspect_gps_collars([[]]) == "ONLINE"


def test_gps_signal_stays_online():
    assert inspect_gps_collars([[30, 25, 40]]) == "ONLINE"


def test_gps_single_low_signal():
    assert inspect_gps_collars([[10, 30, 15]]) == "ONLINE"


def test_gps_consecutive_low_signals():
    assert inspect_gps_collars([[10, 15]]) == "LOST_SIGNAL_ALERT"

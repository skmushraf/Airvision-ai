"""
AirVision AI — CPCB provider tests
===================================
These tests exercise the full CPCB path (parse → aggregate → NAQI → city
record) against a captured-shape sample of the data.gov.in resource, so they
pass on any machine regardless of whether api.data.gov.in is reachable.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import aqi as aqi_svc  # noqa: E402
from services import cpcb as cpcb_svc  # noqa: E402

# Rows mirroring the real resource schema (one pollutant per station)
SAMPLE = [
    {"country": "India", "state": "Delhi", "city": "Delhi",
     "station": "Anand Vihar, Delhi - DPCC", "last_update": "03-10-2026 11:00:00",
     "latitude": "28.6469", "longitude": "77.3159",
     "pollutant_id": "PM2.5", "pollutant_min": "60", "pollutant_max": "140",
     "pollutant_avg": "95"},
    {"country": "India", "state": "Delhi", "city": "Delhi",
     "station": "Anand Vihar, Delhi - DPCC", "last_update": "03-10-2026 11:00:00",
     "latitude": "28.6469", "longitude": "77.3159",
     "pollutant_id": "PM10", "pollutant_min": "110", "pollutant_max": "260",
     "pollutant_avg": "180"},
    {"country": "India", "state": "Delhi", "city": "Delhi",
     "station": "Anand Vihar, Delhi - DPCC", "last_update": "03-10-2026 11:00:00",
     "latitude": "28.6469", "longitude": "77.3159",
     "pollutant_id": "NO2", "pollutant_min": "20", "pollutant_max": "70",
     "pollutant_avg": "45"},
    {"country": "India", "state": "Delhi", "city": "Delhi",
     "station": "RK Puram, Delhi - DPCC", "last_update": "03-10-2026 11:00:00",
     "latitude": "28.5633", "longitude": "77.1869",
     "pollutant_id": "PM2.5", "pollutant_min": "40", "pollutant_max": "90",
     "pollutant_avg": "65"},
    # 'NA' average → midpoint of min/max must be used
    {"country": "India", "state": "Andhra_Pradesh", "city": "Amaravati",
     "station": "Secretariat, Amaravati - APPCB", "last_update": "03-10-2026 11:00:00",
     "latitude": "16.515083", "longitude": "80.518167",
     "pollutant_id": "PM2.5", "pollutant_min": "20", "pollutant_max": "40",
     "pollutant_avg": "NA"},
    {"country": "India", "state": "Andhra_Pradesh", "city": "Amaravati",
     "station": "Secretariat, Amaravati - APPCB", "last_update": "03-10-2026 11:00:00",
     "latitude": "16.515083", "longitude": "80.518167",
     "pollutant_id": "OZONE", "pollutant_min": "10", "pollutant_max": "60",
     "pollutant_avg": "35"},
    # Unparseable row must be skipped, not crash the batch
    {"country": "India", "state": "Bihar", "city": "",
     "pollutant_id": "PM2.5", "pollutant_avg": "nonsense"},
]


@pytest.fixture(scope="module")
def index():
    return cpcb_svc.aggregate_by_city(SAMPLE)


# --- CPCB NAQI engine ------------------------------------------------------
def test_naqi_breakpoints_match_cpcb_table():
    # PM2.5 = 90 µg/m³ sits exactly on the 'Moderate' ceiling (sub-index 200)
    assert aqi_svc.compute_cpcb_aqi({"pm2_5": 90})["aqi"] == 200
    # PM2.5 = 30 is the top of 'Good'
    assert aqi_svc.compute_cpcb_aqi({"pm2_5": 30})["aqi"] == 50
    # PM10 = 250 is the top of 'Moderate'
    assert aqi_svc.compute_cpcb_aqi({"pm10": 250})["aqi"] == 200


def test_naqi_differs_from_us_epa():
    """Same concentration, different standard — proves CPCB math is in use."""
    pollutants = {"pm2_5": 90}
    cpcb = aqi_svc.compute_cpcb_aqi(pollutants)["aqi"]
    epa = aqi_svc.compute_aqi_from_components(pollutants)["aqi"]
    assert cpcb == 200 and epa < cpcb


def test_naqi_is_max_of_sub_indices_and_names_driver():
    out = aqi_svc.compute_cpcb_aqi({"pm2_5": 30, "pm10": 250, "no2": 40})
    assert out["aqi"] == 200
    assert out["driver"] == "PM10"
    assert out["reliable"] is True


def test_naqi_flags_unreliable_when_no_pm():
    out = aqi_svc.compute_cpcb_aqi({"no2": 40, "so2": 20})
    assert out["reliable"] is False


def test_naqi_clamped_to_500():
    assert aqi_svc.compute_cpcb_aqi({"pm2_5": 9999})["aqi"] == 500


# --- Feed parsing / aggregation -------------------------------------------
def test_city_names_normalised():
    assert cpcb_svc.normalize_city("  Andhra_Pradesh-City ") == "andhra pradesh city"
    assert cpcb_svc.normalize_city("BENGALURU") == "bengaluru"


def test_stations_averaged_per_city(index):
    delhi = index["delhi"]
    # PM2.5 averaged across the two stations: (95 + 65) / 2
    assert delhi["pollutants"]["pm2_5"] == 80.0
    assert delhi["station_count"] == 2


def test_na_average_falls_back_to_minmax_midpoint(index):
    assert index["amaravati"]["pollutants"]["pm2_5"] == 30.0


def test_bad_rows_skipped(index):
    assert "" not in index
    assert all(v["city"] for v in index.values())


def test_timestamp_parsed(index):
    assert index["delhi"]["updated_epoch"] is not None
    assert index["delhi"]["last_update"] == "03-10-2026 11:00:00"


def test_city_record_carries_cpcb_metadata(index):
    delhi = index["delhi"]
    assert delhi["standard"] == "CPCB NAQI"
    assert delhi["aqi_category"] in {
        "Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"}
    assert delhi["stations"][0]["lat"] == pytest.approx(28.6469)


# --- CO unit handling ------------------------------------------------------
def test_co_microgram_values_converted_to_mg():
    # 1200 µg/m³ → 1.2 mg/m³ (sub-index ~60), NOT 1200 mg/m³ (off-scale)
    assert cpcb_svc._co_to_mg_m3(1200) == pytest.approx(1.2)


def test_co_small_values_treated_as_mg():
    assert cpcb_svc._co_to_mg_m3(1.4) == pytest.approx(1.4)


# --- Graceful degradation --------------------------------------------------
def test_provider_reports_status_without_network():
    status = cpcb_svc.provider_status()
    assert status["resource_id"] == "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
    assert "standard" in status and status["standard"].startswith("CPCB")


def test_live_falls_back_when_cpcb_unavailable(monkeypatch):
    """An Indian city must still produce a record when CPCB returns nothing."""
    from services import live as live_svc

    monkeypatch.setattr(cpcb_svc, "get_city", lambda *a, **k: None)
    monkeypatch.setattr("services.cities.cpcb_proxy_name", lambda c: None)
    air, meta = live_svc._cpcb_air(
        {"id": "delhi", "name": "Delhi", "cc": "IN"})
    assert air is None and meta is None

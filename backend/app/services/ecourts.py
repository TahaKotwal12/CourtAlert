"""
eCourts India API service.

The real NIC eCourts API requires government approval (weeks).
For the hackathon demo we use a realistic mock that:
  - Validates CNR format
  - Returns plausible case + hearing data keyed to the state prefix in the CNR
  - Exposes the same interface as a real client would — swap mock=False when
    real credentials arrive.
"""
import re
from datetime import date, timedelta
from typing import Optional
import httpx

from app.config.logger import get_logger

logger = get_logger(__name__)

# CNR format: 4-letter code (state+district) + 2-digit court + 6-digit case number + 4-digit year
# e.g. DLHC010012342022  (total 16 chars: 4 letters + 12 digits)
CNR_REGEX = re.compile(r"^[A-Z]{4}\d{12}$", re.IGNORECASE)

# State code → court city mapping for realistic mock data
STATE_COURTS = {
    "MH": ("Maharashtra", "Bombay High Court, Mumbai"),
    "DL": ("Delhi", "Delhi High Court, New Delhi"),
    "KA": ("Karnataka", "Karnataka High Court, Bengaluru"),
    "TN": ("Tamil Nadu", "Madras High Court, Chennai"),
    "TS": ("Telangana", "Telangana High Court, Hyderabad"),
    "GJ": ("Gujarat", "Gujarat High Court, Ahmedabad"),
    "RJ": ("Rajasthan", "Rajasthan High Court, Jaipur"),
    "UP": ("Uttar Pradesh", "Allahabad High Court, Prayagraj"),
}

HEARING_TYPES = [
    "Final Arguments",
    "IA Hearing",
    "Evidence",
    "Framing of Issues",
    "First Hearing",
    "Written Statement",
]

CASE_TITLES = [
    "Patil vs State of Maharashtra",
    "Sharma vs Union of India",
    "Reddy vs State of Telangana",
    "Kumar vs Municipal Corporation",
    "Devi vs Collector",
    "Khan vs State Government",
    "Iyer vs Revenue Authority",
    "Nair vs District Collector",
]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_cnr(cnr: str) -> bool:
    """Basic structural validation of CNR number."""
    return bool(CNR_REGEX.match(cnr.upper()))


def parse_state_from_cnr(cnr: str) -> str:
    """Extract 2-letter state code from CNR (first 2 chars)."""
    return cnr[:2].upper()


# ---------------------------------------------------------------------------
# Mock data generator
# ---------------------------------------------------------------------------

def _mock_case_data(cnr: str) -> dict:
    """
    Generate deterministic mock case data from CNR so the same CNR always
    returns the same title / court (useful for demo consistency).
    """
    cnr = cnr.upper()
    state = parse_state_from_cnr(cnr)
    state_name, court_name = STATE_COURTS.get(state, ("India", "District Court"))

    # Deterministic index from CNR digits so same CNR → same title
    digits = re.sub(r"\D", "", cnr)
    idx = int(digits[-4:]) % len(CASE_TITLES) if digits else 0
    case_title = CASE_TITLES[idx]

    today = date.today()
    # Generate 3 hearings: one past, two future
    hearings = [
        {
            "hearing_date": today - timedelta(days=30),
            "hearing_type": "First Hearing",
            "court_room": f"Court No. {(idx % 5) + 1}",
            "judge_name": "Hon. Justice A.K. Sharma",
            "purpose": "Filing of documents",
            "is_completed": True,
        },
        {
            "hearing_date": today + timedelta(days=7),
            "hearing_type": HEARING_TYPES[idx % len(HEARING_TYPES)],
            "court_room": f"Court No. {(idx % 5) + 1}",
            "judge_name": "Hon. Justice A.K. Sharma",
            "purpose": "Arguments",
            "is_completed": False,
        },
        {
            "hearing_date": today + timedelta(days=37),
            "hearing_type": "Final Arguments",
            "court_room": f"Court No. {(idx % 5) + 1}",
            "judge_name": "Hon. Justice A.K. Sharma",
            "purpose": "Final arguments and judgment",
            "is_completed": False,
        },
    ]

    return {
        "case_title": case_title,
        "court_name": court_name,
        "state_code": state,
        "district_code": cnr[2:4],
        "hearings": hearings,
    }


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

async def fetch_case(cnr: str) -> Optional[dict]:
    """
    Fetch case data for a CNR number.
    Returns None if CNR is invalid / not found.

    Returns:
        {
            "case_title": str,
            "court_name": str,
            "state_code": str,
            "district_code": str,
            "hearings": [
                {
                    "hearing_date": date,
                    "hearing_type": str | None,
                    "court_room": str | None,
                    "judge_name": str | None,
                    "purpose": str | None,
                    "is_completed": bool,
                },
                ...
            ],
        }
    """
    if not validate_cnr(cnr):
        logger.warning(f"Invalid CNR format: {cnr}")
        return None

    # --- real API call would go here ---
    # async with httpx.AsyncClient() as client:
    #     resp = await client.get(
    #         "https://services.ecourts.gov.in/ecourtindiaapi/",
    #         params={"cnr": cnr, "key": settings.ECOURTS_API_KEY},
    #         timeout=10,
    #     )
    #     resp.raise_for_status()
    #     return _parse_real_response(resp.json())

    logger.info(f"[MOCK] Fetching case data for CNR: {cnr}")
    return _mock_case_data(cnr)

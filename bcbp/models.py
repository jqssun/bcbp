from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Leg:
    operating_carrier_pnr: Optional[str] = None
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    operating_carrier_designator: Optional[str] = None
    flight_number: Optional[str] = None
    flight_date: Optional[datetime] = None
    compartment_code: Optional[str] = None
    seat_number: Optional[str] = None
    check_in_sequence_number: Optional[str] = None
    passenger_status: Optional[str] = None
    airline_numeric_code: Optional[str] = None
    serial_number: Optional[str] = None
    selectee_indicator: Optional[str] = None
    international_documentation_verification: Optional[str] = None
    marketing_carrier_designator: Optional[str] = None
    frequent_flyer_airline_designator: Optional[str] = None
    frequent_flyer_number: Optional[str] = None
    id_indicator: Optional[str] = None
    free_baggage_allowance: Optional[str] = None
    fast_track: Optional[bool] = None
    airline_info: Optional[str] = None


@dataclass
class BoardingPassData:
    legs: Optional[List[Leg]] = None
    passenger_name: Optional[str] = None
    passenger_description: Optional[str] = None
    check_in_source: Optional[str] = None
    boarding_pass_issuance_source: Optional[str] = None
    issuance_date: Optional[datetime] = None
    document_type: Optional[str] = None
    boarding_pass_issuer_designator: Optional[str] = None
    baggage_tag_number: Optional[str] = None
    first_baggage_tag_number: Optional[str] = None
    second_baggage_tag_number: Optional[str] = None
    security_data_type: Optional[str] = None
    security_data: Optional[str] = None


@dataclass
class BoardingPassMetaData:
    format_code: Optional[str] = None
    number_of_legs: Optional[int] = None
    electronic_ticket_indicator: Optional[str] = None
    version_number_indicator: Optional[str] = None
    version_number: Optional[int] = None
    security_data_indicator: Optional[str] = None


@dataclass
class BarcodedBoardingPass:
    data: Optional[BoardingPassData] = None
    meta: Optional[BoardingPassMetaData] = None
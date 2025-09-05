from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


class LENGTHS:
    FORMAT_CODE = 1
    NUMBER_OF_LEGS_ENCODED = 1
    PASSENGER_NAME = 20
    ELECTRONIC_TICKET_INDICATOR = 1
    OPERATING_CARRIER_PNR_CODE = 7
    FROM_CITY_AIRPORT_CODE = 3
    TO_CITY_AIRPORT_CODE = 3
    OPERATING_CARRIER_DESIGNATOR = 3
    FLIGHT_NUMBER = 5
    DATE_OF_FLIGHT = 3
    COMPARTMENT_CODE = 1
    SEAT_NUMBER = 4
    CHECK_IN_SEQUENCE_NUMBER = 5
    PASSENGER_STATUS = 1
    BEGINNING_OF_VERSION_NUMBER = 1
    VERSION_NUMBER = 1
    PASSENGER_DESCRIPTION = 1
    SOURCE_OF_CHECK_IN = 1
    SOURCE_OF_BOARDING_PASS_ISSUANCE = 1
    DATE_OF_ISSUE_OF_BOARDING_PASS = 4
    DOCUMENT_TYPE = 1
    AIRLINE_DESIGNATOR_OF_BOARDING_PASS_ISSUER = 3
    BAGGAGE_TAG_LICENCE_PLATE_NUMBER = 13
    FIRST_NON_CONSECUTIVE_BAGGAGE_TAG_LICENCE_PLATE_NUMBER = 13
    SECOND_NON_CONSECUTIVE_BAGGAGE_TAG_LICENCE_PLATE_NUMBER = 13
    AIRLINE_NUMERIC_CODE = 3
    DOCUMENT_FORM_SERIAL_NUMBER = 10
    SELECTEE_INDICATOR = 1
    INTERNATIONAL_DOCUMENTATION_VERIFICATION = 1
    MARKETING_CARRIER_DESIGNATOR = 3
    FREQUENT_FLYER_AIRLINE_DESIGNATOR = 3
    FREQUENT_FLYER_NUMBER = 16
    ID_AD_INDICATOR = 1
    FREE_BAGGAGE_ALLOWANCE = 3
    FAST_TRACK = 1
    BEGINNING_OF_SECURITY_DATA = 1
    TYPE_OF_SECURITY_DATA = 1
    SECURITY_DATA = 100


@dataclass
class Leg:
    operating_carrier_pnr_code: Optional[str] = None
    from_city_airport_code: Optional[str] = None
    to_city_airport_code: Optional[str] = None
    operating_carrier_designator: Optional[str] = None
    flight_number: Optional[str] = None
    date_of_flight: Optional[datetime] = None
    compartment_code: Optional[str] = None
    seat_number: Optional[str] = None
    check_in_sequence_number: Optional[str] = None
    passenger_status: Optional[str] = None
    airline_numeric_code: Optional[str] = None
    document_form_serial_number: Optional[str] = None
    selectee_indicator: Optional[str] = None
    international_documentation_verification: Optional[str] = None
    marketing_carrier_designator: Optional[str] = None
    frequent_flyer_airline_designator: Optional[str] = None
    frequent_flyer_number: Optional[str] = None
    id_ad_indicator: Optional[str] = None
    free_baggage_allowance: Optional[str] = None
    fast_track: Optional[bool] = None
    for_individual_airline_use: Optional[str] = None


@dataclass
class BoardingPassData:
    legs: Optional[List[Leg]] = None
    passenger_name: Optional[str] = None
    passenger_description: Optional[str] = None
    source_of_check_in: Optional[str] = None
    source_of_boarding_pass_issuance: Optional[str] = None
    date_of_issue_of_boarding_pass: Optional[datetime] = None
    document_type: Optional[str] = None
    airline_designator_of_boarding_pass_issuer: Optional[str] = None
    baggage_tag_licence_plate_number: Optional[str] = None
    first_non_consecutive_baggage_tag_licence_plate_number: Optional[str] = None
    second_non_consecutive_baggage_tag_licence_plate_number: Optional[str] = None
    type_of_security_data: Optional[str] = None
    security_data: Optional[str] = None


@dataclass
class BoardingPassMetaData:
    format_code: Optional[str] = None
    number_of_legs_encoded: Optional[int] = None
    electronic_ticket_indicator: Optional[str] = None
    beginning_of_version_number: Optional[str] = None
    version_number: Optional[int] = None
    beginning_of_security_data: Optional[str] = None


@dataclass
class BarcodedBoardingPass:
    data: Optional[BoardingPassData] = None
    meta: Optional[BoardingPassMetaData] = None

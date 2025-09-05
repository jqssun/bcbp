from datetime import datetime
from typing import Optional

from .models import (
    LENGTHS,
    BarcodedBoardingPass,
    BoardingPassData,
    BoardingPassMetaData,
    Leg,
)
from .utils import date_to_day_of_year, day_of_year_to_date, hex_to_number


class SectionDecoder:
    def __init__(self, barcode_string: Optional[str] = None):
        self.barcode_string = barcode_string
        self.current_index = 0

    def _get_next_field(self, length: Optional[int] = None) -> Optional[str]:
        """Extract the next field from the barcode string."""
        if self.barcode_string is None:
            return None

        barcode_length = len(self.barcode_string)
        if self.current_index >= barcode_length:
            return None

        start = self.current_index
        if length is None:
            value = self.barcode_string[start:]
            self.current_index = barcode_length
        else:
            value = self.barcode_string[start : start + length]
            self.current_index += length

        trimmed_value = value.rstrip()
        if trimmed_value == "":
            return None
        return trimmed_value

    def get_next_string(self, length: int) -> Optional[str]:
        """Get next string field."""
        return self._get_next_field(length)

    def get_next_number(self, length: int) -> Optional[int]:
        """Get next number field."""
        value = self._get_next_field(length)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def get_next_date(
        self, length: int, has_year_prefix: bool, reference_year: Optional[int] = None
    ) -> Optional[datetime]:
        """Get next date field."""
        value = self._get_next_field(length)
        if value is None:
            return None
        return day_of_year_to_date(value, has_year_prefix, reference_year)

    def get_next_boolean(self) -> Optional[bool]:
        """Get next boolean field."""
        value = self._get_next_field(1)
        if value is None:
            return None
        return value == "Y"

    def get_next_section_size(self) -> int:
        """Get the size of the next section."""
        return hex_to_number(self._get_next_field(2) or "00")

    def get_remaining_string(self) -> Optional[str]:
        """Get remaining string."""
        return self._get_next_field()


def decode(
    barcode_string: str, reference_year: Optional[int] = None
) -> BarcodedBoardingPass:
    """Decode a BCBP barcode string to BarcodedBoardingPass object."""
    bcbp = BarcodedBoardingPass()
    main_section = SectionDecoder(barcode_string)

    bcbp.data = BoardingPassData()
    bcbp.meta = BoardingPassMetaData()

    # decode main fields
    bcbp.meta.format_code = main_section.get_next_string(LENGTHS.FORMAT_CODE)
    bcbp.meta.number_of_legs_encoded = (
        main_section.get_next_number(LENGTHS.NUMBER_OF_LEGS_ENCODED) or 0
    )
    bcbp.data.passenger_name = main_section.get_next_string(LENGTHS.PASSENGER_NAME)
    bcbp.meta.electronic_ticket_indicator = main_section.get_next_string(
        LENGTHS.ELECTRONIC_TICKET_INDICATOR
    )

    bcbp.data.legs = []
    added_unique_fields = False

    # decode legs
    for leg_index in range(bcbp.meta.number_of_legs_encoded):
        leg = Leg()

        # mandatory leg fields
        leg.operating_carrier_pnr_code = main_section.get_next_string(
            LENGTHS.OPERATING_CARRIER_PNR_CODE
        )
        leg.from_city_airport_code = main_section.get_next_string(
            LENGTHS.FROM_CITY_AIRPORT_CODE
        )
        leg.to_city_airport_code = main_section.get_next_string(
            LENGTHS.TO_CITY_AIRPORT_CODE
        )
        leg.operating_carrier_designator = main_section.get_next_string(
            LENGTHS.OPERATING_CARRIER_DESIGNATOR
        )
        leg.flight_number = main_section.get_next_string(LENGTHS.FLIGHT_NUMBER)
        leg.date_of_flight = main_section.get_next_date(
            LENGTHS.DATE_OF_FLIGHT, False, reference_year
        )
        leg.compartment_code = main_section.get_next_string(LENGTHS.COMPARTMENT_CODE)
        leg.seat_number = main_section.get_next_string(LENGTHS.SEAT_NUMBER)
        leg.check_in_sequence_number = main_section.get_next_string(
            LENGTHS.CHECK_IN_SEQUENCE_NUMBER
        )
        leg.passenger_status = main_section.get_next_string(LENGTHS.PASSENGER_STATUS)

        # conditional section
        conditional_section_size = main_section.get_next_section_size()
        conditional_section = SectionDecoder(
            main_section.get_next_string(conditional_section_size)
        )

        # unique fields (only in first leg)
        if not added_unique_fields:
            bcbp.meta.beginning_of_version_number = conditional_section.get_next_string(
                LENGTHS.BEGINNING_OF_VERSION_NUMBER
            )
            bcbp.meta.version_number = conditional_section.get_next_number(
                LENGTHS.VERSION_NUMBER
            )

            # section A
            section_a_size = conditional_section.get_next_section_size()
            section_a = SectionDecoder(
                conditional_section.get_next_string(section_a_size)
            )
            bcbp.data.passenger_description = section_a.get_next_string(
                LENGTHS.PASSENGER_DESCRIPTION
            )
            bcbp.data.source_of_check_in = section_a.get_next_string(
                LENGTHS.SOURCE_OF_CHECK_IN
            )
            bcbp.data.source_of_boarding_pass_issuance = section_a.get_next_string(
                LENGTHS.SOURCE_OF_BOARDING_PASS_ISSUANCE
            )
            bcbp.data.date_of_issue_of_boarding_pass = section_a.get_next_date(
                LENGTHS.DATE_OF_ISSUE_OF_BOARDING_PASS, True, reference_year
            )
            bcbp.data.document_type = section_a.get_next_string(LENGTHS.DOCUMENT_TYPE)
            bcbp.data.airline_designator_of_boarding_pass_issuer = (
                section_a.get_next_string(
                    LENGTHS.AIRLINE_DESIGNATOR_OF_BOARDING_PASS_ISSUER
                )
            )
            bcbp.data.baggage_tag_licence_plate_number = section_a.get_next_string(
                LENGTHS.BAGGAGE_TAG_LICENCE_PLATE_NUMBER
            )
            bcbp.data.first_non_consecutive_baggage_tag_licence_plate_number = (
                section_a.get_next_string(
                    LENGTHS.FIRST_NON_CONSECUTIVE_BAGGAGE_TAG_LICENCE_PLATE_NUMBER
                )
            )
            bcbp.data.second_non_consecutive_baggage_tag_licence_plate_number = (
                section_a.get_next_string(
                    LENGTHS.SECOND_NON_CONSECUTIVE_BAGGAGE_TAG_LICENCE_PLATE_NUMBER
                )
            )

            added_unique_fields = True

        # section B (leg-specific data)
        section_b_size = conditional_section.get_next_section_size()
        section_b = SectionDecoder(conditional_section.get_next_string(section_b_size))
        leg.airline_numeric_code = section_b.get_next_string(
            LENGTHS.AIRLINE_NUMERIC_CODE
        )
        leg.document_form_serial_number = section_b.get_next_string(
            LENGTHS.DOCUMENT_FORM_SERIAL_NUMBER
        )
        leg.selectee_indicator = section_b.get_next_string(LENGTHS.SELECTEE_INDICATOR)
        leg.international_documentation_verification = section_b.get_next_string(
            LENGTHS.INTERNATIONAL_DOCUMENTATION_VERIFICATION
        )
        leg.marketing_carrier_designator = section_b.get_next_string(
            LENGTHS.MARKETING_CARRIER_DESIGNATOR
        )
        leg.frequent_flyer_airline_designator = section_b.get_next_string(
            LENGTHS.FREQUENT_FLYER_AIRLINE_DESIGNATOR
        )
        leg.frequent_flyer_number = section_b.get_next_string(
            LENGTHS.FREQUENT_FLYER_NUMBER
        )
        leg.id_ad_indicator = section_b.get_next_string(LENGTHS.ID_AD_INDICATOR)
        leg.free_baggage_allowance = section_b.get_next_string(
            LENGTHS.FREE_BAGGAGE_ALLOWANCE
        )
        leg.fast_track = section_b.get_next_boolean()

        leg.for_individual_airline_use = conditional_section.get_remaining_string()

        bcbp.data.legs.append(leg)

    # security data
    bcbp.meta.beginning_of_security_data = main_section.get_next_string(
        LENGTHS.BEGINNING_OF_SECURITY_DATA
    )
    bcbp.data.type_of_security_data = main_section.get_next_string(
        LENGTHS.TYPE_OF_SECURITY_DATA
    )

    security_section_size = main_section.get_next_section_size()
    security_section = SectionDecoder(
        main_section.get_next_string(security_section_size)
    )
    bcbp.data.security_data = security_section.get_next_string(LENGTHS.SECURITY_DATA)

    # adjust flight dates based on issuance date
    if bcbp.data.date_of_issue_of_boarding_pass is not None:
        issuance_year = bcbp.data.date_of_issue_of_boarding_pass.year
        for leg in bcbp.data.legs:
            if leg.date_of_flight is not None:
                day_of_year = date_to_day_of_year(leg.date_of_flight)
                leg.date_of_flight = day_of_year_to_date(
                    day_of_year, False, issuance_year
                )
                if leg.date_of_flight < bcbp.data.date_of_issue_of_boarding_pass:
                    leg.date_of_flight = day_of_year_to_date(
                        day_of_year, False, issuance_year + 1
                    )

    return bcbp

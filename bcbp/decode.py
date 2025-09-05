from datetime import datetime
from typing import Optional
from . import field_lengths as LENGTHS
from .models import BarcodedBoardingPass, BoardingPassData, BoardingPassMetaData, Leg
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
            value = self.barcode_string[start:start + length]
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
    
    def get_next_date(self, length: int, has_year_prefix: bool, reference_year: Optional[int] = None) -> Optional[datetime]:
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


def decode(barcode_string: str, reference_year: Optional[int] = None) -> BarcodedBoardingPass:
    """Decode a BCBP barcode string to BarcodedBoardingPass object."""
    bcbp = BarcodedBoardingPass()
    main_section = SectionDecoder(barcode_string)
    
    bcbp.data = BoardingPassData()
    bcbp.meta = BoardingPassMetaData()
    
    # Decode main fields
    bcbp.meta.format_code = main_section.get_next_string(LENGTHS.FORMAT_CODE)
    bcbp.meta.number_of_legs = main_section.get_next_number(LENGTHS.NUMBER_OF_LEGS) or 0
    bcbp.data.passenger_name = main_section.get_next_string(LENGTHS.PASSENGER_NAME)
    bcbp.meta.electronic_ticket_indicator = main_section.get_next_string(LENGTHS.ELECTRONIC_TICKET_INDICATOR)
    
    bcbp.data.legs = []
    added_unique_fields = False
    
    # Decode legs
    for leg_index in range(bcbp.meta.number_of_legs):
        leg = Leg()
        
        # Mandatory leg fields
        leg.operating_carrier_pnr = main_section.get_next_string(LENGTHS.OPERATING_CARRIER_PNR)
        leg.departure_airport = main_section.get_next_string(LENGTHS.DEPARTURE_AIRPORT)
        leg.arrival_airport = main_section.get_next_string(LENGTHS.ARRIVAL_AIRPORT)
        leg.operating_carrier_designator = main_section.get_next_string(LENGTHS.OPERATING_CARRIER_DESIGNATOR)
        leg.flight_number = main_section.get_next_string(LENGTHS.FLIGHT_NUMBER)
        leg.flight_date = main_section.get_next_date(LENGTHS.FLIGHT_DATE, False, reference_year)
        leg.compartment_code = main_section.get_next_string(LENGTHS.COMPARTMENT_CODE)
        leg.seat_number = main_section.get_next_string(LENGTHS.SEAT_NUMBER)
        leg.check_in_sequence_number = main_section.get_next_string(LENGTHS.CHECK_IN_SEQUENCE_NUMBER)
        leg.passenger_status = main_section.get_next_string(LENGTHS.PASSENGER_STATUS)
        
        # Conditional section
        conditional_section_size = main_section.get_next_section_size()
        conditional_section = SectionDecoder(main_section.get_next_string(conditional_section_size))
        
        # Unique fields (only in first leg)
        if not added_unique_fields:
            bcbp.meta.version_number_indicator = conditional_section.get_next_string(LENGTHS.VERSION_NUMBER_INDICATOR)
            bcbp.meta.version_number = conditional_section.get_next_number(LENGTHS.VERSION_NUMBER)
            
            # Section A
            section_a_size = conditional_section.get_next_section_size()
            section_a = SectionDecoder(conditional_section.get_next_string(section_a_size))
            bcbp.data.passenger_description = section_a.get_next_string(LENGTHS.PASSENGER_DESCRIPTION)
            bcbp.data.check_in_source = section_a.get_next_string(LENGTHS.CHECK_IN_SOURCE)
            bcbp.data.boarding_pass_issuance_source = section_a.get_next_string(LENGTHS.BOARDING_PASS_ISSUANCE_SOURCE)
            bcbp.data.issuance_date = section_a.get_next_date(LENGTHS.ISSUANCE_DATE, True, reference_year)
            bcbp.data.document_type = section_a.get_next_string(LENGTHS.DOCUMENT_TYPE)
            bcbp.data.boarding_pass_issuer_designator = section_a.get_next_string(LENGTHS.BOARDING_PASS_ISSUER_DESIGNATOR)
            bcbp.data.baggage_tag_number = section_a.get_next_string(LENGTHS.BAGGAGE_TAG_NUMBER)
            bcbp.data.first_baggage_tag_number = section_a.get_next_string(LENGTHS.FIRST_BAGGAGE_TAG_NUMBER)
            bcbp.data.second_baggage_tag_number = section_a.get_next_string(LENGTHS.SECOND_BAGGAGE_TAG_NUMBER)
            
            added_unique_fields = True
        
        # Section B (leg-specific data)
        section_b_size = conditional_section.get_next_section_size()
        section_b = SectionDecoder(conditional_section.get_next_string(section_b_size))
        leg.airline_numeric_code = section_b.get_next_string(LENGTHS.AIRLINE_NUMERIC_CODE)
        leg.serial_number = section_b.get_next_string(LENGTHS.SERIAL_NUMBER)
        leg.selectee_indicator = section_b.get_next_string(LENGTHS.SELECTEE_INDICATOR)
        leg.international_documentation_verification = section_b.get_next_string(LENGTHS.INTERNATIONAL_DOCUMENTATION_VERIFICATION)
        leg.marketing_carrier_designator = section_b.get_next_string(LENGTHS.MARKETING_CARRIER_DESIGNATOR)
        leg.frequent_flyer_airline_designator = section_b.get_next_string(LENGTHS.FREQUENT_FLYER_AIRLINE_DESIGNATOR)
        leg.frequent_flyer_number = section_b.get_next_string(LENGTHS.FREQUENT_FLYER_NUMBER)
        leg.id_indicator = section_b.get_next_string(LENGTHS.ID_INDICATOR)
        leg.free_baggage_allowance = section_b.get_next_string(LENGTHS.FREE_BAGGAGE_ALLOWANCE)
        leg.fast_track = section_b.get_next_boolean()
        
        leg.airline_info = conditional_section.get_remaining_string()
        
        bcbp.data.legs.append(leg)
    
    # Security data
    bcbp.meta.security_data_indicator = main_section.get_next_string(LENGTHS.SECURITY_DATA_INDICATOR)
    bcbp.data.security_data_type = main_section.get_next_string(LENGTHS.SECURITY_DATA_TYPE)
    
    security_section_size = main_section.get_next_section_size()
    security_section = SectionDecoder(main_section.get_next_string(security_section_size))
    bcbp.data.security_data = security_section.get_next_string(LENGTHS.SECURITY_DATA)
    
    # Adjust flight dates based on issuance date
    if bcbp.data.issuance_date is not None:
        issuance_year = bcbp.data.issuance_date.year
        for leg in bcbp.data.legs:
            if leg.flight_date is not None:
                day_of_year = date_to_day_of_year(leg.flight_date)
                leg.flight_date = day_of_year_to_date(day_of_year, False, issuance_year)
                if leg.flight_date < bcbp.data.issuance_date:
                    leg.flight_date = day_of_year_to_date(day_of_year, False, issuance_year + 1)
    
    return bcbp
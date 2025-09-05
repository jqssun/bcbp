from datetime import datetime
from typing import Union, Optional
from . import field_lengths as LENGTHS
from .models import BarcodedBoardingPass, BoardingPassMetaData
from .utils import date_to_day_of_year, number_to_hex


class FieldSize:
    def __init__(self, size: int, is_defined: bool):
        self.size = size
        self.is_defined = is_defined


class SectionBuilder:
    def __init__(self):
        self.output = []
        self.field_sizes = []
    
    def add_field(self, field: Union[str, int, bool, datetime, None], length: Optional[int] = None, add_year_prefix: bool = False):
        """Add a field to the section with proper formatting."""
        value = ""
        
        if field is None:
            value = ""
        elif isinstance(field, bool):
            value = "Y" if field else "N"
        elif isinstance(field, (int, float)):
            value = str(field)
        elif isinstance(field, datetime):
            value = date_to_day_of_year(field, add_year_prefix)
        else:
            value = str(field)
        
        value_length = len(value)
        
        if length is not None:
            if value_length > length:
                value = value[:length]
            elif value_length < length:
                value = value + " " * (length - value_length)
        
        self.output.append(value)
        
        self.field_sizes.append(FieldSize(
            size=length if length is not None else len(value),
            is_defined=field is not None
        ))
    
    def add_section(self, section: 'SectionBuilder'):
        """Add another section to this section with length prefix."""
        section_string = section.to_string()
        
        found_last_value = False
        section_length = 0
        
        # Calculate section length by finding the last defined field (from the end)
        for field_size in reversed(section.field_sizes):
            if not found_last_value and field_size.is_defined:
                found_last_value = True
            
            if found_last_value:
                section_length += field_size.size
        
        self.add_field(number_to_hex(section_length), 2)
        self.add_field(section_string, section_length)
    
    def to_string(self) -> str:
        """Convert section to string."""
        return "".join(self.output)


def encode(bcbp: BarcodedBoardingPass) -> str:
    """Encode a BarcodedBoardingPass object to BCBP string format."""
    # Set default meta values if not provided
    if bcbp.meta is None:
        bcbp.meta = BoardingPassMetaData()
    
    bcbp.meta.format_code = bcbp.meta.format_code or "M"
    bcbp.meta.number_of_legs = bcbp.meta.number_of_legs or (len(bcbp.data.legs) if bcbp.data and bcbp.data.legs else 0)
    bcbp.meta.electronic_ticket_indicator = bcbp.meta.electronic_ticket_indicator or "E"
    bcbp.meta.version_number_indicator = bcbp.meta.version_number_indicator or ">"
    bcbp.meta.version_number = bcbp.meta.version_number or 6
    bcbp.meta.security_data_indicator = bcbp.meta.security_data_indicator or "^"
    
    barcode_data = SectionBuilder()
    
    if not bcbp.data or not bcbp.data.legs or len(bcbp.data.legs) == 0:
        return ""
    
    # Main mandatory fields
    barcode_data.add_field(bcbp.meta.format_code, LENGTHS.FORMAT_CODE)
    barcode_data.add_field(bcbp.meta.number_of_legs, LENGTHS.NUMBER_OF_LEGS)
    barcode_data.add_field(bcbp.data.passenger_name, LENGTHS.PASSENGER_NAME)
    barcode_data.add_field(bcbp.meta.electronic_ticket_indicator, LENGTHS.ELECTRONIC_TICKET_INDICATOR)
    
    added_unique_fields = False
    
    for leg in bcbp.data.legs:
        # Mandatory leg fields
        barcode_data.add_field(leg.operating_carrier_pnr, LENGTHS.OPERATING_CARRIER_PNR)
        barcode_data.add_field(leg.departure_airport, LENGTHS.DEPARTURE_AIRPORT)
        barcode_data.add_field(leg.arrival_airport, LENGTHS.ARRIVAL_AIRPORT)
        barcode_data.add_field(leg.operating_carrier_designator, LENGTHS.OPERATING_CARRIER_DESIGNATOR)
        barcode_data.add_field(leg.flight_number, LENGTHS.FLIGHT_NUMBER)
        barcode_data.add_field(leg.flight_date, LENGTHS.FLIGHT_DATE)
        barcode_data.add_field(leg.compartment_code, LENGTHS.COMPARTMENT_CODE)
        barcode_data.add_field(leg.seat_number, LENGTHS.SEAT_NUMBER)
        barcode_data.add_field(leg.check_in_sequence_number, LENGTHS.CHECK_IN_SEQUENCE_NUMBER)
        barcode_data.add_field(leg.passenger_status, LENGTHS.PASSENGER_STATUS)
        
        # Conditional section
        conditional_section = SectionBuilder()
        
        # Add unique fields only once (for first leg)
        if not added_unique_fields:
            conditional_section.add_field(bcbp.meta.version_number_indicator, LENGTHS.VERSION_NUMBER_INDICATOR)
            conditional_section.add_field(bcbp.meta.version_number, LENGTHS.VERSION_NUMBER)
            
            # Section A (unique passenger data)
            section_a = SectionBuilder()
            section_a.add_field(bcbp.data.passenger_description, LENGTHS.PASSENGER_DESCRIPTION)
            section_a.add_field(bcbp.data.check_in_source, LENGTHS.CHECK_IN_SOURCE)
            section_a.add_field(bcbp.data.boarding_pass_issuance_source, LENGTHS.BOARDING_PASS_ISSUANCE_SOURCE)
            section_a.add_field(bcbp.data.issuance_date, LENGTHS.ISSUANCE_DATE, True)
            section_a.add_field(bcbp.data.document_type, LENGTHS.DOCUMENT_TYPE)
            section_a.add_field(bcbp.data.boarding_pass_issuer_designator, LENGTHS.BOARDING_PASS_ISSUER_DESIGNATOR)
            section_a.add_field(bcbp.data.baggage_tag_number, LENGTHS.BAGGAGE_TAG_NUMBER)
            section_a.add_field(bcbp.data.first_baggage_tag_number, LENGTHS.FIRST_BAGGAGE_TAG_NUMBER)
            section_a.add_field(bcbp.data.second_baggage_tag_number, LENGTHS.SECOND_BAGGAGE_TAG_NUMBER)
            
            conditional_section.add_section(section_a)
            added_unique_fields = True
        
        # Section B (leg-specific data)
        section_b = SectionBuilder()
        section_b.add_field(leg.airline_numeric_code, LENGTHS.AIRLINE_NUMERIC_CODE)
        section_b.add_field(leg.serial_number, LENGTHS.SERIAL_NUMBER)
        section_b.add_field(leg.selectee_indicator, LENGTHS.SELECTEE_INDICATOR)
        section_b.add_field(leg.international_documentation_verification, LENGTHS.INTERNATIONAL_DOCUMENTATION_VERIFICATION)
        section_b.add_field(leg.marketing_carrier_designator, LENGTHS.MARKETING_CARRIER_DESIGNATOR)
        section_b.add_field(leg.frequent_flyer_airline_designator, LENGTHS.FREQUENT_FLYER_AIRLINE_DESIGNATOR)
        section_b.add_field(leg.frequent_flyer_number, LENGTHS.FREQUENT_FLYER_NUMBER)
        section_b.add_field(leg.id_indicator, LENGTHS.ID_INDICATOR)
        section_b.add_field(leg.free_baggage_allowance, LENGTHS.FREE_BAGGAGE_ALLOWANCE)
        section_b.add_field(leg.fast_track, LENGTHS.FAST_TRACK)
        
        conditional_section.add_section(section_b)
        conditional_section.add_field(leg.airline_info)
        barcode_data.add_section(conditional_section)
    
    # Security data section
    if bcbp.data.security_data is not None:
        barcode_data.add_field(bcbp.meta.security_data_indicator, LENGTHS.SECURITY_DATA_INDICATOR)
        barcode_data.add_field(bcbp.data.security_data_type or "1", LENGTHS.SECURITY_DATA_TYPE)
        
        security_section = SectionBuilder()
        security_section.add_field(bcbp.data.security_data, LENGTHS.SECURITY_DATA)
        barcode_data.add_section(security_section)
    
    return barcode_data.to_string()
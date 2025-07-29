# WFRMLS Python Client

A comprehensive Python wrapper for the Wasatch Front Regional MLS (WFRMLS) API, providing easy access to all RESO-certified endpoints.

## 🚀 Quick Start

```python
from wfrmls import WFRMLSClient

# Initialize client with bearer token
client = WFRMLSClient(bearer_token="your_bearer_token")

# Or use environment variable WFRMLS_BEARER_TOKEN
client = WFRMLSClient()

# Get active properties
properties = client.property.get_properties(
    top=10,
    filter_query="StandardStatus eq 'Active'"
)

# Get property details with photos
property_detail = client.property.get_property("12345678")
property_with_media = client.property.get_properties(
    filter_query="ListingId eq '12345678'",
    expand="Media"
)
```

## 📦 Installation

```bash
pip install wfrmls
```

## 🔧 Setup

### Environment Variables

Create a `.env` file in your project root:

```env
WFRMLS_BEARER_TOKEN=your_bearer_token_here
```

### Getting Your Bearer Token

1. Visit the [Vendor Dashboard](https://vendor.utahrealestate.com)
2. Login to your account
3. Navigate to Service Details to retrieve your bearer token

## 📚 API Reference

### Core Resources

- **Property** - Real estate listings and property data
- **Member** - Real estate agent information  
- **Office** - Brokerage and office details
- **OpenHouse** - Open house schedules and events
- **Media** - Property photos and media files

### Service Clients

```python
# Property operations
client.property.get_properties()
client.property.get_property(listing_id)
client.property.search_properties_by_radius(lat, lng, radius)

# Member (agent) operations  
client.member.get_members()
client.member.get_member(member_id)

# Office operations
client.office.get_offices()
client.office.get_office(office_id)

# Open house operations
client.openhouse.get_openhouses()
client.openhouse.get_openhouse(openhouse_id)

# Media operations
client.media.get_media()
client.media.get_media_for_property(property_id)
```

## 🔍 Advanced Features

### OData Query Support

```python
# Field selection
properties = client.property.get_properties(
    select=["ListingId", "ListPrice", "StandardStatus"],
    top=50
)

# Complex filtering
properties = client.property.get_properties(
    filter_query="ListPrice ge 200000 and ListPrice le 500000 and StandardStatus eq 'Active'",
    orderby="ListPrice desc"
)

# Include related data
properties = client.property.get_properties(
    expand=["Media", "Member"],
    top=25
)
```

### Geolocation Search

```python
# Search within radius (miles)
properties = client.property.search_properties_by_radius(
    latitude=40.7608,  # Salt Lake City
    longitude=-111.8910,
    radius_miles=10,
    additional_filters="StandardStatus eq 'Active'"
)

# Search within polygon area
polygon = [
    {"lat": 40.7608, "lng": -111.8910},
    {"lat": 40.7708, "lng": -111.8810},
    {"lat": 40.7508, "lng": -111.8710},
    {"lat": 40.7608, "lng": -111.8910}  # Close polygon
]

properties = client.property.search_properties_by_polygon(
    polygon_coordinates=polygon,
    additional_filters="PropertyType eq 'Residential'"
)
```

### Data Synchronization

```python
from datetime import datetime, timedelta

# Get incremental updates (recommended every 15 minutes)
cutoff_time = datetime.utcnow() - timedelta(minutes=15)
updates = client.property.get_properties(
    filter_query=f"ModificationTimestamp gt {cutoff_time.isoformat()}Z"
)

# Track deletions for data integrity
deleted_records = client.deleted.get_deleted(
    filter_query="ResourceName eq 'Property'"
)
```

## 🏗️ Architecture

The client follows a modular architecture with service separation:

```
WFRMLSClient
├── property          # Property listings
├── member           # Real estate agents  
├── office           # Brokerages/offices
├── openhouse        # Open house events
├── media            # Property photos
├── history_transactional  # Transaction history
├── lookup           # Lookup tables
├── deleted          # Deletion tracking
└── service_discovery     # API metadata
```

## ⚠️ Error Handling

```python
from wfrmls.exceptions import (
    WFRMLSError, 
    AuthenticationError, 
    NotFoundError, 
    RateLimitError
)

try:
    property = client.property.get_property("12345678")
except NotFoundError:
    print("Property not found")
except RateLimitError:
    print("Rate limit exceeded - wait before retrying")  
except AuthenticationError:
    print("Invalid bearer token")
except WFRMLSError as e:
    print(f"API error: {e}")
```

## 📊 Utah Grid Address System

The API supports Utah's unique grid address system:

```python
# Standard address: "123 Main Street"
# Grid address: "1300 E 9400 S"

# Grid addresses are automatically detected and handled
properties = client.property.get_properties(
    filter_query="StreetName eq '9400 S'"
)
```

## 🚦 Rate Limits

- **200 records** per request maximum
- **15-minute** recommended update frequency for data sync
- Use NextLink pagination for large datasets (more efficient than $skip)

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/theperrygroup/wfrmls.git
cd wfrmls

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -e .[dev]
```

### Running Tests

```bash
# Run tests with coverage
pytest --cov=wfrmls --cov-report=html

# Run specific test file
pytest tests/test_property.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black wfrmls tests
isort wfrmls tests

# Lint code
flake8 wfrmls tests
pylint wfrmls

# Type checking
mypy wfrmls
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the style guide in `STYLE_GUIDE.md`
4. Ensure 100% test coverage
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [API Documentation](https://docs.utahrealestate.com)
- [Vendor Dashboard](https://vendor.utahrealestate.com)
- [RESO Standards](https://www.reso.org/)

## 🆘 Support

For API access issues, contact UtahRealEstate.com support.
For library issues, open an issue in this repository. 
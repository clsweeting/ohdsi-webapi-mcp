# HTTP API Integration Tests

This directory contains comprehensive integration tests for the OHDSI WebAPI MCP HTTP API, organized by router for easier test value discovery and maintenance.

## Test Organization

### Main Test Files

- **`test_http_api.py`** - Comprehensive existing tests with realistic workflows
- **`test_integration.py`** - MCP server integration tests (subprocess-based)

### Router-Specific Test Files

The HTTP API integration tests are organized by router to make it easier to discover and maintain tests for specific functionality:

#### 🔍 `test_http_vocabulary.py`
Tests for vocabulary and concept search endpoints:
- Concept search with filters (domain, vocabulary, class)
- Concept details retrieval
- Concept hierarchy browsing (ancestors/descendants) 
- Domain and vocabulary listing
- Search pagination and limits
- Error handling for invalid concepts

**Key endpoints tested:** `/vocabulary/search`, `/vocabulary/details`, `/vocabulary/hierarchy`, `/vocabulary/domains`, `/vocabulary/vocabularies`

#### 📚 `test_http_concept_sets.py`
Tests for concept set management endpoints:
- Concept set creation from concept IDs
- Concept set creation from search queries
- Concept set details retrieval
- List existing concept sets
- Various inclusion options (descendants, mapped)
- Search-based concept set creation with filters
- Validation and error handling

**Key endpoints tested:** `/concept-sets/create`, `/concept-sets/create-from-search`, `/concept-sets/details`, `/concept-sets`

#### 👥 `test_http_cohorts.py`
Tests for cohort definition and management endpoints:
- Primary criteria definition
- Inclusion rule management
- Cohort validation
- Cohort size estimation
- Cohort listing and loading
- Cohort saving and cloning
- Cohort comparison
- Complete workflow integration

**Key endpoints tested:** `/cohorts/primary-criteria`, `/cohorts/inclusion-rules`, `/cohorts/validate`, `/cohorts/estimate-size`, `/cohorts`, `/cohorts/load`, `/cohorts/save`, `/cohorts/clone`, `/cohorts/compare`

#### ℹ️ `test_http_info.py`
Tests for WebAPI information and health endpoints:
- WebAPI info retrieval
- Version information
- Health checks
- Connectivity testing
- Response consistency
- Performance validation

**Key endpoints tested:** `/info`, `/info/version`, `/info/health`

#### ⚙️ `test_http_jobs.py`
Tests for background job monitoring endpoints:
- Job listing with filters
- Job status retrieval
- Job pagination
- Job type and status filtering
- Error handling for invalid job IDs
- Job response structure validation

**Key endpoints tested:** `/jobs`, `/jobs/{execution_id}`

#### 🗄️ `test_http_sources.py`
Tests for data source management endpoints:
- Data source listing
- Source details retrieval
- Default source information
- Source key validation
- Multi-database support testing
- Error handling for invalid sources

**Key endpoints tested:** `/sources`, `/sources/{source_key}`, `/sources/default/info`

#### 💾 `test_http_persistence.py`
Tests for definition persistence and storage endpoints:
- Definition saving and loading
- Definition listing with filters
- Definition deletion and cloning
- Import/export functionality
- Various definition types (cohort, concept_set, etc.)
- Export format support
- Workflow integration

**Key endpoints tested:** `/persistence/save`, `/persistence/load`, `/persistence/definitions`, `/persistence/delete`, `/persistence/clone`, `/persistence/export`, `/persistence/import`

## Running Tests

### Run All HTTP API Tests
```bash
# Run all HTTP API integration tests
pytest tests/integration/test_http*.py -v

# Run all integration tests (including MCP server tests)
pytest tests/integration/ -v
```

### Run Router-Specific Tests
```bash
# Run vocabulary tests only
pytest tests/integration/test_http_vocabulary.py -v

# Run cohorts tests only
pytest tests/integration/test_http_cohorts.py -v

# Run concept sets tests only
pytest tests/integration/test_http_concept_sets.py -v
```

### Run Tests with Coverage
```bash
# Run with coverage reporting
pytest tests/integration/test_http*.py --cov=src/ohdsi_webapi_mcp --cov-report=html
```

## Test Configuration

The tests require the following environment variables:

```bash
# Required for connecting to OHDSI WebAPI
WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI"

## Test Data and Fixtures

### Common Test Fixtures
- `client`: FastAPI TestClient for HTTP API testing  
- `sample_*`: Sample data fixtures for different entity types
- `app`: FastAPI application instance

### Test Data Guidelines
- Use well-known OMOP concept IDs (e.g., 201826 for Type 2 diabetes)
- Test with common vocabularies (SNOMED, RxNorm, ICD10CM)
- Include both positive and negative test cases
- Test edge cases and error conditions

## Test Design Principles

### 🎯 **Test Value Discovery**
Each test file is focused on a specific router, making it easy to find tests related to particular functionality.

### 🔧 **Maintainability**  
Tests are organized by functional area, with clear naming conventions and comprehensive docstrings.

### 🚀 **Realistic Scenarios**
Tests include both unit-level endpoint testing and realistic workflow scenarios.

### ⚡ **Performance Awareness**
Tests include timeouts and performance expectations for critical endpoints.

### 🛡️ **Error Resilience**
Comprehensive error handling testing for invalid inputs, missing data, and network issues.

## Contributing to Tests

When adding new HTTP API endpoints:

1. **Add tests to appropriate router file** based on functionality
2. **Include positive and negative test cases** 
3. **Add workflow integration tests** showing realistic usage
4. **Update this README** with new endpoint information
5. **Ensure tests are independent** and can run in any order

### Test Naming Conventions
- `test_{endpoint_name}_endpoint` - Basic endpoint functionality
- `test_{functionality}_integration` - Multi-step workflow tests
- `test_{feature}_edge_cases` - Edge cases and error conditions
- `test_{feature}_validation` - Input validation and error handling

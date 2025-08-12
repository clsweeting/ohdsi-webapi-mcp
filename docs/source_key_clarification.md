# Source ID vs Source Key Clarification

## The Issue

The original configuration used `WEBAPI_SOURCE_ID=SYNPUF1K` which was confusing because:
- **SYNPUF1K** is a **source key** (string identifier)
- **Source ID** suggests a numeric identifier

## The Fix

Updated the configuration to be consistent with OHDSI WebAPI terminology:

### Environment Variables
- **Before**: `WEBAPI_SOURCE_ID=SYNPUF1K` 
- **After**: `WEBAPI_SOURCE_KEY=SYNPUF1K`

### Configuration Class
```python
@dataclass
class McpServerConfig:
    webapi_base_url: str
    webapi_source_key: Optional[str] = None  # Changed from webapi_source_id
    log_level: str = "INFO"
```

## Understanding OHDSI Source Identifiers

OHDSI WebAPI uses two different identifiers for data sources:

### 1. Source ID (Integer)
- **Type**: `int` (e.g., `7`, `1`, `2`)
- **Usage**: Internal database primary key
- **Example**: `source_id=7`

### 2. Source Key (String)
- **Type**: `str` (e.g., `"SYNPUF1K"`, `"ATLASPROD"`, `"DEMO"`)
- **Usage**: Human-readable identifier for cohort generation and API endpoints
- **Example**: `source_key="SYNPUF1K"`

### WebAPI Endpoint Usage

**Cohort Generation Endpoints** (require source_key):
```python
# These use source_key (string)
client.cohorts.generate(cohort_id=123, source_key="SYNPUF1K")
client.cohorts.generation_status(cohort_id=123, source_key="SYNPUF1K")
client.cohorts.inclusion_rules(cohort_id=123, source_key="SYNPUF1K")
```

**Vocabulary/Concept Endpoints** (no source context needed):
```python
# These don't require source parameters
client.vocabulary.search_concepts("diabetes")
client.vocabulary.get_concept(201826)
```

## Real Example from Demo Server

```python
sources = client.sources.list()
for source in sources:
    print(f"ID: {source.source_id}, Key: {source.source_key}, Name: {source.source_name}")
    
# Output:
# ID: 7, Key: ATLASPROD, Name: Network prevalence counts
```

## Configuration Files Updated

1. **`.env.example`**: Changed `WEBAPI_SOURCE_ID=1` → `WEBAPI_SOURCE_KEY=SYNPUF1K`
2. **`DEVELOPMENT.md`**: Updated documentation to show correct variable name
3. **`server.py`**: Updated config class and loading function
4. **`tests/test_server.py`**: Updated test cases

## Why This Matters

- **Consistency**: Aligns with OHDSI WebAPI terminology
- **Clarity**: Makes it clear we're dealing with string identifiers
- **Functionality**: Cohort generation requires source_key, not source_id
- **Documentation**: Reduces confusion for users setting up the MCP server

## Correct Usage

```bash
# .env file
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI
WEBAPI_SOURCE_KEY=SYNPUF1K
LOG_LEVEL=INFO
```

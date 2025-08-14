# Source Key Configuration Guide

## Understanding WEBAPI_SOURCE_KEY

The `WEBAPI_SOURCE_KEY` environment variable is **optional** in most cases and serves as a convenience for setting a default data source.

### Key Points:

- **Not required for server startup** - The MCP server runs without it
- **Optional for most operations** - Most endpoints work independently of source configuration  
- **Can be overridden per-request** - Individual API calls can specify their own `source_key`
- **Only truly required for cohort size estimation** - And even then, can be passed as a request parameter

## When WEBAPI_SOURCE_KEY is Used

### Required (but can be provided per-request):
- **Cohort size estimation** (`estimate_cohort_size`)
  - Falls back to `WEBAPI_SOURCE_KEY` if no `source_key` provided in request
  - Throws error if neither is available

### Optional/Graceful:
- **Sources endpoints** - Uses it for default source info but works without it
- **Cohort validation** - Doesn't use source_key at all (just validates JSON structure)
- **Vocabulary/Concept endpoints** - No source context needed
- **All other endpoints** - Work independently

## Understanding OHDSI Source Identifiers

OHDSI WebAPI uses two different identifiers for data sources:

### 1. Source ID (Integer)
- **Type**: `int` (e.g., `7`, `1`, `2`)
- **Usage**: Internal database primary key
- **Example**: `source_id=7`

### 2. Source Key (String)
- **Type**: `str` (e.g., `"SYNPUF1K"`, `"EUNOMIA"`, `"DEMO"`)
- **Usage**: Human-readable identifier for cohort generation and API endpoints
- **Example**: `source_key="SYNPUF1K"`

## Configuration Options

### Option 1: No Default Source (Recommended)
```bash
# .env file
WEBAPI_BASE_URL=http://your-webapi-url
# No WEBAPI_SOURCE_KEY defined
```

**Benefits:**
- More flexible - specify sources per request as needed
- Works with multiple sources without reconfiguration
- Clearer about which operations need source context

### Option 2: With Default Source
```bash
# .env file
WEBAPI_BASE_URL=http://your-webapi-url
WEBAPI_SOURCE_KEY=EUNOMIA
```

**Benefits:**
- Convenience for single-source environments
- Default for cohort size estimation operations

## API Usage Examples

### Per-Request Source Specification (Preferred)
```python
# Cohort size estimation with explicit source
size_request = {
    "cohort_definition": {...},
    "source_key": "EUNOMIA"  # Explicit source per request
}
response = client.post("/cohorts/estimate-size", json=size_request)
```

### Multiple Sources in Same Session
```python
# Different sources for different operations
size_eunomia = client.post("/cohorts/estimate-size", 
                          json={"cohort_definition": {...}, "source_key": "EUNOMIA"})

size_synpuf = client.post("/cohorts/estimate-size", 
                         json={"cohort_definition": {...}, "source_key": "SYNPUF1K"})
```

### Operations That Don't Need Sources
```python
# These work regardless of WEBAPI_SOURCE_KEY configuration
concepts = client.post("/vocabulary/search", json={"query": "diabetes"})
validation = client.post("/cohorts/validate", json={"cohort_definition": {...}})
sources_list = client.get("/sources")
```

## Real Example from Demo Server

```python
sources = client.sources.list()
for source in sources:
    print(f"ID: {source.source_id}, Key: {source.source_key}, Name: {source.source_name}")
    
# Output:
# ID: 7, Key: EUNOMIA, Name: Synthetic Claims Data
# ID: 2, Key: SYNPUF1K, Name: SynPUF 1K Sample
```

## Best Practices

1. **Start without WEBAPI_SOURCE_KEY** - Most operations don't need it
2. **Specify sources per-request** - More explicit and flexible
3. **Use environment variable only for single-source setups** - When you always use the same source
4. **List available sources first** - Use `/sources` endpoint to discover what's available

## Common Misconceptions

❌ **"WEBAPI_SOURCE_KEY is required to start the server"**  
✅ Server starts and most operations work without it

❌ **"All operations need a source"**  
✅ Only cohort size estimation truly requires a source

❌ **"Must be set in environment"**  
✅ Can be provided per-request, which is often more flexible


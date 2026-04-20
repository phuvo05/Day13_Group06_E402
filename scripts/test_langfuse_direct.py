from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client

lf = get_client()

# Test auth
try:
    result = lf.auth_check()
    print("Auth check:", result)
except Exception as e:
    print("Auth error:", e)

# Create a trace directly
span = lf.start_span(name="test-span")
print("Span created, trace_id:", span.trace_id)
span.update(input={"test": "value"}, metadata={"message": "hello world"})
span.end()

# Get project info
print("Trace URL: https://cloud.langfuse.com/project/cmo6ibnd300d9ad08ewr0fwcp/traces/" + span.trace_id)

lf.flush()

# V1

Types:

```python
from samplehc.types import V1QueryAuditLogsResponse, V1SqlExecuteResponse
```

Methods:

- <code title="post /api/v1/audit-logs">client.v1.<a href="./src/samplehc/resources/v1.py">query_audit_logs</a>(\*\*<a href="src/samplehc/types/v1_query_audit_logs_params.py">params</a>) -> <a href="./src/samplehc/types/v1_query_audit_logs_response.py">V1QueryAuditLogsResponse</a></code>
- <code title="post /api/v1/sql">client.v1.<a href="./src/samplehc/resources/v1.py">sql_execute</a>(\*\*<a href="src/samplehc/types/v1_sql_execute_params.py">params</a>) -> <a href="./src/samplehc/types/v1_sql_execute_response.py">V1SqlExecuteResponse</a></code>

# V2

## AsyncResults

Types:

```python
from samplehc.types.v2 import AsyncResultRetrieveResponse
```

Methods:

- <code title="get /api/v2/async-results/{asyncResultId}">client.v2.async_results.<a href="./src/samplehc/resources/v2/async_results.py">retrieve</a>(async_result_id) -> <a href="./src/samplehc/types/v2/async_result_retrieve_response.py">AsyncResultRetrieveResponse</a></code>

## WorkflowRuns

Types:

```python
from samplehc.types.v2 import (
    WorkflowRunRetrieveResponse,
    WorkflowRunGetStartDataResponse,
    WorkflowRunResumeWhenCompleteResponse,
)
```

Methods:

- <code title="get /api/v2/workflow-runs/{workflowRunId}">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">retrieve</a>(workflow_run_id) -> <a href="./src/samplehc/types/v2/workflow_run_retrieve_response.py">WorkflowRunRetrieveResponse</a></code>
- <code title="put /api/v2/workflow-runs/{workflowRunId}/cancel">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">cancel</a>(workflow_run_id) -> object</code>
- <code title="get /api/v2/workflow-runs/start-data">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">get_start_data</a>() -> <a href="./src/samplehc/types/v2/workflow_run_get_start_data_response.py">WorkflowRunGetStartDataResponse</a></code>
- <code title="post /api/v2/workflow-runs/resume-when-complete">client.v2.workflow_runs.<a href="./src/samplehc/resources/v2/workflow_runs/workflow_runs.py">resume_when_complete</a>(\*\*<a href="src/samplehc/types/v2/workflow_run_resume_when_complete_params.py">params</a>) -> <a href="./src/samplehc/types/v2/workflow_run_resume_when_complete_response.py">WorkflowRunResumeWhenCompleteResponse</a></code>

### Step

Types:

```python
from samplehc.types.v2.workflow_runs import StepGetOutputResponse
```

Methods:

- <code title="get /api/v2/workflow-runs/step/{stepId}/output">client.v2.workflow_runs.step.<a href="./src/samplehc/resources/v2/workflow_runs/step.py">get_output</a>(step_id) -> <a href="./src/samplehc/types/v2/workflow_runs/step_get_output_response.py">StepGetOutputResponse</a></code>

## Tasks

Types:

```python
from samplehc.types.v2 import (
    TaskRetrieveResponse,
    TaskCancelResponse,
    TaskCompleteResponse,
    TaskGetSuspendedPayloadResponse,
    TaskRetryResponse,
    TaskUpdateScreenTimeResponse,
)
```

Methods:

- <code title="get /api/v2/tasks/{taskId}">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">retrieve</a>(task_id) -> <a href="./src/samplehc/types/v2/task_retrieve_response.py">TaskRetrieveResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/cancel">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">cancel</a>(task_id) -> <a href="./src/samplehc/types/v2/task_cancel_response.py">TaskCancelResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/complete">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">complete</a>(task_id, \*\*<a href="src/samplehc/types/v2/task_complete_params.py">params</a>) -> <a href="./src/samplehc/types/v2/task_complete_response.py">TaskCompleteResponse</a></code>
- <code title="get /api/v2/tasks/{taskId}/suspended-payload">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">get_suspended_payload</a>(task_id) -> <a href="./src/samplehc/types/v2/task_get_suspended_payload_response.py">TaskGetSuspendedPayloadResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/retry">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">retry</a>(task_id) -> <a href="./src/samplehc/types/v2/task_retry_response.py">TaskRetryResponse</a></code>
- <code title="post /api/v2/tasks/{taskId}/update-screen-time">client.v2.tasks.<a href="./src/samplehc/resources/v2/tasks/tasks.py">update_screen_time</a>(task_id, \*\*<a href="src/samplehc/types/v2/task_update_screen_time_params.py">params</a>) -> Optional[TaskUpdateScreenTimeResponse]</code>

### State

Types:

```python
from samplehc.types.v2.tasks import StateUpdateResponse, StateGetResponse
```

Methods:

- <code title="post /api/v2/tasks/{taskId}/state">client.v2.tasks.state.<a href="./src/samplehc/resources/v2/tasks/state.py">update</a>(task_id, \*\*<a href="src/samplehc/types/v2/tasks/state_update_params.py">params</a>) -> <a href="./src/samplehc/types/v2/tasks/state_update_response.py">StateUpdateResponse</a></code>
- <code title="get /api/v2/tasks/{taskId}/state">client.v2.tasks.state.<a href="./src/samplehc/resources/v2/tasks/state.py">get</a>(task_id) -> <a href="./src/samplehc/types/v2/tasks/state_get_response.py">StateGetResponse</a></code>

## Workflows

Types:

```python
from samplehc.types.v2 import WorkflowDeployResponse, WorkflowQueryResponse, WorkflowStartResponse
```

Methods:

- <code title="post /api/v2/workflows/{workflowId}/deploy">client.v2.workflows.<a href="./src/samplehc/resources/v2/workflows.py">deploy</a>(workflow_id) -> <a href="./src/samplehc/types/v2/workflow_deploy_response.py">WorkflowDeployResponse</a></code>
- <code title="post /api/v2/workflows/{workflowSlug}/query">client.v2.workflows.<a href="./src/samplehc/resources/v2/workflows.py">query</a>(workflow_slug, \*\*<a href="src/samplehc/types/v2/workflow_query_params.py">params</a>) -> <a href="./src/samplehc/types/v2/workflow_query_response.py">WorkflowQueryResponse</a></code>
- <code title="post /api/v2/workflows/{workflowSlug}/start">client.v2.workflows.<a href="./src/samplehc/resources/v2/workflows.py">start</a>(workflow_slug, \*\*<a href="src/samplehc/types/v2/workflow_start_params.py">params</a>) -> <a href="./src/samplehc/types/v2/workflow_start_response.py">WorkflowStartResponse</a></code>

## Documents

Types:

```python
from samplehc.types.v2 import (
    DocumentRetrieveResponse,
    DocumentClassifyResponse,
    DocumentCreateFromSplitsResponse,
    DocumentExtractResponse,
    DocumentGenerateCsvResponse,
    DocumentPresignedUploadURLResponse,
    DocumentRetrieveCsvContentResponse,
    DocumentRetrieveMetadataResponse,
    DocumentSearchResponse,
    DocumentSplitResponse,
    DocumentTransformJsonToHTMLResponse,
    DocumentUnzipResponse,
)
```

Methods:

- <code title="get /api/v2/documents/{documentId}">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">retrieve</a>(document_id) -> <a href="./src/samplehc/types/v2/document_retrieve_response.py">DocumentRetrieveResponse</a></code>
- <code title="post /api/v2/documents/classify">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">classify</a>(\*\*<a href="src/samplehc/types/v2/document_classify_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_classify_response.py">DocumentClassifyResponse</a></code>
- <code title="post /api/v2/documents/create-from-splits">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">create_from_splits</a>(\*\*<a href="src/samplehc/types/v2/document_create_from_splits_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_create_from_splits_response.py">DocumentCreateFromSplitsResponse</a></code>
- <code title="post /api/v2/documents/extract">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">extract</a>(\*\*<a href="src/samplehc/types/v2/document_extract_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_extract_response.py">DocumentExtractResponse</a></code>
- <code title="post /api/v2/documents/generate-csv">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">generate_csv</a>(\*\*<a href="src/samplehc/types/v2/document_generate_csv_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_generate_csv_response.py">DocumentGenerateCsvResponse</a></code>
- <code title="post /api/v2/documents/presigned-upload-url">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">presigned_upload_url</a>(\*\*<a href="src/samplehc/types/v2/document_presigned_upload_url_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_presigned_upload_url_response.py">DocumentPresignedUploadURLResponse</a></code>
- <code title="get /api/v2/documents/{documentId}/csv-content">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">retrieve_csv_content</a>(document_id) -> <a href="./src/samplehc/types/v2/document_retrieve_csv_content_response.py">DocumentRetrieveCsvContentResponse</a></code>
- <code title="get /api/v2/documents/{documentId}/metadata">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">retrieve_metadata</a>(document_id) -> <a href="./src/samplehc/types/v2/document_retrieve_metadata_response.py">DocumentRetrieveMetadataResponse</a></code>
- <code title="post /api/v2/documents/search">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">search</a>(\*\*<a href="src/samplehc/types/v2/document_search_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_search_response.py">DocumentSearchResponse</a></code>
- <code title="post /api/v2/documents/split">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">split</a>(\*\*<a href="src/samplehc/types/v2/document_split_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_split_response.py">DocumentSplitResponse</a></code>
- <code title="post /api/v2/documents/json-to-html">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">transform_json_to_html</a>(\*\*<a href="src/samplehc/types/v2/document_transform_json_to_html_params.py">params</a>) -> <a href="./src/samplehc/types/v2/document_transform_json_to_html_response.py">DocumentTransformJsonToHTMLResponse</a></code>
- <code title="post /api/v2/documents/{documentId}/unzip">client.v2.documents.<a href="./src/samplehc/resources/v2/documents/documents.py">unzip</a>(document_id) -> <a href="./src/samplehc/types/v2/document_unzip_response.py">DocumentUnzipResponse</a></code>

### Legacy

Types:

```python
from samplehc.types.v2.documents import LegacyExtractResponse, LegacyReasonResponse
```

Methods:

- <code title="post /api/v2/documents/legacy/extract">client.v2.documents.legacy.<a href="./src/samplehc/resources/v2/documents/legacy.py">extract</a>(\*\*<a href="src/samplehc/types/v2/documents/legacy_extract_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/legacy_extract_response.py">LegacyExtractResponse</a></code>
- <code title="post /api/v2/documents/legacy/reason">client.v2.documents.legacy.<a href="./src/samplehc/resources/v2/documents/legacy.py">reason</a>(\*\*<a href="src/samplehc/types/v2/documents/legacy_reason_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/legacy_reason_response.py">LegacyReasonResponse</a></code>

### Templates

Types:

```python
from samplehc.types.v2.documents import (
    TemplateGenerateDocumentAsyncResponse,
    TemplateRenderDocumentResponse,
)
```

Methods:

- <code title="post /api/v2/documents/templates/generate-document">client.v2.documents.templates.<a href="./src/samplehc/resources/v2/documents/templates.py">generate_document_async</a>(\*\*<a href="src/samplehc/types/v2/documents/template_generate_document_async_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/template_generate_document_async_response.py">TemplateGenerateDocumentAsyncResponse</a></code>
- <code title="post /api/v2/documents/templates/render">client.v2.documents.templates.<a href="./src/samplehc/resources/v2/documents/templates.py">render_document</a>(\*\*<a href="src/samplehc/types/v2/documents/template_render_document_params.py">params</a>) -> <a href="./src/samplehc/types/v2/documents/template_render_document_response.py">TemplateRenderDocumentResponse</a></code>

## Communication

Types:

```python
from samplehc.types.v2 import CommunicationSendFaxResponse
```

Methods:

- <code title="post /api/v2/communication/send-email">client.v2.communication.<a href="./src/samplehc/resources/v2/communication.py">send_email</a>(\*\*<a href="src/samplehc/types/v2/communication_send_email_params.py">params</a>) -> object</code>
- <code title="post /api/v2/communication/send-fax">client.v2.communication.<a href="./src/samplehc/resources/v2/communication.py">send_fax</a>(\*\*<a href="src/samplehc/types/v2/communication_send_fax_params.py">params</a>) -> <a href="./src/samplehc/types/v2/communication_send_fax_response.py">CommunicationSendFaxResponse</a></code>

## Clearinghouse

Types:

```python
from samplehc.types.v2 import ClearinghouseCheckEligibilityResponse
```

Methods:

- <code title="post /api/v2/clearinghouse/check-eligibility">client.v2.clearinghouse.<a href="./src/samplehc/resources/v2/clearinghouse/clearinghouse.py">check_eligibility</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse_check_eligibility_params.py">params</a>) -> <a href="./src/samplehc/types/v2/clearinghouse_check_eligibility_response.py">ClearinghouseCheckEligibilityResponse</a></code>
- <code title="post /api/v2/clearinghouse/coordination-of-benefits">client.v2.clearinghouse.<a href="./src/samplehc/resources/v2/clearinghouse/clearinghouse.py">coordination_of_benefits</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse_coordination_of_benefits_params.py">params</a>) -> object</code>

### Payers

Types:

```python
from samplehc.types.v2.clearinghouse import PayerListResponse, PayerRetrieveSearchResponse
```

Methods:

- <code title="get /api/v2/clearinghouse/payers">client.v2.clearinghouse.payers.<a href="./src/samplehc/resources/v2/clearinghouse/payers.py">list</a>() -> <a href="./src/samplehc/types/v2/clearinghouse/payer_list_response.py">PayerListResponse</a></code>
- <code title="get /api/v2/clearinghouse/payers/search">client.v2.clearinghouse.payers.<a href="./src/samplehc/resources/v2/clearinghouse/payers.py">retrieve_search</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse/payer_retrieve_search_params.py">params</a>) -> <a href="./src/samplehc/types/v2/clearinghouse/payer_retrieve_search_response.py">PayerRetrieveSearchResponse</a></code>

### Claim

Types:

```python
from samplehc.types.v2.clearinghouse import ClaimSubmitResponse
```

Methods:

- <code title="get /api/v2/clearinghouse/claim/{claimId}">client.v2.clearinghouse.claim.<a href="./src/samplehc/resources/v2/clearinghouse/claim.py">retrieve_status</a>(claim_id) -> object</code>
- <code title="post /api/v2/clearinghouse/claim">client.v2.clearinghouse.claim.<a href="./src/samplehc/resources/v2/clearinghouse/claim.py">submit</a>(\*\*<a href="src/samplehc/types/v2/clearinghouse/claim_submit_params.py">params</a>) -> <a href="./src/samplehc/types/v2/clearinghouse/claim_submit_response.py">ClaimSubmitResponse</a></code>

## Ledger

Types:

```python
from samplehc.types.v2 import (
    LedgerClaimAdjustmentResponse,
    LedgerClaimPaymentResponse,
    LedgerInstitutionAdjustmentResponse,
    LedgerInstitutionPaymentResponse,
    LedgerNewOrderResponse,
    LedgerOrderWriteoffResponse,
    LedgerPatientAdjustmentResponse,
    LedgerPatientPaymentResponse,
)
```

Methods:

- <code title="post /api/v2/ledger/claim-adjustment">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">claim_adjustment</a>(\*\*<a href="src/samplehc/types/v2/ledger_claim_adjustment_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_claim_adjustment_response.py">LedgerClaimAdjustmentResponse</a></code>
- <code title="post /api/v2/ledger/claim-payment">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">claim_payment</a>(\*\*<a href="src/samplehc/types/v2/ledger_claim_payment_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_claim_payment_response.py">LedgerClaimPaymentResponse</a></code>
- <code title="post /api/v2/ledger/institution-adjustment">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">institution_adjustment</a>(\*\*<a href="src/samplehc/types/v2/ledger_institution_adjustment_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_institution_adjustment_response.py">LedgerInstitutionAdjustmentResponse</a></code>
- <code title="post /api/v2/ledger/institution-payment">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">institution_payment</a>(\*\*<a href="src/samplehc/types/v2/ledger_institution_payment_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_institution_payment_response.py">LedgerInstitutionPaymentResponse</a></code>
- <code title="post /api/v2/ledger/new-order">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">new_order</a>(\*\*<a href="src/samplehc/types/v2/ledger_new_order_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_new_order_response.py">LedgerNewOrderResponse</a></code>
- <code title="post /api/v2/ledger/order-writeoff">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">order_writeoff</a>(\*\*<a href="src/samplehc/types/v2/ledger_order_writeoff_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_order_writeoff_response.py">LedgerOrderWriteoffResponse</a></code>
- <code title="post /api/v2/ledger/patient-adjustment">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">patient_adjustment</a>(\*\*<a href="src/samplehc/types/v2/ledger_patient_adjustment_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_patient_adjustment_response.py">LedgerPatientAdjustmentResponse</a></code>
- <code title="post /api/v2/ledger/patient-payment">client.v2.ledger.<a href="./src/samplehc/resources/v2/ledger.py">patient_payment</a>(\*\*<a href="src/samplehc/types/v2/ledger_patient_payment_params.py">params</a>) -> <a href="./src/samplehc/types/v2/ledger_patient_payment_response.py">LedgerPatientPaymentResponse</a></code>

## Integrations

### Snowflake

Types:

```python
from samplehc.types.v2.integrations import SnowflakeQueryResponse
```

Methods:

- <code title="post /api/v2/integrations/snowflake/{slug}/query">client.v2.integrations.snowflake.<a href="./src/samplehc/resources/v2/integrations/snowflake.py">query</a>(slug, \*\*<a href="src/samplehc/types/v2/integrations/snowflake_query_params.py">params</a>) -> <a href="./src/samplehc/types/v2/integrations/snowflake_query_response.py">SnowflakeQueryResponse</a></code>

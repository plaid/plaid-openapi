### 2020-09-14_1.652.0
- Add optional `cursor` and `count` fields to the `/payment_initiation/recipient/list` request and `next_cursor` to its response

### 2020-09-14_1.651.2
- (beta) Add `user_id` field to `link/token/create` request
- [BREAKING for Go] (beta) Make `user` object optional in `link/token/create` if `user_id` is included

### 2020-09-14_1.651.1
- Add `error` field to `WALLET_TRANSACTION_STATUS_UPDATE` webhook and to responses of `/wallet/transaction/get` and `/wallet/transaction/list`, containing error details for failed transactions.

### 2020-09-14_1.651.0
- Rename all `/verify/client/*` routes to `/protect/client/*` and update request/response body and field names accordingly.

### 2020-09-14_1.650.1
- Update description for `days_required`

### 2020-09-14_1.650.0
- Add `account_numbers` to `Counterparty` in `/transaction/get` and `/transaction/sync`

### 2020-09-14_1.649.2
- Add `InsitutionID` and `InstitutionName` to `/cra/monitoring_insights/get` response

### 2020-09-14_1.649.1
- Update max value for `cra_options.days_requested` in `link/token/create` to 731 (2 years + 1 days for leap year)
- Reduce max value for `cra_options.days_required` in `link/token/create` to 184 (most number of days in a 6 month period) from 730
- Set max value for `days_required` in `cra/check_report/create` to 184 (most number of days in a 6 month period)

### 2020-09-14_1.649.0
- Add wire_return_fee to Transfer and Transfer Event objects

### 2020-09-14_1.648.2
- Docs-only change to add additional subtypes to the accounts schema

### 2020-09-14_1.648.1
- Add `last_successful_update_time` to `/cashflow_report/get`

### 2020-09-14_1.648.0
- Add `require_identity` to `cra_options.base_report` in `link/token/create` and `/cra/check_report/create` requests 

### 2020-09-14_1.647.1
- Update `/transfer/ledger/distribute` summary

### 2020-09-14_1.647.0
- Add `webhook_codes` field to `/sandbox/cashflow_updates/update` request

### 2020-09-14_1.646.0
- [Breaking] Replacing `voe` references to instead be `employment_refresh` in `/cra/check_report/verification/get` and `/cra/check_report/create`
  - `/cra/check_report/verification/get`'s `reports_requested` options are now `VOA` and `employment_refresh`
  - `voe_options` in the request is now `employment_refresh_options`
  - `/cra/check_report/verification/get`'s response now has `report.employment_refresh` instead of `report.voe`
  - `gse_options.report_type` in `/cra/check_report/create` are now `VOA` and `employment_refresh` 

### 2020-09-14_1.645.1
- Update description of `/transfer/ledger/distribute`

### 2020-09-14_1.645.0
- Removes the `payment_details` field from `/accounts/balance/get` request
- Removes the `payment_risk_assessment` from `/accounts/balance/get` response

### 2020-09-14_1.644.1
- Fixed incorrect event type in example for `ProtectUserEventWebhook`.

### 2020-09-14_1.644.0
- [Breaking] For Signal, remove enum values `REAL_TIME_PAYMENTS` and `DEBIT_CARD` as these payment methods are not supported by the Signal product.
- [Breaking] Rename client library `/cra/check_report/create`'s `partner_insights` object to type `CraCheckReportCreatePartnerInsightsOptions` instead of `CraCheckReportPartnerInsightsGetOptions`. All the object fields are identical.
- [Breaking] Rename client library `/cra/check_report/partner_insights/get`'s `option.prism_versions` object to type `PrismVersionsDeprecated` instead of `PrismVersions`. All the object fields' are identical.

### 2020-09-14_1.642.2
- Added `ProtectUserEventWebhook`.

### 2020-09-14_1.642.1
- Deprecated `/link/token/create`'s `base_report`. Revert erroneous deprecation of `cra_options.base_report`.

### 2020-09-14_1.642.0
- Add `error` field to responses of `/payment_initiation/payment/get` and `/payment_initiation/consent/payment/execute` containing error details when the payment fails.

### 2020-09-14_1.641.1
- Fix descriptions for BaseReportAccountMetadata

### 2020-09-14_1.641.0
- Deprecated `/link/token/create`'s `cra_options.base_report` object in favor of `cra_options.client_report_id`

### 2020-09-14_1.640.0
- [Breaking] Add /cashflow_report/transactions/get route, identital to /cashflow_report/get minus days_requested request parameter
- Remove historical_balances from BusinessAccounts object

### 2020-09-14_1.639.0
- Add `webhook` field to `/session/token/create` request

### 2020-09-14_1.638.6
- Deprecate Prism Products field from Partner Insights generation and retrieval

### 2020-09-14_1.638.5
- Add client report id to partner insights

### 2020-09-14_1.638.4
- Remove unused enums for MonitoringInsightsStatus and MonitoringItemStatusCode

### 2020-09-14_1.638.3
- Add Prism Detect and Extend cashscores to CRA Partner Insights 

### 2020-09-14_1.638.2
- (beta) expect a boolean instead of a string in generated client interfaces for PLAID-NEW-USER-API-ENABLED

### 2020-09-14_1.638.1
- Support for upcoming results in `link/token/get`.

### 2020-09-14_1.638.0
-  (pre-release) Preparation for upcoming products.

### 2020-09-14_1.637.6
- Deprecate `report.items.accounts.account_insights` for `/cra/check_report/base_report/get`

### 2020-09-14_1.637.5
- Fix incorrect placement of `nullable: true` on `AccountBaseNullable` object, making the object actually `nullable`.

### 2020-09-14_1.637.4
- Add missing `unsent` value as a possible `verification_status` to reflect actual API behavior.

### 2020-09-14_1.637.3
- (beta) Add `PLAID-NEW-USER-API-ENABLED` as a header parameter to `/user/create`
- (beta) Add `PLAID-NEW-USER-API-ENABLED` as a header parameter to `/user/remove`

### 2020-09-14_1.637.2
- (beta) Add `user_id` to `/session/token/create` response

### 2020-09-14_1.637.1
- Add optional `institution_id` to `/item/import`

### 2020-09-14_1.637.0
- Add `android_package_name` to `/session/token/create`

### 2020-09-14_1.636.0
- Update `average_inflow_amount` to be positive.

### 2020-09-14_1.635.4
- [BREAKING] (beta) Updated `user_token` field in `UserCreateResponse` to be optional.
- [BREAKING for Go] (beta) Updated `user_token` field in `UserRemoveRequest` to be optional.
- Other hidden changes.

### 2020-09-14_1.635.3
- (beta) Add `user_id` to `/link/token/create` response

### 2020-09-14_1.635.2
- Update description of `ruleset.outcome` in `/signal/evaluate` response

### 2020-09-14_1.635.1
- Fix description undeprecating `report.items.accounts.attributes` after it was mistakenly deprecated for `/cra/check_report/base_report/get`

### 2020-09-14_1.635.0
- Add `expected_funds_available_date` to `transfer` and `sweep` objects in responses for `/transfer/create`, `/transfer/get`, `/transfer/list`, `/transfer/sweep/get`, `/transfer/sweep/list`

### 2020-09-14_1.634.3
- Undeprecated `report.items.accounts.attributes` after it was mistakenly deprecated for `/cra/check_report/base_report/get`

### 2020-09-14_1.634.2
- Removed `deposit_switch` from the `products` field in the `/link/token/create` request

### 2020-09-14_1.634.1
- [BREAKING] Move `result` from `triggered_rule_details` to `ruleset` in response of `/signal/evaluate`

### 2020-09-14_1.634.0
- [BREAKING] `client_user_id` is now required for `/session/token/create`

### 2020-09-14_1.633.1
- [BREAKING] Update `account` object to nullable in `/processor/transactions/sync` response

### 2020-09-14_1.633.0
- Move `user_id` field of `/session/token/create` request to be within `user`

### 2020-09-14_1.632.6
- Update descriptions for `CashFlowUpdatesLowBalanceWebhook` and `CashFlowUpdatesLargeDepositWebhook`

### 2020-09-14_1.632.5
- Add new `CashFlowUpdatesInsightsWebhook` for Cash Flow Updates

### 2020-09-14_1.632.4
- Add `triggered_rule_details` to `/signal/evaluate` response

### 2020-09-14_1.632.3
- [BREAKING] Update `webhook` field in `IssuesSubscribeRequest` to be required

### 2020-09-14_1.632.2
- Update the `warnings` field in `/cra/check_report/verification/get` response to be required

### 2020-09-14_1.632.1
- Add `AT` and `FI` to the list of available countries

### 2020-09-14_1.632.0
- Add `user_id` field to `/session/token/create` request

### 2020-09-14_1.631.0
- [BREAKING] Correct the schema object returned by `AssetReport` `investments` field -- it is now correctly represented as an `AssetReportInvestments` object, not an `AssetReportInvestmentsTransaction` object, to accurately reflect the API behavior.

### 2020-09-14_1.630.0
- Add optional `income_categories` param to `/cra/monitoring_insights/subscribe` request

### 2020-09-14_1.629.0
- [Breaking] Date of birth is now required within consumer report user identity for `user/create` and `user/update`

### 2020-09-14_1.628.4
- Renamed CRA Cash Flow Updates webhook types

### 2020-09-14_1.628.3
- Adde `warnings` to responses for `cra/check_report/income_insights/get`, `cra/check_report/network_insights/get`, `cra/check_report/cashflow_insights/get`, and `cra/check_report/partner_insights/get`

### 2020-09-14_1.628.2
- Update description for the `options.add_ons` field in `asset_reports/create`

### 2020-09-14_1.628.1
- Add `client_report_id` field to `cra/check_report/create` request and deprecate `base_report.client_report_id` field in `cra/check_report/create`.
- Add `client_report_id` field to `LinkTokenCreateRequestCraOptions` field
- Deprecate `client_report_id` field in `LinkTokenCreateRequestBaseReport`
- Add `client_report_id` field to `CraIncomeInsights`

### 2020-09-14_1.628.0
- Add `redirect_uri` field to `/session/token/create` request

### 2020-09-14_1.627.1
- Update description of `transfer_id` field on `TransferEvent` schema to be empty string for Plaid Ledger Sweep events

### 2020-09-14_1.627.0
- [BREAKING] Update `posted_date` field on `/statements/list` response to be nullable

### 2020-09-14_1.626.0
- Add reason_code field to /transfer/cancel request

### 2020-09-14_1.625.2
- Add `USER_PERMISSION_REVOKED` and `USER_ACCOUNT_REVOKED` webhook codes to `WebhookCodeEnum` in `SandboxItemFireWebhookRequest` to reflect actual API behavior.

### 2020-09-14_1.625.1
- Add new `verification_name` field to `Account`

### 2020-09-14_1.625.0
- Add new `posted_date` field to `/statements/list` response

### 2020-09-14_1.624.0
- (pre-release) Add `human_review` object to the `analysis`  object within each `documentary_verification.documents` object. This change affects the response of all of the identity verification endpoints:
   - `identity_verification/create`
   - `identity_verification/get`
   - `identity_verification/list`
   - `identity_verification/retry`

### 2020-09-14_1.623.0

### 2020-09-14_1.622.0
- [BREAKING] Updated the `investments` schema returned by `/asset_report/get` (`AssetReportInvestments`) to accurately reflect the actual API behavior, including renaming the schema object
- Updated the Auth descriptions to reflect the fact that the preferred method to enable database and micro-deposit-based Auth verification flows is now the Dashboard, and that Database Insights has been deprecated and replaced by the similar product Database Auth.

### 2020-09-14_1.621.0
- [BREAKING] Changed `score` in `PlaidCheckScore` from a float to an integer

### 2020-09-14_1.620.0
- Add `intent_id` field to `/transfer/event/sync` response

### 2020-09-14_1.619.1
- Add new `cashflow_updates` webhook triggers
- Remove `reason` field from `MonitoringInsightsWebhook`

### 2020-09-14_1.619.0
- Add `/session/token/create` endpoint

### 2020-09-14_1.618.2
- Add `beacon_user_id` to `/beacon/report_syndication/get` and `/beacon/report_syndication/list` response

### 2020-09-14_1.618.1
- `/cashflow_report/get` endpoint is added. This includes defining the `CashflowReportGetRequest` and `CashflowReportGetResponse` fields. Adding `access_token` as required field in `CashflowReportRefreshRequest`.

### 2020-09-14_1.618.0
- Add `attributes` object to `BaseReport` definition.

### 2020-09-14_1.617.6
- `/cashflow_report/refresh` endpoint is added. This includes defining the `CashflowReportRefreshRequest` and `CashflowReportRefreshResponse` fields.

### 2020-09-14_1.617.5
- `submitted_at` is added as an optional field to `/signal/decision/report`.

### 2020-09-14_1.617.4
- `persistentId` and `isTokenizedAccountNumber` fields now only populated for select institutions in sandbox related to TAN-based institutions (ins_13, ins_56) or the default testing OAuth institution (ins_127287)

### 2020-09-14_1.617.3
- Modified how contribution transactions are summed up in `account_details_401k.contribution_details` object in `/investments/auth/get` endpoint.

### 2020-09-14_1.617.2
- Updated PrismCashScore and PrismFirstDetect to allow Score in /cra/check_report/partner_insights/get to be nullable

### 2020-09-14_1.617.1
- For Plaid Check: `date_of_birth` is now required within the `consumer_report_user_identity` object when creating or updating a user token.

### 2020-09-14_1.617.0
- [Breaking] Removed the deprecated longest_gap_between_transactions, average_inflow_amount, and average_outflow_amount fields from the BaseReportAccountInsights object in the /cra/check_report/base_report/get response.

### 2020-09-14_1.616.0
- Add `originating_fund_source` to `/wallet/transaction/execute` endpoint.

### 2020-09-14_1.615.0
- Add `account_details_401k` objects to `/investments/auth/get` endpoint.

### 2020-09-14_1.614.1
- Update `owners` field description for empty case

### 2020-09-14_1.614.0
- Add model for the new `retirement_401k` numbers object to the `InvestmentsAuthGetNumbers` schema.

### 2020-09-14_1.613.0
- Add `POST /signal/schedule` endpoint

### 2025-01-27_1.611.0
- Add `end_to_end_id` to `/payment_initiation/payment/get`

### 2020-09-14_1.611.0
- Add RfP to /transfer/capabilities/get

### 2020-09-14_1.610.2
- Update `cashflow_updates` docs to reflect proper cadence

### 2020-09-14_1.610.1
- Add `funds_available` sweep status and event type

### 2020-09-14_1.610.0
- Add `PaymentInitiationConsentStatusUpdateWebhook` definition.

### 2020-09-14_1.609.0
- Remove `/profile/get` and `/link/profile/eligibility/check` endpoints

### 2020-09-14_1.608.0
- Remove erroneous UserToken object from LinkTokenGetMetadataResponse, as the specification was incorrect and the object was never returned as part of the response.

### 2020-09-14_1.607.0
- Add failure_code and description fields to `/transfer/sweep/get` and `transfer/sweep/list` endpoints. Deprecated `ach_return_code` field of the TransferFailure and TransferRefundFailure objects.

### 2020-09-14_1.606.1
- Updated description to `funding_account_id` field of `transfer/ledger/deposit` and `transfer/ledger/withdraw`

### 2020-09-14_1.606.0
- Add `sandbox/payment/simulate` endpoint to enable testing of payment status transitions.

### 2020-09-14_1.605.0
- Add `nsf_overdraft_transactions_count_30d/60d/90d` fields to `attributes` field of `cra/check_report/base_report/get`

### 2020-09-14_1.604.1
- Add `account_id` to `/transactions/sync` request `options` object.

### 2020-09-14_1.603.2
- Fix incorrect `USER_ACCOUNT_REVOKED` schema and example

### 2020-09-14_1.603.1
- Internal changes only

### 2020-09-14_1.603.0
- (pre-release) Add `fraud_analysis_details` and `image_quality_details` objects to the `analysis`  object within each `documentary_verification.documents` object. These changes affect the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.602.1
- Documentation-only change to `/cra/monitoring_insights/subscribe` for cadence

### 2020-09-14_1.602.0
- Added `payer_details` field to `payment_initiation/consent/get` response

### 2020-09-14_1.601.2
- Documentation-only change to Investments `Security` object for new Fixed Income fields and sandbox availability

### 2020-09-14_1.601.1
- Update descriptions for `/network/status/get` request fields

### 2020-09-14_1.601.0
- Clean up legacy `/cra/base_report/*` endpoints from libraries in favor of `/cra/check_report/*`
  endpoints.

### 2020-09-14_1.600.2
- Update descriptions for `/network/status/get` request and response fields
- Add `nullable: true` to mortgage `account_number` field in the `MortgageLiability` schema to reflect actual behavior.
- Add `transactions_refresh` to `Products` array to reflect actual behavior; this field is not accepted as input to `/link/token/create` but can be part of supported products array in the `Institution` object.

### 2020-09-14_1.600.1
- `depository`+`cash management` Accounts are now eligible for Auth data for certain institutions

### 2020-09-14_1.600.0
- Added `is_tokenized_account_number` to the `numbers.ach` object

### 2020-09-14_1.599.0
- Added `auth_method` field to `Item` object

### 2020-09-14_1.598.0
- Add `user_insights_id` to `/cra/monitoring_insights/get` response
-
### 2020-09-14_1.597.0
- (beta) Add /network/status/get endpoint

### 2020-09-14_1.596.0
- Unhide `/sandbox/cra/cashflow_updates/update`

### 2020-09-14_1.595.0
- Add `ruleset_key` to `/transfer/authorization/create` request

### 2020-09-14_1.594.0
- Deprecated `consumer_dispute_id` field on consumer dispute object

### 2020-09-14_1.593.0
- Add `fixed_income` object (which contains the `yield_rate`, `maturity_date`, `issue_date`, and `face_value` fields) to the Security object (Investments)

### 2020-09-14_1.592.1

### 2020-09-14_1.592.0
- Add `/sandbox/cra/cashflow_updates/update` endpoint

### 2020-09-14_1.591.1
- Hide `TransferMigratedFundingAccountIDRequest` from docs

### 2020-09-14_1.591.0
- (pre-release) Add overall `risk_level`, and in some cases `factors` to each type of `risk_check` object. Also add `first_party_synthentic_fraud` and `third_party_synthentic_fraud` objects to`risk_check.identity_abuse_signals.synthetic_identity`. These changes affect the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.590.0
- Add `webhook` field to `TransferPlatformOriginatorCreateRequest`

### 2020-09-14_1.589.0
- Add `PLATFORM_ONBOARDING_UPDATE` webhook for transfer

### 2020-09-14_1.588.0
- Add `/processor/investments/transactions/get` endpoint

### 2020-09-14_1.587.1
- Add `institution_name` field in the `Item` object

### 2020-09-14_1.587.0
- Add `/processor/investments/holdings/get` endpoint

### 2020-09-14_1.586.4
- Update `cause` and make it nullable

### 2020-09-14_1.586.3
- Update `email` description in `/user_account/session/get` response

### 2020-09-14_1.586.2
- Update `event_type` description of `/sandbox/transfer/simulate`. Added `funds_available` to status list

### 2020-09-14_1.586.1
- [Breaking] Changed `ConsentEventCode` enum values. Replaced `PLAID_END_USER_PRIVACY_POLICY` with `USER_AGREEMENT`

### 2020-09-14_1.586.0
- Add `webhook` field to requests for `/sandbox/transfer/simulate`, `/sandbox/transfer/refund/simulate`, `/sandbox/transfer/ledger/simulate_available` and `/sandbox/transfer/sweep/simulate`.

### 2020-09-14_1.585.5
- Correct a typo in /link/token/create description

### 2020-09-14_1.585.4
- Updated transition date to move away from deprecated fields in CRA Base Report API

### 2020-09-14_1.585.3
- Fixed erroneous missing `last_statement_balance` field in `StudentLoan` object -- field was returned in API but not in specification.

### 2020-09-14_1.585.2
- Remove minimum length for `end_customer` in `user/create`

### 2020-09-14_1.585.1
- Deprecate `options` in `payment_initiation/consent/create`

### 2020-09-14_1.585.0
- [Breaking] Created `ItemWithConsentFields`, a new object definition that extends the `Item` object to include 1033-related consent fields.
- [Breaking] Removed the 1033-related consent fields from the `Item` object, ensuring that these fields now only appear in the `ItemWithConsentFields` object within the `/item/get` response.

### 2020-09-14_1.584.1
- Deprecated `version` in `cra/check_report/partner_insights/get` in favor of `model_version`

### 2020-09-14_1.584.0
- Made total inflow/outflow amount fields in the `cra/check_report/base_report/get` response nullable

### 2020-09-14_1.583.1
- Updated `description` field in `payment_configuration` object in `/link/token/create` to be optional

### 2020-09-14_1.583.0
- Added total inflow/outflow amount fields to `attributes` object in the `cra/check_report/base_report/get` response

### 2020-09-14_1.582.0
- Added a new field in `/link/token/create`

### 2020-09-14_1.581.0
-  Update `verify_sms` object in the response of all of the identity verification endpoints to add `redacted_at` timestamp:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.580.4
- Fixed an incorrect example response in `/user_account/session/get`

### 2020-09-14_1.580.3
- Fix wrong nullable annotation in `/signal/evaluate` response

### 2020-09-14_1.580.2
- Make `scores` nullable in `/signal/evaluate` and `/processor/signal/evaluate` response

### 2020-09-14_1.580.1
- Add new `payer_details` field to `payment_initiation/consent/create` in preparation to new account restrictions

### 2020-09-14_1.579.1
- Add new `type` field to `payment_initiation/consent/create` and deprecate the `scopes` field

### 2020-09-14_1.578.1
-  Update `verify_sms` object in the response of all of the identity verification endpoints to support nullable `verification.phone_number` and expand allowed statuses for `verification.status`:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.578.0
-  Add `verify_sms` object in the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.577.1
- Added support for `signal` to `required_if_supported_products`.
- Added support for `cra_network_insights` to `Products` array.
- Define `MonitoringInsightsWebhook`
- Fix definition for JWTHeader object

### 2020-09-14_1.577.0
- Updated description for the `is_primary_account` field of base reports

### 2020-09-14_1.576.0
- Expose beacon_user_id in `/identity_verification/*` endpoints
- Added new optional parameter `days_required` to `cra_options` in `/link/token/create` and to `/cra/check_report/create`
- Added new metadata object with `start_date` and `end_date` in the responses for:
    - `/cra/check_report/base_report/get`
    - `/cra/check_report/income_insights/get`
    - `/cra/check_report/partner_insights/get`

### 2020-09-14_1.575.1
- Update `date_of_birth` field description in `user/create`

### 2020-09-14_1.575.0
- Add `primary_account_score` and `is_primary_account` fields to the `cra/check_report/base_report/get` response

### 2020-09-14_1.574.1
- Add `FAILED` enum for Monitoring

### 2020-09-14_1.574.0
- Make `MonitoringInsights` nullable

### 2020-09-14_1.573.2
- Update session results array fields in `/link/token/get` response to be required

### 2020-09-14_1.573.1
- mark `category_id` in BaseReport transaction as nullable
- Update `date_of_birth` description in `user/create`

### 2020-09-14_1.573.0
- Removed `is_missing_income` from `/cra/monitoring_insights/get`

### 2020-09-14_1.572.0
- Add `uuid` validation for `subscription_id` in `/cra/monitoring_insights/get`
- Add `ConsumerReportPermissiblePurpose` to `CraMonitoringInsightsGetRequest`
- Add `HistoricalAnnualIncome` insight

### 2020-09-14_1.571.0
- Add `attributes` and `nsf_overdraft_transactions_count` to `cra/check_report/base_report/get`

### 2020-09-14_1.570.3
- Update product list for `/partner/customer/create`

### 2020-09-14_1.570.2
- Add `predicted_next_date` field to `/transactions/recurring/get`

### 2020-09-14_1.570.1
- Add `end_customer` hidden field to `user/create` for client RealPage

### 2020-09-14_1.569.5
- Show `date_of_birth` on the open API doc

### 2020-09-14_1.569.4
- Add `ssn_last_4` to ConsumerReportUserIdentity

### 2020-09-14_1.569.3
- Add `USER_FRAUD_ALERT` to BaseReportWarningCode

### 2020-09-14_1.569.2
- Removed erroneous `required` attribute from `request_id` field in LinkMetadataEvent object.

### 2020-09-14_1.569.1
-  Add `processing_mode` field to the `PaymentInitiationConsentPaymentExecuteRequest` object for the `/payment_initiation/consent/payment/execute` endpoint

### 2020-09-14_1.568.1
- Updated description of CRA Base Report API fields with new deprecation date

### 2020-09-14_1.568.0
-  Add `name` object to the `extracted_data` within each `documentary_verification.documents` object in the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.567.5
- Add `error_reason` to `/cra/check_report/partner_insights/get`

### 2020-09-14_1.567.4
- [internal only] Hiding plaid_check_score_version from docs

### 2020-09-14_1.567.3
- Update description for `email` field in `/identity_verification/create` and `/identity_verification/retry` to include link to RFC specification on email format

### 2020-09-14_1.567.2
- Publish processor Paynote

### 2020-09-14_1.567.1
- Update description for `add_ons` field in `/asset_report/create`

### 2020-09-14_1.567.0
- [BREAKING] removed `products` field from `cra/check_report/create` request

### 2020-09-14_1.566.0
- Added `status` to the `MonitoringInsightsWebhook` object
- Changed `webhook_code` to be deterministic

### 2020-09-14_1.565.1
- Update `days_available` field description for Asset Reports and CRA Base Reports.

### 2020-09-14_1.565.0
- Removed `deposit_switch` from the `products` field in the `/link/token/create` request
- Deprecated DepositSwitch endpoints, requests and response

### 2020-09-14_1.564.0
- add `/issues/get`, `/issues/search`, and `/issues/subscribe` for Support API endpoints.

### 2020-09-14_1.563.0
- Update fields on `item` object in `/item/get` response
    - Add `consented_use_cases` field
    - Add `consented_data_scopes` field
    - Add `created_at` field
    - Update descriptions for `consented_products` and `consent_expiration_time` fields
- Add `/consent/events/get` endpoint

### 2020-09-14_1.157.1
- Internal changes

### 2020-09-14_1.157.0
- (pre-release) Add `facial_analysis` to the `analysis` within each `selfie_check.selfies` object in the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.156.2
- [BREAKING] Remove `from_client_id` and `to_client_id` from `/transfer/ledger/distribute` request
- Add `from_ledger_id` and `to_ledger_id` to `/transfer/ledger/distribute` request
- Add `ledger_id` in transfer routes response examples

### 2020-09-14_1.156.1
- Update `account type schema` link to reference the correct URL.

### 2020-09-14_1.562.0
- Add `data_sources` object to the `/investments/auth/get` response
    - `data_sources` object contains the `numbers`, `owners`, and `holdings` fields

### 2020-09-14_1.561.0
- [BREAKING] Add `authorization_id` to /transfer/get request and make `transfer_id` optional.

### 2020-09-14_1.560.0
- Add `pay_by_bank` to product enum list

### 2020-09-14_1.559.0
- Add `name`, `is_default` to /transfer/ledger/get response
- [BREAKING] Move `ledger_id` from nested `balance` struct to top level in /transfer/ledger/get response

### 2020-09-14_1.558.0
- Add `liveness_check` to the `analysis` within each `selfie_check.selfies` object in the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.557.2
- Internal changes only

### 2020-09-14_1.557.1
- Internal changes only

### 2020-09-14_1.557.0
- Add `ledger_id` to /transfer/ledger/get response

### 2020-09-14_1.556.0
- Added plural named array fields to `BaseReportAccountInsights` in  /cra/base_report/get

### 2020-09-14_1.555.0
- Add `require_all_items` field to /asset_report/create

### 2020-09-14_1.554.0
- Add `sector` and `industry` properties to the `Security` model.

### 2020-09-14_1.553.0
- Add `ISSUE_RESOLVED` webhook

### 2020-09-14_1.552.0
- Add `ytd_amount` to `PaystubOverrideEarningsTotal` in /credit/payroll_income/get

### 2020-09-14_1.551.0
- Internal changes only

### 2020-09-14_1.550.0
- Add `/fdx/recipient` and `/fdx/recipients` endpoints

### 2020-09-14_1.549.0
- Made fields required instead of omitempty for CRA Income Insights Transactions

### 2020-09-14_1.548.4
- Set CreditAmountWithCurrency fields as required

### 2020-09-14_1.548.3
- Added missing `LOGIN_REPAIRED` enum value to possible webhook codes for `/sandbox/item/fire_webhook` request in order to match endpoint description.

### 2020-09-14_1.548.2
- [BREAKING] Moved `forecasted_monthly_income` to be a level higher.

### 2020-09-14_1.548.1
- Made the fields in account_insights array fields as required.

### 2020-09-14_1.548.0
- [BREAKING] Changed fields of `CraMonitoringGetResponse` to be simple `objects` instead of `arrays`
- [BREAKING] Moved `income_sources` to the `income` module in the response

### 2020-09-14_1.547.2
- Add `cra_item_add_results` field to `results` object in `/link/token/get` response.

### 2020-09-14_1.547.1
- Increase `/wallet/transactions/list` cursor size to 1024 characters.

### 2020-09-14_1.547.0
- Add `ledger_id` to the request and response of a number of transfer endpoints.

### 2020-09-14_1.546.0
- Added `WalletTransactionRelation` object.
- Added `related_transactions` field to WalletTransaction object.

### 2020-09-14_1.545.3
- Some description updates to CRA Base Report fields

### 2020-09-14_1.545.2
- Updated phone number examples in Identity Verification endpoints.

### 2020-09-14_1.545.1
- Add `update.item_ids` field to `/link/token/create` request.

### 2020-09-14_1.545.0
- [BREAKING] Rename network attributes to network insights in the `cra/check_report/network_insights/get` schemas

### 2020-09-14_1.544.0
- Added `is_shareable` field to the `/identity_verification/retry` endpoint

### 2020-09-14_1.543.2
- [Breaking] Added `data_breach` report type to BeaconReport response object

### 2020-09-14_1.543.1
- Added `consumer_statement` field to `Account` in `BaseReport`
- make `warnings` for BaseReportGetResponse required

### 2020-09-14_1.543.0
- Add `/network_insights/report/get`

### 2020-09-14_1.542.0
- Added `error_code_reason` field to plaidError

### 2020-09-14_1.541.1
- Add `update.user` field to `/link/token/create` request.

### 2020-09-14_1.541.0
- (pre-release) Add `reauthorization_enabled` field to /link/token/create request

### 2020-09-14_1.540.2
- [Breaking] Updated `document_status` field in `identity/document/upload` to include parsing_type

### 2020-09-14_1.540.1
- Added `MonitoringInsightsWebhook`
- Added `webhook` field in `cra/monitoring_insights/subscribe`

### 2020-09-14_1.540.0
- Added `file_type` field to `/credit/payroll_income/risk_signals/get`

### 2020-09-14_1.539.0
- Add `authorization_usage` field to the `transfer/metrics/get` response

### 2020-09-14_1.538.0
- Added cra/monitoring_insights/subscribe
- Added cra/monitoring_insights/unsubscribe
- Added cra/monitoring_insights/get

### 2020-09-14_1.537.0
- Added depository_accounts to Beacon
- Added event_date to BeaconReports

### 2020-09-14_1.536.0
- Internal changes only

### 2020-09-14_1.535.3

- Added missing values to `PlaidErrorType` enum.

### 2020-09-14_1.535.2
- Make some `CraBankIncomeSummary` fields visible.

### 2020-09-14_1.535.1

### 2020-09-14_1.535.0
- [Breaking for Go] Updated `consumer_report_user_identity` field in `/user/update` to be required to reflect actual API behavior.

### 2020-09-14_1.534.7
- Add `stated_account_number_enabled` to `investments_auth` in `LinkTokenCreateRequest`

### 2020-09-14_1.534.6
- [Breaking] Updated base report endpoints and objects to include `cra` prefix

### 2020-09-14_1.534.5
- Add `enable_multi_item_link` field to `/link/token/create`

### 2020-09-14_1.534.4
- Undeprecate `/identity/match`'s `legal_name.is_business_name_detected`

### 2020-09-14_1.534.3
- Add 'Beacon' to product enum list and make available in `/link/token/create` products

### 2020-09-14_1.534.2
- Mark some `BaseReportAccountInsights` fields as optional.

### 2020-09-14_1.534.1

- Internal changes only

### 2020-09-14_1.533.1
- Add `user_action_required` to transfer authorization's `decision` enum.
- Add `authorization_id` to transfer object in `/link/token/create` request.

### 2020-09-14_1.533.0
- Made `user` request field optional in `beacon/user/update`

### 2020-09-14_1.532.4
- fix `/cra/check_report/pdf/get` external doc url

### 2020-09-14_1.532.3
- Docs updates

### 2020-09-14_1.532.2
- [Breaking] Rename `/cra/check_report/network_attributes/get` to `/cra/check_report/network_insights/get`

### 2020-09-14_1.532.1

- Internal changes only

### 2020-09-14_1.531.1
- Update idempotency key expiration time to 48 hours in `virtual-accounts/#wallet-transaction-execute-request-idempotency-key`

### 2020-09-14_1.531.0
- Add `balance_plus` to `products` in `LinkTokenCreateRequest`
- Add `balance_plus` to `additional_consented_products` in `LinkTokenCreateRequest`

### 2020-09-14_1.530.0
- Add `/user/remove` endpoint

### 2020-09-14_1.529.0
- Added `/sandbox/user/reset_login` endpoint

### 2020-09-14_1.528.0
- Added `beacon/user/account_insights/get` endpoint
- Updated `description`field for `access_tokens` in `beacon/user/create` and `beacon/user/update` requests
- [Breaking] Renamed `/user_account/session/get` operationId `sessionGet` to `userAccountSessionGet` for consistency with existing API naming scheme.

### 2020-09-14_1.527.0
- [Breaking] Removed `development.plaid.com` as a valid server and updated docs to remove references to Development, due to the decomissioning of the Development environment

### 2020-09-14_1.526.1
- Add `/user/items/get` endpoint

### 2020-09-14_1.526.0
- Add `/cra/check_report/network_attributes/get`

### 2020-09-14_1.525.1

[Breaking] Renamed `bank_income` to `report` in the `cra/check_report/income_insights/get` response

### 2020-09-14_1.524.1

- [Breaking] Remove `minLength` validations from several attributes. Fixes multiple validation bugs in the ruby client libraries which do not handle `nil` gracefully before this change.

### 2020-09-14_1.524.0

- Add transfer refund event types to TransferEventType enum.

### 2020-09-14_1.523.0

- Added support for the `layer` product.

### 2020-09-14_1.522.0

- Added support for the `/user_account/session/get` API.

### 2020-09-14_1.521.0

- Internal changes only

### 2020-09-14_1.520.0

- [Breaking] Contains fixes to Balance Plus (beta):
    - [Breaking] Convert `risk_level` string to an enum object `RiskLevel`.
    - [Breaking] Adds missing `required` labels to certain fields within `BalancePlusAttributes`, `AccountsBalanceGetResponsePaymentRiskAssessment`, `AccountsBalanceGetRequestPaymentDetails`, and `RiskReason`.
    - Adds missing `additionalProperties` field to `BalancePlusAttributes`
    - Fix incorrect response example for Balance Plus
    - Docs updates for Balance Plus

### 2020-09-14_1.519.0

- Add `rtp` to network options in `/transfer/intent/create`
- Added `access_tokens` field to `/beacon/user/create` and `/beacon/user/update` requests
- Added `item_ids` to `/beacon/user/*` responses

### 2020-09-14_1.518.9

- Update `description` field for `decision_rationale` in `transfer/authorization/create` response

### 2020-09-14_1.518.8

- Fix incorrect documentation for ENTITY_SCREENING: STATUS_UPDATED webhook which wrongly documented `screening_id` instead of `entity_screening_id` in the payload.

### 2020-09-14_1.518.7

- Internal changes only

### 2020-09-14_1.518.6

- Add `add_ons` in cra/check_report/pdf/get

### 2020-09-14_1.518.5

- Internal changes only

### 2020-09-14_1.518.4

- Add `Recall` as a possible Virtual Account wallet transaction type

### 2020-09-14_1.518.3

- Internal changes only

### 2020-09-14_1.518.2

- Documentation edits to cra endpoints
- Add `income-sensitive repayment` to StudentRepaymentPlan and update description for repayment plan type

### 2020-09-14_1.518.1

- Documentation edits to cra endpoints
- Add item, account, and transaction IDs to `/cra/base_report/get` response

### 2020-09-14_1.518.0

- Add several cra related properties to `/user/create` and `/link/token/create`

### 2020-09-14_1.517.7

- Add `cra/check_report/pdf/get` endpoint

### 2020-09-14_1.517.6

- Add `cra/check_report/base_report/get` endpoint

### 2020-09-14_1.517.5

- Add `error_message` to `document_metadata` object for `credit/payroll_income/get` and `credit/bank_statements/uploads/get`

### 2020-09-14_1.517.4

- Add `production` to the `secrets` object in `/partner/customer/create` response and deprecate `development`

### 2020-09-14_1.517.3

- Add new enums to `canonical_description` in `credit/payroll_income/get`: `RETIREMENT`, `GIG ECONOMY`, and `STOCK COMPENSATION`

### 2020-09-14_1.517.2

- Added `ITEM: EVENTS` webhook and example to documentation

### 2020-09-14_1.517.1

- Added `public_tokens` on `SESSION_FINISHED` webhook
- Deprecated `public_token` on `SESSION_FINISHED` webhook
- Added `ITEM_ADD_RESULT` webhook

### 2020-09-14_1.517.0

- [Breaking] Update `/link/token/get` response structure

### 2020-09-14_1.516.0

- Internal changes only

### 2020-09-14_1.515.0

- Added `/cra/loans/applications/register`
- Added `/cra/loans/register`
- Added `/cra/loans/update`
- Added `/cra/loans/unregister`

### 2020-09-14_1.514.2

- Added `days_since_first_observed transaction` as a field in the Account Risk Insights response.

### 2020-09-14_1.514.1

- Update `risk_profile_key`and `RiskProfile` description

### 2020-09-14_1.514.0

- Added `transfer/authorization/cancel` endpoint

### 2020-09-14_1.513.0

- Added `consumer_report/pdf/get` endpoint

### 2020-09-14_1.512.0

- Added support for address and date of birth in `/payment_initiation/payment/reverse` request.

### 2020-09-14_1.511.0

- Added `user_token` to `link/token/get` response metadata
- Internal changes

### 2020-09-14_1.510.2

- Added `include_insights` to `/credit/relay/get` request
-

### 2020-09-14_1.510.1

- Add `database_insights_pending` as a potential enum value to `LinkDeliveryVerificationStatus` and `LinkSessionSuccessMetadataAccount.VerificationStatus`.
- Remove `database_insights_pass`, `database_insights_pass_with_caution` and `database_insights_fail` as potential values from `LinkDeliveryVerificationStatus` and `LinkSessionSuccessMetadataAccount.VerificationStatus`

### 2020-09-14_1.510.0

- Internal changes only

### 2020-09-14_1.509.4

- Internal changes only

### 2020-09-14_1.509.3

- Update description of transfer authorization decision code `MANUALLY_VERIFIED_ITEM`

### 2020-09-14_1.509.2

- Fixes to `RemovedTransaction` object definition: set `additionalProperties` explicitly to true and list `account_id` and `transaction_id` as `required`.

### 2020-09-14_1.509.1

- add `SMS_MICRODEPOSITS_VERIFICATION` to the `webhook_code` field of `/sandbox/item/fire_webhook`

### 2020-09-14_1.509.0

- Add `supports_payment_consents` to institution's `payment_initiation_metadata`.

### 2020-09-14_1.508.0

- Add new fields to `/cra/bank_income/get` endpoint

### 2020-09-14_1.507.3

- Add `paystub` and `w2` values to custom sandbox configuration schema

### 2020-09-14_1.507.2

- Mark `/transfer/balance/get` endpoint deprecated

### 2020-09-14_1.507.1

- Update `funds_available` description

### 2020-09-14_1.507.0

- Add `funds_available` transfer status and transfer event type

### 2020-09-14_1.506.0

- Add `statements` to the `options` field in the request object for `/sandbox/public_token/create` endpoint

### 2020-09-14_1.505.1

- Internal changes only

### 2020-09-14_1.505.0

- Add `profile` product

### 2020-09-14_1.504.2

- [Breaking] Update `network` field type in `/transfer/recurring/create` request from `TransferACHNetwork` to `TransferRecurringNetwork` as recurring now supports rtp.
- [Breaking] Update `network` field type in `RecurringTransfer` and `RecurringTransferNullable` from `TransferACHNetwork` to `TransferRecurringNetwork` as recurring now supports rtp.

### 2020-09-14_1.504.1

- Documentation updates for `/transactions/sync` and Database Match / Database Insights (beta).

### 2020-09-14_1.504.0

- Add new fields to `/transactions/sync` and `/processor/transactions/sync` endpoints

### 2020-09-14_1.503.6

- [Breaking change for Go client library] Make `start_date` and `end_date` required in the `statements` object for the `/link/token/create` endpoint

### 2020-09-14_1.503.5

- Improve description for `RiskCheckIdentityAbuseSignals`

### 2020-09-14_1.503.4

- Improve description for `TransferNetworkTraceID`

### 2020-09-14_1.503.3

- Update description for `TransferNetworkTraceID`

### 2020-09-14_1.503.2

- Change `forecasted_average_monthly_income_prediction_intervals` to plural.

### 2020-09-14_1.503.1

- Add `has_more` field to /transfer/event/list and /transfer/event/sync to indicate there are more events to be pulled

### 2020-09-14_1.503.0

- Add new `/cra/base_report/create` endpoint

### 2020-09-14_1.502.4

- Add `sms_microdeposits_verification_enabled` to `auth` object inside `/link/token/create` calls.

### 2020-09-14_1.502.3

- Added descriptions for `vested_quantity` and `vested_amount` fields for `investments/holdings/get`
- Removed description for `vested_quantity` and `vested_amount` fields for `HoldingsOverride` object (for sandbox)

### 2020-09-14_1.502.2

- [Breaking] Update `network` field type in `/transfer/recurring/create` request from `TransferNetwork` to `TransferACHNetwork` since recurring currently only works for ACH.
- [Breaking] Update `network` field type in `RecurringTransfer` and `RecurringTransferNullable` from `TransferNetwork` to `TransferACHNetwork` since recurring currently only works for ACH.

### 2020-09-14_1.502.1

- Update description for `/item/remove` and `/asset_report/remove`

### 2020-09-14_1.502.0

- Add `client_report_id` fields to `/link/token/create` and `/cra/base_report/get`

### 2020-09-14_1.501.2

- Updating `insights` field in `/cra/partner_insights/get` response to contain both numerical and string values

### 2020-09-14_1.501.1

- Enable original description for all customers on `/transactions/get` endpoint

### 2020-09-14_1.501.0

[Breaking change for Go client library] Mark `address` field in `/beacon/user/create` as optional

### 2020-09-14_1.500.0

- Remove `prime_trust` processor partner

### 2020-09-14_1.499.2

- Fix broken link from previous update

### 2020-09-14_1.499.1

- Updated doc url for some Transfer and processor endpoints to support documentation reorganization
- Minor documentation updates and clarifications

### 2020-09-14_1.499.0

- [Breaking change for Go client library] Make `account_id` optional in `/transactions/recurring/get` endpoint

### 2020-09-14_1.489.3

- Update description of `network_trace_id`

### 2020-09-14_1.489.2

- Correct documentation to indicate that `assets` is not supported in the `additional_consented_products` field
- Remove `additionalProperties: true` incorrectly applied to `transferIntentGet` object and missed in `2020-09-14_1.352.0`. This will result in more strict type checking for this object, but should not be a breaking change.

### 2020-09-14_1.498.1

- Enable original description for all customers

### 2020-09-14_1.498.0

- Add `POST /beacon/account_risk/v1/evaluate` endpoint

### 2020-09-14_1.497.0

- Add `institution_id` to `processor/account/get` endpoint.

### 2020-09-14_1.496.5

- Update the description and enum values for `linked_services` in the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.496.4

Add `POST /beacon/user/history/list`

### 2020-09-14_1.496.3

- Add `timestamp` to the beacon user's `audit_trail` object
- Add `version` to the beacon user object.

### 2020-09-14_1.496.2

- Adds prediction interval to `/cra/bank_income/get`

### 2020-09-14_1.496.1

- Update the descriptions for `risk_level` and `score` in `/accounts/balance/get`

### 2020-09-14_1.496.0

- Add `verification_insights` object to `Account` (closed beta feature - Database Insights)
- Add `database_insights_pass`, `database_insights_pass_with_caution`, and `database_insights_fail` as new values for `verification_status` field (closed beta feature - Database Insights)

### 2020-09-14_1.495.2

- Add `pending idr` to student loan liability statuses

### 2020-09-14_1.495.1

- Add `processor_identity` product

### 2020-09-14_1.494.1

- Mark `wire_details` as nullable in the transfer object

### 2020-09-14_1.494.0

- Add `vested_quantity` and `vested_value` fields to the `Holding` object.

### 2020-09-14_1.493.0

- Add `POST /cra/partner_insights/get`

### 2020-09-14_1.492.1

- Added documentation for the `HOSTED_VERIFICATION` webhook.
- Add `wire` to request and response of `/transfer/authorization/create`

### 2020-09-14_1.492.0

- Remove `page_count`, `name`, and `status` fields from Identity Document Upload's document metadata.

### 2020-09-14_1.491.3

- Increase max length of description field on `/transfer/intent/create` from 8 to 15

### 2020-09-14_1.491.2

- Added documentation for the `securities.type` field in `investments/holdings/get` and `investments/transactions/get` endpoints.

### 2020-09-14_1.491.1

- Add new `no_data` type to `name` and `date_of_birth` fields in `documentary_verification.documents[].analysis.extracted_data` in the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.491.0

- Add `identity` object to `link/token/create` request body

### 2020-09-14_1.490.0

- Add `events` field to the `sessions` parameter in the `/link/token/get` response

### 2020-09-14_1.489.1

- Mark optional `scope` and `reference` fields in `/payment_initiation/consent/payment/execute` as nullable

### 2020-09-14_1.489.0

- Add optional `scope` and `reference` fields to `/payment_initiation/consent/payment/execute`

### 2020-09-14_1.488.0

- Add optional `item_ids` field to the request of `credit/payroll_income/get` and `credit/bank_statements/uploads/get`

### 2020-09-14_1.487.2

- Add `num_1099s_uploaded` to `document_income_results` object in `/credit/sessions/get` response

### 2020-09-14_1.487.1

- Correct the Document Income Verification `parsing_config` enum used by `/link/token/create` to contain `risk_signals` instead of `fraud_risk` to match the actual API implementation.
- Dcumentation updates to reflect updates to Signal, including that new Items with Signal should now be created with `signal` in `/link/token/create` instead of using `/signal/prepare`.

### 2020-09-14_1.487.0

- [Breaking] Introduce a new `AssetReportAccountBalance` object which duplicates the existing `AccountBalance` object with an additional `margin_loan_amount` field. Updated `AccountAssets.balances` to return the new `AssetReportAccountBalance` object instead of the existing `AccountBalance` object.
- Add `vested_quantity` and `vested_value` fields to the `AssetReportInvestments` object.

### 2020-09-14_1.486.1

- Update `bank_income_sources` in CRA Bank Income Get to be required in response since the empty array is being omitted.

### 2020-09-14_1.486.0

- Add `requires_real_time_balance_refresh`, `risk_reasons`, `attributes`, `balance_last_updated`, and `score` fields to `/accounts/balance/get` endpoint

### 2020-09-14_1.485.1

- Update `legal_name` description in `user` object in `/link/token.create` request

### 2020-09-14_1.485.0

- Add `/processor/liabilities/get` endpoint

### 2020-09-14_1.484.1

- Add `/identity_verification/autofill/create` (closed beta)

### 2020-09-14_1.484.0

- Add `/statements/refresh` endpoint

### 2020-09-14_1.483.2

- Add `/beacon/duplicate/get` route

### 2020-09-14_1.483.1

- Internal changes only

### 2020-09-14_1.483.0

- Added net new fields to StatementsAccount object: `account_mask`, `account_subtype`, `account_official_name`

### 2020-09-14_1.482.3

- Update `description` description for `/transfer/create`

### 2020-09-14_1.482.2

- Update /credit/relay/get response example

### 2020-09-14_1.482.1

- Update `funding_account_id` description for `/transfer/intent/create`

### 2020-09-14_1.482.0

- Adds a new field `payment_details` to `/accounts/balance/get` request
- Adds a new field `payment_risk_assessment` to `/accounts/balance/get` response

### 2020-09-14_1.481.1

- Update `USER_ACCOUNT_REVOKED` description and set to visible

### 2020-09-14_1.481.0

- Add `available` to balance object in `wallet/get` and `wallet/list` response

### 2020-09-14_1.480.1

- Documentation-only change to Investments `Security` object for new fields and sandbox availability

### 2020-09-14_1.480.0

- Add `phone_number` to `/transactions/enrich` response

### 2020-09-14_1.479.0

- [Breaking change for Go client library] Make `street` and `city` optional in the address attribute of `identity_verification/create`

### 2020-09-14_1.478.4

- Add `registration_number` to `/partner/customer/create` request

### 2020-09-14_1.478.3

- Update `/identity/get` response for identity document upload beta customers

### 2020-09-14_1.478.2

- Deprecate `funding_account_id` from `/transfer/recurring/create` request

### 2020-09-14_1.478.1

- Description-only changes to support Hosted Link (beta)

### 2020-09-14_1.478.0

- Add `market_identifier_code` and `option_contract` fields in the Security (investment) object
- `option_contract` object contains `contract_type`, `expiration_date`, `strike_price`, and `underlying_security_ticker`

### 2020-09-14_1.477.1

- Changes `last_user_modified_date` to `last_user_modified_datetime` on transaction stream object.

### 2020-09-14_1.477.0

- Bug fix nullability definitions for `/beacon/user/create` and `/beacon/user/update` request payloads

### 2020-09-14_1.476.1

- Update Recurring Transaction description

### 2020-09-14_1.476.0

- Add `/beacon/user/update`

### 2020-09-14_1.475.0

- Add `/beacon/report_syndication/get` route

### 2020-09-14_1.474.4

- Add Statements Refresh webhook

### 2020-09-14_1.474.3

- Internal changes only

### 2020-09-14_1.474.2

- Deprecate `credit_funds_source` in `/transfer/authorization/create` request

### 2020-09-14_1.474.1

- Added `identity_match` to Products schema object

### 2020-09-14_1.474.0

- Added `statements/refresh` endpoint

### 2020-09-14_1.473.0

- Add Beacon webhooks

### 2020-09-14_1.472.0

- Change client library visibility of `options.transactions.days_requested` field for `/link/token/create` and `/sandbox/public_token/create`
- Add `options.days_requested` field to `/transactions/get` and `/transactions/sync`

### 2020-09-14_1.471.0

[Breaking change for Go client libraries] Make `products` field in `/institutions/search` request optional to fix https://github.com/plaid/plaid-ruby/issues/476

### 2020-09-14_1.470.1

- Bug fixes and improvements

### 2020-09-14_1.470.0

- Add balance insights firleds to CRA Base Reports

### 2020-09-14_1.469.1

- Change visibility of `/transactions/recurring/streams/...` endpoints

### 2020-09-14_1.469.0

- Update date format in Base reports

### 2020-09-14_1.468.0

- [Breaking change for Go client library] Mark `income_verification.access_tokens` and `access_token` nullable in `link/token/create` request, to match the actual behavior of the API.
- Add `other` to `account_filters` in `link/token/create` request

### 2020-09-14_1.467.0

- Change `/transactions/recurring/streams/merge` and `/transactions/recurring/streams/update` return type

### 2020-09-14_1.466.0

- Add `/transactions/recurring/streams/create`, `/transactions/recurring/streams/merge`, and `/transactions/recurring/streams/update` endpoints

### 2020-09-14_1.465.0

- [Breaking change for Go client library] Mark `products`, `required_if_supported_products`, `optional_products`, `additional_consented_products`, and `user.ssn` as nullable in `/link/token/create` request.
- Set `minLength` for `client_name`, `language`, `access_token`, and `user.client_user_id` in `/link/token/create` request, to match actual validation behavior of the API.

### 2020-09-14_1.464.1

- Add `webhook_code` to `/sandbox/income/fire_webhook`
- Change `verification_status` to be an optional field in `/sandbox/income/fire_webhook`

### 2020-09-14_1.464.0

- Add `/processor/signal/prepare` endpoint.

### 2020-09-14_1.463.7

- Internal changes only

### 2020-09-14_1.463.6

- Add `database_matched` to `verification_status` for database matched items.

### 2020-09-14_1.463.5

- Add `hosted_link.url_lifetime_seconds` to `/link/token/create` request

### 2020-09-14_1.463.4

- Add `database_match_enabled` field to `auth` object in `link/token/create`

### 2020-09-14_1.463.3

- Mark `RecurringInsightsStream` fields `is_active`, `merchant_name`, and `average_days_apart` as required.

### 2020-09-14_1.463.2

- Add `user_id` into the webhook schema for `AssetsProductReadyWebhook`

### 2020-09-14_1.463.1

- [Breaking change for Go client library] Mark `access_token` and `account_id` required in `/transfer/create`, to match the actual behavior of the API.

### 2020-09-14_1.463.0

- Add is_user_modified and last_user_modified_date to TransactionStream

### 2020-09-14_1.462.0

- Update `/beta/transactions/user_insights/v1/get` endpoint with recurring transactions and feature updates.

### 2020-09-14_1.461.2

- Clean up description for transfer refund simulate route.

### 2020-09-14_1.461.1

- Remove `client_id` and `secret` from required param list of `/transfer/ledger/distribute`

### 2020-09-14_1.461.0

- Add `/beacon/user/review` route for updating the status of Beacon Users

### 2020-09-14_1.460.0

- Permissions manager API: bug fix: update `date` field in ConnectedApplication schema to `date-time` to match API behavior
- Permissions manager API: add `/item/application/unlink` endpoint

### 2020-09-14_1.459.2

- Do not support .docx or .doc file for `/transfer/diligence/document/upload`

### 2020-09-14_1.459.1

- Make `products` request parameter for `/partner/customer/create` optional.

### 2020-09-14_1.459.0

- Add route `/transfer/ledger/distribute`

### 2020-09-14_1.458.1

- Refunds start processing after 4 days (not 3 days).

### 2020-09-14_1.458.0

- Remove `account_ids` parameter `/processor/transactions/get` options object
- Change `accounts` response field for `/processor/transactions/get` to `account`

### 2020-09-14_1.457.4

Add BASE_REPORT_WARNING warning type

### 2020-09-14_1.457.3

Add `BE` to the list of available countries

### 2020-09-14_1.457.2

- Add `access_tokens` field to `/link/token/create` request

### 2020-09-14_1.457.1

- Clean up description for transfer ledger simulate routes.

### 2020-09-14_1.457.0

- Remove `account_ids` parameter from `/processor/transactions/recurring/get` request

### 2020-09-14_1.456.0

- Add `hosted_link.completion_redirect_uri` to `link/token/create` request

### 2020-09-14_1.455.2

- Deprecate max_single_transfer_amount and max_monthly_amount in /transfer/configuration/get response.
- Deprecate monthly_transfer_volume in /transfer/metrics/get response.

### 2020-09-14_1.455.1

- Update documentation for `/credit/payroll_income/parsing_config/update`

### 2020-09-14_1.455.0

- Add new /sandbox/transfer/refund/simulate route to simulate refund events in sandbox.

### 2020-09-14_1.454.0

- Add `is_investments_fallback_item` field to `/investments/holdings/get` and `/investments/transactions/get` responses

### 2020-09-14_1.453.0

- Add `/credit/payroll_income/parsing_config/update` for updating the parsing configuration for document income verficiations

### 2020-09-14_1.452.0

- Add `warnings` field to `/cra/base_report/get` response

### 2020-09-14_1.451.0

- Add `/beacon/report_syndication/list` for listing `BeaconReportSyndication` objects linked to a specific `BeaconUser`

### 2020-09-14_1.450.0

- [Breaking] Remove `user_token` field from `asset_report/create` request.

### 2020-09-14_1.449.2

- Updates `isin` and `cusip` field descriptions for new call to action.

### 2020-09-14_1.449.1

- Add new refund event types.

### 2020-09-14_1.449.0

- Add `/beacon/report/list` for listing `BeaconReport` objects created for a specific `BeaconUser`

### 2020-09-14_1.448.0

- Make `publisher` field from `FDXNotifications` as optional

### 2020-09-14_1.447.0

- Mark `fraud_amount` as nullable for `BeaconReport` objects in `/beacon/report/create`

### 2020-09-14_1.446.0

- Add `allow_manual_entry` field to `investments` object in `link/token/create`
- Update `/credit/freddie_mac/reports/get` return type data shape to contain one object with both VOA and VOE assets combined

### 2020-09-14_1.445.0

- Add new insights and counterparty fields for Transactions endpoints
- Deprecate legacy category fields for Transactions endpoints

### 2020-09-14_1.444.0

- Add new webhook type `AUTHORIZATION_GRANTED` to `sandbox/item/fire_webhook`

### 2020-09-14_1.443.0

- Add `RETURN` as possible Virtual Account wallet transaction type

### 2020-09-14_1.442.0

- Add `facilitator_fee` field for the Transfers endpoints

### 2020-09-14_1.441

- [Breaking change for Go client library] Update `/transfer/capabilities/get` to no longer accept payment profile token and require an `account_id` and `access_token`
- Update examples for ledger endpoints to be more realistic

### 2020-09-14_1.440.0

- Add `optional_products` parameter to `/link/token/create` request.

### 2020-09-14_1.439.0

- [Breaking] Renamed `TransactionsEnrichGetRequest` and `TransactionsEnrichGetResponse` objects to
  `TransactionsEnrichRequest` and `TransactionsEnrichResponse`.

### 2020-09-14_1.438.1

- [Breaking change for Go client library] remove `device`, `user_present` from required request param list of `/transfer/recurring/create`

### 2020-09-14_1.438.0

- Add new `/beta/transactions/user_insights/v1/get` endpoint

### 2020-09-14_1.437.0

- Remove min/max restriction of `days_requested` in OpenAPI.

### 2020-09-14_1.436.0

- Update `days_requested` to be a required field in base reports in `link/token/create`

### 2020-09-14_1.435.0

- Update `/sandbox/transfer/sweep/simulate` to mark `swept` transfers as `swept_settled`.

### 2020-09-14_1.434.0

- Added a new type of webhook for dashboard alerts, `InstitutionStatusAlertWebhook`.

### 2020-09-14_1.433.0

- Update response of `/transfer/authorizarion/create`

### 2020-09-14_1.432.0

- Update `days_requested` in `base_report` in `link/token/create` to enforce a min/max of 1/731 days

### 2020-09-14_1.431.7

- Add processor Zero Hash

### 2020-09-14_1.431.6

- Update response example of `sandbox/transfer/ledger/deposit/simulate` and `sandbox/transfer/ledger/withdraw/simulate`

### 2020-09-14_1.431.5

- Update the description of `sweep.settled` event

### 2020-09-14_1.431.4

- Update description of endpoint `/sandbox/transfer/ledger/simulate_available`

### 2020-09-14_1.431.3

- Deprecate `originator_client_id` in `/transfer/get`, `/transfer/cancel`, and `/transfer/balance/get`

### 2020-09-14_1.431.2

- Docs updates for Statements endpoints

### 2020-09-14_1.431.1

- Remove `balance` field from response of `/sandbox/transfer/ledger/simulate_available`

### 2020-09-14_1.431.0

- Add `/user/update` and update the description for consumer report user identity

### 2020-09-14_1.430.3

- Add `sandbox/transfer/ledger/deposit/simulate` and `sandbox/transfer/ledger/withdraw/simulate`

### 2020-09-14_1.430.2

- Update `transfer/sweep/list` to support filter by `trigger`

### 2020-09-14_1.430.1

- Add `transfer/ledger/withdraw` route

### 2020-09-14_1.430.0

- Add `transfer/originator/funding_account/update` route

### 2020-09-14_1.429.3

- add ledger sweep event types to `TransferEventType`

### 2020-09-14_1.429.2

- Documentation updates for `LOGIN_REPAIRED` webhook and transfer.
- Add `transfer/ledger/deposit` route

### 2020-09-14_1.429.1

- Updated /identity/match's address score threshold recommendation from 80 or above to 70 or above

### 2020-09-14_1.429.0

- [Breaking change for Go client library] For Transfer endpoints that take payment profiles as input, remove `payment_profile` field and make
  `account_id` and `access_token` mandatory. The removed field is not in use.
- Mark all payment profile-specific endpoints as `deprecated`.
- Docs updates for Transfer, including clarifying that certain request fields for `/transfer/authorization/create`
  are not currently used.
- Propagate Signal docs update from 2020-09-14_1.419.0 to all relevant endpoints.
- Add `institution_not_supported` as a property to `LinkSessionExitMetadata.Status`

### 2020-09-14_1.428.1

- Change `/credit/reports/freddie_mac/get` schema to contain new `ReportingInformationParentIdentifier` field

### 2020-09-14_1.428.0

- Add `verification_report_type` to `asset_report/create` request

### 2020-09-14_1.427.1

- Remove references to the verification `report_type` field in `asset_report/get` and `asset_report/pdf/get`

### 2020-09-14_1.427.0

- Add `/processor/account/get` route

### 2020-09-14_1.426.0

- Add `instant_microdeposits_enabled` field to `auth` object in `link/token/create`

### 2020-09-14_1.425.0

- Add `investments` field to `asset_report/get` response as part of the `items.accounts` object

### 2020-09-14_1.424.2

- Update descriptions of some Transactions endpoint fields

### 2020-09-14_1.424.1

- Add clarification to processor webhook doc that the processor can call it
- Fix `sandbox/transfer/ledger/simulate_available` doc url

### 2020-09-14_1.424.0

- Add `/sandbox/transfer/ledger/simulate_available` route

### 2020-09-14_1.423.0

- Update code of `BaseReportsErrorWebhook` to `ERROR`
- Add new enum to StudentRepaymentPlan and add to description of repayment_plan_type

### 2020-09-14_1.422.0

- Move `BaseReportsProductReadyWebhook` and `BaseReportsErrorWebhook`
- Remove `asset_report_id` and add `user_id` to `BaseReportsErrorWebhook`

### 2020-09-14_1.421.0

- Update permissible purpose code `LEGITIMATE_BUSINESS_NEED_TENANT_OTHER` to `LEGITIMATE_BUSINESS_NEED_OTHER`

### 2020-09-14_1.420.1

- Add new enums to `canonical_description` in `credit/payroll_income/get`

### 2020-09-14_1.420.0

- Add `database_match_enabled` field to `auth` object in `link/token/create`

### 2020-09-14_1.419.2

- Add `/transfer/ledger/get` route

### 2020-09-14_1.419.1

- Add `submitted` and `not_submitted` to transferDiligenceStatus

### 2020-09-14_1.419.0

- Update `/signal/decision/report` description
    - Overwriting `initiated` field is now supported and no longer returns an `INVALID_FIELD` error

### 2020-09-14_1.418.0

- Add `frequency` to `/transactions/enrich`

### 2020-09-14_1.417.0

- Remove `category`, `category_id`, `transaction_type`, `name`, `payment_meta` fields from Base Report insights

### 2020-09-14_1.416.0

- Add `card_switch` to `/link/token/create`

### 2020-09-14_1.415.0

- Add `consumer_report_permissible_purpose` to `link/token/create`

### 2020-09-14_1.414.0

- Update `currency` on `payment/reverse` and `amount_refunded` on `payment/get`

### 2020-09-14_1.413.0

- Add `statements` to `/link/token/create` request

### 2020-09-14_1.412.0

- Add `hosted_link_url` to `/link/token/create` response
- Add `hosted_link.delivery_method` to `/link/token/create`

### 2020-09-14_1.411.0

- Add `link_sessions` to `/link/token/get`
- Add `LINK:SESSION_FINISHED` webhook

### 2020-09-14_1.410.1

- Add `statements` to the list of supported Plaid products in the `/link/token/create` endpoint

### 2020-09-14_1.410.0

- add `/credit/relay/pdf/get` endpoint

### 2020-09-14_1.409.0

- Add `original_client_id` to `/transfer/balance/get`
- Mark `type` optional in `/transfer/balance/get` request

### 2020-09-14_1.408.0

- Add `status` to `document_reference` in `/credit/payroll_income/risk_signals/get`

### 2020-09-14_1.407.0

- Add `consumer_report_user_identity` to `/user/create`

### 2020-09-14_1.406.1

- Add comment explaining availability of `confidence_level` field for `/transactions/*` endpoints

### 2020-09-14_1.406.0

- Added insights fields to `/cra/base_report/get`

### 2020-09-14_1.405.0

- Update identity/match user.address such that none of the fields are required
- Add `AddressDataNullableNoRequiredFields`

### 2020-09-14_1.404.1

- Allowing null failure_reason for refunds to be displayed
-

### 2020-09-14_1.404.0

- Add `failure_reason` to `/wallet/transaction/get` and `/wallet/transaction/list` endpoint in virtual accounts.

### 2020-09-14_1.403.1

- Add `parsing_config` to `/link/token/create`

### 2020-09-14_1.403.0

- Add `failure_reason` field to refunds for failed and returned refunds

### 2020-09-14_1.402.0

- Add `area_code` match status to the response of the `identity_verification/get` and `identity_verification/list` endpoint

### 2020-09-14_1.401.0

- Add `POST /cra/bank_income/get`

### 2020-09-14_1.400.0

- Add `cra/base_report/get` endpoint

### 2020-09-14_1.399.0

- Add `base_report` field to `/link/token/create` and corresponding Base Report webhooks

### 2020-09-14_1.398.0

- Make CreditBankIncomeWebhookUpdateResponse visible

### 2020-09-14_1.397.0

- Remove extraneous `Item` field from `/processor/transactions/get` response
- Reference new `/processor/token/webhook/update` endpoint in processor Transactions routes.

### 2020-09-14_1.396.2

- Document cash management account support

### 2020-09-14_1.396.1

- Fix document capitalization of `confidence_level` field in `/transactions/enrich`

### 2020-09-14_1.396.0

- Add `/beacon/report/create`

### 2020-09-14_1.395.0

- Add `POST /beacon/user/create`
- Add `POST /beacon/user/get`

### 2020-09-14_1.394.0

- Made `/statements/list` and `/statements/download` APIs for Plaid's Statements PDF beta product available in client SDKs

### 2020-09-14_1.393.0

- Add `date_of_birth` and `address` fields to `documentary_verification.documents[].extracted_data` in the response of all of the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.392.4

- Update the following about identity/match name, phone number, email, and address score descriptions:
    - Ensure consistent language across all fields
    - Include score recommended "match" threshold for all fields.

### 2020-09-14_1.392.3

- Update the `async_update` field description.

### 2020-09-14_1.392.2

- Mark a few response fields as always present in the identity verification API:
    - `selfie_check.selfies[].capture.image_url`
    - `selfie_check.selfies[].capture.video_url`
    - `risk_check.identity_abuse_signals`
    - `risk_check.identity_abuse_signals.synthetic_identity.score`
    - `risk_check.identity_abuse_signals.stolen_identity.score`

### 2020-09-14_1.392.1

- Documentation updates for the `/link/token/create` endpoint

### 2020-09-14_1.392.0

- Add `confidence_level` field to Counterparty and PersonalFinanceCategory for `/transactions/enrich`

### 2020-09-14_1.391.3

- Remove the `core_attributes` field in `signal_insights` of /transfer/authorization/create

### 2020-09-14_1.391.2

- Update the `pending_manual_verification` field's description in `/auth/get` response

### 2020-09-14_1.391.1

- Update the description of `/investments/transactions/get`

### 2020-09-14_1.391.0

- Update the `async_update` option to be visible in `/investments/transactions/get`

### 2020-09-14_1.390.1

- Update the `signal_insights` field's description in `/transfers/authorization/create` request

### 2020-09-14_1.390.0

- Add `transfer_id` field to `/transfers/sweep/list` request

### 2020-09-14_1.389.0

- Add `InvestmentsHistoricalUpdateWebhook`, a `HISTORICAL_UPDATE` webhook of type `INVESTMENTS_TRANSACTIONS`.

### 2020-09-14_1.388.1

- Add `status` field to a sweep object. Add `status` field to `/transfers/sweep/list` request

### 2020-09-14_1.388.0

- [Breaking] Remove `asset_report_token` as required field in `/asset_report/get` and mark as nullable

### 2020-09-14_1.387.1

- Allow empty `mask` on the `meta` field of overridden accounts in the sandbox custom user configuration object schema.

### 2020-09-14_1.387.0

- Mark `region` and `postal_code` fields as nullable in `/identity_verification/create`, `/identity_verification/retry`, and `/link/token/create`

### 2020-09-14_1.386.0

- Add payloads for processor Transactions webhooks.

### 2020-09-14_1.385.2

- Mark `next_origination_date` nullable

### 2020-09-14_1.385.1

- Add expiration time description to `transfer/authorization/create` `idempotency_key` parameter

### 2020-09-14_1.385.0

- Add `user` field to `/identity_verification/retry`
- Add `client_user_id` field to `/identity_verification/create`
- Deprecate `user.client_user_id` field in `/identity_verification/create`
- [Breaking] Renamed `IdentityVerificationRequestUser` object to `IdentityVerificationCreateRequestUser`

### 2020-09-14_1.384.0

- Remove `maxLength` constraint from `client_user_id` field for `/processor/signal/evaluate` and `/signal/evaluate` requests

### 2020-09-14_1.383.3

- Add `test_clock_id` to `transfer/authorization/create` request

### 2020-09-14_1.383.2

- Update `InvestmentsAuthOwner` title

### 2020-09-14_1.383.1

- Add `account_id` to `bank_accounts` and `transactions` in `/credit/bank_statements/uploads/get` response

### 2020-09-14_1.383.0

- Add `transfer/diligence/document/upload` endpoint

### 2020-09-14_1.382.1

- Add `amount` to `/transfer/sweep/list` request

### 2020-09-14_1.382.0

- Add `signal_insights` to `/transfer/authorization/create` request

### 2020-09-14_1.381.0

- Add definitions for `/sandbox/bank_income/fire_webhook`

### 2020-09-14_1.380.0

- Update validation `sweep_id` for `/transfers/sweep/get` to allow UUID or 8 character hexadecimal string

### 2020-09-14_1.379.0

- Add `scheme` to `/wallet/transaction/get` and `/wallet/transaction/list`

### 2020-09-14_1.378.1

- Fix issue in which `request_id` was erroneously not listed as required in `ItemActivityListResponse`

### 2020-09-14_1.378.0

- Add `reroute_to_credentials` to `/link/token/create` auth request

### 2020-09-14_1.377.0

- Add definitions for `/investments/auth/get`

### 2020-09-14_1.376.0

- Add `required_if_supported_products` to `/link/token/create` request

### 2020-09-14_1.375.0

- Add hidden `account_type` to `/transactions/enrich` request and response
- Add hidden `account_subtype` to `/transactions/enrich` request and response

### 2020-09-14_1.374.3

- Add `num_bank_statements_uploaded` to `document_income_results` object in `/credit/sessions/get` response

### 2020-09-14_1.374.2

- Add `income_source` enum to `/transactions/enrich` `counterparty_type` field

### 2020-09-14_1.374.1

- Update `oauth` descriptions for `/institutions/get` and `/institutions/search`

### 2020-09-14_1.374.0

- Add `/credit/bank_statements/uploads/get` endpoint

### 2020-09-14_1.373.0

- Add support for address and date of birth in `virtual-accounts/#wallettransactionexecute` endpoint

### 2020-09-14_1.372.3

- Modify `/transactions/enrich` field `user_id` to `client_user_id`
- Modify `/transactions/enrich` field `account_id` to `client_account_id`

### 2020-09-14_1.372.2

- Update docs for `/transactions/enrich` response to include non-null example values for `lat` and `lon` fields

### 2020-09-14_1.372.1

- Update descriptions for `PAYMENT_STATUS_EXECUTED` and `PAYMENT_STATUS_INITIATED`
- Update description for `PaymentAmountCurrency`

### 2020-09-14_1.372.0

- Add `user_id` and `account_id` fields to `/transactions/enrich` request and resposne

### 2020-09-14_1.371.4

- Update descriptions for `/credit/payroll_income/risk_signals/get` and `INCOME_VERIFICATION_RISK_SIGNALS` webhook

### 2020-09-14_1.371.3

- Add test_clock_id to `/transfer/simulate`
- [Breaking change for Go] Make `virtual_time` optional in `/sandbox/transfer/test_clock/create`

### 2020-09-14_1.371.2

- Add test_clock_id to `/sandbox/transfer/simulate` and `/sandbox/transfer/sweep/simulate` endpoints

### 2020-09-14_1.371.1

- Update `transfer/diligence/submit` copy

### 2020-09-14_1.370.0

- Add `investments/refresh` endpoint

### 2020-09-14_1.369.3

- Update `description` field in `/transfer/create` to have max length of 15

### 2020-09-14_1.369.2

- Add new `CreditBankIncomeCategory` value

### 2020-09-14_1.369.1

- Fix `/processor/transactions` routes doc links

### 2020-09-14_1.369.0

- Add `/processor/token/permissions/get` endpoint
- Add `/processor/token/permissions/set` endpoint

### 2020-09-14_1.368.2

- Add `transfer/diligence/submit` endpoint

### 2020-09-14_1.368.1

- Update `client_user_id` description for Identity Verification endpoints
- Update `user` description for Identity Match via Identity Verification Data use case

### 2020-09-14_1.368.0

- Add `/transfer/balance/get` endpoint

### 2020-09-14_1.367.0

- Added `LinkEventsWebhook` schema

### 2020-09-14_1.366.0

- Add `credit_funds_source` field for authorizations and transfers
- Make `funding_account_id` nullable in various /transfer API responses

### 2020-09-14_1.356.0

- Update `notificationsPayload.customFields` datatype from an object to an array of objects

### 2020-09-14_1.355.1

- Added `warnings` to `/processor/signal/evaluate` response.

### 2020-09-14_1.355.0

- Added `/processor/identity/match` endpoint.

### 2020-09-14_1.354.0

- Adds a `selfie_check` object to the response schema of all the identity verification endpoints:
    - `identity_verification/create`
    - `identity_verification/get`
    - `identity_verification/list`
    - `identity_verification/retry`

### 2020-09-14_1.353.1

- Update `INCOME_VERIFICATION_RISK_SIGNALS` with webhook tag

### 2020-09-14_1.353.0

- Add `ASSETS: PRODUCT_READY` and `ASSETS: ERROR` webhooks to `/sandbox/item/fire_webhook` endpoint

### 2020-09-14_1.352.0

- Removed explicit `additionalProperties: true` marker for request objects and objects used only within request objects, primarily impacting the Payment Initiation API. This will result in more strict type checking for those objects, but should not be a breaking change.

### 2020-09-14_1.351.1

- Update `transfer/authorization/create` copy

### 2020-09-14_1.351.0

- Add new `INCOME_VERIFICATION_RISK_SIGNALS` webhook

### 2020-09-14_1.350.0

- Remove `settled_amount`
- Rename `expected_settlement_schedule` as `expected_sweep_settlement_schedule`

### 2020-09-14_1.349.0

- [Breaking] Converts several types that were incorrectly typed as `number` to `integer`. In some languages, this will change the type used for this field, which may be a breaking change for some Plaid integrations. The following fields are impacted:

For all products:

- `PlaidError.status`

For Liabilities:

- `PSLFStatus.payments_made`
- `PSLFStatus.payments_remaining`

For Identity Verification and Monitor:

- `DocumentaryVerificationDocument.DocumentAnalysis.attempt`
- `EntityScreeningHitAnalysis.search_terms_version`
- `EntityWatchlistScreeningSearchTerms.search_terms_version`
- `IdentityVerificationTemplateReference.version`

The following client library languages are impacted:

- Go: Type changes from Float64 to Int32
- Java: Type changes from Double to Integer
- Python: Type changes from float to int
- Ruby: Type changes from Float to Integer

### 2020-09-14_1.348.2

- Update `/identity/match`'s score description to explicitly mention that null values are returned if input is missing from either the financial institution or the API
- Update `/identity/match` sample response to include `is_business_name_detected`

### 2020-09-14_1.348.1

- Make the `warnings` field in `SignalEvaluateResponse` non-nullable

### 2020-09-14_1.348.0

- Add `STARTED` and `INTERNAL_ERROR` to bank income and employment `/credit/sessions/get` status

### 2020-09-14_1.347.1

- Change invalid format `datetime` to `date` on `initiated_date` field
- Update `SignalWarning` descriptions

### 2020-09-14_1.347.0

Fix npm publish

### 2020-09-14_1.346.0

- Releasing new `/credit/payroll_income/risk_signals/get` endpoint

### 2020-09-14_1.345.4

- Revert `sweep_amount` description

### 2020-09-14_1.345.3

- Update `sweep_amount` description

### 2020-09-14_1.345.2

- Internal changes

### 2020-09-14_1.345.1

- Update `/transactions/enrich` field `is_recurring` field to be optional.bool

### 2020-09-14_1.345.0

- Fix bug in which `environment` field was incorrectly missing from Assets webhooks.

### 2020-09-14_1.344.0

- Add recurrence and is_recurring fields to `/transactions/enrich`

### 2020-09-14_1.343.6

- Update incorrect required fields for `/watchlist_screening/entity/update`

### 2020-09-14_1.343.5

- Update `owners` description for `/credit/bank_income/get` and `/beta/credit/v1/bank_employment/get`

### 2020-09-14_1.343.4

- Make comment about `webhook` field in `/link/token/create` request more explicit

### 2020-09-14_1.343.3

- Make VOA in /credit/freddie_mac/reports/get optional

### 2020-09-14_1.343.2

- Update `warnings` description for `/credit/bank_income/get` and `/beta/credit/v1/bank_employment/get`

### 2020-09-14_1.343.1

- Updated Asset endpoint descriptions related to Verification of Employment

### 2020-09-14_1.343.0

- Add new `warnings` field to the response of `/signal/evaluate`

### 2020-09-14_1.342.0

- Add `report_type` to assets webhook docs
- Make `add_ons` public in assets docs for /asset_report/create
- Make `fast_report` public in assets docs for /asset_report/get

### 2020-09-14_1.341.0

- Add `risk_check` attribute to all Identity Verification responses

### 2020-09-14_1.340.1

- Update examples for `entity_id` in `/transactions/enrich`

### 2020-09-14_1.340.0

- Create `options` in `/link_delivery/create`
- Create `recipient` within `options` field
- Move `communication_methods` from top level to `recipient`
- Add `first_name` in `recipient`

### 2020-09-14_1.339.0

- Add `callback_type` to link delivery webhooks

### 2020-09-14_1.338.2

- Make `communication_methods` optional in `/link_delivery/create`

### 2020-09-14_1.338.1

- Remove beta description from `/transactions/enrich` endpoint docs

### 2020-09-14_1.338.0

- Add `transaction_id` to `/payment-initiation/#payment_status_update`
- Add `payment_id` and `wallet_id` to `/virtual-accounts/#wallet_transaction_status_update`

### 2020-09-14_1.337.4

- Add `credit_category` to the `/asset_report/get` endpoint

### 2020-09-14_1.337.3

- Update description for the `address` field in `/payment_initiation/recipient/create`.

### 2020-09-14_1.337.2

- Add annually recurring frequency to `/transactions/recurring/get`

### 2020-09-14_1.337.1

- Make documentation for credit categories in the `/asset_report/get` endpoint public

### 2020-09-14_1.337.0

- Add bank employment results to `/credit/sessions/get`

### 2020-09-14_1.336.1

- Add `signal` to Products array.

### 2020-09-14_1.336.0

- Add options to `/credit/payroll_income/refresh` to allow item-level refresh

### 2020-09-14_1.335.2

- Updated `amount.value` description field with new minimum requirement for `/payment_initiation/payment/reverse` and `/wallet/transaction/execute`

### 2020-09-14_1.335.1

- Add 'employment' as an available product in the request to `/partner/customer/create`

### 2020-09-14_1.335.0

- [Breaking] Renamed Identity Verification UserName objects to IdentityVerificationRequestUserName and IdentityVerificationResponseUserName

### 2020-09-14_1.334.0

- Add "entity_id" field to /transactions/enrich

### 2020-09-14_1.333.0

- Add "add_ons" field to asset_report/create

### 2020-09-14_1.332.0

- [Breaking] Remove `/wallet/transaction/list` endpoint
    - [Note] Determined that `/wallet/transaction/list` is unused

### 2020-09-14_1.331.0

Add `LinkDeliveryCallbackWebhook`, `LinkUserDeliveryStatusWebhook` for Link Delivery.

### 2020-09-14_1.330.0

- [Breaking] Remove `options.wallet_id` field in `/payment_initiation/payment/create` and `/payment_initiation/consent/create` request.
    - [Note] Determined that this field is unused.

### 2020-09-14_1.229.2

- Undeprecated the `legal_name` field in the `/link/token/create` request.

### 2020-09-14_1.229.1

- Add `income_verification` as a supported product in the request for `/partner/customer/create`.

### 2020-09-14_1.229.0

- Add `network` field to `/transfer/intent/create` request.
- Updated `reference` minLength for `/wallet/transaction/execute` request and `/payment_initiation/payment/reverse` request.

### 2020-09-14_1.228.0

- Add `access_tokens` and `item_ids` to `/link_delivery/get` response

### 2020-09-14_1.227.0

- Add optional `persistent_account_id` field to account responses

### 2020-09-14_1.226.0

- Add `employment` fields to `/link/token/create`

### 2020-09-14_1.225.0

- Add `redacted_at` field in Identity Verification response and Documentary Verification Document component
- Update `original_front` field in Identity Verification Document Images to be nullable in redacted Identity Verification sessions

### 2020-09-14_1.224.0

- Add `earliest_deposit_date` and change `last_deposit_date` to `latest_deposit_date` for `/beta/credit/v1/bank_employment/get`

### 2020-09-14_1.223.0

- Add `redirect_uris` to `/partner/customer/create` request.

### 2020-09-14_1.222.0

- Add `wallet_id` field to `/wallet/transaction/get` and `/wallet/transaction/list` responses

### 2020-09-14_1.221.0

- Update `link_delivery/get` to remove `public_tokens` from the response

### 2020-09-14_1.220.0

- Update `link_delivery/create` to accept `communication_methods` and deprecate `delivery_method` and `delivery_destination`

### 2020-09-14_1.219.1

- Fix the `refund_id` example.
- Update address objects to reflect that in rare instances, `city` may be `null`.

### 2020-09-14_1.219.0

- Add partner webhook event type

### 2020-09-14_1.218.1

- Mark `phone_number_verified_time` and `email_address_verified_time` as deprecated, since it is no longer required to provide these fields to enable to enable the Returning User Experience.

### 2020-09-14_1.218.1

- Introduce `expected_settlement_date` field in the Transfer object

### 2020-09-14_1.218.0

- Add `/beta/credit/v1/bank_employment/get` endpoint

### 2020-09-14_1.217.0

- Add `updated` field to `/credit/audit_copy_token/update` response
- Add `SchemaVersion` to VOE and VOA schemas for `/credit/freddie_mac/reports/get`

### 2020-09-14_1.216.0

- Introduce `funding_account_id` field in the Transfer API
- Remove deprecated `origination_account_id` field from the Transfer documentation

### 2020-09-14_1.215.2

- Use more strict validation for `payment_id` and `recipient_id` fields in API

### 2020-09-14_1.215.1

- Use more strict validation for payment `consent_id` field in API

### 2020-09-14_1.215.0

- Add `status` to Wallet schema

### 2020-09-14_1.214.0

- Add `/credit/freddie_mac/reports/get` endpoint

### 2020-09-14_1.213.1

- Reflect that `days_requested` field in Bank Income Verification object in `/link/token/create` request is required when using Bank Income.
- Reflect that `is_update_mode` field in Bank Income Verification object in `/link/token/create` request defaults to `false`.
- Update description to reflect that Document Income object in `/link/token/create` request is not required, even when using Document Income.

### 2020-09-14_1.213.0

- Update `PartnerEndCustomerStatus` enum values.

### 2020-09-14_1.212.0

- Add `/credit/audit_copy_token/update` endpoint
- Add `report_type` to AssetReportCreateRequest

### 2020-09-14_1.211.1

- Fix `US_MBS` list code which was mistakenly documented as `US_MBC` for screening individuals with Monitor
- Document `TR_CMB` list code for screening individuals with Monitor
- Document `IZ_WBK` list code for screening individuals and entities with Monitor

### 2020-09-14_1.211.0

- Add `/partner/customer/oauth_institutions/get` endpoint.

### 2020-09-14_1.210.8

- Update example response for `/credit/bank_income/get`

### 2020-09-14_1.210.7

- Documentation updates for Investments APIs and Bank Transfer APIs.

### 2020-09-14_1.210.6

- Add validation on `originator_client_id` and `redirect_uri` for `/transfer/originator/create` and `transfer/originator/get` request

### 2020-09-14_1.210.5

- Add `company_name` to TransferOriginatorGetResponse

### 2020-09-14_1.210.4

- Add `recurring_transfer_id` to Transfer

### 2020-09-14_1.210.3

- Make `id_numbers` field hidden in `/user/create` request

### 2020-09-14_1.210.2

- Make `transfer_ids` required in RecurringTransfer

### 2020-09-14_1.210.1

- Change the `/transactions/enrich` `options.include_legacy_categories` field to `options.include_legacy_category`
- Make documentation for the `/transactions/enrich` `options.include_legacy_category` request field visible
- Make documentation for the `/transactions/enrich` `legacy_category` and `legacy_category_id` response fields visible
- Add `direction` to required fields for `ClientProvidedTransaction`

### 2020-09-14_1.210.0

- Add `/transfer/capabilities/get` endpoint to fetch RTP eligibility for a linked plaid item

### 2020-09-14_1.209.2

- Renamed the `NullableRecurringTransfer` type to `RecurringTransferNullable` type

### 2020-09-14_1.209.1

Add `nullable` property to `date_of_birth`, `phone_number_verified_time`, and `email_address_verified_time` fields within `LinkTokenCreateRequestUser` to resolve undesireable client library behavior in certain languages.

### 2020-09-14_1.209.0

- add `NullableRecurringTransfer` field
- replace `RecurringTransfer` with `NullableRecurringTransfer` for `TransferRecurringCreateResponse`
- and `Decision` in required fields for `TransferRecurringCreateResponse`
- add required fields for `TransferRecurringSchedule`

### 2020-09-14_1.208.0

- Add `total_amounts` field to `/credit/bank_income/get` response
- Deprecate `amount`, `iso_currency_code`, and `unofficial_currency_code` at top levels in `/credit/bank_income/get` response

### 2020-09-14_1.207.0

- Add `id_numbers` field to `/user/create` request

### 2020-09-14_1.206.11

- Add `RECURRING_NEW_TRANSFER` webhook event.
- Add `RECURRING_TRANSFER_SKIPPED` webhook event.
- Add `RECURRING_CANCELLED` webhook event.

### 2020-09-14_1.206.10

- make `idempotency_key` field for `/transfer/recurring/create` non-nullable

### 2020-09-14_1.206.9

- Add `description` field for `RecurringTransfer` object
- Make `TransferRecurringStatus` non-nullable

### 2020-09-14_1.206.8

- Make all mentions of relay tokens lowercase

### 2020-09-14_1.206.7

- Updated external URLs for Credit Relay endpoints, and marked them as beta in the summary

### 2020-09-14_1.206.6

- Add more enums values to `pay_rate` field in `/credit/payroll_income/get` response
- Add `pay_basis` field to `/credit/payroll_income/get`

### 2020-09-14_1.206.5

- Updated Credit Relay Token descriptions

### 2020-09-14_1.206.4

- Add `FUNDS_SWEEP` as a `type` enum for the `WalletTransaction` object

### 2020-09-14_1.206.3

- Make `test_clock_id` non-nullable in `test_clock`.

### 2020-09-14_1.206.2

- Update `CounterpartyType` to rename `delivery_marketplace` to `marketplace`
- Update `CounterpartyType` to add `payment_terminal`

### 2020-09-14_1.206.1

- Update the `transactions/enrich` transaction description example to match the request.

### 2020-09-14_1.206.0

- Add `/sandbox/transfer/test_clock/list` for recurring transfer
- rm `decision` and `decision_rationale` from `RecurringTransfer`
- add `decision` and `decision_rationale` in `TransferRecurringCreateResponse`
- rename `frozen_timestamp` to `virtual_time`
- not requiring `client_id` and `secret` for recurring transfer APIs

### 2020-09-14_1.205.9

- Use a nested `options` field for optional request params to `transactions/enrich`
- Make nullable fields required for `transactions/enrich`

### 2020-09-14_1.205.8

- Update supported payment scheme options for `/payment_initiation/payment/create`
  – Update description of `/payment_initiation/recipient/create` to mention non-Eurozone countries.
  – Update `/payment_initiation/payment/create` mentioning new currencies and non-Eurozone markets.
  – Removed `CHF` and `CZK` from the list of supported currencies.

### 2020-09-14_1.205.7

- Add website and logo_url to the `Counterparty` object for the Enrich product.
- Update descriptions for logo_url field in `Counterparty`, `TransactionCounterparty`, `Enrichments` and `Enhancements`.

### 2020-09-14_1.205.6

- Update field descriptions and response examples for `transactions/enrich`

### 2020-09-14_1.205.5

- Add support for optional request parameters in /transactions/enrich
- Add `location` field to `ClientProvidedTransaction` object
- Add `mcc` field to `ClientProvidedTransaction` object
- Add `date_posted` field to `ClientProvidedTransaction` object

### 2020-09-14_1.205.4

- Document partial refunds
- Update description for `/payment_initiation/payment/reverse` endpoint
- Update description for `/payment_initiation/payment/get` endpoint

### 2020-09-14_1.205.3

- Update description for `/signal/evaluate` endpoint

### 2020-09-14_1.205.2

- Update response examples, descriptions, and formatting for `/transactions/enrich` endpoint

### 2020-09-14_1.205.1

- Update descriptions for `CUSIP` and `ISIN` fields in the investments `Security` type to reflect CGS license requirements

### 2020-09-14_1.205.0

- Add `/transactions/enrich` endpoint, the EA version of `/beta/transactions/v1/enhance`.

### 2020-09-14_1.204.0

- Remove `/income/verification/refresh` endpoint

### 2020-09-14_1.203.0

- Add 7 brand new recurring transfer APIs
- Add `/transfer/recurring/create`
- Add `/transfer/recurring/list`
- Add `/transfer/recurring/get`
- Add `/transfer/recurring/cancel`
- Add `/sandbox/transfer/test_clock/create`
- Add `/sandbox/transfer/test_clock/advance`
- Add `/sandbox/transfer/test_clock/get`

### 2020-09-14_1.202.6

- IdentityMatchResponse `PhoneNumberMatchScore` and `EmailAddressMatchScore` use `score` instead of `scores`

### 2020-09-14_1.202.5

- Add `/partner/customer/remove` endpoint

### 2020-09-14_1.202.4

- Internal changes

### 2020-09-14_1.202.3

- New Transfer API routes for hosted onboarding of TPS end-customers

### 2020-09-14_1.202.0

- Add `refunds` field to `Transfer` object
- Add `refund_id` field to `TransferEvent` object
- Fix typo for `transfer/get` and `transfer/refund/get`

### 2020-09-14_1.201.0

- Add support for partial refunds
- Add `amount` field to `/payment_initiation/payment/reverse` request
- Add `amount_refunded` field to `/payment_initiation/payment/get` and `/payment_initiation/payment/list` responses

### 2020-09-14_1.200.0

- Add `risk_summary` and `page_number` to `/beta/credit/payroll_income/risk_signals/get`

### 2020-09-14_1.199.0

- Renamed `/wallet/transactions/list` into `/wallet/transaction/list` as endpoint

### 2020-09-14_1.198.8

- `/transfer/authorization/create` and `/transfer/create` may not return `account_id` in response.

### 2020-09-14_1.198.7

- Add `SYNC_UPDATES_AVAILABLE` support to `/sandbox/item/fire_webhook`

### 2020-09-14_1.198.6

- Make `ProductStatus` object nullable to reflect Sandbox-specific behavior.
- Clarify documentation for `SYNC_UPDATES_AVAILABLE` webhook.

### 2020-09-14_1.198.5

- Internal changes

### 2020-09-14_1.198.4

- Add `deleted_at` to `/payment_profile/get` response.

### 2020-09-14_1.198.3

- Change `start_date` to `start_time` for `/wallet/transaction/list` response.

### 2020-09-14_1.198.2

- Update list of available products for `/partner/customer/create`.

### 2020-09-14_1.198.1

- Add `institution_name` and `institution_id` fields to `/credit/payroll_income/get` response.

### 2020-09-14_1.198.0

- Add `options.start_date` and `options.end_date` to `/wallet/transaction/list` endpoint.
- Add `last_status_update` and `payment_id` field to `WalletTransaction`.
- Add `transaction_id` field to `PaymentInitiationPayment`

### 2020-09-14_1.197.6

- Add `originator_client_id` to Transfer API endpoints

### 2020-09-14_1.197.5

- Deprecate `origination_account_id` from `/transfer/authorization/create` endpoint.

### 2020-09-14_1.197.4

- Add `asset_under_management` field to `PartnerCustomerCreateRequest`.

### 2020-09-14_1.197.3

- Update supported `CountryCode`'s in `link/token/create` docs.

### 2020-09-14_1.197.2

- ach_class optional
- add rtp network option

### 2020-09-14_1.197.1

- Add newly supported languages for Link

### 2020-09-14_1.197.0

- Add `PAYMENT_PROFILE_LOGIN_REQUIRED` to transfer authorization `decision_rationale.code`.

### 2020-09-14_1.196.3

- Add `institution_name` field to `payroll_income_result` of `/credit/sessions/get`

### 2020-09-14_1.196.2

- Add requirements for `logo` in `PartnerCustomerCreateRequest`.

### 2020-09-14_1.196.2

- Deprecate webhook status `VERIFICATION_STATUS_PENDING_APPROVAL` in `income_verification` apis.

### 2020-09-14_1.196.1

- Add a note in the description of `/transfer/authorization/create`

### 2020-09-14_1.196.0

- Added endpoint `/sandbox/payment_profile/reset_login`

### 2020-09-14_1.195.0

- Consolidate usages of `Error` into `PlaidError`
- Add a `PlaidErrorType` enum

### 2020-09-14_1.194.2

- Fix typo for `income_verification` in `/sandbox/public_token/create` options

### 2020-09-14_1.194.1

- Update field descriptions in `/partner/customer/*` responses.
- Make `PartnerEndCustomerWithSecrets` extend `PartnerEndCustomer`.
- Fix documentation links in `/partner/customer/*` endpoints.

### 2020-09-14_1.194.0

- Add `/partner/customer/enable` endpoint

### 2020-09-14_1.193.0

- Rename `LOGIN_REQUIRED` from transfer authorizations `decision_rationale` to `ITEM_LOGIN_REQUIRED`

### 2020-09-14_1.192.3

- Add `/fdx/notifications` endpoint.

### 2020-09-14_1.192.2

- Add `USER_REPORTED_NO_INCOME` to CreditSessionBankIncomeStatus

### 2020-09-14_1.192.1

- Update description for `payment_profile_token` field

### 2020-09-14_1.192.0

- Add `income_verfication` field to `/sandbox/public_token/create`

### 2020-09-14_1.191.1

- Add `document_income_result` field to `credit/sessions/get`

### 2020-09-14_1.191.0

- Remove `payment_profile_id` from `/payment_profile/*`, `/transfer/authorization/create`, and `/transfer/create` endpoints and replace with `payment_profile_token`

### 2020-09-14_1.190.0

- Removed auditor_id from /credit/audit_copy/token/create

### 2020-09-14_1.189.0

- Add length boundary for the `client_user_id` field in `user/create`

### 2020-09-14_1.188.0

- Add `SchemaVersion` field to Freddie Mac Verification of Assets Schema

### 2020-09-14_1.187.0

- Add `non-custodial wallet` to account subtypes supported for investments
- Add `trade` investment transaction subtype as a subtype of `transfer` investment transaction type

### 2020-09-14_1.186.2

- Add `errors` field to `credit/sessions/get`

### 2020-09-14_1.186.1

- Add `payroll_income_result` field to `credit/sessions/get`

### 2020-09-14_1.186.0

- Update `IdentityVerificationRequestUser.date_of_birth` to be required to match the existing behavior of the API.

### 2020-09-14_1.185.0

- Add support for `USER_INPUT_TIMEOUT` as a value for `force_error` in the sandbox custom user schema.

### 2020-09-14_1.184.0

- Make `payment_id` not required in `/link/token/create` under the `payment_initiation` field.

### 2020-09-14_1.183.0

- Add `beacon_session_id` field in req of /transfer/authorization/create endpoint.

### 2020-09-14_1.182.0

- Add `/link/oauth/correlation_id/exchange` endpoint.

### 2020-09-14_1.181.1

- Update `report_tokens` in `/credit/relay/create` endpoint request to be a list of strings instead a list of objects

### 2020-09-14_1.181.0

- Add `credit/sessions/get` endpoint

### 2020-09-14_1.180.0

- Remove `Date` and `DateNullable` types in identity_verification and monitor endpoints. Replace with `ISO8601Date` and `ISO8601DateNullable`
  instead.

### 2020-09-14_1.179.0

- Remove `idempotency_key` field from resp of /transfer/authorization/create endpoint.

### 2020-09-14_1.178.2

- Change `institution_price_as_of` field on the Holdings object to nullable

### 2020-09-14_1.178.1

- Add `AUTHORISING` wallet transaction status

### 2020-09-14_1.178.0

- Add `/partner/customer/get` endpoint.
- Add `status` to the response for `/partner/customer/create`.

### 2020-09-14_1.177.4

- Add `settled` as a valid event type for `/sandbox/transfer/simulate`

### 2020-09-14_1.177.3

- Replace `ASSET_TRANSACTION_DESCRIPTION` with `ASSET_TRANSACTION_DESCRIPTON` in Freddie Mac
  Asset Report

### 2020-09-14_1.177.2

- Add `ownership_type` to Asset Report account object, to reflect actual API behavior.
- Update and clarify docs, including update to reflect new Transfers cutoff times.

### 2020-09-14_1.177.1

- Add `settled` as a possible Transfer status and `swept_settled` as a possible Transfer sweep status
- Add `settled` and `swept_settled` as new Transfer event types
- Add `settled` field to Transfer sweep object
- Add `standard_return_window` and `unauthorized_return_window` fields to Transfer object

### 2020-09-14_1.177.0

- Add `options` and `days_to_included` to `AssetReportGetRequest`

### 2020-09-14_1.176.2

- Add `recipient_id` field examples to the `/wallet/create`, `/wallet/get`, and `/wallet/list` responses

### 2020-09-14_1.176.1

- Set `employment_report_token` field in the `/credit/employment/get` endpoint to be not required

### 2020-09-14_1.176.0

- Add `mask` to the `meta` field of overridden accounts in the sandbox custom user configuration object schema.

### 2020-09-14_1.175.0

- Remove `MiddleName` and add `VALIDATION_SOURCES` to Freddie Mac Asset Report

### 2020-09-14_1.174.1

- Add `adyen` as processor partner

### 2020-09-14_1.174.0

- Add `environment` as an attribute to all webhook payloads

### 2020-09-14_1.173.0

- Add `idempotency_key` field in req/resp of /transfer/authorization/create endpoint.

### 2020-09-14_1.172.1

- Removed `/asset_report/relay/` endpoints

### 2020-09-14_1.172.0

- Add payroll institution to /credit/income/precheck endpoint.

### 2020-09-14_1.171.0

- Add `recipient_id` to the `/wallet/create`, `/wallet/get`, and `/wallet/list` responses

### 2020-09-14_1.170.1

- Fix that `client_id` and `secret` were erroneously marked as `required` for the request bodies of some endpoints. (These fields can be sent in the header and thus are not required in bodies).

### 2020-09-14_1.170.0

- Add `with_guarantee` field in request of `/transfer/authorization/create`

### 2020-09-14_1.169.0

- Add `issuing_region` as a field in the extracted data to documentary verification documents `/identity_verification/create`, `/identity_verification/get`, `/identity_verification/list` and `/identity_verification/retry` responses.

### 2020-09-14_1.168.2

- Add `bacs`/`iban` recommendation for `/payment_initiation/recipient/create`

### 2020-09-14_1.168.1

- Update descriptions for `/payment_profile/create`, `/payment_profile/get` and `/payment_profile/remove`

### 2020-09-14_1.168.0

-- Add `counterparties` to `/beta/transactions/v1/enhance` response

### 2020-09-14_1.167.1

- Added `MICRODEPOSIT_ERROR` which was returned by the API but missing from the error type enum.
- Various fixes to typos and descriptions

### 2020-09-14_1.167.0

- Add authorization code `MIGRATED_ACCOUNT_ITEM` for Items created via `/transfer/migrate_account` endpoint

### 2020-09-14_1.166.0

- Add `updated_at` field to Payroll Item entries in `/credit/payroll_income/get`

### 2020-09-14_1.165.3

- removed LoanRoleType, ReportIdentifierType, and ReportDateTime fields from `/credit/asset_report/freddie_mac/get`

### 2020-09-14_1.165.2

- Remove deprecated reverse_swept enum value from documentation

### 2020-09-14_1.165.1

- Update example response for the `wallet/list` endpoint

### 2020-09-14_1.165.0

- Add details for `IdentityMatchResponse` for `/identity/match` endpoint

### 2020-09-14_1.164.10

- Update descriptions for `HOLDINGS: DEFAULT_UPDATE` and `INVESTMENT_TRANSACTIONS: DEFAULT_UPDATE` webhooks

### 2020-09-14_1.164.9

- Removed report_type from the request to `/credit/asset_report/freddie_mae/get`

### 2020-09-14_1.164.8

- Add documentation for credit categories in the `/asset_report/get` endpoint

### 2020-09-14_1.164.7

- Remove redundant parameters from the `/transfer/create` endpoint from docs and mark them as deprecated

### 2020-09-14_1.164.6

- Add the following new currencies for the `/payment_initiation` API route group: PLN, SEK, DKK, NOK, CHF, CZK

### 2020-09-14_1.164.5

- Update description for `/payment_initiation/payment/reverse` to indicate that this endpoint only works with virtual accounts
- Update description for `/wallet/transaction/execute` to indicate that settlement will take seconds to days

### 2020-09-14_1.164.4

- Remove verification fields from `/credit/payroll_income/get` and `/income/verification/paystubs/get`

### 2020-09-14_1.164.3

- Remove pull_id field from `/credit/payroll_income/get`

### 2020-09-14_1.164.2

- Update external documentation links for the `/wallet/` API route group
- Update `/payment_initiation/payment/reverse` description to cover which payments are eligible for refunds
- Update `/payment_initiation/payment/create` reference field description to indicate that references should be unique and will be adjusted automatically
- Update `PaymentInitiationPaymentStatus` description to indicate that payments may take seconds to days to settle depending on the payment rail used
- Update `WalletTransactionStatus` description to indicate that transactions may take seconds to days to settle depending on the payment rail used

### 2020-09-14_1.164.1

- Make `is_savings_or_money_market_account` field in `SignalEvaluateCoreAttributes` nullable

### 2020-09-14_1.164.0

- Add new endpoint `/credit/asset_report/freddie_mac`

### 2020-09-14_1.163.0

- Add `/link_delivery/create` endpoint
- Add `/link_delivery/get` endpoint

### 2020-09-14_1.162.2

- Fix minimum and maximum values in `/signal/evaluate` scores

### 2020-09-14_1.162.1

- Make holdings `institution_price_as_of` non-nullable

### 2020-09-14_1.162.0

- Add `WalletTransactionStatusUpdateWebhook` object
- Update `WalletTransactionStatus` to include an additional `SETTLED` enum
- Update `PaymentInitiationPaymentStatus` to include an additional `PAYMENT_STATUS_SETTLED` enum

### 2020-09-14_1.161.5

- Reverts the changes made in 2020-09-14_1.157.0

### 2020-09-14_1.161.4

- Update description for webhook `USER_PERMISSION_REVOKED`

### 2020-09-14_1.161.3

- Bug fix: Put quotes around the '529' account type to prevent generated client libraries from treating it as an integer.
- Add `RECURRING_TRANSACTIONS_UPDATE` to description of sandbox webhook testing endpoint

### 2020-09-14_1.161.2

- Change the Item schema to refer to `PlaidError` rather than `Error` to avoid namespace conflicts in client libraries.

### 2020-09-14_1.161.1

- Add required fields back to AssetReport schema

### 2020-09-14_1.161.0

- Remove `access_token` request parameter from `/beta/partner/v1/customers/create`

### 2020-09-14_1.160.0

- Add `user` fields to the `/link/token/create` `user` object.

### 2020-09-14_1.159.0

- Add `RECURRING_TRANSACTIONS_UPDATE` webhook specification
- Fix typo in `/sandbox/item/fire_webhook` description

### 2020-09-14_1.158.1

- Add x-plaid-validation for Credit Relay Tokens

### 2020-09-14_1.158.0

- Add `address` and `id_number` fields to the `/link/token/create` `user` object.

### 2020-09-14_1.157.0

- Update and add schemas referred by `AssetReportGetResponse`

### 2020-09-14_1.156.0

- Add `payment_profile_id` to `/transfer/authorization/create` and `/transfer/create`
- Make `access_token` and `account_id` optional in `/transfer/authorization/create` and `/transfer/create`

### 2020-09-14_1.155.0

- Add `payment_profile_id` as a field under `transfer` for `/link/token/create`

### 2020-09-14_1.154.0

- Create `/credit/bank_income/pdf/get` to allow customers to retrieve the bank income product as a PDF

### 2020-09-14_1.153.1

-- Add `personal_finance_category_icon_url` to `/beta/transactions/v1/enhance` response

### 2020-09-14_1.153.0

-- Add new endpoint `/beta/partner/v1/customers/create`

### 2020-09-14_1.152.0

- Add `form1099s` as part of the `credit/payroll_income/get` response.
- Add `Credit1099` object and corresponding subtypes.

### 2020-09-14_1.151.1

- Update required fields list for guaranteed ACH customers

### 2020-09-14_1.151.0

- Mark `verification` field under `paystubs` object in `/credit/payroll_income/get` as deprecated

### 2020-09-14_1.150.0

- Make `user_present` under `/transfer/authorization/create` nullable

### 2020-09-14_1.149.1

- Update fields description for guaranteed ACH customers

### 2020-09-14_1.149.0

- Add `gave_consent` as a field under `identity_verification` for `/link/token/create`
- Remove `identity_verification.consent`, which is deprecated, from documentation for `/link/token/create`

### 2020-09-14_1.148.0

- Add `user_present` a an optional field under `/transfer/authorization/create`, update fields description for guaranteed ACH customers

### 2020-09-14_1.147.1

- Remove deprecated `reversed` status from Transfer schema
- Remove deprecated `reverse_swept` status from Transfer Event schema

### 2020-09-14_1.147.0

- Add new endpoints `/credit/relay/get`, `/credit/relay/refresh` and `/credit/relay/remove`

### 2020-09-14_1.146.0

- make item_logins field not required

### 2020-09-14_1.145.0

- Make changes to IdentityMatchRequest to support options data

### 2020-09-14_1.144.0

- Remove unsupported error_code (`PRODUCTS_NOT_SUPPORTED`) for the `force_error` config in Sandbox

### 2020-09-14_1.143.0

- Make changes to support crypto in Investments product

### 2020-09-14_1.142.0

- Add new endpoints `/payment_profile/get` and `/payment_profile/remove`

### 2020-09-14_1.141.1

- Bug fix: add `identity_verification` to `Products` array

### 2020-09-14_1.141.0

- Add a new endpoint `/payment_profile/create`

### 2020-09-14_1.140.1

- Add `stated_income_sources` as a field under `income_verification` for `/link/token/create`

### 2020-09-14_1.140.0

- Add `bin` as a field under `institution_metadata` for `/link/token/create`

### 2020-09-14_1.139.0

- Add `international` IBAN numbers to `WalletNumbers` field in `/wallet/get` and `/wallet/list` responses.
- Wrap the `iban` field in the `WalletTransactionCounterpartyNumbers` under new field `international`.

### 2020-09-14_1.138.0

- Add new `identity/match` endpoint, and `IdentityMatchRequest` and `IdentityMatchResponse`

### 2020-09-14_1.137.1

- Update comment for the `recipient.name` field with recommendation to avoid long strings and special characters.

### 2020-09-14_1.137.0

- Reverts the changes made in 2020-09-14_1.135.0. ProductAccess and AccountProductAccess once again have all fields explicitly defined.

### 2020-09-14_1.136.0

- Add `products` in `asset_report/create` endpoint.

### 2020-09-14_1.135.0

- Convert ProductAccess and AccountProductAccess to optional.Map

### 2020-09-14_1.134.0

- Rename `merchant_website` and `merchant_logo_url` in `/beta/transactions/v1/enhance` to `website` and `logo_url`

### 2020-09-14_1.133.0

- Update `/credit/payroll_income/get` response to have a `pull_id` instead of an `income_report_token` and add `pull_id` to `/credit/employment/get` response

### 2020-09-14_1.132.1

- Made several fields nullable for `/signal/evaluate`

### 2020-09-14_1.132.0

- Add `/credit/audit_copy_token/remove` to invalidate Audit Copy tokens

### 2020-09-14_1.131.3

- Update external URL for `/transfer/migrate_account` endpoint

### 2020-09-14_1.131.2

- Add `TRANSFER_LIMIT_REACHED` to enum `TransferAuthorizationDecisionRationaleCode`

### 2020-09-14_1.131.1

- Update `/payment_initiation/consent/*` external docs URLs

### 2020-09-14_1.131.0

- Add `iban` to `counterparty`'s `numbers` field in `/wallet/transaction/execute`

### 2020-09-14_1.130.0

- Update description of `/user/create` to make it more clear what would happen when a client calls the user creation endpoint with the same client_user_id multiple times.

### 2020-09-14_1.129.0

- Add `signal_description` for each risk signal in `/beta/credit/payroll_income/risk_signals/get`
- Change `DocumentRiskSignalInstitutionMetadata` to be nullable

### 2020-09-14_1.128.6

- Fix category rules formatting

### 2020-09-14_1.128.5

- Change description in `UserCustomPassword` to reflect that only top level fields are optional not all fields

### 2020-09-14_1.128.4

- Move Category Rules description to `include_personal_finance_category` flag

### 2020-09-14_1.128.4

- Add `identity_verification` as a new optional parameter for `/link/token/create`

### 2020-09-14_1.128.3

- Add category rules beta to `personal_finance_category` field description
  in `/transactions/get`

### 2020-09-14_1.128.2

- Update description of `/investments/transactions/get` endpoint
- Update description of `cost_basis` field

### 2020-09-14_1.128.1

- Add `merchant_website` and `merchant_logo_url` to `/beta/transactions/v1/enhance` response

### 2020-09-14_1.128.0

- Add `auth_type_select_enabled`, `automated_microdeposits_enabled`, `instant_match_enabled`, and `same_day_microdeposits_enabled` to `/link/token/create`
- Marked `flow_type` parameter as deprecated

### 2020-09-14_1.127.0

- Add `consent_id` filter to `/payment_initiation/payment/list`
- Add `consent_id` to `/link/token/create`

### 2020-09-14_1.126.0

- Added `/credit/relay/create` endpoint

### 2020-09-14_1.125.0

- Add `accounts` object to `/credit/payroll_income/get` response

### 2020-09-14_1.124.0

- Added `include_fast_report` in `asset_report/create` endpoint. Added `fast_report` in `asset_report/get` endpoint

### 2020-09-14_1.123.1

- Removed `reversed` and `reverse_swept` from possible event_type values in TransferEventListRequest docs

### 2020-09-14_1.123.0

- Change `tokens` to `report_tokens` in `/credit/audit_copy_token/create` request

### 2020-09-14_1.122.0

- Add `request_id` to all Identity Verification and Monitor responses

### 2020-09-14_1.121.2

- Added sample user_id to INCOME_VERIFICATION webhook

### 2020-09-14_1.121.1

- Pre-release API refinements to Monitor and Flow endpoints

### 2020-09-14_1.121.0

- Add TimestampNullable type

### 2020-09-14_1.120.0

- Removed `Uploaded`, `Created` and `APPROVAL_STATUS_APPROVED` enum strings from `PayrollItemStatus` field.

### 2020-09-14_1.119.0

- Add `returned` to TransferStatus enum
- Add `return_swept` to TransferSweepStatus enum
- Add `returned` and `return_swept` to TransferEventType enum

### 2020-09-14_1.118.0

- Added `employee_type` and `last_paystub_date` to `/credit/employment/get` response

### 2020-09-14_1.117.1

- Make `/payment_initiation/consent/create` API more strict

### 2020-09-14_1.117.0

- Add `/credit/audit_copy_token/create` endpoint

### 2020-09-14_1.116.0

- Add `/wallet/list` endpoint

### 2020-09-14_1.115.2

- Update description fields to fix formatting errors
- Reflect that `error.suggested_action` is `nullable`

### 2020-09-14_1.115.1

- Update OpenAPI spec

### 2020-09-14_1.115.0

- Added `income_report_token` to `/credit/payroll_income/get` response

### 2020-09-14_1.114.2

- Add `/wallet/create` endpoint

### 2020-09-14_1.114.1

- Add beta `additional_consented_products` field to `/link/token/create`

### 2020-09-14_1.113.1

- Updated `/transactions/recurring/get` description

### 2020-09-14_1.113.0

- Add webhooks for new Monitor and Identity Verification products

### 2020-09-14_1.112.0

- Add endpoints for new Monitor and Identity Verification products

### 2020-09-14_1.111.15

- Remove `emi_recipient_id` from Payment Initiation Recipient

### 2020-09-14_1.111.14

- Add optional `iban` and `bacs` fields to `options` in the `/payment_initiation/consent/create` request

### 2020-09-14_1.111.13

- Updated `/transactions/sync` description

### 2020-09-14_1.111.12

- Add more accurate enum documentations to `/transactions/recurring/get` API doc

### 2020-09-14_1.111.11

- Additional documentation for `/transactions/sync`

### 2020-09-14_1.111.9

- Remove deprecated field `createdAt` from `/application/get` response

### 2020-09-14_1.111.8

- Add field validation to `BankTransferDirection`

### 2020-09-14_1.111.7

- Remove deprecated field `createdAt` from `/application/get` response

### 2020-09-14_1.111.6

- Add external doc link to `transactions/recurring/get`

### 2020-09-14_1.111.5

- Updating the API doc for Recurring Transactions

### 2020-09-14_1.111.4

- Add `DisplayName` in `/application/get` response

### 2020-09-14_1.111.3

- Updated sample responses for all Transfer endpoints

### 2020-09-14_1.111.2

- Changing `beta/transactions/rules/` routes to `beta/transactions/rules/v1`

### 2020-09-14_1.111.1

- Fixing `InsitututionMetadata` typo to `InstitutionMetadata` in private `/beta/credit/payroll_income/risk_signals/get`endpoint response

### 2020-09-14_1.111.0

- Added `require_guarantee`, `guarantee_decision`, and `guarantee_decision_rationale` to `/transfer/intent` in order to support Guarantee when using Transfer UI.

### 2020-09-14_1.110.2

- Add additional supported `type` enums in `WalletTransaction`.

### 2020-09-14_1.110.1

- Add Additional History billing information for /asset_report/create.

### 2020-09-14_1.110.0

- Add `user_id` to income verification webhook payload

### 2020-09-14_1.109.1

- Make `consent_id` field nullable in `PaymentInitiationPayment`.

### 2020-09-14_1.109.0

- Replace `initiated_refunds` with `refund_ids` in the `/payment_initiation/payment/get` and `/payment_initiation/payment/list` responses

### 2020-09-14_1.108.0

- Added `/beta/credit/payroll_income/risk_signals/get` endpoint (currently private)

### 2020-09-14_1.107.4

- Remove unsupported ACH classes from `bank_transfer/` and `transfer/` endpoints.

### 2020-09-14_1.107.3

- Add `enable_multiple_items` parameter for bank income.

### 2020-09-14_1.107.2

- Fix typo in `institution_name` parameter for credit endpoints.

### 2020-09-14_1.107.0

- Added `reference` and `idempotency_key` fields to the `payment_initiation/payment/reverse` request.

### 2020-09-14_1.106.0

- Added `is_update_mode` to `income_verification` in the `/link/token/create` body

### 2020-09-14_1.105.2

- Consolidate item schemas

### 2020-09-14_1.105.1

- Removed `client_id` and `secret` as required fields from `/transfer/intent/{get,create}` to match actual API behavior.

### 2020-09-14_1.105.0

- Add `/credit/payroll_income/refresh` endpoint

### 2020-09-14_1.104.0

- Added `/signal/prepare`

### 2020-09-14_1.102.0

- Added `/watchlist_screening/individual/list` (currently private)
- Added `/watchlist_screening/individual/create` (currently private)
- Added `/watchlist_screening/individual/get` (currently private)
- Added `/watchlist_screening/individual/update` (currently private)
- Added `/watchlist_screening/individual/history/list` (currently private)
- Added `/watchlist_screening/individual/review/list` (currently private)
- Added `/watchlist_screening/individual/review/create` (currently private)
- Added `/watchlist_screening/individual/hit/list` (currently private)
- Added `/watchlist_screening/entity/list` (currently private)
- Added `/watchlist_screening/entity/create` (currently private)
- Added `/watchlist_screening/entity/get` (currently private)
- Added `/watchlist_screening/entity/update` (currently private)
- Added `/watchlist_screening/entity/history/list` (currently private)
- Added `/watchlist_screening/entity/hit/list` (currently private)
- Added `/watchlist_screening/entity/review/list` (currently private)
- Added `/watchlist_screening/entity/review/create` (currently private)
- Added `/watchlist_screening/individual/program/list` (currently private)
- Added `/watchlist_screening/individual/program/get` (currently private)
- Added `/watchlist_screening/entity/program/list` (currently private)
- Added `/watchlist_screening/entity/program/get` (currently private)
- Added `/dashboard_user/list` (currently private)
- Added `/dashboard_user/get` (currently private)
- Added `/identity_verification/list` (currently private)
- Added `/identity_verification/get` (currently private)
- Added `/identity_verification/retry` (currently private)
- Modified `/identity_verification/create` (currently private)

### 2020-09-14_1.101.0

- Add endpoint for `/credit/bank_income/refresh`

### 2020-09-14_1.100.0

- Add `include_original_description`, `include_personal_finance_category` options to `/transactions/sync` request.

### 2020-09-14_1.99.0

- API changes for /credit/employment/get

### 2020-09-14_1.98.1

- Add `gusto` as processor partner

### 2020-09-14_1.98.0

- Add `user_token` as a request parameter for `/sandbox/public_token/create`

### 2020-09-14_1.97.1

- Remove `auth`, `transactions_updates`, `investments_updates`, and `identity` as required fields from Item status to match actual API behavior.

### 2020-09-14_1.97.0

- Rename some `Credit` refs that were preventing client library generation from completing successfully

### 2020-09-14_1.96.0

- remove unused `payroll_income_id` from `/credit/payroll_income/get` field
- add status object to items in `/credit/payroll_income/get` response body

### 2020-09-14_1.95.1

- Add `TransferEventsUpdateWebhook` schema

### 2020-09-14_1.95.0

- Add `institution_data` parameter to `/link/token/create`

### 2020-09-14_1.94.2

- Tidy up YAML

### 2020-09-14_1.94.1

- Add `highnote` processor to `/processor/token/create`

### 2020-09-14_1.94.0

- Add `use_case`, `company_legal_name`, `city`, `region`, `country_code`, `postal_code` as a required response field of `Application`

### 2020-09-14_1.93.2

- Remove `income_verification_id` from income webhook example
- Fix incorrect URL for `/user/create` endpoint

### 2020-09-14_1.93.1

- Remove deprecated `income_verification_id` from income webhooks
- Standardize income webhook casing

### 2020-09-14_1.93.0

- Add several new fields to `/signal/evaluate` response
-

### 2020-09-14_1.92.4

- Add `/sandbox/transfer/fire_webhook` endpoint

### 2020-09-14_1.91.4

- Mark certain Income endpoints as deprecated in favor of the new `/credit/*` endpoints.

### 2020-09-14_1.91.3

- Add `checkout` processor to `/processor/token/create`

### 2020-09-14_1.91.2

- Add `webhook_type` parameter to `/sandbox/item/fire_webhook`
- Support for investments transactions, investments holdings and liabilities `DEFAULT_UPDATE` webhooks

### 2020-09-14_1.90.2

- Add new warning type to `/credit/bank_income/get` response

### 2020-09-14_1.90.1

- Add `marqeta` and `solid` as Auth processor partners
- Fix schema of `cause` parameter for Asset Reports
- Fix some invalid examples

### 2020-09-14_1.90.0

- Add `/credit/employment/get` endpoint
- Add optional `access_tokens` array to `/credit/payroll_income/precheck` request

### 2020-09-14_1.89.3

- Update description of `/sandbox/item/fire_webhook`

### 2020-09-14_1.89.2

- Update description of `accounts/get`

### 2020-09-14_1.89.1

- Added `AUTH_DATA_UPDATE` webhook code as valid input to `/sandbox/item/fire_webhook`
- Update description for `/sandbox/item/fire_webhook`

### 2020-09-14_1.89.0

- Add `/transfer/migrate_account` endpoint

### 2020-09-14_1.88.2

- Fix operationId for `/credit/payroll_income/precheck`

### 2020-09-14_1.88.1

- Remove deprecated fields from `/item/application/list`

### 2020-09-14_1.88.0

- Add `wire_routing_number` parameter to `/bank_transfer/migrate_account`

### 2020-09-14_1.87.1

- Specify minimum length of 1 for `description` on `TransferIntentCreateRequest`

### 2020-09-14_1.87.0

- Add `consent_id` support in the Institutions Search request

### 2020-09-14_1.86.1

- Add `apex_clearing` as a processor partner

### 2020-09-14_1.86.0

- Introduce Credit Payroll Income APIs
- Introduce Credit Precheck API

### 2020-09-14_1.85.1

- Add `/identity_verification/create` endpoint, kept private for now

### 2020-09-14_1.85.0

- Add `status` field to `ConnectedApplication`

### 2020-09-14_1.84.5

- Added missing `asset_report_id` field to `/asset_report/relay/refresh`

### 2020-09-14_1.84.4

- Change summary description and url for `/credit/bank_income/get`

### 2020-09-14_1.84.3

- Slight wording change for `/credit/bank_income/get` response fields

### 2020-09-14_1.84.3

- Move `user_token` to top level of `link/token/create` request

### 2020-09-14_1.84.2

- Correct typo in enum value for Investment subtypes (`person` -> `pension`)

### 2020-09-14_1.84.1

- Fix schema to properly handle personal finance categories in `/transactions/get`

### 2020-09-14_1.84.0

- Add `user_token` parameter to `link/token/create`

### 2020-09-14_1.83.1

- Add new fields to `/credit/bank_income/get` response

### 2020-09-14_1.83.0

- Remove `permitted` decision for `/transfer/authorization/create`

### 2020-09-14_1.82.0

- Add beta field `consented_products` to `/item/get/` endpoint response

### 2020-09-14_1.82.0

- Revamp LinkTokenCreate.IncomeVerificationOptions for GA

### 2020-09-14_1.81.0

- Add `/transaction/rules/create`, `/transaction/rules/list` and `/transaction/rules/remove` endpoints

### 2020-09-14_1.80.0

- Added `/user/create` endpoint

### 2020-09-14_1.79.0

- Update to include all changes up to `2020-09-14_1.77.4` (Undo revert from `1.78.x` updates)

### 2020-09-14_1.78.2

- Revert to `2020-09-14_1.64.13`

### 2020-09-14_1.78.1

- Revert to `2020-09-14_1.62.7`

### 2020-09-14_1.78.0

- Revert to `2020-09-14_1.64.14`

### 2020-09-14_1.77.5

- Add support for `IT` country code for use with Payments.
- More prominently highlight that the Identity response body changed in the 2019-05-29 API version.

### 2020-09-14_1.77.4

- Remove the word "Asset" before "Relay" in every asset report relay related responses and request objects

### 2020-09-14_1.77.3

- Add "AssetReport" at the beginning of relay related responses and request objects to match the same pattern as other assets related objects

### 2020-09-14_1.77.2

- Add `ProductAccess` fields for upcoming partner

### 2020-09-14_1.77.1

- Fix extraneous field in enum that caused issue in code generation
- Added `asset_report_id` to the example for `/asset_report/relay/refresh`

### 2020-09-14_1.77.0

- Explicitly set `format: double` for non-integer numbers so generated fields prefer float64

### 2020-09-14_1.76.0

- Add three new endpoints for Assets: `/asset_report/relay/create`, `/asset_report/relay/get`, and `/asset_report/relay/rmeove`

### 2020-09-14_1.75.0

- Added `/asset_report/relay/refresh` endpoint

### 2020-09-14_1.74.0

- Add `recurring_transactions` to list of products

### 2020-09-14_1.73.0

- Add new endpoint for `/credit/bank_income/get`

### 2020-09-14_1.72.0

- Updated documentation URLs for all product endpoints. They can now be found
  at `/docs/api/products/<product-name>/#endpoint` instead of `/docs/api/products/#endpoint`

### 2020-09-14_1.71.0

- internal changes

### 2020-09-14_1.70.0

- Remove deprecated `income_verification_id` from `/sandbox/income/fire_webhook`

### 2020-09-14_1.69.1

- Reorder processors enum

### 2020-09-14_1.69.0

- Added `/beta/transactions/v1/enhance` endpoint

### 2020-09-14_1.68.1

- Added `status` object to sample responses for `/institutions/get` and `institutions/search` endpoints

### 2020-09-14_1.68.0

- Mark `include_personal_finance_category_beta` property as deprecated.
- Add new argument `include_personal_finance_category` to TransactionsGetRequestOptions.
- Update docs for `/transactions/get` request and response, referencing personal_finance_category taxonomy csv file.

### 2020-09-14_1.67.1

- internal changes

### 2020-09-14_1.67.0

- Removed unused `/income/verification/summary/get` endpoint

### 2020-09-14_1.66.0

- Added Payment Consent endpoints

### 2020-09-14_1.65.0

- Removed unused `/income/verification/paystub/get` endpoint

### 2020-09-14_1.64.15

- De-anonymized enums:
    - `PaymentInitiationPaymentReverseResponse.properties.status` => `PaymentInitiationRefundStatus`
    - `PaymentInitiationPaymentCreateResponse.properties.status` => `PaymentInitiationPaymentCreateStatus`
    - `PaymentInitiationRefund.properties.status` => `PaymentInitiationRefundStatus`
    - `PaymentAmount.properties.currency` => `PaymentAmountCurrency`
    - `InvestmentTransaction.properties.type` => `InvestmentTransactionType`
    - `InvestmentTransaction.properties.subtype` => `InvestmentTransactionSubtype`
    - `TransferAuthorizationDecisionRationale.properties.code` => `TransferAuthorizationDecisionRationaleCode`
    - `TransferAuthorizationGuaranteeDecisionRationale.properties.code` => `TransferAuthorizationGuaranteeDecisionRationaleCode`
    - `TransferAuthorization.properties.decision` => `TransferAuthorizationDecision`
    - `TransferEventListRequest.properties.transfer_type` => `TransferEventListTransferType`
    - `BankTransferEventListRequest.properties.bank_transfer_type` => `BankTransferEventListBankTransferType`
    - `BankTransferEventListRequest.properties.direction` => `BankTransferEventListDirection`
    - `TransferIntentCreate.properties.status` => `TransferIntentStatus`
    - `TransferIntentGet.properties.status` => `TransferIntentStatus`
    - `TransferIntentGet.properties.authorization_decision` => `TransferIntentAuthorizationDecision`
- `IncomeVerificationPrecheckMilitaryInfo.properties.branch` is now a string field (previously enum)

### 2020-09-14_1.64.15

- Made `last_statement_balance` and `minimum_payment_amount` `nullable` for credit card liabilities schema to reflect existing API behavior.

### 2020-09-14_1.64.14

- Made `last_payment_amount` and `last_statement_issue_date` `nullable` for credit card liabilities schema to reflect existing API behavior.
- Fix transfers examples to reflect more consistent usage of `region` field.

### 2020-09-14_1.64.13

- Deprecate `idempotency_key` parameter in transfer/create

### 2020-09-14_1.64.12

- Removed the unused `required_product_access` and `optional_product_access` parameters from `RequestedScopes`

### 2020-09-14_1.64.11

- Fix some examples that were not consistent with their schemas
- Add `adjustments` as an investments transaction type to make OpenAPI file consistent with values returned by the API
- Clarify description field for `marital_status` to reflect possible values

### 2020-09-14_1.64.10

- Updated the external docs URL for Bank Transfers sandbox endpoints

### 2020-09-14_1.64.9

- De-anonymized the object filters under `LinkTokenCreateRequestAccountSubtypes`, as anonymous objects aren't compatible with the generated CLibs.
- De-anonymized some misc. objects
    - `PaymentInitiationMetadata/properties/maximum_payment_amount`
    - `PaystubOverride/properties/employer`
    - `PaystubOverride/properties/employee`
    - `PaystubOverride/properties/employee/properties/address`
    - `LiabilitiesDefaultUpdateWebhook/properties/account_ids_with_updated_liabilities`

### 2020-09-14_1.64.8

- Updated the description of the historical_balances array

### 2020-09-14_1.64.7

- Add new possible enums for income verification earnings breakdown canonical description

### 2020-09-14_1.64.6

- Hid a few product enum values that are deprecated or no longer valid for certain request fields. This affects the documentation only.

### 2020-09-14_1.64.5

- Make guarantee fields required in Transfer endpoints

### 2020-09-14_1.64.4

- Updated description for `failure_reason` field in Transfer endpoints

### 2020-09-14_1.64.3

- Make `repayment_id` required in `/transfer/repayment/return/list` endpoint

### 2020-09-14_1.64.2

- Update description for legal name field in `BankTransferUser`

### 2020-09-14_1.64.1

- Update descriptions for `/transfer/repayment/list` and `/transfer/repayment/return/list` endpoints

### 2020-09-14_1.64.0

- Remove `scheme_automatic_downgrade` from `/payment_initiation/payment/create`

### 2020-09-14_1.63.1

- Update description for `/sandbox/transfer/sweep/simulate` endpoint

### 2020-09-14_1.63.0

- Refactor account subtype enums for greater specificity. This has no changes to the API but is a major semver change for Python, Node, Go, and Java client library interfaces to the AccountSubtype object within account filtering contexts in `/link/token/create`. The `AccountSubtype` namespace in this context is now prefixed with the AccountType. (Example for Node: Old: `AccountSubtype.checking` New: `DepositoryAccountSubtype.checking`)

### 2020-09-14_1.62.7

- Update description for `datetime` and `authorized_datetime` fields in Transactions endpoints

### 2020-09-14_1.62.6

- Make `sweep_id` / `sweep_amount` fields on Transfer Event nullable

### 2020-09-14_1.62.6

- Set `institution_status` to be nullable in `InstitutionsGetResponse`

### 2020-09-14_1.62.5

- Update external docs URLs for Transfer and Bank Transfer endpoints
- Update description for `ach_return_code` field in Transfer endpoints

### 2020-09-14_1.62.4

- Add `join_date` to `/application/get` and `/item/application/list`
- Remove `created_at` from `/application/get`

### 2020-09-14_1.62.3

- Updated various description fields for Income

### 2020-09-14_1.62.2

- Add `employment` as an available product in Product array.

### 2020-09-14_1.62.1

- Add `minItems` and `minLength` validation to various fields in `/institution/*` request schemas

### 2020-09-14_1.62.0

- Add guarantee_decision and guarantee_decision rationale fields to the transfer API
- Add repayment-related resources to the transfer API

### 2020-09-14_1.61.7

- Remove `receiver_pending` and `receiver_posted` from bank transfer event types.
- Remove `BankTransferReceiverDetails` from bank transfer event types.

### 2020-09-14_1.61.6

- Update description formatting for `sweep` and `amount` fields for sweep endpoints

### 2020-09-14_1.61.5

- Added `NEW_ACCOUNTS_AVAILABLE` webhook code as valid input to `/sandbox/item/fire_webhook`
- Update description for `/sandbox/item/fire_webhook`

### 2020-09-14_1.61.4

- Set the `minimum` for the `count` and `offset` fields in `InstitutionsGetRequest`
- Set `products`, `routing_numbers`, and `oauth` fields to be nullable in `InstitutionsGetRequestOptions`
- Set `products` to be nullable in `InstitutionsSearchRequest`
- Set `oauth`, `include_auth_metadata`, and `include_payment_initiation_metadata` fields to be nullable in `InstitutionsSearchRequestOptions`
- Set `payment_id` field to be nullable in `InstitutionsSearchPaymentInitiationOptions`

### 2020-09-14_1.61.3

- Adds `DOCUMENT_TYPE_NONE` enum value for document metadata

### 2020-09-14_1.61.2

- Relax length restrictions on the `currency` field in the `Pay` schema

### 2020-09-14_1.61.1

- Use new payment statuses in `PaymentStatusUpdateWebhook`

### 2020-09-14_1.61.0

- Added payment scheme support for EU payments

### 2020-09-14_1.60.7

- Rename `created_at` field on `sweep` object to `created`
- Rename `start_time` and `end_time` fields on request to `/transfer/sweep/list` to `start_date` and `end_date`

### 2020-09-14_1.60.6

- Added `iso_currency_code` to `/transfer/authorization/create`, `/transfer/create`, `/transfer/intent/create`, `/transfer/intent/get` and `Transfer` object

### 2020-09-14_1.60.5

- Set the `routing_number` field in the `Institution` schema to be not nullable

### 2020-09-14_1.60.4

- Removed Employer Address fields as required for `/income/verification/precheck` endpoint

### 2020-09-14_1.60.3

- Update response from `/sandbox/transfer/sweep/simulate` to be nullable

### 2020-09-14_1.60.2

- Added example response for `/income/verification/refresh/`

### 2020-09-14_1.60.2

- Allowed empty string or nil values for the `webhook` field in the `/item/webhook/update` request
- Modified the `url` request validator to allow empty strings if the request field with `x-plaid-validation: url` is also nullable

### 2020-09-14_1.60.1

- Removed `balance` from the `InstitutionStatus` object, as this field is no longer returned.

### 2020-09-14_1.60.0

- Sets `format: date-time` on the `created` field in the `transfer/authorization/create` response

### 2020-09-14_1.59.2

- Drop transfer_id from /sweep/list endpoint
- Amend semantics of simulate sweep endpoint

### 2020-09-14_1.59.1

- Updated description for `VERIFICATION_STATUS_PROCESSING_COMPLETE` endpoint
- Deprecated `VERIFICATION_STATUS_DOCUMENT_REJECTED` endpoint

### 2020-09-14_1.59.0

- Migrated embedded errors to `PlaidError` type

### 2020-09-14_1.58.4

- Added missing nullable tag for `client_report_id` in `/asset_report/get` response
- Updated the description for `/accounts/get`

### 2020-09-14_1.58.3

- Fixed `last_payment_date` to indicate that it is `nullable`.
- Fixed example enum for paystub `verification_status`

### 2020-09-14_1.58.2

- Updating example response for `/income/verification/paystubs/get`

### 2020-09-14_1.58.1

- Fixes duplicate entries in `PaymentInitiationPaymentStatus`

### 2020-09-14_1.58.0

- Updated schema definitions for `/transfer/intent/create` and `/transfer/intent/get` paths

### 2020-09-14_1.57.1

- Added `x-plaid-income-enum-lint` property to enums used by income team

### 2020-09-14_1.57.0

- Added `PAYMENT_STATUS_REJECTED` to the `PaymentInitiationPaymentStatus` enum

### 2020-09-14_1.56.0

- Added new payment statuses to `PaymentInitiationPaymentStatus` enum

### 2020-09-14_1.55.1

- Added fields to example response for `/income/verification/precheck`

### 2020-09-14_1.55.0

- Adds enums to `/income/verification/refresh` response

### 2020-09-14_1.54.2

- Added `PAYMENT_STATUS_EXECUTED` to the list of allowed `PaymentInitiationPaymentStatus`s, as the API was already returning this. Also created a separate model for the enum instead of defining it inline.

### 2020-09-14_1.54.1

- Removed `merchant_name` and `check_number` from `TransactionBase`'s required list as they're not actually required.

### 2020-09-14_1.54.0

- internal changes

### 2020-09-14_1.53.0

- define `/transfer/sweep/get` & `/transfer/sweep/list` paths
- update `/transfer/event/list` to accept `sweep_id`
- new event_types `swept` & `reverse_swept`
- new sweep_status field on Transfer
- `sandbox/transfer/sweep/simulate` endpoint to support creating / setting `sweep_status` in sandbox

### 2020-09-14_1.52.0

- Adds `/wallet/transactions/list` endpoint

### 2020-09-14_1.51.0

-- Replaces the `emi_account_id` field on Payment Initiation API routes with `wallet_id`

### 2020-09-14_1.50.0

- Adds `/wallet/transaction/execute` endpoint

### 2020-09-14_1.49.0

- Adds `/wallet/get` endpoint

### 2020-09-14_1.48.0

- Adds `transfer` object to the `/link/token/create` request schema

### 2020-09-14_1.47.2

- Removes the option for `additionalProperties` in `SignalReturnReportRequest`
- Adds `additionalProperties` to `SignalReturnReportResponse`

### 2020-09-14_1.47.1

- Adds description updates and bug fix for Income Verification endpoints
- Adds German as supported language for Link

### 2020-09-14_1.47.0

- Adds `/transfer/intent/create` and `/transfer/intent/get` endpoints for Transfer UI

### 2020-09-14_1.46.3

- Fix for `/transactions/sync` response object

### 2020-09-14_1.46.2

- Adds new options to `VerificationAttributes` enum

### 2020-09-14_1.46.1

- Removes `confidence` field from `IncomeVerificationPrecheckConfidence`. This was typo introduced in version 1.45.2

### 2020-09-14_1.46.0

- Adds `merchant_name` and `check_number` to the transaction base and therefore to the asset transaction schema.

### 2020-09-14_1.45.3

- Changes the type of `sweep_id` from int to UUID string

### 2020-09-14_1.45.2

- Updated `/income/` enums in responses to not use anonymous objects

### 2020-09-14_1.45.1

- Add new webhook status `VERIFICATION_STATUS_PENDING_APPROVAL` in `income_verification` apis.

### 2020-09-14_1.45.0

- Adds product field to item response

### 2020-09-14_1.44.2

- Marks `/income/verification/create` and `/income/verification/summary/get` as deprecated

### 2020-09-14_1.44.1

- Updates documentation for the `authorized` field in `/item/application/scopes/update`

### 2020-09-14_1.44.0

- Add `/transactions/sync` endpoint

### 2020-09-14_1.43.2

- Removes `income_breakdown` and `ytd_earnings` from required fields in `Paystub`

### 2020-09-14_1.43.1

- Adds `transactions_access_tokens` to `/income/verification/precheck` to replace singular field.

### 2020-09-14_1.43.0

- Fix field names on recently created and unused paystub verification fields

### 2020-09-14_1.42.0

- Docs updates
- Deprecates `status` enum returned by `/institutions/` endpoints in favor of more granular data returned by the `breakdown` object
- Adds `DE` as a supported country code to support Payment Initiation

### 2020-09-14_1.41.3

- Adds `item_id` in `IncomeVerificationStatusWebhook`

### 2020-09-14_1.41.2

- Adds `account_product_access`, `account_product_access.tax_documents`, `account_product_access.statements`, and `account_product_access.account_data` fields to `AccountAccess`

### 2020-09-14_1.41.1

- Include `doc_id` in `/income/verification/taxforms/get`

### 2020-09-14_1.41.0

- Adding minimum and maximum string validation for `client_transaction_id` in `signal/` endpoints

### 2020-09-14_1.40.3

- Fixing enum naming for verification object in `income/verification/paystubs/get`

### 2020-09-14_1.40.2

- Fixes typos and updates descriptions

### 2020-09-14_1.40.1

- Adds `user_present` as an optional field of `/signal/evaluate`.
- Adds `days_funds_on_hold` as an optional field of `/signal/decision/report`.

### 2020-09-14_1.40.0

- Updating response body for `income/verification/paystubs/get` to return verification status for each paystub

### 2020-09-14_1.39.1

- Adds `item_id` to `/sandbox/income/fire_webhook` request

### 2020-09-14_1.39.0

- Adds `access_tokens` to `/income/verification/create` and `/link/token/create` for income verification.

### 2020-09-14_1.38.0

- Updates the response body for `/income/verification/paystubs/get` to incorporate new fields that will begin to be populated, and marks old fields as deprecated which will be phased out
- Adds documentation for `/income/verification/taxforms/get`
- Adds documentation for `/employment/verification/get`

### 2020-09-14_1.37.7

- Adds request requirements for `/transactions/recurring/get`

### 2020-09-14_1.37.6

- Adds `inflow_streams` to required field of `/transactions/recurring/get`.

### 2020-09-14_1.37.5

- Make default behavior of `include_insights` in `/asset_report/get` request explicit.

### 2020-09-14_1.37.4

- Adds `url` to `employer` field of `/income/verification/precheck`.

### 2020-09-14_1.37.3

- Adds `address` to `employer` field of `/income/verification/precheck`. Marks `income_verification_id` deprecated in `/link/token/create`

### 2020-09-14_1.37.2

- Adds `precheck_id` to `/income/verification/create` and `/link/token/create` for income verification.

### 2020-09-14_1.37.1

- Adds `document_type` to `/income/verification/paystubs/get` and `/income/verification/taxforms/get`

### 2020-09-14_1.37.0

- Adding `employment/verification/get` route to the API

### 2020-09-14_1.36.5

- Adds ability to fetch individual documents from `/income/verification/documents/download`

### 2020-09-14_1.36.4

- Add additionalProperties to `SignalDecisionReportResponse`
- Add additionalProperties to `SignalReturnReportResponse`
- Make the `CoreAttributes` field of the `SignalEvaluateResponse` optional

### 2020-09-14_1.36.3

- Make the `days_requested` field for `AssetReportRefreshRequest` nullable.

### 2020-09-14_1.36.2

- Update examples

### 2020-09-14_1.36.1

- Fixed a bug for `SignalEvaluateRequest` and removed `additionalProperties: true` for it.

### 2020-09-14_1.36.0

- Add missing `last_statement_balance` liabilities field to OpenAPI file

### 2020-09-14_1.35.0

- Add support for `BSV` currency

### 2020-09-14_1.34.2

- Set the maximum `days_requested` to be 731 in the `AssetReportCreateRequest` and `AssetReportRefreshRequest` schemas
- Set the `client_report_id` and `webhook` fields to be nullable in the `AssetReportCreateRequest` and `AssetReportRefreshRequest` schemas

### 2020-09-14_1.34.1

- Change "403b" to "403B" in the `InvestmentAccountSubtype` schema

### 2020-09-14_1.34.0

- Add `/transactions/recurring/get` route to the API

### 2020-09-14_1.33.0

- Add `update.account_selection_enabled` parameter to `/link/token/create` for Account Select v2
- Update descriptions for `TRANSACTIONS: INITIAL_UPDATE` AND `TRANSACTIONS: HISTORICAL_UPDATE` for Account Select v2
- Add `ITEMS: NEW_ACCOUNTS_AVAILABLE` webhook

### 2020-09-14_1.32.0

- Add Sandbox custom password schema for income verification

### 2020-09-14_1.31.5

- Update Link token shown in example response for `/link/token/create`

### 2020-09-14_1.31.4

- Add `transfer` to products list

### 2020-09-14_1.31.3

- Update description for `/transfer/authorization/create` in sandbox

### 2020-09-14_1.31.2

- Made more fields on `/income/verification/precheck` optional

### 2020-09-14_1.31.1

- Add additional enum for `canonical_description`

### 2020-09-14_1.31.0

- Add `/income/verification/precheck` endpoint

### 2020-09-14_1.30.3

- Update enum strings for `canonical_description`

### 2020-09-14_1.30.2

- Added `initiated_refunds` field to `/payment_initiation/payment/get` and `/payment_initiation/payment/list`

### 2020-09-14_1.30.1

- Add response for `income/verification/paystub/get`

### 2020-09-14_1.30.0

- Add /bank_transfer/sweep/list endpoint

### 2020-09-14_1.29.1

- Added description for 'SignalEvaluateRequest'
- Added description for 'SignalEvaluateResponse'
- Added description for 'SignalScores'
- Added description for 'SignalDecisionReportRequest'
- Added description for 'SignalDecisionReportResponse'
- Added description for 'SignalReturnReportRequest'
- Added description for 'SignalReturnReportResponse'

### 2020-09-14_1.29.0

- Added `include_personal_finance_category_beta` as an optional field to the `TransactionsGetRequestOptions` component
- Added `personal_finance_category` as a nullable field to the `Transaction` component

### 2020-09-14_1.28.4

- Remove iso_currency_code from `/transfer/authorization/create` response

### 2020-09-14_1.28.3

- Remove direction for `/transfer` endpoints
- Remove receiver*details and receiver*\* event types for `/transfer` endpoints
- Remove iso_currency_code from `/transfer` endpoints
- Remove custom_tag from `/transfer` endpoints
- Remove description for authorization object
- Make ach_class required for `/transfer/create`

### 2020-09-14_1.28.2

- Fix misspelled enum for `svb_api`
- Fix incorrect format string for `date_of_birth` from `date-time` to `date`

### 2020-09-14_1.28.1

- Updated `balance` fields availability description for `/accounts/balance/get`

### 2020-09-14_1.28.0

- Add `/payment_initiation/payment/reverse` endpoint

### 2020-09-14_1.27.0

- Added `include_auth_metadata` field to `InstitutionsGetRequestOptions`, `InstitutionsSearchRequestOptions`, `InstitutionsGetByIdRequestOptions`.
- Added `auth_metadata` field to `Institution` object, which is included in `InstitutionsGetResponse`, `InstitutionsSearchResponse`, `InstitutionsGetByIdResponse`.

### 2020-09-14_1.26.2

- Updates documentation for `income/verification/paystubs/get`.

### 2020-09-14_1.26.1

- Fix bug with request generation for `/income/verification/paystub/get`

### 2020-09-14_1.26.0

- Add `/bank_transfer/sweep/get` endpoint

### 2020-09-14_1.25.2

- Fix cursor format for `/payment_initiation/payment/list`
- Update min/max requirements for `count` in `/payment_initiation/payment/list`

### 2020-09-14_1.25.1

- Removed `bacs` and `iban` as required fields for certain Payment Initiation models, as only one of the two is required.
- Added `nullable` to the Income `canonical_description` property.
- Moved some properties that were next to references, which is invalid.
- Added `fixed annuity` to `AccountSubtype` model.
- Added `automatically_verified` to `verification_status` enum.

### 2020-09-14_1.25.0

- Add schema for `/income/verification/paystub/get`.

### 2020-09-14_1.24.4

- Added `income/verification/taxforms/get` documentation.

### 2020-09-14_1.24.3

- Update required and nullable fields for `/transfer/authorization/create`.

### 2020-09-14_1.24.2

- Added `treasury_prime` processor.

### 2020-09-14_1.24.1

- Fix description for `/transfer/authorization/create`

### 2020-09-14_1.24.0

- Changed `investment_transactions` type/subtype hierachy

### 2020-09-14_1.23.1

- Add missing descriptions to `created_at` and `expired_at` webhook verification fields.
- Other small description fixes.

### 2020-09-14_1.23.0

- Add Transfer endpoints

### 2020-09-14_1.22.1

- Updated `IncomeVerificationPaystubResponse` to an updated schema.

### 2020-09-14_1.22.0

- Added `holdings` `investment_transactions` as optional to custom sandbox account overrides.
- Added `holdings` `investment_transactions` and `securities` as optional custom sandbox return values.

### 2020-09-14_1.21.0

- Add `check_number` field to `/transactions/get` endpoint

### 2020-09-14_1.20.8

- Added `context` as a required value of `ItemApplicationScopesUpdateRequest`.
- Added `state` as an optional value of `ItemApplicationScopesUpdateRequest`.

### 2021-08-04_1.20.7

- Added `min_last_updated_datetime` option to `/processor/balance/get` request.

### 2020-09-14_1.20.6

- Added `format:` labels to all date and date-time strings
- Fix missing title attributes
- Converted some strings to enums

### 2020-09-14_1.20.5

- Updated `Select Account` to `Account Select`

### 2020-09-14_1.20.4

- Update Signal risk tier definitions

### 2020-09-14_1.20.3

- Bug fixes to signal endpoints

### 2020-09-14_1.20.1

- Added `/sandbox/oauth/select_accounts` endpoint.

### 2021-07-27_1.20.0

- Added `liabilities_updates`, `liabilities`, and `investments` to institution schema

### 2020-09-14_1.20.0

- Added `/signal/evaluate` endpoint
- Added `/signal/decision/report` endpoint
- Added `/signal/return/report` endpoint
- Added `/income/verification/refresh` endpoint.

### 2020-09-14_1.19.12

- Added `alpaca`, `astra` and `moov` processors.
- Changed naming for some nullable parameters from `NullableParam` to `ParamNullable`.
- Added `/processor/bank_transfer/create` endpoint.
- Changed the inherited model for `AssetReportTransaction` from `Transaction` to `TransactionBase` which has fewer required fields.

### 2020-09-14_1.19.11

- Added `logo_url` as a required value of `ConnectedApplications`
- Made `logo` a deprecated value of `ConnectedApplications` soon to be removed in future versions

### 2020-09-14_1.19.10

- Added `income` back to the list of possible products as it's in sandbox return values.
- Made `switch_method` nullable as the sandbox deposit/switch response has it nulled.

### 2021-07-1_1.19.9

- Added `CountryCode` to the request fields of `deposit_switch/create` and `deposit_switch/alt/create`
- Added `TransactionAccessTokens` to `DepositSwitchCreateOptions`

### 2020-09-14_1.19.8

- Added `options` field to request body for `deposit_switch/create` and `deposit_switch/alt/create` endpoints
- Added webhook documentation for `deposit_switch/`
- Added a new state to the list of possible values for the `state` field in the response body, and updated descriptions of all states

### 2020-09-14_1.19.7

- Added `ItemApplicationListUserAuth` component
- Added `user_auth` as a private field in `/item/application/list` request
- Changed `/item/application/list` request `access_token` field from `AccessToken` to `NullableAccessToken` to support `user_auth` flow (`/item/application/list` can be queried using `user_auth` instead of an access token for certain clients)

### 2020-09-14_1.19.6

- Added the following response fields to the `/deposit_switch/get` docs:
    - `switch_method`
    - `employer_name`
    - `employer_id`
    - `institution_name`
    - `institution_id`

### 2020-09-14_1.19.5

- Added `required` to many fields where it was missing
- Removed `nullable: true` annotation incorrectly applied to some fields
- Added ``nullable: true` annotation incorrectly missing from some fields
- Fixed invalid example for `/processor/balance/get`
- Fixed incorrect formatting for certain `allOf` structures
- Added enum values for some strings that were not treated as enums
- Added missing `created_at` field to `Application`
- Added missing `null` enum to some nullable enums
- Added missing beta `include_original_description` and `original_description` fields to `Transaction`
- Various small description fixes
- Updated external docs URLs for Income endpoints

### 2020-09-14_1.19.4

- Fixed description for `close_price` field returned in `/investments/holdings/get` response

### 2020-09-14_1.19.3

- Updated the `/institutions/get/` description to explain filtering behavior

### 2020-09-14_1.19.2

- Added `error` field to `/income/verification/summary/get` response body

### 2020-09-14_1.19.1

- Fix links to income (beta) docs
- add income webhook example

### 2020-09-14_1.19.0

- Added `/sandbox/income/fire_webhook` endpoint

### 2020-09-14_1.18.2

- Added Lithic and SVB to the list of supported processors for `/processor/token/create` endpoint

### 2020-09-14_1.18.1

- Fixed file to reflect that `category_id` and `next_payment_due_date` are nullable
- Removed spurious `paystub_id` field
- Added missing `SCHEDULED` value to `IncidentUpdate.status` enum
- Various description fixes

### 2020-09-14_1.18.0

- Added `/item/application/scopes/update` endpoint
- Fixed incorrect enum values for `update_type`
- Fixed file to reflect that `current` balance field is nullable.
- Description and textual fixes
- Fix invalid format errors
- Add new investment subtypes

### 2020-09-14_1.17.0

- Small description fix for `/income/verification/create` and `/employers/search`
- Fixed `ytd_net_income` value in `IncomeVerificationSummaryGetResponse` example
- Fixed references to `paystub` to be plural `paystubs` for `/income/verification/paystubs/get` route and schemas
- Added `PaystubEmployer` schema referenced in the `Paystub` object

### 2020-09-14_1.16.6

- Added `ItemApplicationScopesUpdateRequest` and `ItemApplicationScopesUpdateResponse` schema

### 2020-09-14_1.16.5

- Added `emi_account_id` field to `PaymentInitiationPayment` model for `/payment_initiation/payment/get` and `/payment_initiation/payment/list` response
- Added `emi_recipient_id` field to `PaymentInitiationRecipient` model for `/payment_initiation/recipient/get` and `/payment_initiation/recipient/list` response

### 2020-09-14_1.16.4

- Removes erroneous `request_id` that was incorrectly shown to be returned in items from `/payment_initiation/payment/list` and `/payment_initiation/recipient/list`.
- Fix for `ExternalPaymentSchedule` to make `end_date` optional.

### 2020-09-14_1.16.3

- Updated `/investments/transactions/get` count minimum to be 1 instead of 0

### 2020-09-14_1.16.2

- Fixes for required parameters for `JWKPublicKey` and `Security`.
- Fix for `BankTransferMetadata` to be nullable.

### 2020-09-14_1.16.1

- Fixes for descriptions and linter errors.

### 2020-09-14_1.16.0

- Updated `/payment_initiation/payment/create` with ability to pass in iban or account and sort code. If provided, the end user will be able to send payments only from the specified bank account.

### 2020-09-14_1.15.1

- Add clarifying max character line to client_name description.

### 2020-09-14_1.15.0

- Removed erroneous `access_token` that was incorrectly shown to be returned by `/item/get`.
- Added `business` loan type.
- Clarified `date` format for `institution_price_as_of`.
- Various small description fixes.

### 2020-09-14_1.14.0

- Updated `institutions/get`, `institutions/get_by_id`, and `institutions/search` to introduce an optional flag to return Payment Initiation metadata
- Updated `institutions/search` to accept additional options to filter institutions by various Payment Initiation configurations.

### 2020-09-14_1.13.3

- Updated `/accounts/balance/get` documentation to show `INVALID_FIELD` and `LAST_UPDATED_DATETIME_OUT_OF_RANGE` errors that will be returned for `capone-oauth`

### 2020-09-14_1.13.2

- Add specific format attribute to `date_of_birth` under `LinkTokenCreateRequestUser`.

### 2020-09-14_1.13.1

- Remove `last_statement_balance` since it's never been populated and is being removed in the next version
- Correct investment transaction sells quantity to be negative
- Updated documentation to allow `minimum_payment_amount` to be set on loans with type `student`.

### 2020-09-14_1.13.0

- Added `standing_orders` product type.

### 2021-09-14_1.12.0

- Added `min_last_updated_datetime` option to `/accounts/balance/get` request.
- Added `last_updated_datetime` field to `Account` model for `/accounts/balance/get` response.

### 2020-09-14_1.11.0

- Removed erroneous inclusion of `account_filters` as a parameter to `/institutions/search`
- Text fixes to descriptions
- Fixed incorrect field names in some models currently used only for documentation

### 2020-09-14_1.10.0

- Added `BankTransfersEventsUpdateWebhook` schema

### 2020-09-14_1.9.0

- Added new `auth` property to `/link/token/create` request to support Flexible Auth (currently in closed beta).
- Text fixes to descriptions.

### 2020-09-14_1.8.0

- Added `additionalProperties` to all objects to prevent additive keys from breaking.
- Added new propery to `Transaction` model, `authorized_datetime`, `datetime`.
- Update `access_token` to `required` for `TransactionsGet`.
- Require `origination_account_id` in `BankTransferBalanceGetResponse`
- Add new endpoint `/sandbox/bank_transfer/fire_webhook`

### 2020-09-14_1.5.3

- Added new payment processors.

### 2020-09-14_1.5.0

Initial version

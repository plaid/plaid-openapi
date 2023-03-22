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
- Modify documentation for credit categories in the `/asset_report/get` based on GTM feedback

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
–	Update description of `/payment_initiation/recipient/create` to mention non-Eurozone countries.
–	Update `/payment_initiation/payment/create` mentioning new currencies and non-Eurozone markets.
–	Removed `CHF` and `CZK` from the list of supported currencies.

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

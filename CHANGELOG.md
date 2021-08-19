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
    + `switch_method`
    + `employer_name`
    + `employer_id`
    + `institution_name`
    + `institution_id`

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
- Fixed  `ytd_net_income` value in `IncomeVerificationSummaryGetResponse` example
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

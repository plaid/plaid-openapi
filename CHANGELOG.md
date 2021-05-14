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

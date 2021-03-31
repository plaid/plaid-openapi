### 2020-09-14_1.12.0
- Added `standing_orders` product type.

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

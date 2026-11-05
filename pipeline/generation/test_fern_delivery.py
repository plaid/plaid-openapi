"""Private delivery boundary tests; HTTP and the separate crypto boundary are mocked."""

import copy
import gc
import io
import json
import os
from pathlib import Path
import tempfile
import traceback
import unittest
import urllib.error
import urllib.request
import warnings
from unittest.mock import Mock, patch

import fern_delivery as delivery


class Response(io.BytesIO):
    def __init__(self, value, url, *, headers=None, status=200):
        super().__init__(json.dumps(value).encode() if not isinstance(value, bytes) else value)
        self.url, self.status = url, status
        self.headers = headers or {}

    def geturl(self):
        return self.url

    def getcode(self):
        return self.status


class ErrorBody(io.BytesIO):
    read_count = 0

    def read(self, *args):
        self.read_count += 1
        return super().read(*args)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.token = "ghs_TEST_MACHINE_CREDENTIAL_DO_NOT_LOG"
        self.repository = "example/raw-sdk"
        self.base, self.head = "a" * 40, "b" * 40
        self.metadata = {"id": 1234, "full_name": self.repository, "private": True, "fork": False}
        self.envelope = {"payloadType": "application/vnd.in-toto+json", "payload": "ZXhhbXBsZQ==", "signatures": []}
        self.receipt = json.dumps(self.envelope).encode()
        body = delivery.START + "\n```json\n" + self.receipt.decode() + "\n```\n" + delivery.END
        self.pull = {"number": 17, "state": "open", "merged": False, "draft": False, "body": body,
                     "base": {"repo": copy.deepcopy(self.metadata), "sha": self.base, "ref": "main"},
                     "head": {"repo": copy.deepcopy(self.metadata), "sha": self.head, "ref": "generated/example"}}
        self.args = dict(repository=self.repository, repository_id=1234, number=17,
                         expected_base=self.base, machine_token=self.token)
        self.verify_args = dict(sdk_repo=Path("/fixture/git-cache"), public_key=b"PUBLIC KEY",
                                expected={"repository": "https://github.com/" + self.repository,
                                          "job_id": "11111111-1111-4111-8111-111111111111"})
        self.summary = {"receipt_sha256": "c" * 64, "input_sha256": "d" * 64}

    def test_gets_only_fixed_github_endpoints_with_explicit_credential_and_bounds(self):
        values, requests = iter([self.metadata, self.pull]), []
        def respond(request, *, timeout):
            requests.append(request)
            self.assertEqual(timeout, delivery.TIMEOUT_SECONDS)
            return Response(next(values), request.full_url)
        opener = Mock()
        opener.open.side_effect = respond
        with patch.object(delivery.urllib.request, "build_opener", return_value=opener) as factory:
            snapshot = delivery.fetch_snapshot(**self.args, expected_head=self.head)
        self.assertEqual(snapshot.head, self.head)
        self.assertEqual(snapshot.base, self.base)
        self.assertEqual(snapshot.receipt, self.receipt)
        self.assertEqual([request.full_url for request in requests],
                         ["https://api.github.com/repos/example/raw-sdk", "https://api.github.com/repos/example/raw-sdk/pulls/17"])
        for request in requests:
            self.assertEqual(request.get_method(), "GET")
            self.assertIsNone(request.data)
            self.assertEqual(request.get_header("Authorization"), "Bearer " + self.token)
        for call in factory.call_args_list:
            self.assertIsInstance(call.args[0], urllib.request.ProxyHandler)
            self.assertEqual(call.args[0].proxies, {})
            self.assertIsInstance(call.args[1], delivery._NoRedirect)
        self.assertNotIn(self.repository, repr(snapshot))
        self.assertNotIn(self.head, repr(snapshot))

    def test_missing_machine_credential_never_uses_personal_environment_auth(self):
        for token in ("", None, "bad\ncredential", "bad credential"):
            with self.subTest(token=token), patch.dict(os.environ, {"GH_TOKEN": "personal-fixture", "GITHUB_TOKEN": "personal-fixture"}), \
                 patch.object(delivery.urllib.request, "build_opener") as opener, self.assertRaises(delivery.DeliveryError):
                delivery.fetch_snapshot(**dict(self.args, machine_token=token))
            opener.assert_not_called()

    def test_rejects_untrusted_target_or_commit_before_network(self):
        cases = [{"repository": "example/raw-sdk?private=value"}, {"repository": "../raw-sdk"},
                 {"repository": "https://elsewhere.example/repo"}, {"repository_id": True},
                 {"number": True}, {"number": 0}, {"expected_base": "main"}, {"expected_head": "main"}]
        for change in cases:
            with self.subTest(change=change), patch.object(delivery, "_get") as get, self.assertRaises(delivery.DeliveryError):
                delivery.fetch_snapshot(**dict(self.args, **change))
            get.assert_not_called()

    def test_repository_identity_private_and_original_are_required(self):
        for change in ({"id": True}, {"id": 999}, {"full_name": "example/different"}, {"private": False}, {"fork": True}):
            with self.subTest(change=change), patch.object(delivery, "_get", return_value=dict(self.metadata, **change)), \
                 self.assertRaises(delivery.DeliveryError):
                delivery.fetch_snapshot(**self.args)

    def test_pr_identity_and_both_repo_sides_must_match(self):
        changes = [lambda p: p.update(number=18), lambda p: p.update(number=True),
                   lambda p: p.update(state="closed"), lambda p: p.update(merged=True),
                   lambda p: p["head"]["repo"].update(fork=True),
                   lambda p: p["head"]["repo"].update(id=999),
                   lambda p: p["base"]["repo"].update(private=False),
                   lambda p: p["base"]["repo"].update(full_name="example/other"),
                   lambda p: p["base"].update(sha="c" * 40), lambda p: p["head"].update(sha="main"),
                   lambda p: p["head"].update(ref=""), lambda p: p.update(body=None)]
        for change in changes:
            pull = copy.deepcopy(self.pull)
            change(pull)
            with self.subTest(pull=pull), patch.object(delivery, "_get", side_effect=[self.metadata, pull]), \
                 self.assertRaises(delivery.DeliveryError):
                delivery.fetch_snapshot(**self.args)
        with patch.object(delivery, "_get", side_effect=[self.metadata, self.pull]), self.assertRaises(delivery.DeliveryError):
            delivery.fetch_snapshot(**self.args, expected_head="d" * 40)

    def test_provenance_block_must_be_unique_well_formed_and_bounded(self):
        good = self.pull["body"]
        for body in ("", good + good, good + delivery.START, good.replace("```json", "```text"),
                     good.replace(delivery.END, ""), good.replace(self.receipt.decode(), "[]"),
                     good.replace(self.receipt.decode(), '{"duplicate":1,"duplicate":2}'),
                     good.replace(self.receipt.decode(), '{"invalid":NaN}'), "\ud800"):
            with self.subTest(body=body), self.assertRaises(delivery.DeliveryError):
                delivery.extract_receipt(body)
        with patch.object(delivery, "MAX_RECEIPT_BYTES", 10), self.assertRaises(delivery.DeliveryError):
            delivery.extract_receipt(good)
        with patch.object(delivery, "MAX_BODY_BYTES", 10), self.assertRaises(delivery.DeliveryError):
            delivery.extract_receipt(good)

    def test_permission_and_server_failures_never_expose_error_body_url_or_token(self):
        private = "private-example-secret-location"
        for code in (401, 403, 404, 429, 500):
            body = ErrorBody((self.token + private).encode())
            error = urllib.error.HTTPError("https://api.github.com/" + private, code, self.token, {}, body)
            opener = Mock()
            opener.open.side_effect = error
            with self.subTest(code=code), patch.object(delivery.urllib.request, "build_opener", return_value=opener):
                try:
                    delivery.fetch_snapshot(**self.args)
                except delivery.DeliveryError as caught:
                    message = "".join(traceback.format_exception(caught))
                    self.assertIn("HTTP " + str(code), str(caught))
                    self.assertNotIn(self.token, message)
                    self.assertNotIn(private, message)
                else:
                    self.fail("HTTP error accepted")
            self.assertEqual(body.read_count, 0)
            self.assertTrue(body.closed)

    def test_error_cleanup_does_not_emit_a_warning_containing_private_details(self):
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always", ResourceWarning)
            error = urllib.error.HTTPError("https://api.github.com/private", 403, self.token, {}, io.BytesIO(b"private"))
            opener = Mock()
            opener.open.side_effect = error
            with patch.object(delivery.urllib.request, "build_opener", return_value=opener), self.assertRaises(delivery.DeliveryError):
                delivery.fetch_snapshot(**self.args)
            del opener, error
            gc.collect()
        self.assertFalse(captured)

    def test_transport_failure_does_not_log_underlying_error(self):
        for error in (urllib.error.URLError(self.token), TimeoutError(self.token), OSError(self.token)):
            opener = Mock()
            opener.open.side_effect = error
            with self.subTest(error=type(error)), patch.object(delivery.urllib.request, "build_opener", return_value=opener), \
                 self.assertRaisesRegex(delivery.DeliveryError, "read failed") as raised:
                delivery.fetch_snapshot(**self.args)
            self.assertNotIn(self.token, str(raised.exception))

    def test_redirect_handler_never_creates_a_redirected_request(self):
        request = urllib.request.Request("https://api.github.com/repos/example/raw-sdk",
                                         headers={"Authorization": "Bearer " + self.token})
        for target in ("https://other.example/" + self.token, "https://api.github.com/another-private-repo"):
            with self.subTest(target=target), self.assertRaisesRegex(delivery.DeliveryError, "redirects are forbidden") as raised:
                delivery._NoRedirect().redirect_request(request, None, 302, "found", {}, target)
            self.assertNotIn(target, str(raised.exception))

    def test_bounded_or_malformed_http_responses_fail_closed(self):
        url = "https://api.github.com/repos/example/raw-sdk"
        cases = [(b"{}", {"Content-Length": str(delivery.MAX_RESPONSE_BYTES + 1)}, url),
                 (b"{}", {"Content-Length": "invalid"}, url),
                 (b"x" * (delivery.MAX_RESPONSE_BYTES + 1), {}, url),
                 (b'{"duplicate":1,"duplicate":2}', {}, url), (b"[]", {}, url),
                 (b"not JSON", {}, url), (b"{}", {}, "https://other.example/private")]
        for body, headers, returned_url in cases:
            opener = Mock()
            opener.open.return_value = Response(body, returned_url, headers=headers)
            with self.subTest(headers=headers, returned_url=returned_url), \
                 patch.object(delivery.urllib.request, "build_opener", return_value=opener), self.assertRaises(delivery.DeliveryError):
                delivery.fetch_snapshot(**self.args)

    def test_verified_summary_and_private_receipt_are_separated(self):
        with patch.object(delivery, "_get", side_effect=[self.metadata, self.pull, self.metadata, self.pull]) as get, \
             patch.object(delivery.fern_provenance, "verify", return_value=self.summary) as verify:
            result = delivery.fetch_and_verify(**self.args, **self.verify_args)
        verify.assert_called_once_with(self.receipt, self.verify_args["public_key"], self.verify_args["sdk_repo"],
                                       self.head, self.verify_args["expected"])
        self.assertEqual(get.call_count, 4)
        self.assertEqual(result.public_summary, self.summary)
        self.assertEqual(result.snapshot.receipt, self.receipt)
        self.assertNotIn(self.repository, repr(result))
        self.assertNotIn(self.receipt.decode(), repr(result))

    def test_bad_signature_stops_without_rereading_or_returning_a_summary(self):
        with patch.object(delivery, "_get", side_effect=[self.metadata, self.pull]) as get, \
             patch.object(delivery.fern_provenance, "verify", side_effect=ValueError(self.token)), \
             self.assertRaisesRegex(delivery.DeliveryError, "provenance verification failed") as raised:
            delivery.fetch_and_verify(**self.args, **self.verify_args)
        self.assertEqual(get.call_count, 2)
        self.assertNotIn(self.token, str(raised.exception))

    def test_head_base_body_and_repository_changes_during_verification_are_rejected(self):
        changes = [lambda p: p["head"].update(sha="e" * 40), lambda p: p["base"].update(sha="e" * 40),
                   lambda p: p.update(body=p["body"] + "\nText changed outside signature."),
                   lambda p: p["head"].update(ref="renamed"), lambda p: p.update(state="closed")]
        for change in changes:
            pull = copy.deepcopy(self.pull)
            change(pull)
            with self.subTest(change=change), patch.object(delivery, "_get", side_effect=[self.metadata, self.pull, self.metadata, pull]), \
                 patch.object(delivery.fern_provenance, "verify", return_value=self.summary), self.assertRaises(delivery.DeliveryError):
                delivery.fetch_and_verify(**self.args, **self.verify_args)
        with patch.object(delivery, "_get", side_effect=[self.metadata, self.pull, dict(self.metadata, private=False)]), \
             patch.object(delivery.fern_provenance, "verify", return_value=self.summary), self.assertRaises(delivery.DeliveryError):
            delivery.fetch_and_verify(**self.args, **self.verify_args)

    def test_expected_provenance_target_must_match_api_target(self):
        with patch.object(delivery, "_get") as get, self.assertRaises(delivery.DeliveryError):
            delivery.fetch_and_verify(**self.args, **dict(self.verify_args, expected={"repository": "https://github.com/example/other"}))
        get.assert_not_called()

    def test_retrieved_receipt_passes_real_crypto_and_git_verification(self):
        from test_fern_provenance import SignedFixture
        with tempfile.TemporaryDirectory(prefix="fern-delivery-crypto-") as directory:
            fixture = SignedFixture(directory)
            repository = fixture.expected["repository"].removeprefix("https://github.com/")
            metadata = dict(self.metadata, full_name=repository)
            pull = copy.deepcopy(self.pull)
            for side in ("base", "head"):
                pull[side]["repo"] = metadata
            pull["head"]["sha"] = fixture.commit
            receipt = fixture.receipt()
            pull["body"] = delivery.START + "\n```json\n" + receipt.decode() + "\n```\n" + delivery.END
            def verify(original, key, sdk, commit, expected):
                self.assertEqual((original, key, sdk, commit, expected),
                                 (receipt, fixture.public_key, fixture.sdk, fixture.commit, fixture.expected))
                # Only this ephemeral test signer substitutes the production key pin.
                return fixture.verify(original)
            with patch.object(delivery, "_get", side_effect=[metadata, pull, metadata, pull]), \
                 patch.object(delivery.fern_provenance, "verify", side_effect=verify):
                result = delivery.fetch_and_verify(**dict(self.args, repository=repository),
                    sdk_repo=fixture.sdk, public_key=fixture.public_key, expected=fixture.expected)
            self.assertEqual(result.public_summary["git_commit"], fixture.commit)
            self.assertEqual(result.public_summary["git_tree"], fixture.tree)
            self.assertNotIn(repository, json.dumps(result.public_summary))


if __name__ == "__main__":
    unittest.main()

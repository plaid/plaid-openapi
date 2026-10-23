package main

import (
	"strings"
	"testing"
)

const internalFixture = `package internal
import (
 "net/http"
 "example/core"
)
func TestClients() {
 caller := NewCaller(&CallerParams{Client: client})
 params := &CallParams{Client: server.Client(), URL: server.URL}
 caller = NewCaller(&CallerParams{Client: &http.Client{Transport: &cancelAfterRoundTripTransport{base: server.Client().Transport, cancel: cancel, buffer: true}}})
 callParams.Client = server.Client()
 _ = caller
 _ = params
}
`

func TestClientExpressionsAndPerCallOverrideArePreserved(t *testing.T) {
	result, err := transformInternal("fixture", internalFixture, 3, 1)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Count(result, "&core.CustomEndpointClient{BaseURL: server.URL, HTTPClient:") != 4 {
		t.Fatal("all constructor and per-call clients must explicitly allow only their server")
	}
	for _, unchanged := range []string{"HTTPClient: client}", "HTTPClient: server.Client()}", "Transport: &cancelAfterRoundTripTransport{base: server.Client().Transport, cancel: cancel, buffer: true}"} {
		if !strings.Contains(result, unchanged) {
			t.Fatalf("lost original client behavior: %s", unchanged)
		}
	}
	again, err := transformInternal("fixture", result, 3, 1)
	if err != nil || result != again {
		t.Fatalf("second run changed output: %v", err)
	}
}

func TestUnrecognizedClientOrInventoryStopsTransformation(t *testing.T) {
	for _, source := range []string{
		strings.Replace(internalFixture, "Client: client", "Client: customTransport", 1),
		strings.Replace(internalFixture, "callParams.Client", "other.Client", 1),
		strings.Replace(internalFixture, "CallerParams{Client: client}", "Unexpected{Client: client}", 1),
		strings.Replace(internalFixture, "params := &CallParams{Client: server.Client(), URL: server.URL}", "params := &CallParams{URL: server.URL}", 1),
	} {
		if _, err := transformInternal("fixture", source, 3, 1); err == nil {
			t.Fatal("unrecognized shape accepted")
		}
	}
	result, err := transformInternal("fixture", internalFixture, 3, 1)
	if err != nil {
		t.Fatal(err)
	}
	result = strings.Replace(result, "BaseURL: server.URL", "BaseURL: other.URL", 1)
	if _, err := transformInternal("fixture", result, 3, 1); err == nil {
		t.Fatal("changed custom endpoint accepted")
	}
}

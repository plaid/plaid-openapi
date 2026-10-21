package plaid

import (
	"encoding/json"
	"testing"
)

// This offline check also demonstrates the raw-spec generation regression.
func TestPublicDiscriminatorContract(t *testing.T) {
	var union CraReportGetRequestProduct
	if err := json.Unmarshal([]byte(`{"product":"cra_qualify","version":"V1","future_field":true}`), &union); err != nil {
		t.Fatalf("decode known wire discriminator: %v", err)
	}
	if union.CraQualifyProduct == nil || union.CraQualifyProduct.Product != "cra_qualify" {
		t.Fatal("known discriminator did not select its branch")
	}
	if _, err := json.Marshal(union); err != nil {
		t.Fatalf("marshal selected branch: %v", err)
	}
	if err := json.Unmarshal([]byte(`{"product":"CraQualifyProduct","version":"V1"}`), &union); err == nil {
		t.Fatal("Go class name accepted as wire discriminator")
	}
	if union.CraQualifyProduct != nil {
		t.Fatal("failed decode retained previous branch")
	}
	if _, err := json.Marshal(CraReportGetRequestProduct{}); err == nil {
		t.Fatal("empty union accepted")
	}
}

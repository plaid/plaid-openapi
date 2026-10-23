// This standalone tool transforms reviewed generated tests, never SDK runtime code.
package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"os"
	"sort"
	"strconv"
	"strings"
)

type edit struct {
	start, end int
	value      string
}

func transformInternal(name, source string, expectedClients, expectedAssignments int) (string, error) {
	positions := token.NewFileSet()
	file, err := parser.ParseFile(positions, name, source, parser.ParseComments)
	if err != nil {
		return "", err
	}
	coreImport := false
	for _, imp := range file.Imports {
		path, _ := strconv.Unquote(imp.Path.Value)
		if strings.HasSuffix(path, "/core") && (imp.Name == nil || imp.Name.Name == "core") {
			coreImport = true
		}
	}
	if file.Name.Name != "internal" || !coreImport {
		return "", fmt.Errorf("%s: unexpected generated internal test package/imports", name)
	}
	edits := []edit{}
	clients, assignments := 0, 0
	text := func(node ast.Node) string {
		return source[positions.Position(node.Pos()).Offset:positions.Position(node.End()).Offset]
	}
	wrap := func(value ast.Expr) {
		if err != nil {
			return
		}
		expression := value
		alreadyWrapped := false
		if pointer, ok := value.(*ast.UnaryExpr); ok && pointer.Op == token.AND {
			if literal, ok := pointer.X.(*ast.CompositeLit); ok && text(literal.Type) == "core.CustomEndpointClient" {
				fields := map[string]ast.Expr{}
				for _, entry := range literal.Elts {
					field, ok := entry.(*ast.KeyValueExpr)
					if !ok || fields[text(field.Key)] != nil {
						err = fmt.Errorf("%s: unexpected custom endpoint wrapper", name)
						return
					}
					fields[text(field.Key)] = field.Value
				}
				if len(fields) != 2 || fields["BaseURL"] == nil || text(fields["BaseURL"]) != "server.URL" || fields["HTTPClient"] == nil {
					err = fmt.Errorf("%s: custom endpoint wrapper changed", name)
					return
				}
				expression, alreadyWrapped = fields["HTTPClient"], true
			}
		}
		allowed := text(expression) == "client" || text(expression) == "server.Client()"
		if pointer, ok := expression.(*ast.UnaryExpr); ok && pointer.Op == token.AND {
			literal, ok := pointer.X.(*ast.CompositeLit)
			allowed = allowed || (ok && text(literal.Type) == "http.Client")
		}
		if !allowed {
			err = fmt.Errorf("%s: unrecognized HTTP client expression", name)
			return
		}
		if !alreadyWrapped {
			edits = append(edits, edit{positions.Position(value.Pos()).Offset, positions.Position(value.End()).Offset,
				"&core.CustomEndpointClient{BaseURL: server.URL, HTTPClient: " + text(value) + "}"})
		}
	}
	ast.Inspect(file, func(node ast.Node) bool {
		switch node := node.(type) {
		case *ast.CompositeLit:
			for _, entry := range node.Elts {
				field, ok := entry.(*ast.KeyValueExpr)
				if !ok || text(field.Key) != "Client" {
					continue
				}
				if text(node.Type) != "CallerParams" && text(node.Type) != "CallParams" {
					err = fmt.Errorf("%s: unrecognized Client field", name)
					continue
				}
				clients++
				wrap(field.Value)
			}
		case *ast.AssignStmt:
			for index, target := range node.Lhs {
				selector, ok := target.(*ast.SelectorExpr)
				if !ok || selector.Sel.Name != "Client" {
					continue
				}
				if len(node.Lhs) != 1 || len(node.Rhs) != 1 || (text(selector.X) != "clientParams" && text(selector.X) != "callParams") {
					err = fmt.Errorf("%s: unrecognized client assignment", name)
					continue
				}
				assignments++
				wrap(node.Rhs[index])
			}
		}
		return true
	})
	if err != nil {
		return "", err
	}
	if clients != expectedClients || assignments != expectedAssignments {
		return "", fmt.Errorf("%s: generated client inventory changed (%d fields, %d assignments)", name, clients, assignments)
	}
	sort.Slice(edits, func(i, j int) bool { return edits[i].start > edits[j].start })
	for _, change := range edits {
		source = source[:change.start] + change.value + source[change.end:]
	}
	if len(edits) == 0 {
		return source, nil
	}
	formatted, err := format.Source([]byte(source))
	return string(formatted), err
}

func main() {
	var sources map[string]string
	if err := json.NewDecoder(os.Stdin).Decode(&sources); err != nil {
		panic(err)
	}
	inventory := map[string][2]int{"caller_test.go": {9, 0}, "pager_test.go": {1, 0}, "retrier_test.go": {5, 1}}
	if len(sources) != len(inventory) {
		panic("unexpected internal test inventory")
	}
	for name, counts := range inventory {
		updated, err := transformInternal(name, sources[name], counts[0], counts[1])
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		sources[name] = updated
	}
	if err := json.NewEncoder(os.Stdout).Encode(sources); err != nil {
		panic(err)
	}
}

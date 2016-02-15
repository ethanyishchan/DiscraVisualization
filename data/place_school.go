package main

import (
	"encoding/json"
	"os"
)

func getSchools() []Place {
	f, err := os.Open("const/schools.json")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	var places []Place
	if err := json.NewDecoder(f).Decode(&places); err != nil {
		panic(err)
	}
	for i := range places {
		places[i].Type = "school"
	}
	return places
}

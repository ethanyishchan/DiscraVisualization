package main

import (
	"encoding/json"
	"os"
	"strings"
)

type Activity struct {
	Unique
	Name  string `json:"name"`
	Desc  string `json:"desc"`
	Categ string `json:"categ"`
	Point string `json:"point"`
	Loc   string `json:"loc"`
	Start string `json:"start"`
	End   string `json:"end"`
	Owner int    `json:"owner"`
	Parts []int  `json:"participants"`
	Cap   int    `json:"cap"`
}

func getActivities() []Activity {
	f, err := os.Open("var/activities.json")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	var activities []Activity
	if err := json.NewDecoder(f).Decode(&activities); err != nil {
		panic(err)
	}
	return activities
}

func putActivities(activities []Activity) {
	f, err := os.Create("var/activities.json")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	if err := json.NewEncoder(f).Encode(&activities); err != nil {
		panic(err)
	}
}

func (a Activity) Matches(s string) bool {
	s = strings.ToLower(s)
	fields := []string{
		strings.ToLower(a.Name),
		strings.ToLower(a.Desc),
		strings.ToLower(a.Loc),
		strings.ToLower(a.Start),
		strings.ToLower(a.End),
	}
	for _, sub := range strings.Split(s, " ") {
		if !anyContains(fields, sub) {
			return false
		}
	}
	return true
}

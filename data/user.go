package main

import (
	"encoding/json"
	"os"
)

type User struct {
	Unique
	Name    string `json:"name"`
	Surname string `json:"surname"`
}

func getUsers() []User {
	f, err := os.Open("const/users.json")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	var users []User
	if err := json.NewDecoder(f).Decode(&users); err != nil {
		panic(err)
	}
	return users
}

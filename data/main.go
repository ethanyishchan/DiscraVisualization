/* Copyright (c) 2014-2015, Daniel Martí <mvdan@mvdan.cc> */
/* See LICENSE for licensing information */

package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"path/filepath"
	"strconv"
	"sync"

	"github.com/gorilla/mux"
)

var (
	listen = flag.String("l", ":8080", "Host and port to listen to")
)

func logr(w http.ResponseWriter, r *http.Request) {
	log.Printf("%s %s %s", r.RemoteAddr, r.Method, r.URL.Path)
}

type handler struct {
	tmpl   *template.Template
	places []Place
	users  []User
	activs []Activity
	m      sync.RWMutex
}

func newHttpHandler() *handler {
	h := &handler{
		users:  getUsers(),
		activs: getActivities(),
	}
	h.addPlaces(getClubs())
	h.addPlaces(getSchools())
	return h
}

func (h *handler) addPlaces(places []Place) {
	for _, p := range places {
		p.Id = len(h.places) + 1
		h.places = append(h.places, p)
	}
}

func (h *handler) index(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	http.ServeFile(w, r, "README.md")
}

func filterPlaces(places []Place, search string) []Place {
	if search == "" {
		return places
	}
	found := []Place{}
	for _, p := range places {
		if !p.Matches(search) {
			continue
		}
		found = append(found, p)
	}
	return found
}

func (h *handler) searchplaces(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	search := mux.Vars(r)["search"]
	places := filterPlaces(h.places, search)
	doMarshal(w, r, &places)
}

func filterActivs(activs []Activity, search string) []Activity {
	if search == "" {
		return activs
	}
	found := []Activity{}
	for _, p := range activs {
		if !p.Matches(search) {
			continue
		}
		found = append(found, p)
	}
	return found
}

func (h *handler) searchactivs(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	h.m.RLock()
	defer h.m.RUnlock()
	search := mux.Vars(r)["search"]
	activs := filterActivs(h.activs, search)
	doMarshal(w, r, &activs)
}

func (h *handler) getplacebyid(id string) (*Place, error) {
	n, err := strconv.Atoi(id)
	if err != nil {
		return nil, err
	}
	if n < 1 || n > len(h.places) {
		return nil, errors.New("place not found")
	}
	return &h.places[n-1], nil
}

func (h *handler) getplace(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	id := mux.Vars(r)["id"]
	p, err := h.getplacebyid(id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	doMarshal(w, r, p)
}

func (h *handler) getuserbyid(id string) (*User, error) {
	n, err := strconv.Atoi(id)
	if err != nil {
		return nil, err
	}
	if n < 1 || n > len(h.users) {
		return nil, errors.New("user not found")
	}
	return &h.users[n-1], nil
}

func (h *handler) getuser(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	id := mux.Vars(r)["id"]
	u, err := h.getuserbyid(id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	doMarshal(w, r, u)
}

func (h *handler) postactivity(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	h.m.Lock()
	defer h.m.Unlock()
	decoder := json.NewDecoder(r.Body)
	var a Activity
	if err := decoder.Decode(&a); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		log.Println(err)
		return
	}
	a.Id = len(h.activs) + 1
	if a.Cap < 1 {
		a.Cap = 1
	}
	if a.Cap > 50 {
		a.Cap = 50
	}
	if a.Owner < 1 {
		a.Owner = 1
	}
	a.Parts = []int{a.Owner}
	if a.Owner > len(h.users) {
		a.Owner = 1
	}
	h.activs = append(h.activs, a)
	doOK(w, r)
}

func (h *handler) getactivitybyid(id string) (*Activity, error) {
	n, err := strconv.Atoi(id)
	if err != nil {
		return nil, err
	}
	if n < 1 || n > len(h.activs) {
		return nil, errors.New("activity not found")
	}
	return &h.activs[n-1], nil
}

func (h *handler) getactivity(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	h.m.RLock()
	defer h.m.RUnlock()
	id := mux.Vars(r)["id"]
	a, err := h.getactivitybyid(id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	doMarshal(w, r, a)
}

func (h *handler) joinactivity(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	h.m.Lock()
	defer h.m.Unlock()
	uid := mux.Vars(r)["uid"]
	u, err := h.getuserbyid(uid)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	aid := mux.Vars(r)["aid"]
	a, err := h.getactivitybyid(aid)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if len(a.Parts) >= a.Cap {
		http.Error(w, "activity already full", http.StatusBadRequest)
		return
	}
	for _, id := range a.Parts {
		if id == u.Id {
			http.Error(w, "user already part of activity", http.StatusBadRequest)
			return
		}
	}
	a.Parts = append(a.Parts, u.Id)
	doOK(w, r)
}

func (h *handler) leaveactivity(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	h.m.Lock()
	defer h.m.Unlock()
	uid := mux.Vars(r)["uid"]
	u, err := h.getuserbyid(uid)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	aid := mux.Vars(r)["aid"]
	a, err := h.getactivitybyid(aid)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	if u.Id == a.Owner {
		http.Error(w, "owner cannot leave activity", http.StatusBadRequest)
		return
	}
	found := false
	newparts := []int{}
	for _, id := range a.Parts {
		if id == u.Id {
			found = true
			continue
		}
		newparts = append(newparts, id)
	}
	if !found {
		http.Error(w, "user not part of activity", http.StatusBadRequest)
		return
	}
	a.Parts = newparts
	doOK(w, r)
}

func (h *handler) getusers(w http.ResponseWriter, r *http.Request) {
	logr(w, r)
	doMarshal(w, r, &h.users)
}

func (h *handler) getidimg(kind, name string) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		logr(w, r)
		id := mux.Vars(r)["id"]
		doFile(w, r, filepath.Join(kind, "img", name, id+".jpg"))
	}
}

func addHeaders(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
}

func doFile(w http.ResponseWriter, r *http.Request, path string) {
	addHeaders(w, r)
	http.ServeFile(w, r, path)
}

func doMarshal(w http.ResponseWriter, r *http.Request, v interface{}) {
	addHeaders(w, r)
	b, err := json.MarshalIndent(v, "", "\t")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Write(b)
}

func doOK(w http.ResponseWriter, r *http.Request) {
	addHeaders(w, r)
	fmt.Fprintln(w, "OK")
}

func main() {
	flag.Parse()
	h := newHttpHandler()
	r := mux.NewRouter()
	r.HandleFunc("/", h.index).Methods("GET")
	r.HandleFunc("/place/{id}", h.getplace).Methods("GET")
	r.HandleFunc("/places", h.searchplaces).Methods("GET")
	r.HandleFunc("/places/", h.searchplaces).Methods("GET")
	r.HandleFunc("/places/{search}", h.searchplaces).Methods("GET")
	r.HandleFunc("/user/{id}", h.getuser).Methods("GET")
	r.HandleFunc("/user/{uid}/join/{aid}", h.joinactivity).Methods("GET")
	r.HandleFunc("/user/{uid}/leave/{aid}", h.leaveactivity).Methods("GET")
	r.HandleFunc("/users", h.getusers).Methods("GET")
	r.HandleFunc("/users/", h.getusers).Methods("GET")
	r.HandleFunc("/activity", h.postactivity).Methods("POST")
	r.HandleFunc("/activity/{id}", h.getactivity).Methods("GET")
	r.HandleFunc("/activities", h.searchactivs).Methods("GET")
	r.HandleFunc("/activities/", h.searchactivs).Methods("GET")
	r.HandleFunc("/img/place/{id}", h.getidimg("const", "place")).Methods("GET")
	r.HandleFunc("/img/user/{id}", h.getidimg("const", "user")).Methods("GET")
	r.HandleFunc("/img/activity/{id}", h.getidimg("var", "activity")).Methods("GET")
	log.Printf("listen = %s", *listen)
	http.Handle("/", r)
	log.Println("Up and running!")
	log.Fatal(http.ListenAndServe(*listen, nil))
}

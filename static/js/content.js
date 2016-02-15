var myip

$(document).ready(function () {
	console.log("hello there")
	// setDefaultLocation()

	// initializeMaps()

// 	$(function(){
// 	    $("[data-hide]").on("click", function(){
// 	        $("." + $(this).attr("data-hide")).hide();
// 	    });
// 	});

// 	$('html').on('click', '.action.like', function (e) {
// 		var curr_div = $(e.currentTarget),
// 			idea_id = curr_div.parents('.idea').attr('id').split("_")[1]

// 		$.post("/accounts/upvote/", $('#if_'+idea_id.toString()).serialize(), function (data) {
// 			console.log(data)
// 			var html = "<span class=\"glyphicon glyphicon-thumbs-up\"></span> " + data
// 			curr_div.html(html)
// 		})	
// 	})

// 	$('#add_idea').on('click', function (e) {
// 		$.post("/accounts/add_idea/", $('#new-idea').serialize(), function (data) {
// 			$('#ideas_1').append(data)
// 		})
// 	})

// 	$('.nearby_ideas_item').on('click', function (e) {
// 		getCurrentLocation(function (location_data) {
// 			$('#current_location_lat').val(location_data['location_lat'])
// 			$('#current_location_long').val(location_data['location_long'])
// 			$.post("/accounts/get_nearby_ideas/", $('#nearby_form').serialize(), function (html) {
// 				console.log(html)
// 				$('.ideas').html(html)	
// 			})
// 		})
// 	})

// 	$('.filter_category_item').on('click', function (e) {
// 		var curr_div = $(e.currentTarget),
// 			category = curr_div.attr('category')
// 		$.post("/accounts/filter_ideas/", $("#filter_category_form_"+category).serialize(), function (data) {
// 			if (data == "empty") {
// 				$('.ideas_not_found').html("<strong>Oops!</strong> Looks like nobody has an idea about "+category+" yet!")
// 				$('.alert').show()
// 			} else {
// 				$('.ideas').html(data)
// 			}
// 		})
// 	})

// 	$('.popular_ideas_item').on('click', function (e) {
// 		var curr_div = $(e.currentTarget)
// 		$.post("/accounts/sort_ideas/", $("#popular_ideas_form").serialize(), function (data) {
// 			$('.ideas').html(data)
// 		})
// 	})

// 	$('.recent_ideas_item').on('click', function (e) {
// 		var curr_div = $(e.currentTarget)
// 		$.post("/accounts/recent_ideas/", $("#whats_new_form").serialize(), function (data) {
// 			$('.ideas').html(data)
// 		})
// 	})

// 	$('.category_menu a').on('click', function (e) {
// 		var curr_div = $(e.currentTarget),
// 			parent_li = $(curr_div.parent('li'))
// 		$('.category_menu li').each(function () {
// 			$(this).removeClass('active')
// 		})
// 		parent_li.addClass('active')
// 	})

// 	$('.sorting_menu a').on('click', function (e) {
// 		var curr_div = $(e.currentTarget),
// 			parent_li = $(curr_div.parent('li'))
// 		$('.sorting_menu li').each(function () {
// 			$(this).removeClass('active')
// 		})
// 		parent_li.addClass('active')
// 	})


// 	$('#search_query_form').submit(function (e) {
// 		var curr_div = $(e.currentTarget)
// 		$.post("/accounts/search_ideas/", $("#search_query_form").serialize(), function (data) {
// 			$('.ideas').html(data)
// 		})
// 		return false
// 	})

// })

// function initializeMaps() {
// 	var search_bar = document.getElementById('ideaLocation'),
// 		autocomplete = new google.maps.places.Autocomplete(search_bar),
// 		init = false

// 	google.maps.event.addListener(autocomplete, 'place_changed', function () {
// 		var place = autocomplete.getPlace()
// 		if (!place.geometry) {
// 			return
// 		}
//   		var returned_location = []
//   		for (var key in place.geometry.location)
//   			if (typeof place.geometry.location[key] == 'number' && returned_location.length < 2)
//   				returned_location.push(place.geometry.location[key])
//   		$('#new_idea_loc_lat').val(returned_location[0])
//   		$('#new_idea_loc_long').val(returned_location[1])
// 	})
// }


// function setDefaultLocation() {
// 	$.post("/accounts/get_location/", {url : "http://www.geoplugin.net/json.gp?ip="+myip.toString()}, function (data) {
// 		getCurrentLocation(function (data) {
// 			$('#ideaLocation').val(data.location_name)
// 			$('#new_idea_loc_lat').val(data.location_lat)
// 	  		$('#new_idea_loc_long').val(data.location_long)
// 		})
// 	})
// }

// function getCurrentLocation(cb) {
// 	$.post("/accounts/get_location/", {url : "http://www.geoplugin.net/json.gp?ip="+myip.toString()}, function (data) {
// 		data = $.parseJSON(data)
// 		cb({
// 			location_name : data['geoplugin_city'] + ", " + data['geoplugin_region'],
// 			location_lat : parseFloat(data['geoplugin_latitude']),
// 			location_long : parseFloat(data['geoplugin_longitude'])
// 		})
// 	})
// }


	// $('.ideaLocation').keypress(function(e) {
 
 //    google.maps.event.trigger(autocomplete, 'place_changed');
 //    return false;

	// });	


	$('#add_activity').on('click', function (e) {
		$.post("/add_activity", $('#new-idea').serialize(), function (data) {
			// $('#ideas_1').append(data)
			console.log("trying to add activity")
		})
	})

})
function initializeMaps() {



	var search_bar = document.getElementById('ideaLocation'),
		autocomplete = new google.maps.places.Autocomplete(search_bar),
		init = false

	console.log("initalizing maps")

	google.maps.event.addListener(autocomplete, 'place_changed', function () {
		console.log("hi before place")
		var place = autocomplete.getPlace()
		console.log(place)
		console.log("hi after place")
		if (!place.geometry) {
			return
		}
  		var returned_location = []
  		for (var key in place.geometry.location)
  			if (typeof place.geometry.location[key] == 'number' && returned_location.length < 2)
  				returned_location.push(place.geometry.location[key])
  		$('#new_idea_loc_lat').val(returned_location[0])
  		$('#new_idea_loc_long').val(returned_location[1])
	})
}


$(document).on("submit", "#phrase_form", function(evt) {
    evt.preventDefault();
    data = {'phrase':$('#text_input').val()};
    $("video").remove();
    $("#upload_text").remove();

    $('#text_container').prepend("<p id='upload_text'>Building Bumblebee.....</p>");
    
    $.ajax({
      type: "POST",
      url: "/upload_phrase",
      data: data
    }).done(function(msg) {
        console.log(msg)
       var video_container_div = $('<div style = "position: absolute; left:200px" id="video_container"></div>')
       video_container_div.empty();
       var video_div = $('<video id="video_elem" width="854" height="480" controls></video>')
       var source_div = $(' <source src="static/concat_output_with_subs.mp4" type="video/mp4">')
       video_div.append(source_div);
       video_container_div.append(video_div)
       $('#text_container').prepend(video_container_div);
       var vid = document.getElementById("video_elem");
       vid.playbackRate = .75;
       document.getElementById("video_elem").play();

       
    })
});
/*
<video width="320" height="240" controls>
  <source src="static/fast7.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
*/
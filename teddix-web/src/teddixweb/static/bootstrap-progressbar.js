
function updateProgress(percentage){
    $('#progressBar').css('width', percentage+'%');
    $('#progressBar').html(percentage+'%');
    if(percentage >= 100) {
      $('#progressBar').removeClass("active");
      $('#progressBar').addClass("progress-bar-success");
      $('#progressBar').html('Done');
    }
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


$(document).ready(function(){
  percentage = 0; 
  agent_id = getParameterByName('agent_id');
  $("#test1").load("/connection/?agent_id="+agent_id+"&action=test1", function(responseTxt,statusTxt,xhr){
      if(statusTxt=="success")
        percentage += 20
        updateProgress(percentage);
      if(statusTxt=="error")
        alert("Error: "+xhr.status+": "+xhr.statusText);
      });
  $("#test2").load("/connection/?agent_id="+agent_id+"&action=test2", function(responseTxt,statusTxt,xhr){
      if(statusTxt=="success")
        percentage += 20
        updateProgress(percentage);
      if(statusTxt=="error")
        alert("Error: "+xhr.status+": "+xhr.statusText);
    });
  $("#test3").load("/connection/?agent_id="+agent_id+"&action=test3", function(responseTxt,statusTxt,xhr){
      if(statusTxt=="success")
        percentage += 20
        updateProgress(percentage);
      if(statusTxt=="error")
        alert("Error: "+xhr.status+": "+xhr.statusText);
    });
  $("#test4").load("/connection/?agent_id="+agent_id+"&action=test4", function(responseTxt,statusTxt,xhr){
      if(statusTxt=="success")
        percentage += 20
        updateProgress(percentage);
      if(statusTxt=="error")
        alert("Error: "+xhr.status+": "+xhr.statusText);
    });
  $("#test5").load("/connection/?agent_id="+agent_id+"&action=test5", function(responseTxt,statusTxt,xhr){
      if(statusTxt=="success")
        percentage += 20
        updateProgress(percentage);
      if(statusTxt=="error")
        alert("Error: "+xhr.status+": "+xhr.statusText);
    });

});



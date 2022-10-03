$(document).delegate("#btn-upload", "click", function(){
	console.log(this.id);
	
	var btn = this.id;
	var fn = $(this).attr("fn");
	console.log("fn="+fn);
	if (fn == 'upload')
		var url = "/codergame/uploadfile";

	if (!$('#codefile').val()) {
		alert("File non caricato!");
		return false;
	}
	
	
	var fd = new FormData();
	var codefile = $('#codefile')[0].files;
	console.log("codefile : " + codefile)
	fd.append('codefile',codefile[0]);
	fd.append('taskid',$("#taskid").val());
	
	$.ajax({
	  type: "POST",			// il method
	  url: url,				// la action
	  dataType: "json",
	  data: fd,
	  contentType: false,
      processData: false,
	  beforeSend: function() {
			$("#results-panel").html("<img src='/images/icons/hourglass-sand-top--v1.png' height=14 class='fa-spin mr-3'>Salvataggio dati in corso...<br>")
	  },
	  success: function(risposta) {
			var status = risposta["status"];
			var html = risposta["html"];
			$("#results-panel").html(html)
	  },
	  // ed una per il caso di fallimento
	  error: function(){
			$("#results-panel").removeClass("d-none");
			$("#results-panel").html("Errore generico !")
	  },
	  complete: function (data) {
        $('#codefile').val(""); // this will reset the form fields
	  }
	});
});


$(document).delegate(".btn-abilita-disabilita", "click", function(){
	var fn = $(this).attr("fn");
	var task_id = $(this).attr("task_id");
	var gruppo_id = $(this).attr("gruppo_id");
	var mode = $(this).attr("mode");
	var fd = new FormData();
	var $this = $(this);
	fd.append("task_id", task_id)
	fd.append("gruppo_id", gruppo_id)
	$.ajax({
	  type: "POST",			// il method
	  url: fn,				// la action
	  dataType: "json",
	  data: fd,
	  contentType: false,
      processData: false,
	  beforeSend: function() {
			
	  },
	  success: function(risposta) {
		var status = risposta["status"];
		var html = risposta["html"];
		if (status == "OK") {
			if (mode == "abilita") {
				$("#task_"+task_id+"_gruppo_"+gruppo_id).attr("checked", true);
				$("#btn-disabilita_"+task_id+"_"+gruppo_id).removeClass("d-none");
				$("#btn-abilita_"+task_id+"_"+gruppo_id).addClass("d-none");
			}
			if (mode == "disabilita") {
				$("#task_"+task_id+"_gruppo_"+gruppo_id).attr("checked", false);
				$("#btn-disabilita_"+task_id+"_"+gruppo_id).addClass("d-none");
				$("#btn-abilita_"+task_id+"_"+gruppo_id).removeClass("d-none");
			}
		}
	  },
	  // ed una per il caso di fallimento
	  error: function(){
		  alert("Errore nel server");
	  },
	});
});
	

$(document).delegate("#scheda_task #btn-modify", "click", function(){
	var task_id = $(this).attr("task_id");
	var url = "/admin/task/update/"+task_id;

	formvalues = $("#scheda_task .form-group input, #scheda_task .form-group select, #scheda_task .form-group textarea");

	values = {}
	for (i=0; i<formvalues.length; i++) {
		values[formvalues[i].id] = formvalues[i].value;
	}
	
	$.ajax({
	  type: "POST",			// il method
	  url: url,				// la action
	  dataType: "json",
	  data: values,
	  beforeSend: function() {
	  },
	  success: function(risposta) {
		  if (risposta["status"] != 'OK') {
			  alert("Errore generico");
		  }
		  else {
			  $("#text-result").html(risposta["html"]);
		  }
	  },
	  // ed una per il caso di fallimento
	  error: function(){
	  }
	});
});



$(document).delegate("#link_add_testcase", "click", function(){
	alert("QUI");
	var task_id = $(this).attr("task_id");
	var fn = $(this).attr("fn");
	var new_input = $("#new_input").val();
	var new_output = $("#new_output").val();
	var new_punteggio = $("#new_punteggio").val();
		
	$.ajax({
	  type: "POST",			// il method
	  url: fn,				// la action
	  dataType: "json",
	  data: {
		task_id : task_id,
		new_input: new_input,
		new_output: new_output,
		new_punteggio : new_punteggio
	  },
	  beforeSend: function() {
	  },
	  success: function(risposta) {
		  if (risposta["status"] != 'OK') {
			  alert("Errore in inserimento test case");
		  }
		  else {
			  var html = "<div>"
			  html += "<b>INPUT : </b> "+new_input+" <span class='fa fa-arrow-right'></span> ";
			  html += "<b>OUTPUT ATTESO : </b> "+new_output+" : ";
			  html += "<b>PUNTEGGIO : </b> "+new_punteggio+ " <br>";
			  html += "</div>";
			  $("#testcases_list").append(html);
			  $("#new_input").val("");
			  $("#new_output").val("");
			  $("#new_punteggio").val("");
		  }
	  },
	  // ed una per il caso di fallimento
	  error: function(){
		  alert("Errore generico in inserimento test case");
	  }
	});

});


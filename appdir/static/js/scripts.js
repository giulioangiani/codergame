function genericError() {
	alert("Errore generico");
}

$(document).delegate(".closeModal", "click", function(){
	$("#BasicModal").modal("hide")
});


$(document).delegate("#sidebar li a, .ajaxlink", "click", function(){

	var fn = $(this).attr("fn");
	console.log(fn)
	var url = "/"+fn+"?ts="+$.now();
	
	var replacecontentid = $(this).attr("replacecontentid");
	var hideelementid = $(this).attr("hideelementid");
	var id_domanda = $(this).attr("id_domanda");
	var id_database = $(this).attr("id_database");
	var method = $(this).attr("method");
	if (!method) method = "GET"
	var target = $(this).attr("target")

	if ($(this).attr("confirm")) {
		if (!confirm("Confermi questa operazione ?")) 
			return false;
	}


	$.ajax({
	  type: method,			// il method
	  url: url,				// la action
	  dataType: "json",
	  data: {
		  id_domanda: id_domanda,
		  id_database: id_database,
	  },
	  beforeSend: function() {
		if (!replacecontentid) {
			$("#content").html("<img src='images/loader.gif' class='small'>");
		}
	  },
	  success: function(risposta) {	
		  
		  if (!replacecontentid) {
			  if (risposta["status"] == 'OK') {
				  $("#content").html(risposta["html"]);
			  }
			  else {
				  $("#content").html("Errore generico");
			  }
		  }
		  else {
			  if (replacecontentid=='hideelement') {
				 $("#"+hideelementid).fadeOut(1000)  
			  }
			  
			  else {
				alert(risposta["html"]);
			  }
			  
		  }
	  },
	  // ed una per il caso di fallimento
	  error: function(){
		  if (!replacecontentid) { 
			$("#content").html("Errore generico [2]");
		  }
		  else {
			  alert("Errore generico [2]");
		  }
	  }
	});
});


$(document).delegate("#search", "click", function(){
	$(".ajaxcombo").change();
});



$(document).delegate("#btn-close", "click", function(){
	$("#BasicModal").modal("hide");
});


$(document).delegate(".editobject", "click", function(){
	var fn = $(this).attr("fn");
	var _object_id = $(this).attr("_object_id");
	console.log(fn)
	var url = "/"+fn+"/"+_object_id;
	var delete_current_row = $(this).attr("delete_current_row");
	$this=$(this);
	$.ajax({
	  type: "GET",			// il method
	  url: url,				// la action
	  dataType: "json",
	  data: {
	  },
	  beforeSend: function() {
		  $("#BasicModal").modal()
	  },
	  success: function(risposta) {
		  if (risposta["status"] == 'OK') {
			  $("#BasicModal .modal-content").html(risposta["html"]);
			  if (delete_current_row=='Y') {
				  $this.parent().parent().fadeOut("slow");
			  }
		  }
		  else {
			  $("#BasicModal .modal-content").html("Errore generico");
		  }
	  },
	  // ed una per il caso di fallimento
	  error: function(){
		  $("#BasicModal .modal-content").html("Errore generico [2]");
	  }
	});
});


$(document).delegate(".filtrarighe", "click", function(){
	var table_ref_id = $(this).attr("table_ref_id");
	var findattribute = $(this).attr("findattribute");
	var checked = $(this).prop("checked");
	console.log(checked);
	var valore = $(this).attr("valore");
//	$("#"+table_ref_id+" tbody tr").show();
	if (!checked) {		// valore precedente al click
		$("#"+table_ref_id+" tbody tr["+findattribute+"="+valore+"]").hide();
	}
	else {
		$("#"+table_ref_id+" tbody tr["+findattribute+"="+valore+"]").show();
	}
})

$(document).delegate(".tr_ordering", "click", function(){
	var table_ref_id = $(this).attr("table_ref_id");
	var order_attribute = $(this).attr("order_attribute");
	var rows = $("#"+table_ref_id+" tbody tr");
	var mode = $(this).attr("mode");
	var ordered_rows = Array();
	var table_body = $("#"+table_ref_id+" tbody");
	for (var i=0; i<rows.length; i++) {
		var elem = rows[i];
		console.log(elem.getAttribute("punti_studente"));
		var order_code = elem.getAttribute("punti_studente");
		ordered_rows.push(Array(order_code, elem));
	}
	ordered_rows.sort()
	if (mode == 'asc') { 
		$(this).attr("mode", "desc");
		ordered_rows.reverse()
	}
	else {
		$(this).attr("mode", "asc");
	}
	console.log(ordered_rows)
	table_body.children().remove()
	for (var i=0; i<rows.length; i++) {
		table_body.append(ordered_rows[i][1]);
	}
	
})



function setSpin(spinid) {
	if (!spinid) spinid="basicspin"
	$("#"+spinid).html("<img src='/images/icons/hourglass-sand-top--v1.png' height=18 class='fa-spin'>")
}

function stopSpin(spinid, status) {
	if (!spinid) spinid="basicspin"
	console.log("stopSpin" + spinid);
	if (status == 'OK') $("#"+spinid).html("<i class='fa fa-check'>OK</i>");
	if (status == 'KO') $("#"+spinid).html("<i class='fa fa-times'>KO</i>");
	if (status == 'BLANK') $("#"+spinid).html("");
}



// INSERIMENTO VALUTAZIONE
$(document).delegate(".starvalutazione", "click", function(){
	var valutazione = parseInt($(this).attr("valutazione"));
	var tipologia = $(this).attr("tipologia");
	var idelaborato = $("#idelaborato").val();
	$(".starvalutazione[tipologia="+tipologia+"]").removeClass("text-warning");
	for (var i=1; i<=valutazione; i++) {
		console.log("I="+i);
		$(".starvalutazione[tipologia="+tipologia+"][valutazione="+i+"]").addClass("text-warning");
	}

	$.ajax({
	  type: "POST",			// il method
	  url: "/setvalutazione",	// la action
	  dataType: "json",
	  data: {
		"idelaborato": idelaborato,
		"valutazione": valutazione,
		"tipologia": tipologia,
	  },
	  error: function(){ alert("Ops! Si è verificato un errore");},
	}); 

	
});








function GonLoad() {
    gapi.load('auth2', function() {
    gapi.auth2.init();
  });
}

function GsignOut() {
	var auth2 = gapi.auth2.getAuthInstance();
	auth2.signOut().then(function () {
	  console.log('User signed out.');
	});

}

function init() {
	console.log("call init");
	gapi.load('auth2', function() {
		gapi.auth2.init();
	});
}

$(document).delegate("#link_logout", "click", function(){
	GsignOut();
	GsignOut();
	location = "/logout";
});


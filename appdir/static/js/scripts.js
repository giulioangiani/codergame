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


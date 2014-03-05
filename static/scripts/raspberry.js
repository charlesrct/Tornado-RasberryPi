var ipDir = '//192.168.1.111:5000';  //IP Oficina  
//var ipDir = '//192.168.0.9:5000';	//IP Casa

$(document).ready(function() {
	document.session = $('#session').val();
	setTimeout(requestRaspberry, 100);
	$('#add-button').click(function(event) {
		jQuery.ajax({
			url: ipDir + '/led',
			type: 'POST',
			data: {
				session: document.session,
				action: 'ledon'
			},
			dataType: 'json',
			beforeSend: function(xhr, settings) {
			},
			success: function(data, status, xhr) {
			}
		});
	});

$('#remove-button').click(function(event) {
	jQuery.ajax({
		url: ipDir + '/led',
		type: 'POST',
		data: {
			session: document.session,
			action: 'ledoff'
		},
		dataType: 'json',
		beforeSend: function(xhr, settings) {
		},
		success: function(data, status, xhr) {
		}
	});
	});

});

function requestRaspberry() {
	var host = 'ws:'+ipDir+'/status';
	
	var websocket = new WebSocket(host);

	websocket.onopen = function (evt) { };
	websocket.onmessage = function(evt) {

		//console.log($.parseJSON(evt.data))

		if ($.parseJSON(evt.data)['estado'] != "-1") {
			$('#estado').html($.parseJSON(evt.data)['estado']);
		};

		if($.parseJSON(evt.data)['ledStdo'] == 0){
			$('#led-off').hide();
			$('#led-on').show();
			$('.count').html($.parseJSON(evt.data)['ledStdo']);
		}
		
		if($.parseJSON(evt.data)['ledStdo'] == 1){
			$('#led-off').show();
			$('#led-on').hide();
			$('.count').html($.parseJSON(evt.data)['ledStdo']);
		}
		
		if($.parseJSON(evt.data)['distancia'] > 0){
			$('#dist').html($.parseJSON(evt.data)['distancia']);
		}

	};
	websocket.onerror = function (evt) { };
}